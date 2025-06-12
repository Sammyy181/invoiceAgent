import subprocess
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import platform

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
    service = Service()  # auto-finds chromedriver in PATH
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    
    try:
        # Open the select_service page served by Flask  
        driver.get("http://127.0.0.1:7001/select_service")  # or localhost, adjust if needed

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
        
        select_service_via_browser(service_name, driver)

        return f"✅ Service '{service_name}' added via UI."

    except Exception as e:
        return f"❌ Error while interacting with browser: {e}"

    finally:
        time.sleep(1)
        driver.quit()


def select_service_via_browser(service_name, driver=None):
    """service = Service()
    driver = webdriver.Chrome(service=service)

    driver.get("http://localhost:7001/select_service")  # adjust if needed
    time.sleep(1)

    # Find all service buttons"""
    buttons = driver.find_elements(By.CSS_SELECTOR, ".service-buttons button")
    
    # Loop through buttons and click the one matching the service_name
    found = False
    for btn in buttons:
        if btn.text.strip().lower() == service_name.lower():
            btn.click()
            found = True
            print(f"✅ Selected service: {service_name}")
            break

    if not found:
        print(f"❌ Service '{service_name}' not found.")
    
    """time.sleep(2)
    driver.quit()"""
    
def kill_process(port=7001):
    try:
        if platform.system() == "Windows":
            # Windows
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    pid = line.split()[-1]
                    subprocess.run(['taskkill', '/F', '/PID', pid])
                    return f"✅ Process on port {port} killed successfully."
        else:
            # Linux/Mac
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pid = result.stdout.strip()
                subprocess.run(['kill', '-9', pid])
                return f"✅ Process on port {port} killed successfully."
    except Exception as e:
        print(f"Error: {e}")
        return f"❌ Failed to kill process on port {port}: {str(e)}"

    return f"❌ No process found on port {port}."
    time.sleep(2)
    driver.quit()
    
def view_invoice_for_service(service_name):
    service = Service(r"C:\Users\mathu\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")  # Update path
    driver = webdriver.Chrome(service=service)

    try:
        driver.get("http://localhost:5000/select_service")  # Update if route differs
        wait = WebDriverWait(driver, 10)

        select_service_via_browser(service_name)

        # Step 2: Click "View Last Generated Invoice"
        # Step 2: Click "View Last Month Invoice" button
        buttons = driver.find_elements(By.CLASS_NAME, "popup-button")
        clicked = False
        for btn in buttons:
            if btn.text.strip().lower() == "view last month invoice":
                btn.click()
                clicked = True
                break

        if not clicked:
            driver.quit()
            return "❌ 'View Last Month Invoice' button not found."


        # Step 3: Wait for invoice content to load
        invoice_element = wait.until(EC.presence_of_element_located((By.ID, "invoiceContent")))
        invoice_text = invoice_element.get_attribute("innerHTML")

        driver.quit()

        if invoice_text:
            return f"🧾 Invoice for **{service_name}**:\n\n{invoice_text}"
        else:
            return f"⚠️ No invoice content found for service: {service_name}"

    except Exception as e:
        driver.quit()
        return f"❌ Error occurred: {e}"