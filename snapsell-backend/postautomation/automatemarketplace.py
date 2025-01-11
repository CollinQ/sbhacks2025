from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os


def automate_facebook_marketplace(js_path):
    
    

    load_dotenv()
    driver_path = os.getenv("CHROMEDRIVER_PATH")
    if not driver_path:
        raise Exception("CHROMEDRIVER_PATH not set in .env file")


    # Set up Chrome options for headless mode
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Enable headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size for rendering
    prefs = {
        "profile.default_content_setting_values.notifications": 2  # 2 means block notifications
        }
    chrome_options.add_experimental_option("prefs", prefs)
    
    service = Service(driver_path)  
    
    
    
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Facebook login credentials (DO NOT HARDCODE in production)
    email = "bbobbqq@gmail.com"
    password = "snapsell"
    
    wait = WebDriverWait(driver, 10)

    try:
        # Open Facebook Marketplace login page
        driver.get("https://www.facebook.com/marketplace/")

        email_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id=":r10:"]')))
        password_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id=":r13:"]')))

        print(email_field)
        print(password_field)
        
        # Input credentials
        email = "bbobbqq@gmail.com"  # Replace with your Facebook email
        password = "snapsell"        # Replace with your Facebook password
        

        email_field.send_keys(email)
        password_field.send_keys(password)

        # # Submit the form
        password_field.send_keys(Keys.RETURN)
        
        #now we are logged in:
        time.sleep(2)

        print("trying listings:")
        # Navigate to the 'Create Multiple Listings' button
        create_listings_button = wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Create new listing"]')))
        create_listings_button.click()
        
        time.sleep(1)
        
        yo = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="x1lliihq x6ikm8r x10wlt62 x1n2onr6" and text()="Create a single listing for one or more items to sell."]')))
        yo.click()
        
        

        # print("Navigated to 'Create Multiple Listings' section.")

        # # Click the specific button as per the second XPath
        # specific_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mount_0_0_bw"]/div/div[1]/div/div[5]/div/div/div[3]/div[2]/div[2]/div/div/div[2]/div[1]/div/span/div/a/div[1]/div/div/div[2]/div/div[1]/span')))
        # specific_button.click()

        # Optional: Wait for some time to confirm login
        time.sleep(200)


        print("Successfully clicked on 'Create Multiple Listings'.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

# Replace with the actual JavaScript path or selector
JS_PATH = "//path/to/button"
automate_facebook_marketplace(JS_PATH)
