import requests
from bs4 import BeautifulSoup
import time
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Setting up Chrome WebDriver
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode if needed
chrome_service = Service(executable_path=r"C:/Users/mayurbpa/Downloads/chromedriver-win32/chromedriver-win32/chromedriver.exe")

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Flag to track if the terms and conditions popup has been handled
popup_handled = False

# Setup logging configuration
logging.basicConfig(
    filename="scrape_progress.log", 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# File to store the last successfully scraped page number
PROGRESS_FILE = "progress.txt"

def handle_terms_and_conditions():
    global popup_handled  # Use the global variable to keep track of the popup
    if not popup_handled:  # Only handle the popup if it hasn't been handled yet
        try:
            # Wait for the "I AGREE" button and click it
            agree_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='forced-modal-accept']"))
            )
            agree_button.click()
            time.sleep(10)  # Give time for the page to refresh
            popup_handled = True  # Set the flag to True after handling the popup
            print("Agreed to the Terms & Conditions")
        except Exception as e:
            logging.error(f"Terms & Conditions popup not found or an error occurred: {e}")
            print(f"Error: {e}")

def get_last_scraped_page():
    """Reads the last scraped page number from the progress file."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 1  # Start from page 1 if file is corrupted or empty
    return 1  # Start from page 1 if the progress file doesn't exist

def update_progress(page_number):
    """Updates the progress file with the last successfully scraped page number."""
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(page_number))

def scrape_cpa_names(output_file="names.txt", pages=6000, max_retries=3):
    base_url = "https://www.letsmakeaplan.org/find-a-cfp-professional?Location=&limit=10&pg={}&sort=random&randomKey=65&latitude=&longitude=&location_name=&postalCodeExact=&cityExact=&stateExact=&distance=25&planning_services=&last_name="

    last_scraped_page = get_last_scraped_page()  # Get the last scraped page number
    logging.info(f"Resuming from page {last_scraped_page}...")

    with open(output_file, "a") as f:  # Use 'a' mode to append to the file
        for page in range(last_scraped_page, pages + 1):
            url = base_url.format(page)
            logging.info(f"Scraping page {page}...")  # Log the page number
            print(f"Scraping page {page}...")

            retry_count = 0
            while retry_count < max_retries:
                try:
                    driver.get(url)
                    
                    # Handle Terms and Conditions Popup if present
                    handle_terms_and_conditions()

                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # Extracting names based on the new HTML structure
                    for name_tag in soup.find_all('div', class_='h5 find-cfp-item-name'):
                        name = name_tag.get_text(strip=True)
                        f.write(name + "\n")
                        logging.info(f"Scraped: {name}")  # Log each name scraped
                        print(f"Scraped: {name}")
                    
                    time.sleep(20)  # Delay between pages to avoid overloading the server
                    
                    # Update progress after successfully scraping a page
                    update_progress(page)
                    logging.info(f"Successfully scraped page {page}")  # Log success
                    break  # Exit retry loop on success

                except (TimeoutException, WebDriverException) as e:
                    # Handle connection errors, timeouts, or server issues
                    retry_count += 1
                    logging.error(f"Error scraping page {page}, retrying {retry_count}/{max_retries}: {e}")
                    print(f"Error scraping page {page}: {e}. Retrying {retry_count}/{max_retries}...")
                    time.sleep(10 * retry_count)  # Exponential backoff before retry

                if retry_count == max_retries:
                    logging.error(f"Failed to scrape page {page} after {max_retries} attempts.")
                    print(f"Failed to scrape page {page} after {max_retries} attempts.")
                    return  # Exit if retries are exhausted

if __name__ == "__main__":
    try:
        scrape_cpa_names(output_file="cpa_names.txt", pages=6000)
    finally:
        driver.quit()  # Ensure driver quits after scraping
