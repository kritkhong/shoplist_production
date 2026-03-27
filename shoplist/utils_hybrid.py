from datetime import date, datetime
from dotenv import load_dotenv
import os
import time
import subprocess
import atexit
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Global variable to track Chrome debug session
chrome_debug_process = None

def ensure_chrome_debug_session():
    """Ensure Chrome is running with debug port"""
    global chrome_debug_process
    
    # Check if Chrome debug is already running
    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        test_driver = webdriver.Chrome(options=chrome_options)
        test_driver.quit()
        print("[utils]: Chrome debug session already running")
        return True
    except:
        print("[utils]: Starting new Chrome debug session...")
        
        # Kill any existing Chrome
        subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
        time.sleep(2)
        
        # Start Chrome with debug port
        chrome_cmd = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "--remote-debugging-port=9222",
            "--user-data-dir=/tmp/chrome_dev_session",
            "--no-first-run",
            "--no-default-browser-check"
        ]
        
        chrome_debug_process = subprocess.Popen(
            chrome_cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        time.sleep(5)
        return False

def cleanup_chrome():
    """Cleanup Chrome process on exit"""
    global chrome_debug_process
    if chrome_debug_process:
        chrome_debug_process.terminate()

# Register cleanup
atexit.register(cleanup_chrome)

def get_session_info(target_date: date) -> list:
    """
    Main function called by views.py
    Handles Cloudflare by using persistent Chrome session
    """
    
    if ('RENDER' not in os.environ):  # local development
        print("[utils.get_session_info]: initiated on LOCAL...")
        load_dotenv()
    else:
        print("[utils.get_session_info]: initiated on RENDER...")
        # On Render, fallback to headless
        return get_session_info_headless(target_date)
    
    # Ensure Chrome debug session is running
    is_existing = ensure_chrome_debug_session()
    
    # Connect to Chrome debug session
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the page
        driver.get('https://mickeycafe19.vrich619.com/sale')
        time.sleep(3)
        
        # Check if we need to login
        needs_login = False
        try:
            driver.find_element(By.NAME, 'username')
            needs_login = True
        except:
            # Already logged in
            pass
        
        if needs_login:
            if not is_existing:
                # First time - need manual intervention
                print("\n" + "="*60)
                print("FIRST TIME SETUP - MANUAL LOGIN REQUIRED")
                print("="*60)
                print("1. Complete Cloudflare verification in Chrome")
                print("2. Enter username and password")
                print("3. Click Sign In")
                print("="*60)
                input("\nPress Enter after logging in...")
            else:
                # Try automated login (session expired)
                try:
                    wait = WebDriverWait(driver, timeout=10)
                    input_user = wait.until(EC.element_to_be_clickable((By.NAME, 'username')))
                    input_user.clear()
                    input_user.send_keys(os.environ['VRICH_USER'])
                    
                    input_pass = driver.find_element(By.NAME, 'password')
                    input_pass.clear()
                    input_pass.send_keys(os.environ['VRICH_PASS'])
                    
                    button = driver.find_element(By.XPATH, '//button[text()=\'Sign In\']')
                    driver.execute_script("arguments[0].click();", button)
                    print('[utils.get_session_info]: Auto-login attempted...')
                    time.sleep(3)
                except:
                    print("\n[utils]: Auto-login failed, manual intervention needed")
                    input("Please login manually and press Enter...")
        
        # Now we should be logged in - continue with data extraction
        wait = WebDriverWait(driver, timeout=10)
        
        # Toggle sales-monitor view if needed
        try:
            is_product_list = driver.find_element(By.ID, 'product-list').is_displayed()
            if is_product_list:
                print('[utils.get_session_info]: toggle sales monitor view...')
                monitor_toggle = driver.find_element(By.ID, 'monitor-toggle')
                if monitor_toggle:
                    monitor_toggle.click()
                    time.sleep(2)
        except:
            pass
        
        # Handle date selection
        sale_date_ele = driver.find_element(By.ID, 'search_date')
        date_str = sale_date_ele.get_attribute('value')
        target_date_str = target_date.strftime("%d/%m/%Y")
        
        wait.until(lambda d: d.find_element(
            By.XPATH, '//li[@class=\'monitor-item\'][1]').is_displayed())
        
        first_item_id = driver.find_element(
            By.XPATH, '//li[@class=\'monitor-item\'][1]').get_attribute('id')
        
        if target_date_str == date_str:
            print('[utils.get_session_info]: sale date correct, continue...')
        else:
            print('[utils.get_session_info]: changing sale date...')
            sale_date_ele.clear()
            sale_date_ele.send_keys(target_date_str)
            sale_date_ele.send_keys(Keys.ENTER)
            
            wait.until(lambda d: d.find_element(
                By.XPATH, '//li[@class=\'monitor-item\'][1]').get_attribute('id') != first_item_id)
        
        # Extract data
        monitor_items = driver.find_elements(
            By.XPATH, '//li[@class=\'monitor-item\']')
        print(f'[utils.get_session_info]: Total monitor-items found = {len(monitor_items)}')
        
        output = []
        for monitor_item in monitor_items:
            code = monitor_item.get_attribute('data-code')
            caption = monitor_item.get_attribute('data-description')
            count = monitor_item.get_attribute('data-details_count')
            output.append((code, caption, count))
        
        print(f'[utils.get_session_info]: Sending output len = {len(output)}')
        
        # Don't quit - keep session alive for next call
        # driver.quit()
        
        return output
        
    except Exception as e:
        print(f"[utils.get_session_info]: Error: {e}")
        # Fallback to headless if attach fails
        return get_session_info_headless(target_date)


def get_session_info_headless(target_date: date) -> list:
    """
    Fallback headless version for Render deployment
    This will likely fail with Cloudflare but included for completeness
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get('https://mickeycafe19.vrich619.com/sale')
        
        # Try to login (will likely fail with Cloudflare)
        input_user = driver.find_element(By.NAME, 'username')
        input_user.send_keys(os.environ['VRICH_USER'])
        input_pass = driver.find_element(By.NAME, 'password')
        input_pass.send_keys(os.environ['VRICH_PASS'])
        button = driver.find_element(By.XPATH, '//button[text()=\'Sign In\']')
        button.click()
        
        # Rest of the extraction logic...
        # (same as above)
        
        return []
        
    except Exception as e:
        print(f"[utils.get_session_info_headless]: Error: {e}")
        return []
    finally:
        driver.quit()