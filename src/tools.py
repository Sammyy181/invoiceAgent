import subprocess
import os
import sys
import time
import platform
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'invoiceEditor')))
from update_excel import *

def add_service(service_name: str) -> str: 
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
        
        time.sleep(1)  # wait for service to be added
        
        buttons = driver.find_elements(By.CSS_SELECTOR, ".service-buttons button")
        found = False
        
        for btn in buttons:
            if btn.text.strip() == service_name:
                btn.click()  
                found = True
                break

        if not found:
            return f"❌ Service '{service_name}' not found after adding."

        return f"✅ Service '{service_name}' added via UI."

    except Exception as e:
        return f"❌ Error while interacting with browser: {e}"
    
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


