LinkedIn Connection Automation

					Overview
This project automates the process of sending connection requests on LinkedIn based on a list of profile URLs. It utilizes Selenium WebDriver to simulate user actions such as navigating to LinkedIn profiles, locating and clicking the "Connect" button, and optionally sending personalized notes with the connection requests.

The project includes mechanisms for:

Handling both direct "Connect" buttons and buttons hidden inside the "More" dropdown.
Managing LinkedIn sessions with cookies for automatic login.
Logging interactions and errors for easy troubleshooting.
Introducing random delays to simulate human-like behavior and avoid detection by LinkedIn's anti-bot systems.
Features
Automated Connection Requests: The script visits LinkedIn profiles and sends connection requests based on a pre-defined list of URLs.
Session Management with Cookies: LinkedIn sessions are managed by loading cookies, allowing the script to bypass the login screen.
Personalized Connection Notes: Option to include a custom note in connection requests.
Error Handling & Logging: Detailed logging for tracking actions, errors, and connection requests.
Randomized Delays: Random time delays to mimic human-like behavior and avoid LinkedIn's bot detection algorithms.
Project Structure
The project is divided into several key scripts:

1. search.py
This script searches LinkedIn for profiles using specific keywords and saves the matched profile URLs in a text file for further processing.

2. connect.py
The main script responsible for sending connection requests to LinkedIn profiles listed in the matched_profiles.txt file.

3. scraper.py
This script scrapes names and details from directories (such as CPA and CFP directories) and uses them to generate a list of LinkedIn profile URLs for the connect.py script to process.

Installation
Prerequisites
Python (3.x)
Selenium for browser automation
Chrome WebDriver to control the browser (ensure the version matches your Chrome browser)
Google Chrome installed on your system
Python Dependencies
Install the required Python packages by running:


Copy code:

	pip install selenium

Chrome WebDriver
Download the correct version of ChromeDriver from the official site: ChromeDriver
Place the chromedriver.exe file in a suitable directory and update the path in connect.py:
	chrome_service = Service(executable_path="C:/path/to/chromedriver.exe")

Cookie Management
After logging in to LinkedIn manually, save your session cookies in a file (linkedin_cookies.json). This file is used to bypass LinkedIn's login process.
The cookies should be stored in the following format:
json:

[
    {
        "domain": ".linkedin.com",
        "expiry": 1710123456,
        "httpOnly": true,
        "name": "li_at",
        "path": "/",
        "secure": true,
        "value": "your-session-cookie-value"
    },
    ...
]

Usage
1. Prepare the Profile URLs
Use scraper.py or search.py to generate a list of profile URLs you want to connect with.
The profile URLs should be saved in a file called matched_profiles.txt in the following format:
profile_name: https://www.linkedin.com/in/profile-identifier
profile_name: https://www.linkedin.com/in/another-profile-identifier


2. Running the Connection Automation
Ensure your cookies file (linkedin_cookies.json) is in the same directory as the script.
Run the connection automation by executing the connect.py script:

python connect.py


The script will:

Load the LinkedIn homepage.
Load cookies from linkedin_cookies.json.
Navigate to each profile URL in matched_profiles.txt.
Attempt to send a connection request.
Optionally include a note with each connection request.

Logs:
2024-10-14 09:45:33,340 - INFO - Trying to connect with profile: https://www.linkedin.com/in/example-profile
2024-10-14 09:45:36,421 - INFO - Connection request sent to https://www.linkedin.com/in/example-profile


Configuration
Optional Connection Note
You can include a personalized note with each connection request by modifying the connection_note variable in connect.py:


connection_note = "Hi, I came across your profile and would like to connect. Let's network!"

Random delays are included throughout the script to simulate human interaction and avoid LinkedIn's bot detection. You can adjust the range of delays as needed:


time.sleep(random.uniform(3, 7))  # Random delay between actions



Error Handling
The script is designed to handle various exceptions, such as:

Button Not Found: If the "Connect" button is not found directly or inside the "More" dropdown, the error is logged and the script moves on to the next profile.
Session Expiration: If the session cookies expire or become invalid, the script will log an error and terminate. In such cases, update your session cookies by logging in again and saving the new cookies.
Troubleshooting
Common Issues
Profile Not Found: Ensure the URLs in matched_profiles.txt are valid LinkedIn profile URLs.
Cookies Not Loaded: Check the format and path of the linkedin_cookies. If there are issues, log in manually and save the cookies again.
Connect Button Not Found: LinkedIn's page structure might vary, so ensure the XPaths in the script are up to date. Review the logs for more details on the error.


Debugging
Check the connect.log file for detailed error messages. For example, if the "Connect" button cannot be found:


2024-10-14 09:45:36,421 - ERROR - Connect button not found for https://www.linkedin.com/in/ex


