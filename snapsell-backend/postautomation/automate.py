"""
Facebook Marketplace Listing Bot
-------------------------------
This script automates the process of creating listings on Facebook Marketplace.
It handles session management, login, and listing creation with image uploads.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import pickle
import json
import os
from dotenv import load_dotenv

class FacebookSessionManager:
    """Manages Facebook marketplace sessions, login, and listing creation."""
    
    def __init__(self, driver_path=None):
        """Initialize session manager with driver path from environment or parameter."""
        load_dotenv()
        self.driver_path = driver_path or os.getenv("CHROMEDRIVER_PATH")
        if not self.driver_path:
            raise Exception("CHROMEDRIVER_PATH not set in .env file")
        
        # Initialize class attributes
        self.driver = None
        self.wait = None
        self.cookies_file = "facebook_cookies.pkl"
        self.session_info_file = "facebook_session.json"
        self.base_url = "https://www.facebook.com/marketplace/"

    def init_driver(self):
        """Initialize Chrome driver with optimized settings for Facebook Marketplace."""
        # Set up Chrome options
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Configure browser preferences
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_setting_values.media_stream_camera": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Initialize driver and wait
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        return self.driver

    def save_session(self):
        """Save cookies and session information for future use."""
        if not self.driver:
            return False
            
        # Save browser cookies
        with open(self.cookies_file, "wb") as file:
            pickle.dump(self.driver.get_cookies(), file)
        
        # Save session metadata
        session_info = {
            "last_saved": datetime.now().isoformat(),
            "domain": self.driver.current_url,
            "user_agent": self.driver.execute_script("return navigator.userAgent")
        }
        with open(self.session_info_file, "w") as f:
            json.dump(session_info, f)
        
        return True

    def load_session(self):
        """Attempt to load a previously saved session if valid."""
        # Check if session files exist
        if not all(map(os.path.exists, [self.cookies_file, self.session_info_file])):
            return False

        try:
            # Validate session age
            with open(self.session_info_file, "r") as f:
                session_info = json.load(f)
            
            last_saved = datetime.fromisoformat(session_info["last_saved"])
            if (datetime.now() - last_saved).days >= 7:
                return False

            # Load and apply cookies
            self.driver.get(self.base_url)
            time.sleep(2)
            
            with open(self.cookies_file, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"Error adding cookie: {e}")

            self.driver.refresh()
            time.sleep(3)
            
            # Verify session validity
            try:
                self.wait.until(EC.presence_of_element_located((
                    By.XPATH, '//span[text()="Create new listing"]'
                )))
                return True
            except:
                return False
                
        except Exception as e:
            print(f"Error loading session: {e}")
            return False

    def login(self, email, password):
        """Perform Facebook login with provided credentials."""
        try:
            self.driver.get(self.base_url)
            time.sleep(2)
            
            # Find and fill login fields
            email_field = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id=":r10:"]'
            )))
            password_field = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id=":r13:"]'
            )))
            
            email_field.send_keys(email)
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            
            time.sleep(5)
            
            # Verify login success
            try:
                self.wait.until(EC.presence_of_element_located((
                    By.XPATH, '//span[text()="Create new listing"]'
                )))
                self.save_session()
                return True
            except:
                return False
                
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def create_marketplace_listing(self, title, price, image_path, category, condition, description):
        """Create a new marketplace listing with the provided details."""
        try:
            # Click create listing button
            create_listings_button = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//span[text()="Create new listing"]'
                ))
            )
            create_listings_button.click()
            time.sleep(1)
            
            # Select single listing option
            single_listing_option = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//span[@class="x1lliihq x6ikm8r x10wlt62 x1n2onr6" and contains(text(), "Create a single listing")]'
                ))
            )
            single_listing_option.click()
            time.sleep(3)
            
            # Upload image
            file_input = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//input[@type="file"]'
            )))
            file_input.send_keys(image_path)
            time.sleep(1)
            
            # Fill in basic details
            self._fill_basic_details(title, price)
            
            # Select category
            self._select_category(category)
            
            # Select condition
            self._select_condition(condition)
            
            # Fill description
            self._fill_description(description)
            
            # Navigate through steps
            # self._click_next_button()
            self._click_next_button()
            self._click_publish_button()

            time.sleep(8)
            
            return True
            
        except Exception as e:
            print(f"Error creating listing: {e}")
            return False

    def _fill_basic_details(self, title, price):
        """Helper method to fill in title and price."""
        title_span = self.wait.until(EC.presence_of_element_located((
            By.XPATH, '//span[text()="Title"]'
        )))
        title_input = title_span.find_element(By.XPATH, './following::input[1]')
        title_input.send_keys(title)
        
        price_span = self.wait.until(EC.presence_of_element_located((
            By.XPATH, '//span[text()="Price"]'
        )))
        price_input = price_span.find_element(By.XPATH, './following::input[1]')
        price_input.send_keys(str(price))

    def _select_category(self, category):
        """Helper method to select listing category."""
        try:
            category_span = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//span[text()="Category"]'
            )))
            category_input = category_span.find_element(By.XPATH, './following::input[1]')
            category_input.clear()
            category_input.send_keys(category)
            time.sleep(1)
            
            category_option = self.wait.until(EC.presence_of_element_located((
                By.XPATH, f'//span[contains(text(), "{category}")][1]'
            )))
            category_option.click()
            time.sleep(1)
        except Exception as e:
            print(f"Error selecting category: {e}")

    def _select_condition(self, condition):
        """Helper method to select item condition."""
        try:
            condition_span = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//span[contains(@class, "x1jchvi3") and text()="Condition"]'
            )))
            condition_input = condition_span.find_element(
                By.XPATH, './following::div[contains(@class, "xjyslct")][1]'
            )
            condition_input.click()
            time.sleep(1)
            
            condition_option = self.wait.until(EC.presence_of_element_located((
                By.XPATH, f'//div[@role="option"]//span[text()="{condition}"]'
            )))
            condition_option.click()
            time.sleep(1)
        except Exception as e:
            print(f"Error selecting condition: {e}")

    def _fill_description(self, description):
        """Helper method to fill in listing description."""
        description_span = self.wait.until(EC.presence_of_element_located((
            By.XPATH, '//span[text()="Description"]'
        )))
        description_field = description_span.find_element(By.XPATH, './following::textarea[1]')
        description_field.clear()
        description_field.send_keys(description)
        time.sleep(1)

    def _click_next_button(self):
        """Helper method to click the Next button."""
        try:
            next_button = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//span[contains(text(), "Next")]/ancestor::div[@role="button"]'
            )))
            next_button.click()
            time.sleep(1)
        except Exception as e:
            print(f"Error clicking Next button: {e}")
            
    def _click_publish_button(self):
        """Helper method to click the Next button."""
        try:
            publish_button = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//span[contains(text(), "Publish")]/ancestor::div[@role="button"]'
            )))
            publish_button.click()
        except Exception as e:
            print(f"Error clicking Next button: {e}")

    def quit(self):
        """Clean up resources and close the browser."""
        if self.driver:
            self.driver.quit()


def main():
    """Main execution function."""
    # Initialize session manager
    session_manager = FacebookSessionManager()
    session_manager.init_driver()
    
    try:
        # Attempt to load existing session or perform new login
        if not session_manager.load_session():
            email = os.getenv("FB_EMAIL")
            password = os.getenv("FB_PASSWORD")
            if not session_manager.login(email, password):
                raise Exception("Login failed")
        
        # Create new listing
        image_path = "/Users/mpeng/Desktop/chair.jpg"
        session_manager.create_marketplace_listing(
            title="Chair",
            price=150,
            image_path=image_path,
            category="Miscellaneous",
            condition="Used - Good"
        )
        
        time.sleep(200)  # Keep browser open for user interaction
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        session_manager.quit()


if __name__ == "__main__":
    main()