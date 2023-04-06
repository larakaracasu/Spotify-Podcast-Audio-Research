import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time


def get_prefixes(csv_filename): # Extract show_filename_prefix fields from csv
    df = pd.read_csv(csv_filename)
    prefixes = set()
    for row in df.show_filename_prefix:
        row = row.strip("][").split(', ')
        prefixes.add(row[0].strip("'"))
    return prefixes


def get_parent_folders(csv_filename): # Extract show_filename_prefix fields from csv
    prefixes = get_prefixes(csv_filename)
    parent_folders = set()
    for prefix in prefixes:
        parent_folders.add(prefix[5:7].upper())
    return parent_folders


def get_folder_chain(prefix):
    return [s for s in prefix[5:7].upper()]


def wait_for_load(old_element):
    while True:
        try:
            old_element.find_element(by=By.XPATH, value="//div[contains(@role, 'row')]")  # Ping element
        except StaleElementReferenceException:
            break   # Break once element expires


def move_and_click(driver, element):
    action = ActionChains(driver)
    action.move_to_element(element).click().perform()


def navigate_to_opensmile(credentials_filename):    # Get to openSMILE folder
    # Start driver and navigate to Box login
    service = Service('/usr/lib/chromium-browser/chromedriver')
    driver = webdriver.Chrome(service=service)
    driver.get('https://app.box.com/login')
    driver.implicitly_wait(10)

    # Grab Box credentials from external file
    creds = open(credentials_filename, "r")
    username = creds.readline().replace("username:", "").strip()
    password = creds.readline().replace("password:", "").strip()
    creds.close()

    # Pass username to email prompt
    uname = driver.find_element("id", "login-email")
    uname.send_keys(username)

    # Click on the "Next" button
    next_button = driver.find_element("id", "login-submit")
    next_button.click()

    # Wait for the password input field to appear
    password_field = WebDriverWait(driver, 10).until(
         expected_conditions.visibility_of_element_located((By.ID, "password-login"))
    )

    # Enter your password and click on the "Log In" button
    password_field.send_keys(password)
    login_button = driver.find_element("id", "login-submit-password")
    login_button.click()

    # Click on Spotify-Podcasts folder
    link_element = driver.find_element(by=By.XPATH, value='//a[@href="/folder/107932668321"]')
    link_element.click()

    # Click on EN
    link_element = driver.find_element(by=By.XPATH, value='//a[@href="/folder/175742097782"]')
    link_element.click()

    # Click on OpenSmile
    link_element = driver.find_element(by=By.XPATH, value='//a[@href="/folder/140172208712"]')
    link_element.click()

    # Wait for previous link to expire
    wait_for_load(link_element)

    return driver


def find_folder(driver, prefix):
    chain = get_folder_chain(prefix)
    print(chain)
    # Enter first folder in folder tree
    grandparent_folder = driver.find_element(by=By.LINK_TEXT, value=chain[0])
    move_and_click(driver, grandparent_folder)
    wait_for_load(grandparent_folder)

    # Enter second folder in folder tree
    parent_folder = driver.find_element(by=By.LINK_TEXT, value=chain[1])
    move_and_click(driver, parent_folder)
    wait_for_load(parent_folder)

    # Enter target folder
    folder = driver.find_element(by=By.LINK_TEXT, value=prefix)
    move_and_click(driver, folder)
    wait_for_load(folder)

    #time.sleep(5)

    # Go back to parent folder --> will bring openSMILE folder in frame
    parent_folder = driver.find_element(by=By.LINK_TEXT, value=chain[1])
    move_and_click(driver, parent_folder)
    wait_for_load(parent_folder)

    # Go back to openSMILE folder
    smile_folder = driver.find_element(by=By.XPATH, value='//a[@href="/folder/140172208712"]')
    move_and_click(driver, smile_folder)
    wait_for_load(smile_folder)

    time.sleep(2)


if __name__ == "__main__":

    # Get show_filename_prefix fields from csv and go to proper folder in Box
    prefixes = get_prefixes("refined_metadata_ratings.csv")
    driver = navigate_to_opensmile("credentials.txt")

    successful_prefixes = []
    failed_prefixes = []
    count = 5
    for prefix in prefixes:
        if count < 0:
            break
        try:
            find_folder(driver, prefix)
            successful_prefixes.append(prefix)
        except:
            failed_prefixes.append(prefix)
        count -= 1

    print(successful_prefixes)
    print(failed_prefixes)

    # Grab table elements, the rows of the first one are folders
    # folders = driver.find_elements(by=By.XPATH,
    #                                value="//div[contains(@class, 'ReactVirtualized__Table__row table-row ')]")

    # for folder in folders:
    #     try:
    #         folder_index = folder.get_attribute("data-item-index")
    #         folder_id = folder.get_attribute("data-resin-folder_id")
    #         folder_name = folder.text
    #         print(str(folder_index) + ":\t" + str(folder_name) + " <-> " + str(folder_id) + "\n")
    #     except StaleElementReferenceException:
    #         print("\n\nRETRYING\n\n")
    #         # refresh the page and find the element again
    #         driver.refresh()
    #         time.sleep(5)  # wait 5 seconds before finding elements again
    #         folders = driver.find_elements(by=By.XPATH,
    #                                        value="//div[contains(@class, 'ReactVirtualized__Table__row table-row ')]")
    #         continue

    #     """
    #     if folder_name.startswith(folder_prefix) and folder_id not in downloaded_folders:
    #         # download the folder
    #         downloaded_folders.add(folder_id)
    #         folder.click()
    #         # do something to download the files in this folder
    #         # then go back to the previous page with driver.back()
    #     """
