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
    def __init__(self, driver_path=None):
        load_dotenv()
        self.driver_path = driver_path or os.getenv("CHROMEDRIVER_PATH")
        if not self.driver_path:
            raise Exception("CHROMEDRIVER_PATH not set in .env file")
        
        self.driver = None
        self.wait = None
        self.cookies_file = "facebook_cookies.pkl"
        self.session_info_file = "facebook_session.json"
        self.base_url = "https://www.facebook.com/marketplace/"

    def init_driver(self):
        """Initialize Chrome driver with optimal settings for Facebook"""
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Uncomment for headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Block notifications and optimize for Facebook
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_setting_values.media_stream_camera": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        return self.driver

    def save_session(self):
        """Save both cookies and session information"""
        if not self.driver:
            return False
            
        # Save cookies
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
        """Load saved session if available and valid"""
        if not all(map(os.path.exists, [self.cookies_file, self.session_info_file])):
            return False

        try:
            # Check session age
            with open(self.session_info_file, "r") as f:
                session_info = json.load(f)
            
            last_saved = datetime.fromisoformat(session_info["last_saved"])
            if (datetime.now() - last_saved).days >= 7:  # Session expired if older than 7 days
                return False

            # Load cookies
            self.driver.get(self.base_url)
            time.sleep(2)  # Wait for page to load
            
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
            
            # Verify session is still valid by checking for login indicators
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Create new listing"]')))
                return True
            except:
                return False
                
        except Exception as e:
            print(f"Error loading session: {e}")
            return False

    def login(self, email, password):
        """Perform Facebook login"""
        try:
            self.driver.get(self.base_url)
            time.sleep(2)
            
            email_field = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id=":r10:"]')))
            password_field = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id=":r13:"]')))
            
            email_field.send_keys(email)
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            
            time.sleep(5)  # Wait for login to complete
            
            # Verify login success
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Create new listing"]')))
                self.save_session()
                return True
            except:
                return False
                
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def create_marketplace_listing(self, title, price, image_path):
        """Create a new marketplace listing"""
        try:
            create_listings_button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//span[text()="Create new listing"]'))
            )
            create_listings_button.click()
            time.sleep(1)
            
            single_listing_option = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//span[@class="x1lliihq x6ikm8r x10wlt62 x1n2onr6" and contains(text(), "Create a single listing")]'))
            )
            single_listing_option.click()
            time.sleep(3)
            
            # Upload image
            file_input = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="file"]')))
            file_input.send_keys(image_path)
            time.sleep(1)
            
            # Fill in details
            title_span = self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Title"]')))
            title_input = title_span.find_element(By.XPATH, './following::input[1]')
            title_input.send_keys(title)
            
            price_span = self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Price"]')))
            price_input = price_span.find_element(By.XPATH, './following::input[1]')
            price_input.send_keys(str(price))
            
            
            # Find and enter category
            category_span = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//span[text()="Category"]'
            )))
            category_input = category_span.find_element(By.XPATH, './following::input[1]')
            category_input.clear()
            category_input.send_keys("Furniture")
            
            # Wait explicitly for suggestions to appear
            # self.wait.until(EC.presence_of_element_located((
            #     By.XPATH, '//div[@role="listbox"]'
            # )))
            # time.sleep(2)  # Additional wait to ensure all suggestions are loaded
            
            # # Click first suggestion
            # first_suggestion = self.wait.until(EC.presence_of_element_located((
            #     By.XPATH, '//div[@role="option"]'
            # )))
            # first_suggestion.click()
            # time.sleep(1)  # Wait after clicking


            print("onto the next!")


            try:
                condition_span = self.wait.until(EC.presence_of_element_located((
                    By.XPATH, '//span[contains(@class, "x1jchvi3") and text()="Condition"]'
                )))
                condition_input = condition_span.find_element(By.XPATH, './following::div[contains(@class, "xjyslct")][1]')
                condition_input.click()
                time.sleep(1)
                
                # Select the condition from dropdown
                condition_option = self.wait.until(EC.presence_of_element_located((
                    By.XPATH, f'//div[@role="option"]//span[text()="New"]'
                )))
                condition_option.click()
                time.sleep(1)
            except Exception as e:
                print(f"Error selecting condition: {e}")
                
            more_details = self.wait.until(EC.presence_of_element_located((
                By.XPATH, "//div[text()='Attract more interest by including more details.']"
            )))
            more_details.click()
            time.sleep(2)
            
            # Handle Description field
            description_span = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//span[text()="Description"]'
            )))
            description_field = description_span.find_element(By.XPATH, './following::textarea[1]')
            description_field.clear()
            description_field.send_keys("I am selling a brand new furniture item.")
            time.sleep(1)
                
            return True
            
        except Exception as e:
            print(f"Error creating listing: {e}")
            return False

    def quit(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

def main():
    # Initialize session manager
    session_manager = FacebookSessionManager()
    session_manager.init_driver()
    
    try:
        # Try to reuse existing session
        if not session_manager.load_session():
            # If session loading fails, perform new login
            email = os.getenv("FB_EMAIL")
            password = os.getenv("FB_PASSWORD")
            if not session_manager.login(email, password):
                raise Exception("Login failed")
        
        # Create listing
        image_path = "/Users/mpeng/downloads/bruh.png"  # Update with your image path
        session_manager.create_marketplace_listing(
            title="Sample Title",
            price=100,
            image_path=image_path
        )
        
        time.sleep(200)  # Wait for user interaction
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        session_manager.quit()

if __name__ == "__main__":
    main()