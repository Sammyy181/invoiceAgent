import json
from tools import *
from typing import Dict, Any
from langchain_community.llms import Ollama
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import PromptTemplate
from difflib import SequenceMatcher
import re

function_map = {
    'open_editor' : open_editor,
    'add_service' : add_service,
    'close_editor' : kill_process,
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
        #self.llm = Ollama(model=model)
        self.parser = CommandParser()
        
        self.command_registry = {
            "invoice_management": {
                "function" : "open_editor",
                "description": "Open the invoice management website",
                "parameters": []
            },
            "invoice_system": {
                "function" : "open_editor",
                "description": "Launch the invoice management system",
                "parameters": []
            },
            "service_addition": {
                "function" : "add_service",
                "description" : "Add a New Service",
                "parameters": ["service_name"]
            },
            "service_creation": {
                "function" : "create_service",
                "description" : "Create a new service",
                "parameters": ["service_name"]
            },
            "close_website": {
                "function" : "close_editor",
                "description": "Shut down the invoice management website",
                "parameters": []
            },
            "close_system": {
                "function" : "close_editor",
                "description": "Close the invoice management system",
                "parameters": []
            }
        }

        self.prompt_template = PromptTemplate(
            input_variables=["user_command", "available_commands"],
            template="""
                You are an intelligent command interpreter.

                Your task is to:
                1. Analyze the user's natural language command.
                2. Match it with the most appropriate command from the list below.
                3. Extract any parameters mentioned in the user input that are required by the matched command.

                Respond in the following JSON format:
                {{
                    "command": "...",          // key from available_commands
                    "confidence": ...,         // 0 to 100
                    "action": "...",           // short explanation
                    "parameters": {{           // optional, based on the command
                        "param_name": "value"
                    }}
                }}

                If no command can be confidently matched, respond:
                {{
                    "command": "unknown",
                    "confidence": 0,
                    "action": "Could not confidently determine the appropriate command.",
                    "parameters": {{}}
                }}

                ---

                Available Commands:
                {available_commands}

                User Command:
                "{user_command}"
                ---
            """
        )
        
    def interpret_command(self, user_input:str) -> Dict[str, Any]:
        """commands_text = "\n".join([
            f"- {key}: {info['description']}" 
            for key, info in self.command_registry.items()
        ])
        
        prompt = self.prompt_template.format(
            user_command=user_input,
            available_commands=commands_text
        )
        
        response = self.llm.invoke(prompt)
        #print(f"Result: {response}")
        parsed_response = self.parser.parse(response)"""
        
        user_input_lower = user_input.lower().strip()
        
        best_match = None
        best_score = 0
        best_command_key = None
    
        for cmd_key, cmd_data in self.command_registry.items():
            description_lower = cmd_data["description"].lower()
            
            # Calculate similarity score
            similarity = SequenceMatcher(None, user_input_lower, description_lower).ratio()
            
            # Also check for key word matches
            user_words = set(user_input_lower.split())
            desc_words = set(description_lower.split())
            common_words = user_words.intersection(desc_words)
            word_match_score = len(common_words) / max(len(desc_words), 1)
            
            # Combined score (weighted)
            combined_score = (similarity * 0.6) + (word_match_score * 0.4)
            
            # Set minimum threshold for matching
            if combined_score > best_score and combined_score > 0.3:
                best_score = combined_score
                best_match = cmd_data
                best_command_key = cmd_key
            
        print(f"Best match: {best_command_key} with score {best_score}")
        
        if best_match is None:
            return {
                "command": "unknown",
                "parameters": {}
            }
        
        result = {
            "command": best_command_key
        }
        
        # If the command requires parameters, try to extract them
        if best_match["parameters"]:
            parameters = {}
            
            # For service-related commands, try to extract service name
            if "service_name" in best_match["parameters"]:
                # Look for service name patterns
                service_patterns = [
                    r'service[:\s]+(["\']?)([^"\']+)\1',  # "service: name" or "service name"
                    r'add[:\s]+(["\']?)([^"\']+)\1',      # "add: name" or "add name"
                    r'create[:\s]+(["\']?)([^"\']+)\1',   # "create: name" or "create name"
                    r'new[:\s]+(["\']?)([^"\']+)\1',      # "new: name" or "new name"
                    r'called[:\s]+(["\']?)([^"\']+)\1',   # "called name"
                    r'named[:\s]+(["\']?)([^"\']+)\1'     # "named name"
                ]
                
                service_name = None
                for pattern in service_patterns:
                    match = re.search(pattern, user_input_lower)
                    if match:
                        service_name = match.group(2).strip()
                        break
                
                # If no pattern matched, try to extract the last word/phrase
                if not service_name:
                    words = user_input.strip().split()
                    if len(words) > 2:  # Assume last word(s) might be the service name
                        service_name = ' '.join(words[-2:]) if len(words) > 3 else words[-1]
                
                if service_name:
                    parameters["service_name"] = service_name
            
            result["parameters"] = parameters
        else:
            result["parameters"] = {}
        
        return result
    
    def execute_command(self, user_input: str) -> Dict[str, Any]:
        
        interpretation = self.interpret_command(user_input)
        
        print(f"Interpreted command: {interpretation}")
        
        command = interpretation.get("command", "unknown")
        """confidence = interpretation.get("confidence", 0)
        
        if command == "unknown" or confidence < 50:
            return {
                "status": "failed",
                "message": "Could not understand the command or confidence too low",
                "interpretation": interpretation
            }"""
        
        # Execute the command if it exists in registry
        if command in self.command_registry:
            try:
                command_info = self.command_registry[command]
                function_name = command_info.get("function")
                required_params = command_info.get("parameters", [])

                if function_name:
                    # Get the function from the tools module
                    if function_name in function_map:
                        func = function_map[function_name]

                        if hasattr(func, "invoke"):  # check if it's a Tool
                            result = func.invoke("")  # Optional: pass input string here if needed
                        else:
                            # Collect actual parameter values from the interpreted result
                            param_values = [
                                interpretation.get("parameters", {}).get(param_name, None)
                                for param_name in required_params
                            ]

                            # Check if all required parameters are present
                            if all(val is not None for val in param_values):
                                result = func(*param_values)
                            else:
                                result = {
                                    "status": "failed",
                                    "message": f"Missing required parameters: {required_params}"
                                }
                        
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
                            "function_result" : "",
                            "interpretation": interpretation
                        }
                else:
                    return {
                        "status": "failed",
                        "message": f"No function specified for command {command}",
                        "function_result" : "",
                        "interpretation": interpretation
                    }
                    
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error executing command: {str(e)}",
                    "function_result" : "",
                    "interpretation": interpretation
                }
        else:
            return {
                "status": "failed",
                "message": f"Command {command} not found in registry",
                "function_result" : "",
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
    result = interpreter.execute_command(user_input['prompt'])
    
    status = result.get("status", "unknown")
    function_result = result.get("function_result", None)
    
    print(f"Status: {status}")
    print(f"Result: {function_result}")
    
    return function_result