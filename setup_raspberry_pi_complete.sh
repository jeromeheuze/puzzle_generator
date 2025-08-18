#!/bin/bash
# Complete Setup Script for Raspberry Pi 5 Akari Puzzle Generator
# Includes API server, CDN Bunny integration, and admin control

echo "🎯 Setting up Complete Akari Puzzle Generator on Raspberry Pi 5..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip
echo "🐍 Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv nginx

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3 -m venv akari_env
source akari_env/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p output
mkdir -p ebooks
mkdir -p config
mkdir -p ssl

# Create configuration file
echo "⚙️ Creating configuration file..."
cat > config/generator_config.json << EOF
{
    "api_url": "https://shrinepuzzle.com/api/puzzle_receiver.php",
    "api_key": "shrine_puzzle_api_key_2024",
    "default_sizes": [6, 8, 10, 12],
    "default_difficulties": ["easy", "medium", "hard", "expert"],
    "max_puzzles_per_batch": 50,
    "retry_attempts": 3,
    "retry_delay": 5,
    "cdn_bunny": {
        "storage_zone": "la.storage.bunnycdn.com",
        "api_key": "6d0c408d-5898-42d8-aaeb4a3965b1-c463-4e4c",
        "storage_zone_name": "shrinepuzzle",
        "region": "la"
    }
}
EOF

# Create systemd service for API server
echo "🔧 Creating systemd service for API server..."
cat > akari-api.service << EOF
[Unit]
Description=Akari Puzzle Generator API Server
After=network.target

[Service]
Type=simple
User=rpi
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/akari_env/bin
ExecStart=$(pwd)/akari_env/bin/python3 rpi_api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Install service
sudo cp akari-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable akari-api.service

# Set up nginx reverse proxy
echo "🌐 Setting up nginx reverse proxy..."
cat > akari-api.nginx << EOF
server {
    listen 80;
    server_name rpi-5-001.local;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo cp akari-api.nginx /etc/nginx/sites-available/akari-api
sudo ln -sf /etc/nginx/sites-available/akari-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

# Set up cron job for automatic generation
echo "⏰ Setting up automatic puzzle generation..."
cron_job="0 2 * * * cd $(pwd) && source akari_env/bin/activate && python3 akari_generator_api.py --mode premium --sizes 6 8 10 12 --difficulties easy medium hard --count 5 >> logs/cron.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null; echo "$cron_job") | crontab -

# Create test scripts
echo "🧪 Creating test scripts..."

# API connection test
cat > test_api_connection.py << EOF
#!/usr/bin/env python3
import requests
import json

def test_api_connection():
    api_url = "https://shrinepuzzle.com/api/puzzle_receiver.php"
    api_key = "shrine_puzzle_api_key_2024"
    
    # Test puzzle
    test_puzzle = {
        'layout': [[0, 0, 0], [0, 'X', 0], [0, 0, 0]],
        'seed': 'test_connection',
        'size': 3,
        'difficulty': 'easy',
        'mode': 'premium'
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {'puzzles': [test_puzzle]}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        print(f"API Test - Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"API Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing API connection...")
    success = test_api_connection()
    if success:
        print("✅ API connection successful!")
    else:
        print("❌ API connection failed!")
EOF

# CDN Bunny test
cat > test_cdn_bunny.py << EOF
#!/usr/bin/env python3
from cdn_bunny_uploader import CDNBunnyUploader
import json

def test_cdn_bunny():
    # Load config
    with open('config/generator_config.json', 'r') as f:
        config = json.load(f)
    
    if 'cdn_bunny' not in config:
        print("❌ CDN Bunny not configured")
        return False
    
    cdn_config = config['cdn_bunny']
    
    uploader = CDNBunnyUploader(
        storage_zone=cdn_config['storage_zone'],
        api_key=cdn_config['api_key'],
        storage_zone_name=cdn_config['storage_zone_name'],
        region=cdn_config['region']
    )
    
    # Test listing files
    result = uploader.list_files("ebooks")
    if result['success']:
        print("✅ CDN Bunny connection successful!")
        print(f"Found {len(result['files'])} files")
        return True
    else:
        print(f"❌ CDN Bunny test failed: {result['error']}")
        return False

if __name__ == "__main__":
    test_cdn_bunny()
EOF

chmod +x test_api_connection.py
chmod +x test_cdn_bunny.py

# Create monitoring script
cat > monitor_system.py << EOF
#!/usr/bin/env python3
import subprocess
import json
import os
from datetime import datetime

def get_system_info():
    info = {}
    
    # Disk usage
    try:
        disk = subprocess.check_output(['df', '-h', '/']).decode()
        info['disk'] = disk
    except:
        info['disk'] = 'Error getting disk info'
    
    # Memory usage
    try:
        memory = subprocess.check_output(['free', '-h']).decode()
        info['memory'] = memory
    except:
        info['memory'] = 'Error getting memory info'
    
    # Uptime
    try:
        uptime = subprocess.check_output(['uptime']).decode()
        info['uptime'] = uptime
    except:
        info['uptime'] = 'Error getting uptime'
    
    # Service status
    try:
        api_status = subprocess.check_output(['systemctl', 'is-active', 'akari-api.service']).decode().strip()
        info['api_service'] = api_status
    except:
        info['api_service'] = 'unknown'
    
    try:
        cron_status = subprocess.check_output(['systemctl', 'is-active', 'cron']).decode().strip()
        info['cron_service'] = cron_status
    except:
        info['cron_service'] = 'unknown'
    
    # Log file sizes
    log_files = ['logs/akari_generator_api.log', 'logs/rpi_api_server.log', 'logs/cron.log']
    info['log_sizes'] = {}
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            info['log_sizes'][log_file] = f"{size / 1024:.1f} KB"
        else:
            info['log_sizes'][log_file] = "Not found"
    
    return info

if __name__ == "__main__":
    info = get_system_info()
    print("System Information:")
    print(json.dumps(info, indent=2))
EOF

chmod +x monitor_system.py

# Create startup script
cat > start_services.sh << EOF
#!/bin/bash
echo "🚀 Starting Akari Puzzle Generator services..."

# Start API server
sudo systemctl start akari-api.service

# Check status
echo "📊 Service Status:"
sudo systemctl status akari-api.service --no-pager -l

echo "✅ Services started!"
echo "🌐 API available at: http://$(hostname -I | awk '{print $1}'):8080"
echo "📊 Monitor with: python3 monitor_system.py"
EOF

chmod +x start_services.sh

# Create backup script
cat > backup_config.sh << EOF
#!/bin/bash
echo "💾 Backing up configuration..."

backup_dir="backups/\$(date +%Y%m%d_%H%M%S)"
mkdir -p "\$backup_dir"

# Backup config files
cp -r config/ "\$backup_dir/"
cp *.log "\$backup_dir/" 2>/dev/null || true

# Backup ebooks
cp -r ebooks/ "\$backup_dir/" 2>/dev/null || true

echo "✅ Backup created: \$backup_dir"
EOF

chmod +x backup_config.sh

echo "✅ Complete setup finished!"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Configure CDN Bunny:"
echo "   Edit config/generator_config.json and add your CDN Bunny credentials"
echo ""
echo "2. Test connections:"
echo "   python3 test_api_connection.py"
echo "   python3 test_cdn_bunny.py"
echo ""
echo "3. Start services:"
echo "   ./start_services.sh"
echo ""
echo "4. Monitor system:"
echo "   python3 monitor_system.py"
echo ""
echo "5. Access admin dashboard:"
echo "   Visit: https://shrinepuzzle.com/admin/dashboard.php"
echo ""
echo "🔑 API Keys:"
echo "   Puzzle API: shrine_puzzle_api_key_2024"
echo "   Admin API: shrine_admin_key_2024"
echo "   RPi Control: rpi_control_key_2024"
echo ""
echo "📁 Important files:"
echo "   Config: config/generator_config.json"
echo "   Logs: logs/"
echo "   Ebooks: ebooks/"
echo "   API Server: rpi_api_server.py"
echo ""
echo "⏰ Automatic generation runs daily at 2 AM"
echo "🌐 API server runs on port 8080"
echo "📊 Monitor with: python3 monitor_system.py"
echo ""
echo "🔧 Management:"
echo "   Start API: sudo systemctl start akari-api.service"
echo "   Stop API: sudo systemctl stop akari-api.service"
echo "   Restart API: sudo systemctl restart akari-api.service"
echo "   View logs: sudo journalctl -u akari-api.service -f"
echo ""
echo "💾 Backup: ./backup_config.sh"
