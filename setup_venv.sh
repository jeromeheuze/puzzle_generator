#!/bin/bash
# Setup script for Raspberry Pi 5 Akari Puzzle Generator with Virtual Environment

echo "🎯 Setting up Akari Puzzle Generator on Raspberry Pi 5 with Virtual Environment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and virtual environment tools
echo "🐍 Installing Python and virtual environment tools..."
sudo apt install -y python3 python3-pip python3-venv python3-full

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3 -m venv akari_env

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source akari_env/bin/activate

# Install Python dependencies in virtual environment
echo "📚 Installing Python dependencies in virtual environment..."
pip install --upgrade pip
pip install reportlab==4.0.4
pip install requests==2.31.0

# Create directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p output
mkdir -p ebooks

# Set up systemd service
echo "⚙️ Setting up systemd service..."
sudo cp rpi-polling-venv.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rpi-polling-venv.service

echo "✅ Setup complete!"
echo ""
echo "🚀 Usage:"
echo ""
echo "1. Start the service:"
echo "   sudo systemctl start rpi-polling-venv.service"
echo ""
echo "2. Check service status:"
echo "   sudo systemctl status rpi-polling-venv.service"
echo ""
echo "3. View logs:"
echo "   sudo journalctl -u rpi-polling-venv.service -f"
echo ""
echo "4. Manual testing (activate virtual environment first):"
echo "   source akari_env/bin/activate"
echo "   python3 rpi_polling_client_fixed.py"
echo ""
echo "📊 Monitor generation:"
echo "tail -f logs/rpi_polling.log"
echo ""
echo "🎯 The service will automatically start on boot and restart if it fails."
