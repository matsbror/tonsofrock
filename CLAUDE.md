# Ticketmaster Monitor - Bash Guide

## Problem: 401 Unauthorized Error

The script is getting blocked by Ticketmaster's bot protection. Here are solutions:

---

## Solution 1: Use Selenium with Real Browser (RECOMMENDED)

Selenium opens a real browser, so Ticketmaster can't detect it as a bot.

### Install Dependencies

```bash
# Install Selenium
pip3 install selenium

# Install Chrome and ChromeDriver (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# OR for other systems:
# Arch: sudo pacman -S chromium chromedriver
# macOS: brew install chromedriver
# Windows: Download from https://chromedriver.chromium.org/
```

### Create Selenium Version

Create `ticketmaster_selenium.py`:

```python
#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import subprocess
from datetime import datetime

URL = "https://www.ticketmaster.no/event/1517649920"
CHECK_INTERVAL = 300  # 5 minutes

def notify(msg):
    try:
        subprocess.run(["notify-send", "-u", "critical", "Tickets!", msg])
    except:
        print(f"ALERT: {msg}")

def check():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    time.sleep(5)
    
    page_text = driver.page_source.lower()
    
    # Check if Thursday button is NOT disabled
    thursday_btns = driver.find_elements(By.XPATH, "//*[contains(text(), 'TORSDAG')]")
    
    for btn in thursday_btns:
        parent = btn.find_element(By.XPATH, "..")
        classes = parent.get_attribute("class") or ""
        
        # If button is NOT grayed/disabled AND resale exists
        if "disabled" not in classes.lower() and "resale" in page_text:
            driver.quit()
            return True
    
    driver.quit()
    return False

print(f"Monitoring {URL}")
while True:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking...")
    if check():
        print("✅ TICKETS FOUND!")
        notify(f"Thursday VIP resale tickets available!\n{URL}")
        time.sleep(60)  # Check every minute when found
    else:
        print("⏳ Still unavailable")
        time.sleep(CHECK_INTERVAL)
```

### Run It

```bash
chmod +x ticketmaster_selenium.py
python3 ticketmaster_selenium.py

# Or in background:
nohup python3 ticketmaster_selenium.py > monitor.log 2>&1 &
```

---

## Solution 2: Simple Curl + Browser Cookies (EASIER)

Instead of Python, use bash + curl with cookies from your real browser.

### Get Your Browser Cookies

1. Open the Ticketmaster page in Chrome/Firefox
2. Press F12 (Developer Tools)
3. Go to "Network" tab
4. Refresh the page
5. Click on the first request
6. Copy the "Cookie" header value

### Create Bash Script

Create `monitor.sh`:

```bash
#!/bin/bash

URL="https://www.ticketmaster.no/event/1517649920"
INTERVAL=300  # 5 minutes

# PASTE YOUR COOKIES HERE (from browser dev tools)
COOKIES="YOUR_COOKIES_HERE"

while true; do
    echo "[$(date '+%H:%M:%S')] Checking..."
    
    # Fetch page with cookies
    PAGE=$(curl -s "$URL" \
        -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0" \
        -H "Cookie: $COOKIES" \
        -H "Accept: text/html" \
        -H "Accept-Language: en-US,en;q=0.9")
    
    # Check if Thursday button is enabled (not grayed)
    if echo "$PAGE" | grep -qi "torsdag"; then
        # Look for signs it's available
        if echo "$PAGE" | grep -qi "resale" && ! echo "$PAGE" | grep -qi "disabled.*torsdag"; then
            echo "✅ TICKETS MAY BE AVAILABLE!"
            notify-send -u critical "Tickets Available!" "Check: $URL"
            sleep 60  # Check every minute when found
        else
            echo "⏳ Still unavailable"
            sleep $INTERVAL
        fi
    else
        echo "⚠️  Page structure changed or error"
        sleep $INTERVAL
    fi
done
```

### Run It

```bash
chmod +x monitor.sh
./monitor.sh

# Or in background:
nohup ./monitor.sh > monitor.log 2>&1 &
```

---

## Solution 3: Manual Browser + Notification Script (SIMPLEST)

Just keep the page open in your browser and use a simple script to check.

### Install Browser Extension (No coding!)

Use a browser extension like:
- **Distill Web Monitor** (Chrome/Firefox) - monitors page changes
- **Visualping** - tracks visual changes
- **Page Monitor** (Chrome)

### Or Use This Simple Checker

Create `simple_check.sh`:

```bash
#!/bin/bash
# Just checks if you can access the page

curl -I "https://www.ticketmaster.no/event/1517649920" 2>&1 | head -n 1

# If you get "200 OK", the page is accessible
# If you get "401 Unauthorized", there's an auth issue
```

---

## Testing Your Access

### Test 1: Can you access the page?

```bash
curl -I "https://www.ticketmaster.no/event/1517649920"
```

Expected: `HTTP/2 200` (success) or `HTTP/2 401` (blocked)

### Test 2: With browser headers

```bash
curl -s "https://www.ticketmaster.no/event/1517649920" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0" \
  -H "Accept: text/html" | head -n 50
```

If you see HTML, it's working. If you see error messages, it's blocked.

### Test 3: Check current ticket status

```bash
curl -s "https://www.ticketmaster.no/event/1517649920" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0" \
  | grep -i "torsdag" -A 5 -B 5
```

---

## Background Monitoring Commands

### Start monitoring in background

```bash
nohup python3 ticketmaster_selenium.py > monitor.log 2>&1 &
echo $! > monitor.pid  # Save process ID
```

### Check if it's running

```bash
ps aux | grep ticketmaster
# OR
cat monitor.pid | xargs ps -p
```

### View logs

```bash
tail -f monitor.log
```

### Stop monitoring

```bash
# Using saved PID
kill $(cat monitor.pid)

# OR find and kill
pkill -f ticketmaster
```

### Check status

```bash
# See recent log entries
tail -20 monitor.log

# Count checks performed
grep "Check #" monitor.log | wc -l
```

---

## Using systemd (Run as Service)

Create `/etc/systemd/system/ticketmaster.service`:

```ini
[Unit]
Description=Ticketmaster Monitor
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/script
ExecStart=/usr/bin/python3 /path/to/script/ticketmaster_selenium.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

### Commands

```bash
# Start service
sudo systemctl start ticketmaster

# Enable on boot
sudo systemctl enable ticketmaster

# Check status
sudo systemctl status ticketmaster

# View logs
sudo journalctl -u ticketmaster -f

# Stop service
sudo systemctl stop ticketmaster
```

---

## Troubleshooting

### 401 Unauthorized

**Problem:** Ticketmaster detects automated access

**Solutions:**
1. Use Selenium (opens real browser)
2. Copy cookies from your browser and add to curl
3. Use browser extension instead

### Can't install Selenium

```bash
# Try with --user flag
pip3 install --user selenium

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install selenium
```

### ChromeDriver not found

```bash
# Check if installed
which chromedriver

# Install manually
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
# Download matching version for your Chrome

# Or use Firefox instead (geckodriver)
pip3 install selenium
sudo apt-get install firefox-geckodriver
```

Then change in script: `webdriver.Firefox()` instead of Chrome

### Notifications not working

```bash
# Test notification
notify-send "Test" "This is a test"

# Install if missing
sudo apt-get install libnotify-bin

# Check if notification daemon is running
ps aux | grep notify
```

---

## Alternative: Use Telegram Bot

If you want notifications on your phone:

```bash
# Install telegram-send
pip3 install telegram-send

# Configure (follow prompts)
telegram-send --configure

# Test
telegram-send "Test message"
```

Replace `notify-send` in scripts with `telegram-send`.

---

## Quick Reference

```bash
# Start monitoring
python3 ticketmaster_selenium.py

# Start in background
nohup python3 ticketmaster_selenium.py > monitor.log 2>&1 &

# Check logs
tail -f monitor.log

# Stop
pkill -f ticketmaster

# Check if running
ps aux | grep ticketmaster

# Test notification
notify-send "Test" "This works!"
```

---

## Next Steps

1. Choose a solution (Selenium recommended)
2. Install dependencies
3. Create the script
4. Test it
5. Run in background
6. Monitor the logs

Good luck! 🎸
