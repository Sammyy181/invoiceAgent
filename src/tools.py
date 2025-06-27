import os
import pandas as pd
from flask import url_for
import sys
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'invoiceEditor'))

if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from update_excel import *
from admin_fn import *

from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

def add_service(service_name: str) -> str: 
    try:
        excel_path = os.path.join("data", f"{service_name}.xlsx")
        column_path = os.path.join("columns", f"{service_name}.json")
        titles_path = os.path.join("titles", f"{service_name}.json")
        categories_path = os.path.join("categories", f"{service_name}.json")
        
        now = datetime.now()
        current_month = now.strftime("%B")
        previous_month = (now - relativedelta(months=1)).strftime("%B")
        try:
            df = pd.read_excel("template.xlsx", sheet_name=current_month)
        except Exception:
            df = pd.read_excel("template.xlsx", sheet_name=previous_month)
            
        df.to_excel(excel_path, sheet_name=current_month, index=False)
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
    
def view_invoice_for_service(service_name: str, driver=None) -> str:
    try:
        df = your_invoice_function(action='view', service=service_name)
        
        if df.empty:
            return f"<p>⚠️ No invoice data found for <b>{service_name}</b> (last month).</p>"
        
        sample = df.head(5)
        table_html = sample.to_html(index=False, classes="chatbot-invoice-table", border=1)

        return f"<b>📄 Last Month's Invoice for {service_name}</b><br><br>{table_html}"
    
    except Exception as e:
        return f"<p>❌ Failed to load invoice for <b>{service_name}</b>: {e}</p>"
    
def view_current_invoice_for_service(service_name: str, driver=None, action='generate') -> str:
    try:
        df = your_invoice_function(action, service_name)
        if df.empty:
            return f"<p>⚠️ No invoice data found for <b>{service_name}</b>.</p>"

        sample = df.head(10)
        table_html = sample.to_html(index=False, classes="chatbot-invoice-table", border=1)

        return f"<b>🧾 Current Month's Invoice for {service_name}</b><br><br>{table_html}"
    
    except Exception as e:
        return f"<p>❌ Failed to load invoice for <b>{service_name}</b>: {e}</p>"    

def list_services():
    try:
        services = get_services()

        if not services:
            return "⚠️ No services found."
        
        return "The following services are available:<ul>" + "".join(f"<li>{service}</li>" for service in services) + "</ul>"
    except Exception as e:
        return f"❌ Error while listing services: {e}"


def list_customers(service_name=None):
    try:
        if not service_name:
            return "❌ Please specify a service name to list customers."
        
        customers = get_customers(service_name)

        if not customers:
            return f"⚠️ No customers found for service '{service_name}'."

        return f"Here are the customers for <strong>{service_name}</strong>:<ul>" + "".join(f"<li>{cust}</li>" for cust in customers) + "</ul>"
    
    except Exception as e:
        return f"❌ Error while listing customers for {service_name}: {e}"

def copy_previous(service_name):
    try:
        copy_previous_data(service=service_name)
        return f"Copied previous data for service: {service_name}!"
    except Exception as e:
        return f"Error while copying previous data: {e}"
    
def add_customer_button(service_name):
    try:
        columns = load_service_columns(service_name)
        titles = load_service_titles(service_name)

        html = f'<form id="addCustomerForm" method="POST" action="{url_for("add_customer")}" style="font-size: 0.85rem;">\n'
        html += f'  <div>\n'
        html += f'        <input type="hidden" name="service" value="{service_name}" />\n'
        html += f'    <p style="margin-bottom: 8px; font-weight: bold;">Add Customer:</p>\n'

        def render_input(label, field_id, input_type="text"):
            return f'''    <div style="margin-bottom: 10px;">
      <label for="{field_id}" style="display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 4px;">{label}</label>
      <input type="{input_type}" id="{field_id}" name="{field_id}" style="width: 100%; padding: 6px; font-size: 0.85rem;" />
    </div>\n'''

        def get_title_by_id(titles, target_id):
            for t in titles:
                if t["id"] == target_id:
                    return t["title"]
            return None

        html +=  f'''    <div style="margin-bottom: 10px;">
                            <label for="customerName" style="display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 4px;">{get_title_by_id(titles, 'fixed_1')}</label>
                            <input type="text" id="customerName" name="customer_name" style="width: 100%; padding: 6px; font-size: 0.85rem;" />
                        </div>\n'''
                        
        html +=  f'''    <div style="margin-bottom: 10px;">
                            <label for="category" style="display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 4px;">{get_title_by_id(titles, 'fixed_7')}</label>
                            <input type="text" id="category" name="selected_id" style="width: 100%; padding: 6px; font-size: 0.85rem;" />
                        </div>\n'''
        
        html +=  f'''    <div style="margin-bottom: 10px;">
                            <label for="unitPrice" style="display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 4px;">{get_title_by_id(titles, 'fixed_2')}</label>
                            <input type="number" id="unitPrice" name="unit_price" step="10" style="width: 100%; padding: 6px; font-size: 0.85rem;" />
                        </div>\n'''
        
        html +=  f'''    <div style="margin-bottom: 10px;">
                            <label for="consumptionPeriod" style="display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 4px;">{get_title_by_id(titles, 'fixed_3')}</label>
                            <input type="text" id="consumptionPeriod" name="consumption_period" style="width: 100%; padding: 6px; font-size: 0.85rem;" />
                        </div>\n'''
        
        html +=  f'''    <div style="margin-bottom: 10px;">
                            <label for="usagePercent" style="display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 4px;">{get_title_by_id(titles, 'fixed_4')}</label>
                            <input type="text" id="usagePercent" name="usage_percent" min="0" max="100" step="1" style="width: 100%; padding: 6px; font-size: 0.85rem;" />
                        </div>\n''' 

        for col in columns:
            field_id = col["title"].lower().replace(" ", "_")
            input_type = col.get("type", "text")
            html += render_input(col["title"], field_id, input_type)

        html += '    <button type="submit" style="font-size: 0.85rem; padding: 6px 12px;">Add Customer</button>\n'
        html += '  </div>\n</form>'

        return html

    except Exception as e:
        return { "error": str(e) }
    
def edit_customer(service_name, customer_name):
    try:
        columns = load_service_columns(service_name)
        titles = load_service_titles(service_name)
        
        html = f'<form id="editCustomerForm" method="POST" action="{url_for("update_customer")}" style="font-size: 0.85rem;">\n'
        html += f'  <div>\n'
        html += f'        <input type="hidden" name="service" value="{service_name}" />\n'
        html += f'        <input type="hidden" name="customer" value="{customer_name}" />\n'
        html += f'    <p style="margin-bottom: 8px; font-weight: bold;">Edit Customer:</p>\n'

        def render_input(label, field_id, input_type="text"):
            return f'''    <div style="margin-bottom: 10px;">
                <label for="{field_id}" style="display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 4px;">{label}</label>
                <input type="{input_type}" id="{field_id}" name="{field_id}" style="width: 100%; padding: 6px; font-size: 0.85rem;" />
            </div>\n'''
        
        def get_title_by_id(titles, target_id):
            for t in titles:
                if t["id"] == target_id:
                    return t["title"]
            return None
        
        html +=  f'''    <div style="margin-bottom: 10px;">
                                <label for="category" style="display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 4px;">{get_title_by_id(titles, 'fixed_7')}</label>
                                <input type="text" id="category" name="category" style="width: 100%; padding: 6px; font-size: 0.85rem;" />
                            </div>\n'''
            
        html +=  f'''    <div style="margin-bottom: 10px;">
                            <label for="unitPrice" style="display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 4px;">{get_title_by_id(titles, 'fixed_2')}</label>
                            <input type="number" id="unitPrice" name="cost" step="10" style="width: 100%; padding: 6px; font-size: 0.85rem;" />
                        </div>\n'''
        
        html +=  f'''    <div style="margin-bottom: 10px;">
                            <label for="consumptionPeriod" style="display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 4px;">{get_title_by_id(titles, 'fixed_3')}</label>
                            <input type="text" id="consumptionPeriod" name="period" style="width: 100%; padding: 6px; font-size: 0.85rem;" />
                        </div>\n'''
        
        html +=  f'''    <div style="margin-bottom: 10px;">
                            <label for="usagePercent" style="display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 4px;">{get_title_by_id(titles, 'fixed_4')}</label>
                            <input type="text" id="usagePercent" name="usage" min="0" max="100" step="1" style="width: 100%; padding: 6px; font-size: 0.85rem;" />
                        </div>\n''' 
        
        for col in columns:
                field_id = col["title"].lower().replace(" ", "_")
                input_type = col.get("type", "text")
                html += render_input(col["title"], field_id, input_type)

        html += '    <button type="submit" style="font-size: 0.85rem; padding: 6px 12px;">Edit Customer</button>\n'
        html += '  </div>\n</form>'
        return html
    
    except Exception as e:
        return { "error": str(e) }
    
def update_tax_rates(service_name: str, cgst: float = None, sgst: float = None, driver=None) -> str:
    try:
        if not service_name:
            return "❌ Service name is required."
        service_name = service_name.capitalize()
        
        if type(cgst) != float:
            cgst = cgst.strip().replace('%','')
            cgst = (float(cgst))/100
        if type(sgst) != float:
            sgst = sgst.strip().replace('%','')
            sgst = (float(sgst))/100

        current = get_service_tax(service_name)

        if cgst is None:
            cgst = current.get('cgst', 0.0)
        if sgst is None:
            sgst = current.get('sgst', 0.0)

        update_service_tax(service_name, cgst, sgst)

        return f"✅ Tax rates updated for <strong>{service_name}</strong>: CGST={cgst * 100:.2f}%, SGST={sgst * 100:.2f}%"
    except Exception as e:
        return f"❌ Failed to update tax rates: {e}"


