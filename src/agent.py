import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from invoiceEditor.admin_fn import *
from invoiceEditor.update_excel import *
from src.tools import *
from typing import Dict, Any
from langchain_community.llms import Ollama
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import PromptTemplate

class CommandParser(BaseOutputParser):
    def parse(self, text:str) -> Dict[str, Any]:
        try:
            if text.strip().startswith('{'):
                return json.loads(text.strip())
            
            # Fallback: extract command and action from text
            lines = text.strip().split('\n')
            result = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    result[key.strip().lower()] = value.strip().strip('"')
            
            return result
        except:
            return {"command": "unknown", "action": "none"}

class CommandInterpreter:
    def __init__(self, model: str="llama3.2:1b"):
        self.llm = Ollama(model=model)
        self.parser = CommandParser()
        
        self.command_registry = {
            "invoice_management": {
                "function" : "open_editor",
                "description": "Start the Invoice Management Website"
            },
            "invoice_system": {
                "function" : "open_editor",
                "description": "Open the invoice management system"
            },
            "billing_app": {
                "function" : "open_editor",
                "description": "Launch the billing and invoice application"
            }
        }
        
        self.prompt_template = PromptTemplate(
            input_variables=["user_command", "available_commands"],
            template = """
            You are a command interpreter. Based on the user's natural language command, identify which action to take.

            Available commands:
            {available_commands}

            User command: "{user_command}"

            Respond with a JSON object containing:
            - "command": the matching command key from available commands
            - "confidence": a number from 0-100 indicating your confidence
            - "action": brief description of what will be executed

            If no clear match, use "command": "unknown"

            Response:"""
        )
        
    def interpret_command(self, user_input:str) -> Dict[str, Any]:
        commands_text = "\n".join([
            f"- {key}: {info['description']}" 
            for key, info in self.command_registry.items()
        ])
        
        prompt = self.prompt_template.format(
            user_command=user_input,
            available_commands=commands_text
        )
        
        response = self.llm(prompt)
        print(f"Result: {response}")
        parsed_response = self.parser.parse(response)
        
        return parsed_response

def main():
    interpreter = CommandInterpreter()
    
    user_prompts = [
        "Open the invoice management system",
        "Start the billing app",
        "Launch invoice website",
        "I want to manage invoices"
    ]
    
    for prompt in user_prompts:
        print(f"\n--- Processing: '{prompt}' ---")
        result = interpreter.interpret_command(prompt)
        
if __name__ == "__main__":
    main()