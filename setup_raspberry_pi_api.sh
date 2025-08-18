#!/bin/bash
# Setup script for Raspberry Pi 5 Akari Puzzle Generator (API Version)

echo "🎯 Setting up Akari Puzzle Generator API on Raspberry Pi 5..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip
echo "🐍 Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv

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
    "retry_delay": 5
}
EOF

# Set up cron job for automatic generation
echo "⏰ Setting up automatic puzzle generation..."
cron_job="0 2 * * * cd $(pwd) && source akari_env/bin/activate && python3 akari_generator_api.py --mode premium --sizes 6 8 10 12 --difficulties easy medium hard --count 5 >> logs/cron.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null; echo "$cron_job") | crontab -

# Create test script
echo "🧪 Creating test script..."
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

chmod +x test_api_connection.py

echo "✅ Setup complete!"
echo ""
echo "🚀 Usage examples:"
echo ""
echo "Test API connection:"
echo "python3 test_api_connection.py"
echo ""
echo "Generate premium puzzles:"
echo "python3 akari_generator_api.py --mode premium --sizes 6 8 10 12 --difficulties easy medium hard --count 10"
echo ""
echo "Generate ebook puzzles:"
echo "python3 ebook_generator.py --sizes 6 8 10 12 --count 20 --output ebooks/akari_collection.json"
echo ""
echo "Generate daily puzzles:"
echo "python3 akari_generator_api.py --mode daily --sizes 6 8 --difficulties medium --count 7"
echo ""
echo "📊 Monitor generation:"
echo "tail -f logs/akari_generator_api.log"
echo ""
echo "⏰ Automatic generation runs daily at 2 AM"
echo ""
echo "🔑 API Configuration:"
echo "URL: https://shrinepuzzle.com/api/puzzle_receiver.php"
echo "Key: shrine_puzzle_api_key_2024"
echo ""
echo "📁 Configuration file: config/generator_config.json"
