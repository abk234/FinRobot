#!/usr/bin/env python3
"""
Simple Web Interface for FinRobot

Run this script and open http://localhost:8250 in your browser
(Default port is 8250, or specify a custom port as argument)
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from flask import Flask, render_template_string, request, jsonify
import autogen
from finrobot.agents.workflow import SingleAssistant
from finrobot.utils import get_current_date, register_keys_from_json
import os

app = Flask(__name__)

# Load API keys
try:
    register_keys_from_json("config_api_keys")
except:
    pass

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FinRobot - Market Analyst</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .form-group {
            margin: 20px 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #34495e;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        button {
            background: #3498db;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background: #2980b9;
        }
        button:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            background: #ecf0f1;
            border-radius: 5px;
            white-space: pre-wrap;
            font-family: monospace;
        }
        .loading {
            text-align: center;
            color: #7f8c8d;
        }
        .error {
            color: #e74c3c;
            background: #fadbd8;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 FinRobot - Market Analyst</h1>
        
        <form id="analysisForm">
            <div class="form-group">
                <label for="ticker">Stock Ticker Symbol:</label>
                <input type="text" id="ticker" name="ticker" value="AAPL" required>
            </div>
            
            <div class="form-group">
                <label for="model">AI Model:</label>
                <select id="model" name="model">
                    <option value="gemini">Gemini 2.5 Flash (Free)</option>
                    <option value="openai">OpenAI GPT-4 (Requires Billing)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="query">Custom Query (Optional):</label>
                <textarea id="query" name="query" rows="3" placeholder="Leave empty for default analysis"></textarea>
            </div>
            
            <button type="submit" id="submitBtn">Analyze Stock</button>
        </form>
        
        <div id="result"></div>
    </div>
    
    <script>
        document.getElementById('analysisForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const resultDiv = document.getElementById('result');
            
            submitBtn.disabled = true;
            resultDiv.innerHTML = '<div class="loading">⏳ Analyzing... This may take a minute.</div>';
            
            const formData = {
                ticker: document.getElementById('ticker').value,
                model: document.getElementById('model').value,
                query: document.getElementById('query').value
            };
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = '<div class="result">' + data.result + '</div>';
                } else {
                    resultDiv.innerHTML = '<div class="error">Error: ' + data.error + '</div>';
                }
            } catch (error) {
                resultDiv.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
            } finally {
                submitBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        ticker = data.get('ticker', 'AAPL').upper()
        model_type = data.get('model', 'gemini')
        custom_query = data.get('query', '')
        
        # Select config file based on model
        config_file = "GEMINI_CONFIG_LIST" if model_type == "gemini" else "OAI_CONFIG_LIST"
        model_filter = ["gemini-2.5-flash"] if model_type == "gemini" else ["gpt-4o"]
        
        if not os.path.exists(config_file):
            return jsonify({
                "success": False,
                "error": f"Config file {config_file} not found"
            })
        
        # Configure LLM using new API (replaces deprecated config_list_from_json)
        llm_config_obj = autogen.LLMConfig.from_json(
            path=config_file,
            filter_dict={"model": model_filter},
        )
        llm_config = {
            "config_list": llm_config_obj.config_list,
            "timeout": 120,
            "temperature": 0,
        }
        
        # Create agent
        assistant = SingleAssistant(
            "Market_Analyst",
            llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
        )
        
        # Build query
        if custom_query:
            message = custom_query
        else:
            message = (
                f"Use all the tools provided to retrieve information available for {ticker} "
                f"upon {get_current_date()}. Analyze the positive developments and potential "
                f"concerns of {ticker} with 2-4 most important factors respectively and keep "
                f"them concise. Most factors should be inferred from company related news. "
                f"Then make a rough prediction (e.g. up/down by 2-3%) of the {ticker} stock "
                f"price movement for next week. Provide a summary analysis to support your prediction."
            )
        
        # Run analysis
        assistant.chat(message)
        
        # Get the result from the last message
        messages = assistant.assistant.chat_messages[assistant.user_proxy]
        if messages:
            last_message = messages[-1].get("content", "Analysis completed.")
            return jsonify({
                "success": True,
                "result": last_message
            })
        else:
            return jsonify({
                "success": True,
                "result": "Analysis completed. Check the conversation history."
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == '__main__':
    import sys
    
    # Allow port to be specified as command line argument
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8250
    
    print("=" * 60)
    print("FinRobot Web Interface")
    print("=" * 60)
    print(f"\n🌐 Starting web server on port {port}...")
    print(f"📱 Open your browser and go to: http://localhost:{port}")
    print("🛑 Press Ctrl+C to stop the server\n")
    app.run(host='0.0.0.0', port=port, debug=False)

