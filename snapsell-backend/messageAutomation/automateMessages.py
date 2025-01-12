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
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_PROJECT_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

status_table = {
    "unlisted": 0,
    "listed": 1,
    "negotiating": 2,
    "scheduled": 3,
    "sold": 4,
}

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

    def automate_messages(self):
        try:
            print("reached automation endpoint")
            # Navigate directly to Facebook Messages
            self.driver.get("https://www.facebook.com/messages/t/")
            time.sleep(2)  # Wait for page to load
            
            # Click on Marketplace tab
            marketplace_chats = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//span[text()="Marketplace"]'
            )))
            marketplace_chats.click()

            # Find unvisited chats
            try:
                unvisited_chats = self.wait.until(EC.presence_of_all_elements_located((
                    By.CSS_SELECTOR, 'span.xeuugli.xveuv9e'
                )))
            except Exception as e:
                print(f"Error finding unvisited chats: {e}, 0 unvisited chats found")
                return

            print(f"Found {len(unvisited_chats)} unvisited chats")

            ai_agent = MarketplaceAIAgent(os.environ.get("ANTHROPIC_API_KEY"))

            for chat in unvisited_chats:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", chat)
                    time.sleep(1)  
                    chat.click()
                    
                    time.sleep(2)
                    
                    conversation_history = self._extract_conversation()
                    print("Extracted conversation:")
                    print(conversation_history)
                    
                    # Get item context
                    item_title = "Apple AirPods Max Headphones Grey"
                    item_context = self._get_item_context(item_title)

                    if item_context["status"] == "sold":
                        response = "Sorry this item is sold."
                    
                    else:
                        stage = ai_agent.detect_stage(conversation_history, item_context)
                        print(stage)
                        response = ai_agent.generate_response(conversation_history, item_context, stage)
                        print(response)

                    message_input = self.wait.until(EC.presence_of_element_located((
                        By.CSS_SELECTOR, "div[role='textbox']"
                    )))
                    message_input.send_keys(response)
                    message_input.send_keys(Keys.RETURN)

                    item_status = ai_agent.get_status(conversation_history, response)
                    print("item status: ", item_status)
                    curr_status = item_context["status"]
                    if status_table[item_status] > status_table[curr_status]:
                        response = (
                            supabase.table("items")
                            .update({"status": item_status})
                            .eq("id", item_context["id"])
                            .execute()
                        )
                    
                    time.sleep(2) 
                    
                except Exception as e:
                    print(f"No more unread messages found or error occurred: {e}")
                    break

            time.sleep(10)

        except Exception as e:
            print(f"An error occurred: {e}")

    def _get_item_context(self, item_title):
        """Extract item details from the conversation."""
        try:
            response = (supabase.table("items")
                .select("id, title, description, price, condition, status")
                .eq("title", item_title)
                .execute()
            )
            print("got response from db", response)
            
            if response.data:
                item = response.data[0]
                return {
                    "id": item.get("id", "Unknown"),
                    "title": item.get("title", "Unknown"),
                    "price": item.get("price", "Unknown"),
                    "condition": item.get("condition", "Unknown"),
                    "description": item.get("description", ""),
                    "status": item.get("status", "Available")
                }
            else:
                print("Item is not found")
                return {"title": "Unknown Item", "price": "Unknown Price"}
            
        except Exception as e:
            print(f"Error getting item context: {e}")
            return {"title": "Unknown Item", "price": "Unknown Price"}

    def _extract_conversation(self):
        """Extract conversation history with differentiation between buyer and seller messages"""
        try:
            # Get all message containers
            message_containers = self.wait.until(EC.presence_of_all_elements_located((
                By.CSS_SELECTOR, "div[role='row']"
            )))
            
            conversation_parts = []
            
            for container in message_containers:
                try:
                    # Try to find the message text within the container
                    message_text = container.find_element(By.CSS_SELECTOR, "div[dir='auto']").text.strip()
                    if not message_text:
                        continue
                    
                    # Check if this is a seller message by looking for specific classes and "You sent" text
                    try:
                        # Look for the "You sent" text or x15zctf7 class which indicates seller message
                        container.find_element(By.CSS_SELECTOR, ".x15zctf7")
                        conversation_parts.append(f"seller(me): {message_text}")
                    except:
                        # If the seller indicators aren't found, it's a buyer message
                        conversation_parts.append(f"buyer(them): {message_text}")
                        
                except Exception as e:
                    print(f"Error processing message container: {e}")
                    continue
            
            return "\n".join(conversation_parts)
            
        except Exception as e:
            print(f"Error extracting conversation: {e}")
            return ""

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
        session_manager.automate_messages()
        JS_PATH = "//path/to/button"
        session_manager.automate_messages()
        
        time.sleep(200)  # Wait for user interaction

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        session_manager.quit()

if __name__ == "__main__":
    main()