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
from marketplace_ai_agent import MarketplaceAIAgent

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
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

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

        with open(self.cookies_file, "wb") as file:
            pickle.dump(self.driver.get_cookies(), file)

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
        if not all(map(os.path.exists, [self.cookies_file, self.session_info_file])):
            return False

        try:
            with open(self.session_info_file, "r") as f:
                session_info = json.load(f)
            
            last_saved = datetime.fromisoformat(session_info["last_saved"])
            if (datetime.now() - last_saved).days >= 7:
                return False

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
                self.wait.until(EC.presence_of_element_located((
                    By.XPATH, '//span[text()="Create new listing"]'
                )))
                self.save_session()
                print("session saved")
                return True
            except:
                return False
                
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def automate_messages(self, js_path):
        try:
            print("reached automation endpoint")
            # navigate to messenger marketplace tab
            messenger_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[aria-label='Messenger'][role='button']")))
            messenger_button.click()
            see_all_in_messenger_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='See all in Messenger']")))
            see_all_in_messenger_link.click()
            marketplace_chats = self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Marketplace"]')))
            marketplace_chats.click()

            while True:
                try:
                    # Find and click unread message
                    button_div = self.wait.until(EC.presence_of_element_located((
                        By.CSS_SELECTOR, "div.x9f619.x1n2onr6.x1ja2u2z.xdt5ytf.x2lah0s.x193iq5w.xeuugli.x78zum5"
                    )))
                    print("Found unread message button")
                    button_div.click()
                    
                    # Wait for conversation to load
                    time.sleep(2)
                    
                    # Get conversation history
                    messages = self.wait.until(EC.presence_of_all_elements_located((
                        By.CSS_SELECTOR, "div[role='row']"
                    )))
                    conversation_history = "\n".join([msg.text for msg in messages])
                    
                    # Get item context
                    item_context = self._get_item_context()
                    
                    # Detect conversation stage and generate response
                    stage = ai_agent.detect_stage(conversation_history, item_context)
                    response = ai_agent.generate_response(conversation_history, item_context, stage)
                    
                    # Send response
                    message_input = self.wait.until(EC.presence_of_element_located((
                        By.CSS_SELECTOR, "div[role='textbox']"
                    )))
                    message_input.send_keys(response)
                    message_input.send_keys(Keys.RETURN)
                    
                    time.sleep(2)  # Wait for message to send
                    
                except Exception as e:
                    print(f"No more unread messages found or error occurred: {e}")
                    break

            time.sleep(200)

        except Exception as e:
            print(f"An error occurred: {e}")

    def _get_item_context(self):
        """Extract item details from the conversation."""
        try:
            item_title = self.wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "span[role='heading']"
            )))
            item_price = self.wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "span[class*='price']"
            )))
            
            return {
                "title": item_title.text,
                "price": item_price.text,
                "condition": "New",  # You'll need to extract this
                "location": "Local pickup"  # You'll need to extract this
            }
        except Exception as e:
            print(f"Error getting item context: {e}")
            return {"title": "Unknown Item", "price": "Unknown Price"}

    def quit(self):
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
        JS_PATH = "//path/to/button"
        session_manager.automate_messages(JS_PATH)
        
        time.sleep(200)  # Wait for user interaction

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        session_manager.quit()

if __name__ == "__main__":
    main()