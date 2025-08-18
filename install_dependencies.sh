#!/bin/bash
# Install Python dependencies for Akari Puzzle Generator

echo "📦 Installing Python dependencies for Akari Puzzle Generator..."

# Check if we're in an externally managed environment
if python3 -c "import sys; print('externally-managed' in sys.modules)" 2>/dev/null | grep -q "True"; then
    echo "🔧 Detected externally managed environment. Creating virtual environment..."
    
    # Install python3-venv if not already installed
    if ! dpkg -l | grep -q python3-venv; then
        echo "📥 Installing python3-venv..."
        sudo apt update
        sudo apt install -y python3-venv python3-full
    fi
    
    # Create virtual environment
    echo "🏗️ Creating virtual environment..."
    python3 -m venv akari_env
    
    # Activate virtual environment
    echo "🔌 Activating virtual environment..."
    source akari_env/bin/activate
    
    # Update pip in virtual environment
    pip install --upgrade pip
    
    # Install required packages in virtual environment
    echo "📚 Installing packages in virtual environment..."
    pip install reportlab==4.0.4
    pip install requests==2.31.0
    
    echo "✅ Dependencies installed in virtual environment!"
    echo ""
    echo "📋 To use the puzzle generator:"
    echo "1. Activate the virtual environment:"
    echo "   source akari_env/bin/activate"
    echo ""
    echo "2. Run the polling client:"
    echo "   python3 rpi_polling_client_fixed.py"
    echo ""
    echo "3. Or run individual scripts:"
    echo "   python3 akari_generator_api.py"
    echo "   python3 ebook_generator.py"
    echo ""
    echo "📁 Virtual environment location: ./akari_env/"
    
else
    echo "🔧 Using system Python installation..."
    
    # Try to install via apt first
    echo "📥 Attempting to install via apt..."
    sudo apt update
    
    # Check if packages are available via apt
    if apt search python3-reportlab 2>/dev/null | grep -q "python3-reportlab"; then
        echo "📦 Installing reportlab via apt..."
        sudo apt install -y python3-reportlab
    else
        echo "⚠️ reportlab not available via apt, trying pip with --break-system-packages..."
        pip3 install --break-system-packages reportlab==4.0.4
    fi
    
    if apt search python3-requests 2>/dev/null | grep -q "python3-requests"; then
        echo "📦 Installing requests via apt..."
        sudo apt install -y python3-requests
    else
        echo "⚠️ requests not available via apt, trying pip with --break-system-packages..."
        pip3 install --break-system-packages requests==2.31.0
    fi
    
    echo "✅ Dependencies installed via system package manager!"
fi

echo ""
echo "🚀 Ready to generate ebooks!"
echo ""
echo "📋 Installed packages:"
echo "- reportlab==4.0.4 (for PDF generation)"
echo "- requests==2.31.0 (for API communication)"
