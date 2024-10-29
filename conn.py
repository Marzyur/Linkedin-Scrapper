from selenium import webdriver
import urllib.parse
import time
import os
import logging
import random
import re
import json
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(
    filename="con.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Chrome setup
chrome_options = Options()
chrome_service = Service(executable_path=r"C:/Users/mayurbpa/Downloads/chromedriver-win32/chromedriver-win32/chromedriver.exe")
chrome_options.add_argument('--disable-webrtc')  # Disable WebRTC
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

driver.maximize_window()
# Function to load cookies
def load_cookies(driver, file_path):
    try:
        with open(file_path, "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        logging.info("Cookies loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading cookies from '{file_path}': {e}")

  # Start fresh after clearing cookies

# Function to validate and sanitize LinkedIn profile URLs
def sanitize_profile_url(url):
    logging.info("Sanitizing profile URL.")
    url = re.sub(r'\?.*$', '', url)  # Strip any query parameters
    try:
        clean_url = urllib.parse.unquote(url)
        if clean_url.startswith("https://www.linkedin.com/in/"):
            return clean_url
        else:
            logging.error(f"Invalid profile URL format: {clean_url}")
            return None
    except Exception as e:
        logging.error(f"Error sanitizing URL '{url}': {e}")
        return None

# Function to close any message overlay that might block clicks
def close_message_overlay(driver):
    try:
        close_button = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'msg-overlay-bubble-header__control msg-overlay-bubble-header__control--new-convo-btn artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view'))
        )
        close_button.click()
        logging.info("Message overlay closed.")
    except NoSuchElementException:
        logging.info("No message overlay to close.")
    except Exception as e:
        logging.error(f"Error while closing message overlay: {e}")

# Function to check for and click the direct 'Connect' button
def connect_direct(driver):
    try:
        # Wait for up to 15 seconds for the 'Connect' button
        direct_connect_button = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'artdeco-button--secondary') and contains(@class, 'pvs-profile-actions__action')]"))
        )
        aria_label = direct_connect_button.get_attribute("aria-label")
        button_id = direct_connect_button.get_attribute("id")
        logging.info(f"Found 'Connect' button with aria-label: {aria_label}, id: {button_id}")
        
        direct_connect_button.click()
        logging.info("Direct 'Connect' button clicked.")
        return True
    except NoSuchElementException:
        logging.info("Direct 'Connect' button not found.")
        return False
    except Exception as e:
        logging.error(f"Error clicking direct 'Connect' button: {e}")
        return False

# Function to click 'More' and 'Connect' buttons if direct 'Connect' button isn't found
def connect_after_more(driver):
    try:
        # Click the 'More' button
        more_button = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'artdeco-dropdown__trigger--placement-bottom'))
        )
        more_button.click()
        logging.info("'More' button clicked.")

        # Wait for the 'Connect' button in the dropdown and click it
        connect_button = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Connect']/ancestor::button"))
        )
        connect_button.click()
        logging.info("'Connect' button clicked successfully.")
        time.sleep(2)
    except NoSuchElementException:
        logging.error("No 'Connect' button found in 'More' dropdown.")
    except Exception as e:
        logging.error(f"Error clicking 'Connect' button in 'More' dropdown: {e}")

# Main function to connect with profiles
def connect_with_profile(driver, profile_url, note=None):
    try:
        profile_url = sanitize_profile_url(profile_url)
        if not profile_url:
            logging.error(f"Invalid profile URL: {profile_url}")
            return
        
        driver.get(profile_url)
        time.sleep(random.uniform(3, 7))  # Wait for profile page to load 

        logging.info(f"Attempting to connect with profile: {profile_url}")
        
        # Close any overlay that might obstruct the click
        close_message_overlay(driver)
        
        # First, try the direct 'Connect' button
        if not connect_direct(driver):
            # If direct 'Connect' button is not available, fall back to 'More' button approach
            connect_after_more(driver)
        
        try:
            
            send_without_note_button=WebDriverWait(driver,50).until(
                EC.element_to_be_clickable((By.XPATH,"//span[text()='Send without a note']/ancestor::button"))
            )
            send_without_note_button.click()
            time.sleep(10)
            logging.info("Sending connection request")
        except Exception as e:
            logging.error(f"Could not send connection request:{e}")

        # Add a note if provided
        if note:
            
            try:
                # Click 'Add a note' using the custom XPath and class details provided
                add_note_button = WebDriverWait(driver, 50).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@aria-label='Add a note']"))
                )
                add_note_button.click()
                time.sleep(10)

                # Add note text
                note_textarea = WebDriverWait(driver, 50).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "//*[@id='custom-message']"))
                )
                note_textarea.send_keys(note)
                time.sleep(10)

                # Send the connection request using the custom XPath and class details for the 'Send' button
                send_button = WebDriverWait(driver, 50).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@aria-label='Send invitation']"))
                )
                send_button.click()
                logging.info(f"Sent connection request to: {profile_url} with note.")
            except NoSuchElementException:
                logging.error("No 'Add a note' button found.")
            except Exception as e:
                logging.error(f"Error sending connection request with note: {e}")
        else:
            logging.info(f"No note provided. Sending connection request without a note.")
    except Exception as e:
        logging.error(f"Unexpected error interacting with: {profile_url}, Error: {e}")

if __name__ == "__main__":
    try:
        driver.delete_all_cookies()
        driver.get("https://www.linkedin.com")
        # Load cookies if available
        if os.path.exists("linkedin_cookies.json"):
            load_cookies(driver, "linkedin_cookies.json")
            driver.refresh()
        else:
            logging.error("Cookies file not found. Please log in manually.")
            exit(1)

        # Read profiles from file
        with open("matched_profiles.txt", "r") as f:
            profiles = [line.strip().split(": ")[1] for line in f.readlines()]

        # Connection note
        connection_note = "Hi, I would like to connect with you to discuss potential opportunities."

        # Loop through profiles and send connection requests
        for profile_url in profiles:
            connect_with_profile(driver, profile_url, connection_note)
            time.sleep(random.uniform(5, 10))  # Random wait between each request

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()
