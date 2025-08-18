#!/bin/bash
# Setup script for Raspberry Pi 5 Akari Puzzle Generator

echo "🎯 Setting up Akari Puzzle Generator on Raspberry Pi 5..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip
echo "🐍 Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install MySQL client
echo "🗄️ Installing MySQL client..."
sudo apt install -y mysql-client

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

# Set up cron job for automatic generation
echo "⏰ Setting up automatic puzzle generation..."
cron_job="0 2 * * * cd $(pwd) && source akari_env/bin/activate && python3 akari_generator.py --mode premium --sizes 6 8 10 12 --difficulties easy medium hard --count 5 >> logs/cron.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null; echo "$cron_job") | crontab -

echo "✅ Setup complete!"
echo ""
echo "🚀 Usage examples:"
echo ""
echo "Generate premium puzzles:"
echo "python3 akari_generator.py --mode premium --sizes 6 8 10 12 --difficulties easy medium hard --count 10"
echo ""
echo "Generate ebook puzzles:"
echo "python3 akari_generator.py --mode ebook --sizes 6 8 10 12 --count 20 --output ebooks/akari_collection.json"
echo ""
echo "Generate daily puzzles:"
echo "python3 akari_generator.py --mode daily --sizes 6 8 --difficulties medium --count 7"
echo ""
echo "📊 Monitor generation:"
echo "tail -f logs/akari_generator.log"
echo ""
echo "⏰ Automatic generation runs daily at 2 AM"
