import subprocess
import os
import pandas as pd
import time
import platform
import requests
import sys
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'invoiceEditor'))

if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from update_excel import *

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
    
def view_current_invoice_for_service(service_name: str, driver=None, action='generate') -> str:
    try:
        df = your_invoice_function(action, service_name)
        if df.empty:
            return f"⚠️ No invoice data found for **{service_name}**."

        # Get the top 3-5 rows to summarize
        sample = df.head(5)

        preview = sample.to_markdown(index=False, tablefmt="grid")

        return f"🧾 **Current Month's Invoice for {service_name}**\n```\n{preview}\n```"
    
    except Exception as e:
        return f"❌ Failed to load invoice for {service_name}: {e}"
    

def list_services(driver=None):
    try:
        services = get_services()

        if not services:
            return "⚠️ No services found."
        
        return "The following services are available:<ul>" + "".join(f"<li>{service}</li>" for service in services) + "</ul>"
    except Exception as e:
        return f"❌ Error while listing services: {e}"


def list_customers(service=None, driver=None):
    try:
        if not service:
            return "❌ Please specify a service name to list customers."

        customers = get_customers(service)

        if not customers:
            return f"⚠️ No customers found for service '{service}'."

        return f"Here are the customers for **{service}**:<ul>" + "".join(f"<li>{cust}</li>" for cust in customers) + "</ul>"
    
    except Exception as e:
        return f"❌ Error while listing customers for {service}: {e}"

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
    
def update_tax_rates(service_name: str, cgst: float = None, sgst: float = None, driver=None) -> str:
    try:
        if not service_name:
            return "❌ Service name is required."

        current = get_service_tax(service_name)

        if cgst is None:
            cgst = current.get('cgst', 0.0)
        if sgst is None:
            sgst = current.get('sgst', 0.0)

        update_service_tax(service_name, cgst, sgst)

        return f"✅ Tax rates updated for **{service_name}**: CGST={cgst * 100:.2f}%, SGST={sgst * 100:.2f}%"
    except Exception as e:
        return f"❌ Failed to update tax rates: {e}"


