# README: Steps to Run the Script

## 1. Create a Virtual Environment
python3 -m venv venv
source venv/bin/activate  # For Windows: .\venv\Scripts\activate

# 2. Install the dependencies
pip install -r requirements.txt

## 3. Set Up .env File
# Create a .env file with the following content:
echo "CHROMEDRIVER_PATH=/path/to/chromedriver" > .env
# Replace /path/to/chromedriver with the actual path to your ChromeDriver executable.

## 4. Run the Script
python automate.py

## 5. Deactivate Virtual Environment (Optional)
deactivate