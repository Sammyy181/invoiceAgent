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

function_map = {
    'open_editor' : open_editor
}

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
                "description": "Launch the invoice management website"
            },
            "invoice_system": {
                "function" : "open_editor",
                "description": "Open the invoice management system"
            }
        }

        self.prompt_template = PromptTemplate(
            input_variables=["user_command", "available_commands"],
            template="""
                You are an intelligent command interpreter.

                Your task is to **analyze the user's natural language command** and **match it** with the most appropriate command from the list of available commands.

                Instructions:
                1. Carefully read the user's command.
                2. Review the list of available commands and match the intent.
                3. If you find a good match, respond with:
                    - "command": the key of the matching command from the list
                    - "confidence": your confidence level (0 to 100) in the match
                    - "action": a short explanation of what the command will do
                4. If you **cannot confidently match**, respond with:
                    - "command": "unknown"
                    - "confidence": a low number (e.g., 0–30)
                    - "action": "Could not confidently determine the appropriate command."

                Important: Do **not** invent commands that are not in the list. Match only from available_commands.

                ---

                Available Commands:
                {available_commands}

                User Command:
                "{user_command}"

                ---

                Respond in this exact JSON format:
                {{
                "command": "...",
                "confidence": ...,
                "action": "..."
                }}
                """
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
        
        response = self.llm.invoke(prompt)
        #print(f"Result: {response}")
        parsed_response = self.parser.parse(response)
        
        return parsed_response
    
    def execute_command(self, user_input: str) -> Dict[str, Any]:
        
        interpretation = self.interpret_command(user_input)
        
        print(f"Interpreted command: {interpretation}")
        
        command = interpretation.get("command", "unknown")
        confidence = interpretation.get("confidence", 0)
        
        if command == "unknown" or confidence < 50:
            return {
                "status": "failed",
                "message": "Could not understand the command or confidence too low",
                "interpretation": interpretation
            }
        
        # Execute the command if it exists in registry
        if command in self.command_registry:
            try:
                command_info = self.command_registry[command]
                function_name = command_info.get("function")
                
                if function_name:
                    # Get the function from the tools module
                    if function_name in function_map:
                        func = function_map[function_name]
                        if hasattr(func, "invoke"):  # check if it's a Tool
                            result = func.invoke("")  # pass empty string or real input
                        else:
                            result = func()  # plain Python function
                        
                        return {
                            "status": "success",
                            "message": f"Successfully executed {function_name}",
                            "function_result": result,
                            "interpretation": interpretation
                        }
                    else:
                        return {
                            "status": "failed",
                            "message": f"Function {function_name} not found.",
                            "interpretation": interpretation
                        }
                else:
                    return {
                        "status": "failed",
                        "message": f"No function specified for command {command}",
                        "interpretation": interpretation
                    }
                    
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error executing command: {str(e)}",
                    "interpretation": interpretation
                }
        else:
            return {
                "status": "failed",
                "message": f"Command {command} not found in registry",
                "interpretation": interpretation
            }       

"""def main():
    interpreter = CommandInterpreter()
    
    user_prompts = [
        "Open the invoice management system"
    ]
    
    for prompt in user_prompts:
        print(f"\n--- Processing: '{prompt}' ---")
        result = interpreter.execute_command(prompt)
        print(f"Result: {result}")
        
if __name__ == "__main__":
    main()"""
    
def get_input(user_input):
    interpreter = CommandInterpreter()
    
    result = interpreter.execute_command(user_input)
    print(f"Status: {result['message']}")