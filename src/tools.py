import subprocess
import os
import pandas as pd
import time
import platform
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

def add_service(service_name: str) -> str: 
    try:
        excel_path = os.path.join("data", f"{service_name}.xlsx")
        column_path = os.path.join("columns", f"columns/{service_name}.json")
        titles_path = os.path.join("titles", f"titles/{service_name}.json")
        categories_path = os.path.join("categories", f"categories/{service_name}.json")
        
        now = datetime.now()
        current_month = now.strftime("%B")
        previous_month = (now - relativedelta(months=1)).strftime("%B")
        try:
            df = pd.read_excel("template.xlsx", sheet_name=current_month)
        except Exception:
            df = pd.read_excel("template.xlsx", sheet_name=previous_month)
            
        df.to_excel(excel_path, index=False)
        with open(column_path, 'w') as f:
            json.dump([], f, indent=4)
        with open(categories_path, 'w') as f:
            json.dump([], f, indent=4)
        
        with open('titles_config.json', 'r') as f:
            titles_config = json.load(f)
        with open(titles_path, 'w') as f:
            json.dump(titles_config, f, indent=4)
        
        return f"✅ Service '{service_name}' added successfully!"

    except Exception as e:
        return f"❌ Error while interacting with browser: {e}"

def select_service_via_browser(service_name, driver=None) -> None:
    driver.get("http://localhost:7001/select_service")

    wait = WebDriverWait(driver, 10)
    try:
        # Wait until the first service button is visible
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".service-buttons button")))

        buttons = driver.find_elements(By.CSS_SELECTOR, ".service-buttons button")

        found = False
        for btn in buttons:
            # Use innerText to reliably get dynamic/complex label text
            label = btn.get_attribute("innerText").strip().lower()
            if label == service_name.lower():
                btn.click()
                found = True
                break

        if not found:
            print(f"❌ Service '{service_name}' not found.")

    except Exception as e:
        print(f"⚠️ Error while selecting service: {e}")
        time.sleep(2)
    
    """time.sleep(2)
    driver.quit()"""
    
def kill_process(port=7001) -> str:
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
    
def view_invoice_for_service(service_name, driver=None) -> str:
    try:
        driver.get("http://localhost:7001/select_service")  # Update if route differs
        wait = WebDriverWait(driver, 10)

        select_service_via_browser(service_name, driver=driver)

        print(f"✅ Selected service: {service_name}")
        try:
            view_button = wait.until(EC.presence_of_element_located((By.ID, "viewInvoiceButton")))
            view_button.click()  
        except Exception as e:
            return "❌ 'View Last Month Invoice' button not found."
            
        # Step 3: Wait for invoice content to load
        invoice_element = wait.until(EC.presence_of_element_located((By.ID, "invoiceContent")))
        invoice_text = invoice_element.get_attribute("innerHTML")

        if invoice_text:
            return f"🧾 Invoice for {service_name} can now be seen."
        else:
            return f"⚠️ No invoice content found for service: {service_name}"

    except Exception as e:
        return f"❌ Error occurred: {e}"
    
def view_current_invoice_for_service(service_name, driver=None) -> str:
    try:
        driver.get("http://localhost:7001/select_service")  # Update if route differs
        wait = WebDriverWait(driver, 10)

        select_service_via_browser(service_name, driver=driver)

        print(f"✅ Selected service: {service_name}")
        try:
            view_button = wait.until(EC.presence_of_element_located((By.ID, "viewCurrentInvoiceButton")))
            view_button.click()  # or whatever you need to do with it
        except Exception as e:
            return "❌ 'View Current Month Invoice' button not found."
            
        # Step 3: Wait for invoice content to load
        invoice_element = wait.until(EC.presence_of_element_located((By.ID, "invoiceContent")))
        invoice_text = invoice_element.get_attribute("innerHTML")

        if invoice_text:
            return f"🧾 Invoice for {service_name} can now be seen."
        else:
            return f"⚠️ No invoice content found for service: {service_name}"

    except Exception as e:
        return f"❌ Error occurred: {e}"
    

def list_services(driver=None):
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".service-buttons button")))

        buttons = driver.find_elements(By.CSS_SELECTOR, ".service-buttons button")
        services = []
        
        for btn in buttons:
            label = btn.get_attribute("innerText").strip()
            if label:
                services.append(label)
        
        if not services:
            return "⚠️ No services found."
        
        return "The following services are available:<ul>" + "".join(f"<li>{service}</li>" for service in services) + "</ul>"
    except Exception as e:
        return f"❌ Error while listing services: {e}"
    

def update_preference_button(service_name, driver=None) -> str:
    try:
        driver.get("http://localhost:7001/select_service")  # Update if route differs
        wait = WebDriverWait(driver, 10)

        select_service_via_browser(service_name, driver=driver)

        print(f"✅ Selected service: {service_name}")
        try:
            view_button = wait.until(EC.presence_of_element_located((By.ID, "updatePreferenceButton")))
            view_button.click()  # or whatever you need to do with it
        except Exception as e:
            return "❌ 'Update Preference' button not found."

    except Exception as e:
        return f"❌ Error occurred: {e}"
    
def list_customers(service_name, driver=None):
    try:
        update_preference_button(service_name, driver=driver)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".customer-btn")))

        buttons = driver.find_elements(By.CSS_SELECTOR, ".customer-btn")
        customers = []

        for btn in buttons:
            label = btn.get_attribute("innerText").strip()
            if label:
                customers.append(label)

        if not customers:
            return "⚠️ No customers found."

        return "The following customers are available:<ul>" + "".join(f"<li>{c}</li>" for c in customers) + "</ul>"
    
    except Exception as e:
        return f"❌ Error while listing customers: {e}"


def copy_previous(service_name, driver=None):
    try:
        update_preference_button(service_name, driver=driver)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "copyPreviousData")))
        
        button = driver.find_element(By.ID, "copyPreviousData")
        button.click()
        
        time.sleep(1)
        return f"Copied previous data for service: {service_name}!"
    except Exception as e:
        return f"Error while copying previous data: {e}"
    
def add_customer_button(service_name, driver=None):
    try:
        update_preference_button(service_name, driver=driver)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "addNewCustomer")))
        
        button = driver.find_element(By.ID, "addNewCustomer")
        button.click()
        
        time.sleep(1)
        return f"{service_name} has been selected. Please enter the customer details in the form that appears."
    except Exception as e:
        return f"❌ Error occurred: {e}"
    
def select_customer(service_name, customer_name, driver=None):
    try:
        update_preference_button(service_name, driver=driver)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".customer-btn")))

        buttons = driver.find_elements(By.CSS_SELECTOR, ".customer-btn")
        for btn in buttons:
            label = btn.get_attribute("innerText").strip()
            if label.lower() == customer_name.lower():
                btn.click()
                return f"Customer '{customer_name}' selected for updating. Please proceed with the update."
        
        return f"❌ Customer '{customer_name}' not found on the page."

    except Exception as e:
        return f"❌ Error while selecting customer: {e}"
    
def update_tax_rates(service_name: str, cgst: float = None, sgst: float = None, driver=None) -> str:
    try:
        update_preference_button(service_name, driver=driver)
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.visibility_of_element_located((By.ID, "cgst")))
        
        # Find input fields
        cgst_input = driver.find_element(By.ID, "cgst")
        sgst_input = driver.find_element(By.ID, "sgst")

        # Update CGST only if provided
        if cgst is not None:
            cgst_input.clear()
            cgst_input.send_keys(str(cgst))
        else:
            cgst = cgst_input.get_attribute("value")

        # Update SGST only if provided
        if sgst is not None:
            sgst_input.clear()
            sgst_input.send_keys(str(sgst))
        else:
            sgst = sgst_input.get_attribute("value")

        # Submit the form
        submit_button = driver.find_element(By.CSS_SELECTOR, ".form-btn.save")
        submit_button.click()

        return f"✅ Tax rates updated for '{service_name}': CGST={cgst}%, SGST={sgst}%"

    except Exception as e:
        return f"❌ Failed to update tax rates: {e}"


