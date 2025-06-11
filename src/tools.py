from langchain.tools import tool
import subprocess
import os

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
