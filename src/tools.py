from langchain.tools import tool
import subprocess
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

def open_editor() -> str:
    """
    Launches the invoice editor application located in '../invoiceEditor/app.py'
    """
    try:
        current_dir = os.path.dirname(__file__)
        app_path = "../invoiceEditor/app.py"
        app_full_path = os.path.abspath(os.path.join(current_dir, app_path))
        app_dir = os.path.dirname(app_full_path)
        
        if not os.path.exists(app_full_path):
            return f"❌ App file not found: {app_full_path}"
        
        # Create a log file to capture output
        log_file = os.path.join(app_dir, "flask_debug.log")
        
        with open(log_file, "w") as f:
            process = subprocess.Popen(
                [sys.executable, "app.py"],  # Use relative path since we're in the correct directory
                cwd=app_dir,
                close_fds=True,
                start_new_session=True,
                stdout=f,  # Redirect to log file instead of DEVNULL
                stderr=subprocess.STDOUT  # Combine stderr with stdout
            )
        
        # Check if process is still running
        poll_result = process.poll()
        if poll_result is not None:
            # Process has terminated, read the log
            try:
                with open(log_file, "r") as f:
                    log_content = f.read()
                return f"❌ Flask app terminated with exit code {poll_result}. Log:\n{log_content}"
            except:
                return f"❌ Flask app terminated with exit code {poll_result}. Could not read log file."
        
        return f"✅ Invoice Editor has been launched at http://127.0.0.1:7001/."
        
    except Exception as e:
        print(e)
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
