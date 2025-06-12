from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import datetime
import logging
import os
from agent import *

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # path to /src
TEMPLATE_DIR = os.path.join(BASE_DIR, '../templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store prompts (in production, you'd use a database)
prompts_history = []

@app.route('/')
def home():
    """Serve the HTML frontend"""
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                "error": "No prompt provided",
                "status": "error"
            }), 400
        
        prompt = data['prompt'].strip()
        
        if not prompt:
            return jsonify({
                "error": "Empty prompt provided",
                "status": "error"
            }), 400
        
        # Log the received prompt
        timestamp = datetime.datetime.now().isoformat()
        logger.info(f"Received prompt at {timestamp}: {prompt}")
        
        # Store the prompt with metadata
        prompt_data = {
            "prompt": prompt,
            "timestamp": timestamp
        }
        prompts_history.append(prompt_data)
        
        # For now, just echo back a confirmation
        # This is where you'd integrate your AI model
        response_message = get_input(prompt_data)
        #response_message = f"I received your message: '{prompt}'. This is where your AI response would go!"
        
        return jsonify({
            "response": response_message,
            "status": "success",
            "timestamp": timestamp,
            "prompt_id": len(prompts_history)
        })
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "status": "error"
        }), 500

@app.route('/prompts', methods=['GET'])
def get_prompts():
    """Get all stored prompts (for debugging/monitoring)"""
    try:
        return jsonify({
            "prompts": prompts_history,
            "total_count": len(prompts_history),
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error retrieving prompts: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "status": "error"
        }), 500

@app.route('/prompts/latest', methods=['GET'])
def get_latest_prompt():
    """Get the most recent prompt"""
    try:
        if not prompts_history:
            return jsonify({
                "message": "No prompts found",
                "status": "success"
            })
        
        return jsonify({
            "latest_prompt": prompts_history[-1],
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error retrieving latest prompt: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "status": "error"
        }), 500

@app.route('/prompts/clear', methods=['DELETE'])
def clear_prompts():
    """Clear all stored prompts"""
    try:
        global prompts_history
        prompts_history = []
        return jsonify({
            "message": "All prompts cleared",
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error clearing prompts: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "status": "error"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "status": "error"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "status": "error"
    }), 500

if __name__ == '__main__':
    print("🚀 Starting AI Assistant Backend...")
    """ print("📡 Server will be available at: http://localhost:5000")
    print("💬 Chat endpoint: http://localhost:5000/chat")
    print("📋 View prompts: http://localhost:5000/prompts")
    print("🔍 Latest prompt: http://localhost:5000/prompts/latest")
    print("🧹 Clear prompts: DELETE http://localhost:5000/prompts/clear")"""
    print("-" * 50)
    
    app.run(debug=True, port=8000)