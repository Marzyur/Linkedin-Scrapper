import json
import time
import logging
import random
import os
import unicodedata
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Logging setup
logging.basicConfig(filename="search.log", level=logging.INFO)

# Setup Chrome WebDriver with options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Optional: Use this to run the browser in the background
chrome_service = Service(executable_path=r"C:/Users/mayurbpa/Downloads/chromedriver-win32/chromedriver-win32/chromedriver.exe")

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Function to clean up special characters from name
def clean_name(name):
    # Normalize the unicode characters to remove any encoding issues
    cleaned_name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    
    # Remove any characters that are not letters, numbers, spaces, commas, or periods
    cleaned_name = re.sub(r'[^a-zA-Z0-9\s,.]', '', cleaned_name)

    # Truncate the name at "CFP" or "CPA" (or any other professional designation if needed)
    if "CFP" in cleaned_name:
        cleaned_name = cleaned_name.split("CFP")[0] + "CFP"
    elif "CPA" in cleaned_name:
        cleaned_name = cleaned_name.split("CPA")[0] + "CPA"

    # Additional cleaning to ensure no trailing or leading spaces
    cleaned_name = cleaned_name.strip()

    return cleaned_name


# Load cookies from JSON
def load_cookies(driver, file_path):
    try:
        with open(file_path, "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        logging.info("Cookies loaded successfully.")
    except FileNotFoundError:
        logging.error(f"Cookies file '{file_path}' not found.")
    except Exception as e:
        logging.error(f"Error loading cookies: {e}")

# Save cookies to JSON after login
def save_cookies(driver, file_path):
    cookies = driver.get_cookies()
    with open(file_path, "w") as f:
        json.dump(cookies, f)
    logging.info("Cookies saved successfully.")

# Search LinkedIn profile by name and criteria
def search_profile(driver, name, criteria_keywords):
    try:
        # Clean up name before searching
        clean_search_name = clean_name(name)
        logging.info(f"Searching for profile with name: {clean_search_name}")

        # Wait for the search bar and input the cleaned name
        search_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Search"]'))
        )
        search_box.clear()
        search_box.send_keys(clean_search_name)
        search_box.send_keys(Keys.RETURN)

        # Wait for search results to load (LinkedIn may take some time to display the results)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "reusable-search__result-container"))
        )
        
        # Scrolling to ensure all profiles are visible in case of lazy-loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Find profiles in search results (filter to only profile URLs)
        profiles = driver.find_elements(By.XPATH, "//a[contains(@href, '/in/')]")
        
        if not profiles:
            logging.info(f"No profiles found for {clean_search_name}.")
            return

        # Visit each profile and check for keyword match
        for profile in profiles:
            profile_url = profile.get_attribute("href")

            # Open the profile link
            driver.get(profile_url)
            time.sleep(random.uniform(3, 7))  # Random delay to mimic human behavior

            # Retry mechanism for stale element handling
            for attempt in range(3):  # Retry up to 3 times
                try:
                    profile_body = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    profile_text = profile_body.text

                    # Match keywords
                    if any(keyword.lower() in profile_text.lower() for keyword in criteria_keywords):
                        logging.info(f"Match found for {clean_search_name}: {profile_url}")
                        with open("matched_profiles.txt", "a") as f:
                            f.write(f"{clean_search_name}: {profile_url}\n")
                        print(f"Match found: {profile_url}")
                    else:
                        logging.info(f"No match for {clean_search_name}: {profile_url}")
                    break  # Exit retry loop if successful

                except Exception as e:
                    if attempt < 2:  # Retry on first and second attempts
                        logging.warning(f"Retrying due to error: {e}")
                        time.sleep(2)  # Delay before retrying
                        driver.refresh()  # Refresh the page
                    else:
                        logging.error(f"Error processing profile {profile_url}: {e}")
                        break  # Exit after third failed attempt

    except Exception as e:
        logging.error(f"Error searching for {clean_search_name}: {e}")

if __name__ == "__main__":
    try:
        driver.get("https://www.linkedin.com")

        # Check for the cookie file, if not present, log in manually and save cookies
        if not os.path.exists("linkedin_cookies.json"):
            print("Logging in manually to save cookies...")
            driver.get("https://www.linkedin.com/login")
            
            # Wait for manual login (you'll need to log in via the console or browser)
            input("Press Enter after logging in...")

            # Save cookies after login
            save_cookies(driver, "linkedin_cookies.json")
        else:
            driver.get("https://www.linkedin.com")
            load_cookies(driver, "linkedin_cookies.json")
            driver.refresh()

        # Define search criteria (keywords to match on the profile)
        criteria_keywords = [
            "CPA", "Retirement Planning", "Investment Planning",
            "Financial Planning", "Estate Planning", "Financial Analysis"
        ]

        # List of names from the CPA scraper file
        with open("cpa_names.txt", "r") as f:
            names = [line.strip() for line in f.readlines()]

        # Search each name on LinkedIn
        for name in names:
            search_profile(driver, name, criteria_keywords)
            time.sleep(random.uniform(5, 10))  # Randomized delay between searches

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()
