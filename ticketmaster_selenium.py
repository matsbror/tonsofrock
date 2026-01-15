#!/usr/bin/env python3
"""
Ticketmaster Monitor for Tons of Rock 2026 VIP Thursday Tickets
Selenium-based version that uses a real browser to bypass bot protection
"""

import time
import subprocess
import platform
import sys
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
except ImportError:
    print("Selenium not installed. Install with: pip install selenium")
    sys.exit(1)

# Configuration
URL = "https://www.ticketmaster.no/event/1517649920"
CHECK_INTERVAL = 300  # 5 minutes (300 seconds)
PAGE_LOAD_TIMEOUT = 30  # seconds to wait for page to load


def is_wsl():
    """Check if running under Windows Subsystem for Linux"""
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except:
        return False


def send_notification(title, message):
    """Send a desktop notification based on the operating system"""
    system = platform.system()
    running_in_wsl = is_wsl()

    # Always print prominent console alert
    print("\n" + "!" * 60)
    print(f"!!! {title} !!!")
    print(f"!!! {message}")
    print("!" * 60 + "\n")

    try:
        if running_in_wsl:
            # WSL: Use PowerShell to show Windows notification
            # Escape quotes for PowerShell
            safe_title = title.replace("'", "''").replace('"', '`"')
            safe_message = message.replace("'", "''").replace('"', '`"')
            subprocess.run([
                "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                f'Add-Type -AssemblyName System.Windows.Forms; '
                f'[System.Windows.Forms.MessageBox]::Show("{safe_message}", "{safe_title}", "OK", "Information")'
            ])
            print("Windows notification sent (via WSL)")

        elif system == "Linux":
            result = subprocess.run(
                ["notify-send", "-u", "critical", "-t", "0", title, message],
                capture_output=True
            )
            if result.returncode == 0:
                print("Desktop notification sent")
            # Try to play sound
            subprocess.run(
                ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL
            )

        elif system == "Darwin":
            script = f'display notification "{message}" with title "{title}" sound name "Glass"'
            subprocess.run(["osascript", "-e", script])
            print("Desktop notification sent")

        elif system == "Windows":
            subprocess.run([
                "powershell", "-Command",
                f'[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms"); '
                f'[System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'
            ])
            print("Desktop notification sent")

    except Exception:
        pass  # Console alert already printed above


def create_driver():
    """Create and configure a Chrome WebDriver"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Disable automation flags to appear more human-like
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        return driver
    except WebDriverException as e:
        print(f"Failed to create Chrome driver: {e}")
        print("Make sure Chrome/Chromium and ChromeDriver are installed:")
        print("  Ubuntu/Debian: sudo apt-get install chromium-browser chromium-chromedriver")
        print("  Or try Firefox: pip install selenium and install geckodriver")
        return None


def check_tickets():
    """Check if Thursday VIP resale tickets are available using Selenium"""
    driver = None
    try:
        driver = create_driver()
        if not driver:
            return None, "Could not create browser driver"

        print(f"  Loading page...")
        driver.get(URL)

        # Wait for page to load
        time.sleep(5)

        # Get page content
        page_source = driver.page_source.lower()

        # Look for Thursday/Torsdag day selector buttons
        thursday_found = False
        thursday_enabled = False
        thursday_status = "not found"

        try:
            # Find day selector buttons - look for elements with TORSDAG text
            # These are typically in a day picker/selector component
            thursday_elements = driver.find_elements(
                By.XPATH,
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'torsdag')]"
            )

            for elem in thursday_elements:
                thursday_found = True

                # Get the element and ancestor HTML to check for disabled state
                elem_html = elem.get_attribute("outerHTML").lower()

                # Walk up to check parent containers (up to 5 levels)
                current = elem
                ancestor_html = ""
                for _ in range(5):
                    try:
                        current = current.find_element(By.XPATH, "..")
                        ancestor_html += current.get_attribute("outerHTML").lower()
                    except:
                        break

                # Check for disabled/unavailable indicators in element and ancestors
                disabled_indicators = [
                    "disabled", "unavailable", "sold-out", "soldout",
                    "sold out", "utsolgt", "ikke tilgjengelig",
                    "opacity: 0.5", "opacity:0.5", "pointer-events: none",
                    "cursor: not-allowed", "btn--disabled", "is-disabled"
                ]

                # Check element's own attributes
                elem_class = elem.get_attribute("class") or ""
                elem_disabled = elem.get_attribute("disabled")
                elem_aria_disabled = elem.get_attribute("aria-disabled")

                is_disabled = (
                    elem_disabled == "true" or
                    elem_disabled == "" or  # disabled attribute present without value
                    elem_aria_disabled == "true" or
                    any(ind in elem_html for ind in disabled_indicators) or
                    any(ind in elem_class.lower() for ind in disabled_indicators)
                )

                # Also check if parent/wrapper has disabled styling
                parent_disabled = any(ind in ancestor_html for ind in disabled_indicators)

                if is_disabled or parent_disabled:
                    thursday_status = "disabled/sold out"
                else:
                    # Element appears to be enabled - this could mean tickets available
                    thursday_enabled = True
                    thursday_status = "possibly available"
                    break

        except Exception as e:
            print(f"  Warning checking elements: {e}")

        # Only report as available if we found a Thursday element that is NOT disabled
        if thursday_enabled:
            return True, f"Thursday button appears ENABLED - check manually: {URL}"

        if thursday_found:
            return False, f"Thursday found but {thursday_status}"

        return False, "Thursday section not found on page"

    except TimeoutException:
        return None, "Page load timeout"
    except WebDriverException as e:
        return None, f"Browser error: {e}"
    except Exception as e:
        return None, f"Error: {e}"
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def main():
    """Main monitoring loop"""
    print("=" * 60)
    print("Ticketmaster Monitor - Tons of Rock 2026 (Selenium)")
    print("Monitoring VIP Thursday Resale Tickets")
    print("=" * 60)
    print(f"URL: {URL}")
    print(f"Check interval: {CHECK_INTERVAL} seconds ({CHECK_INTERVAL/60:.1f} minutes)")
    print("Looking for: Thursday/Torsdag VIP Resale tickets")
    print("=" * 60)
    print()

    # Test driver creation
    print("Testing browser setup...")
    test_driver = create_driver()
    if test_driver:
        test_driver.quit()
        print("Browser setup OK")
    else:
        print("Browser setup FAILED - exiting")
        sys.exit(1)
    print()

    tickets_were_available = False
    check_count = 0

    while True:
        check_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{timestamp}] Check #{check_count}")

        available, message = check_tickets()

        if available is None:
            print(f"  Warning: {message}")
        elif available:
            print(f"  FOUND: {message}")
            if not tickets_were_available:
                send_notification(
                    "Tickets Available!",
                    f"Thursday VIP resale tickets may be available!\n{URL}"
                )
                tickets_were_available = True
                print(f"  Increasing check frequency to every 60 seconds")
                time.sleep(60)
                continue
        else:
            print(f"  Status: {message}")
            if tickets_were_available:
                send_notification(
                    "Tickets Status Changed",
                    "Thursday tickets status changed - may have been sold"
                )
                tickets_were_available = False

        print(f"  Next check in {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)
