#!/bin/bash
# Install Python dependencies for Akari Puzzle Generator

echo "📦 Installing Python dependencies for Akari Puzzle Generator..."

# Update pip
pip3 install --upgrade pip

# Install required packages
pip3 install reportlab==4.0.4
pip3 install requests==2.31.0

echo "✅ Dependencies installed successfully!"
echo ""
echo "📋 Installed packages:"
echo "- reportlab==4.0.4 (for PDF generation)"
echo "- requests==2.31.0 (for API communication)"
echo ""
echo "🚀 Ready to generate ebooks!"
