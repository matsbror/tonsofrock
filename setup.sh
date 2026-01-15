#!/bin/bash
# Setup script for Ticketmaster Monitor (Selenium version)

echo "Ticketmaster Monitor Setup"
echo "=============================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"
echo ""

# Install Chrome/Chromium if not present
echo "Checking for Chrome/Chromium..."
if ! command -v chromium-browser &> /dev/null && ! command -v google-chrome &> /dev/null; then
    echo "Installing Chromium and ChromeDriver..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y chromium-browser chromium-chromedriver
    else
        echo "Please install Chrome/Chromium and ChromeDriver manually"
    fi
else
    echo "Chrome/Chromium found"
fi
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully"
else
    echo "Failed to install dependencies"
    exit 1
fi

echo ""
echo "=============================="
echo "Setup complete!"
echo ""
echo "To start monitoring, run:"
echo "  python3 ticketmaster_selenium.py"
echo ""
echo "To run in background:"
echo "  nohup python3 ticketmaster_selenium.py > monitor.log 2>&1 &"
echo ""
echo "To check if it's running:"
echo "  ps aux | grep ticketmaster"
echo ""
echo "To stop it:"
echo "  pkill -f ticketmaster_selenium"
echo ""
echo "=============================="
