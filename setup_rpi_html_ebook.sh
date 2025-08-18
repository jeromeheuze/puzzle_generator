#!/bin/bash
# Setup script for Raspberry Pi 5 HTML Ebook Generation System
# This script installs all dependencies and configures the system

set -e

echo "🎯 Setting up Raspberry Pi 5 HTML Ebook Generation System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as the 'pi' user."
   exit 1
fi

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    print_warning "This script is designed for Raspberry Pi. Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
print_status "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y nginx supervisor
sudo apt install -y git curl wget
sudo apt install -y build-essential libssl-dev libffi-dev

# Create project directory
PROJECT_DIR="/home/pi/shrinepuzzle.com/puzzle_generator"
print_status "Setting up project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install flask flask-cors requests
pip install beautifulsoup4 lxml
pip install pillow
pip install gunicorn

# Create required directories
print_status "Creating required directories..."
mkdir -p generated_ebooks
mkdir -p logs
mkdir -p temp

# Set proper permissions
print_status "Setting permissions..."
chmod 755 generated_ebooks
chmod 755 logs
chmod 755 temp

# Create configuration file
print_status "Creating configuration file..."
cat > config.json << EOF
{
    "api_url": "https://shrinepuzzle.com/api/puzzle_receiver.php",
    "api_key": "shrine_puzzle_api_key_2024",
    "output_dir": "./generated_ebooks",
    "log_file": "./html_ebook_generation.log",
    "cdn_bunny": {
        "storage_zone": "shrinepuzzle-ebooks",
        "api_key": "your_cdn_bunny_api_key_here",
        "pull_zone": "https://shrinepuzzle-ebooks.b-cdn.net"
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8080,
        "debug": false
    }
}
EOF

# Create log file
touch html_ebook_generation.log
chmod 644 html_ebook_generation.log

# Install systemd service
print_status "Installing systemd service..."
sudo cp rpi-html-ebook-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rpi-html-ebook-api.service

# Configure nginx (optional, for reverse proxy)
print_status "Configuring nginx..."
sudo tee /etc/nginx/sites-available/html-ebook-api << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/html-ebook-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

# Create firewall rules
print_status "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 8080/tcp
sudo ufw --force enable

# Create startup script
print_status "Creating startup script..."
cat > start_html_ebook_api.sh << 'EOF'
#!/bin/bash
cd /home/pi/shrinepuzzle.com/puzzle_generator
source venv/bin/activate
python rpi_html_ebook_api.py
EOF

chmod +x start_html_ebook_api.sh

# Create health check script
print_status "Creating health check script..."
cat > health_check.sh << 'EOF'
#!/bin/bash
# Health check script for HTML Ebook API

API_URL="http://localhost:8080/api/health"
LOG_FILE="/home/pi/shrinepuzzle.com/puzzle_generator/logs/health_check.log"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Check API health
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL" 2>/dev/null)

if [ "$response" = "200" ]; then
    echo "$(date): API is healthy (HTTP $response)" >> "$LOG_FILE"
    exit 0
else
    echo "$(date): API is unhealthy (HTTP $response)" >> "$LOG_FILE"
    # Restart service if unhealthy
    sudo systemctl restart rpi-html-ebook-api.service
    exit 1
fi
EOF

chmod +x health_check.sh

# Create cron job for health checks
print_status "Setting up health check cron job..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/pi/shrinepuzzle.com/puzzle_generator/health_check.sh") | crontab -

# Create cleanup script
print_status "Creating cleanup script..."
cat > cleanup_old_files.sh << 'EOF'
#!/bin/bash
# Cleanup script for old generated files

PROJECT_DIR="/home/pi/shrinepuzzle.com/puzzle_generator"
DAYS_TO_KEEP=7

echo "$(date): Starting cleanup of files older than $DAYS_TO_KEEP days..."

# Clean up old HTML files
find "$PROJECT_DIR/generated_ebooks" -name "*.html" -mtime +$DAYS_TO_KEEP -delete

# Clean up old log files
find "$PROJECT_DIR/logs" -name "*.log" -mtime +$DAYS_TO_KEEP -delete

# Clean up temp files
find "$PROJECT_DIR/temp" -name "*" -mtime +1 -delete

echo "$(date): Cleanup completed"
EOF

chmod +x cleanup_old_files.sh

# Add cleanup to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/pi/shrinepuzzle.com/puzzle_generator/cleanup_old_files.sh") | crontab -

# Test the installation
print_status "Testing installation..."
source venv/bin/activate

# Test Python imports
python3 -c "
import flask
import requests
import json
print('✓ All Python dependencies installed successfully')
"

# Start the service
print_status "Starting HTML Ebook API service..."
sudo systemctl start rpi-html-ebook-api.service

# Wait a moment for service to start
sleep 3

# Check service status
if sudo systemctl is-active --quiet rpi-html-ebook-api.service; then
    print_success "Service started successfully!"
else
    print_error "Service failed to start. Check logs with: sudo journalctl -u rpi-html-ebook-api.service"
fi

# Test API endpoint
print_status "Testing API endpoint..."
sleep 2
if curl -s http://localhost:8080/api/health > /dev/null; then
    print_success "API endpoint is responding!"
else
    print_warning "API endpoint not responding yet. It may take a moment to start."
fi

# Display final information
echo ""
print_success "Raspberry Pi 5 HTML Ebook Generation System setup completed!"
echo ""
echo "📋 System Information:"
echo "   • Service: rpi-html-ebook-api"
echo "   • API URL: http://localhost:8080"
echo "   • Nginx: http://$(hostname -I | awk '{print $1}')"
echo "   • Project Directory: $PROJECT_DIR"
echo "   • Log File: $PROJECT_DIR/html_ebook_generation.log"
echo ""
echo "🔧 Useful Commands:"
echo "   • Check service status: sudo systemctl status rpi-html-ebook-api"
echo "   • View logs: sudo journalctl -u rpi-html-ebook-api -f"
echo "   • Restart service: sudo systemctl restart rpi-html-ebook-api"
echo "   • Test API: curl http://localhost:8080/api/health"
echo ""
echo "⚠️  Next Steps:"
echo "   1. Update the CDN Bunny API key in config.json"
echo "   2. Test the API from your dashboard"
echo "   3. Monitor the logs for any issues"
echo ""

print_success "Setup completed successfully! 🎉"
