from langchain.tools import tool
import subprocess
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

@tool
def open_editor() -> str:
    """
    Launches the invoice editor application located in '../invoice-editor/app.py'
    """
    try:
        current_dir = os.path.dirname(__file__)  # this gives path to src/
        app_path = os.path.abspath(os.path.join(current_dir, "../invoiceEditor/app.py"))

        subprocess.Popen(["python", app_path], cwd=os.path.dirname(app_path))
        return "✅ Invoice Editor has been launched."
    except Exception as e:
        return f"❌ Failed to launch Invoice Editor: {str(e)}"


def add_service(service_name: str):
    # Set up Chrome driver
    service = Service(r"C:\Users\mathu\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")  # auto-finds chromedriver in PATH
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=service)
    
    try:
        # Open the select_service page served by Flask  
        driver.get("http://127.0.0.1:5000/select_service")  # or localhost, adjust if needed

        time.sleep(1)  # Wait for page to load

        # Click on "Add New Service" button
        add_button = driver.find_element(By.ID, "add-service-button")  # replace with correct ID
        add_button.click()

        time.sleep(0.5)  # wait for input field to appear

        # Enter service name
        input_box = driver.find_element(By.ID, "newServiceInput")  # replace with actual ID
        input_box.send_keys(service_name)

        time.sleep(0.5)

        # Click on "Done" button
        done_button = driver.find_element(By.ID, "submitNewServiceBtn")  # replace with correct ID
        done_button.click()

        print(f"✅ Service '{service_name}' added via UI.")

    except Exception as e:
        print(f"❌ Error while interacting with browser: {e}")

    finally:
        time.sleep(1)
        driver.quit()
