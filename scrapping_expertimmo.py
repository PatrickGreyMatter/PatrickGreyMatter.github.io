import json
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def launch_driver_and_wait():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment for headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Path to chromedriver
    chromedriver_path = '/usr/bin/chromedriver'

    # Initialize the driver service with logging
    service = Service(executable_path=chromedriver_path, log_path='chromedriver.log')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

def website_login(driver, email, password):
    # Navigate to the login page
    driver.get("https://extranet.expertimo.com/extranet/login/show?ref=noauth")

    # Wait for the email input field to be present in the DOM
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )

    # Fill in the email and submit to reveal the password field
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.btn-block.btn-flat").click()

    # Wait for the password field to become visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.NAME, "password"))
    )

    # Fill in the password
    driver.find_element(By.NAME, "password").send_keys(password)

    # Submit the form
    driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.btn-block.btn-flat").click()

def retrieve_contacts(driver):
    driver.get("https://extranet.expertimo.com/extranet/annuary/show")
    driver.find_element(By.ID, "viewAllUsers").click()

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "title2column"), "Utilisateurs")
    )

    user_elements = driver.find_elements(By.XPATH, "//ul[@id='ulUsers']/li/a[@class='viewUser']")

    profiles = []

    for user_element in user_elements:
        user_id = user_element.get_attribute("id")
        user_name = user_element.find_element(By.TAG_NAME, "b").text.strip()
        user_element.click()

        # Wait for the updated box to be displayed with user information
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "profileContent"))
        )

        # Extract other profile data as needed
        profile_data_element = driver.find_element(By.ID, "profileContent")
        profile_info = profile_data_element.text

        # Extract email, code postal, address, ville, and phone number using regular expressions
        email_match = re.search(r"Email : (.+)", profile_info)
        email = email_match.group(1) if email_match else ""

        code_postal_match = re.search(r"Code postal : (.+)", profile_info)
        code_postal = code_postal_match.group(1) if code_postal_match else ""

        adresse_match = re.search(r"Adresse : (.+)", profile_info)
        adresse = adresse_match.group(1) if adresse_match else ""

        ville_match = re.search(r"Ville : (.+)", profile_info)
        ville = ville_match.group(1) if ville_match else ""

        phone_number_match = re.search(r"\+\d{11}", profile_info)
        phone_number = phone_number_match.group() if phone_number_match else ""

        user_data = {
            "user_id": user_id,
            "user_name": user_name,
            "Adresse": adresse,
            "Code postal": code_postal,
            "Ville": ville,
            "Email": email,
            "Téléphone": phone_number
        }

        profiles.append(user_data)

    # Save the profiles in a JSON file
    with open("contacts_expertimmo.json", "w", encoding="utf-8") as json_file:
        json.dump(profiles, json_file, ensure_ascii=False, indent=4)

def execute():
    driver = launch_driver_and_wait()
    try:
        # Assuming you have the login credentials stored in the variables `my_email` and `my_password`
        website_login(driver, 'molina@cabinetciem.fr', 'Lattes34970$')

        retrieve_contacts(driver)
        # Wait for user input to end the script
        input("Press Enter to quit the browser and end the script...")
    finally:
        # Ensure the driver quits even if an error occurs
        driver.quit()

# Run the execute function
execute()
