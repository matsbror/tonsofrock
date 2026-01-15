# Ticketmaster Monitor for Tons of Rock 2026

This script monitors the Ticketmaster page for VIP Thursday resale tickets at Tons of Rock 2026 and sends you desktop notifications when tickets become available.

Uses Selenium with a headless Chrome browser to bypass Ticketmaster's bot protection.

## Features

- Automatically checks for Thursday VIP resale tickets every 5 minutes
- Uses real browser (Selenium) to bypass bot detection
- Sends desktop notifications when tickets are detected
- Works on Linux, macOS, and Windows
- Shows monitoring status with timestamps
- Increases check frequency when tickets are found

## Installation

### 1. Install Chrome/Chromium and ChromeDriver

**Linux (Ubuntu/Debian/WSL):**
```bash
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver
```

**macOS:**
```bash
brew install chromedriver
```

**Windows:**
Download ChromeDriver from https://chromedriver.chromium.org/ and add to PATH.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install selenium
```

### 3. System-Specific Notification Setup

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libnotify-bin
```

**macOS:** Notifications work natively.

**Windows:** Notifications work through PowerShell (Windows 10+).

## Usage

### Basic Usage
```bash
python3 ticketmaster_selenium.py
```

### Running in Background (Linux/macOS)
```bash
# Run in background
nohup python3 ticketmaster_selenium.py > monitor.log 2>&1 &

# Check the process
ps aux | grep ticketmaster

# View logs
tail -f monitor.log

# Stop the monitor
pkill -f ticketmaster_selenium
```

### Running as a Service (Linux systemd)

Create `/etc/systemd/system/ticketmaster-monitor.service`:

```ini
[Unit]
Description=Ticketmaster Monitor for Tons of Rock
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/script
ExecStart=/usr/bin/python3 /path/to/script/ticketmaster_selenium.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ticketmaster-monitor
sudo systemctl start ticketmaster-monitor
sudo systemctl status ticketmaster-monitor
```

## Configuration

Edit `ticketmaster_selenium.py` to change:

```python
CHECK_INTERVAL = 300  # Check every 5 minutes (300 seconds)
URL = "https://www.ticketmaster.no/event/1517649920"
```

## Troubleshooting

### ChromeDriver Not Found
```bash
# Check if installed
which chromedriver

# On Ubuntu/Debian, install with:
sudo apt-get install chromium-chromedriver
```

### Notifications Not Working

**Linux:**
```bash
notify-send "Test" "This is a test notification"
```

**macOS:** Check System Preferences > Notifications

**Windows:** Ensure notifications are enabled in Settings

### Browser Errors

If you see "Failed to create Chrome driver":
1. Ensure Chrome/Chromium is installed
2. Ensure ChromeDriver version matches your Chrome version
3. Try running without headless mode for debugging

## How It Works

1. Opens a headless Chrome browser
2. Navigates to the Ticketmaster page
3. Waits for page to load
4. Searches for Thursday/Torsdag ticket elements
5. Checks if elements are enabled (not grayed out)
6. Sends notification when availability detected
7. Repeats every 5 minutes (or 1 minute when tickets found)

## License

Free to use and modify for personal use.
