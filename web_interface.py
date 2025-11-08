#!/usr/bin/env python3
"""
Simple Web Interface for FinRobot

Run this script and open http://localhost:8250 in your browser
(Default port is 8250, or specify a custom port as argument)
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from flask import Flask, render_template_string, request, jsonify, send_from_directory, make_response
import autogen
from finrobot.agents.workflow import SingleAssistant
from finrobot.utils import get_current_date, register_keys_from_json
from finrobot.functional.quantitative import TradingStrategyAnalyzer
from finrobot.agents.trading_chat_agent import create_trading_chat_agent, process_chat_message
from finrobot.functional.charting import MplFinanceUtils
import os
import uuid
import re
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Session storage (in-memory dict for simplicity)
# In production, consider using Redis or database
sessions = {}

# Load API keys
try:
    register_keys_from_json("config_api_keys")
except:
    pass

# Create static/charts directory if it doesn't exist
CHARTS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)

def get_or_create_session(session_id=None):
    """Get existing session or create a new one."""
    if session_id and session_id in sessions:
        return sessions[session_id]
    
    new_session_id = str(uuid.uuid4())
    sessions[new_session_id] = {
        "session_id": new_session_id,
        "ticker": None,
        "analysis_params": {},
        "last_analysis": "",
        "conversation_history": [],
        "agent_context": {},
        "created_at": datetime.now()
    }
    return sessions[new_session_id]

def cleanup_old_sessions():
    """Remove sessions older than 24 hours."""
    cutoff = datetime.now() - timedelta(hours=24)
    to_remove = [sid for sid, session in sessions.items() 
                 if session.get("created_at", datetime.now()) < cutoff]
    for sid in to_remove:
        del sessions[sid]

def generate_chart(ticker, period="6mo", chart_type="candle", mav=None):
    """Generate a trading chart and return the URL."""
    try:
        from finrobot.data_source.yfinance_utils import YFinanceUtils
        import yfinance as yf
        import time
        
        # Calculate date range from period
        end_date = datetime.now()
        period_map = {
            "1mo": timedelta(days=30),
            "3mo": timedelta(days=90),
            "6mo": timedelta(days=180),
            "1y": timedelta(days=365),
            "2y": timedelta(days=730)
        }
        start_date = end_date - period_map.get(period, timedelta(days=180))
        
        # Generate unique filename
        chart_filename = f"{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        chart_path = os.path.join(CHARTS_DIR, chart_filename)
        
        # Try to generate chart with retry logic
        max_retries = 2
        for attempt in range(max_retries):
            try:
                MplFinanceUtils.plot_stock_price_chart(
                    ticker_symbol=ticker,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    save_path=chart_path,
                    type=chart_type,
                    mav=mav,
                    style="default"
                )
                return f"/static/charts/{chart_filename}"
            except Exception as e:
                if "401" in str(e) or "Unauthorized" in str(e):
                    if attempt < max_retries - 1:
                        time.sleep(3)  # Wait before retry
                        continue
                    else:
                        return None  # Return None on persistent 401 errors
                else:
                    raise  # Re-raise other errors
        return None
    except Exception as e:
        # Log error but don't crash
        print(f"Chart generation error: {str(e)}")
        return None

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FinRobot - Market Analyst</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .main-wrapper {
            display: flex;
            gap: 20px;
            align-items: flex-start;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            flex: 1;
            min-width: 0;
        }
        .container.full-width {
            flex: 1 1 100%;
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
            display: block !important;
            visibility: visible !important;
            min-height: 50px;
        }
        #result {
            display: block !important;
            visibility: visible !important;
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
        .info-panel {
            background: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .info-panel h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .info-panel ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .info-panel li {
            margin: 8px 0;
        }
        small {
            font-size: 12px;
            line-height: 1.4;
        }
        /* Chat Panel Styles */
        .chat-toggle-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #27ae60;
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
            display: block;
            transition: all 0.3s ease;
        }
        .chat-toggle-btn:hover {
            background: #229954;
            transform: scale(1.05);
        }
        .chat-toggle-btn:active {
            transform: scale(0.95);
        }
        .chat-toggle-btn.has-session {
            background: #3498db;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            50% { box-shadow: 0 4px 12px rgba(52, 152, 219, 0.5); }
        }
        .chat-panel {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            width: 400px;
            display: none;
            flex-direction: column;
            height: 600px;
            position: fixed;
            bottom: 80px;
            right: 20px;
            z-index: 999;
            transition: opacity 0.3s ease;
        }
        .chat-panel.active {
            display: flex !important;
            opacity: 1;
        }
        .chat-header {
            background: #3498db;
            color: white;
            padding: 15px;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chat-header h3 {
            margin: 0;
            font-size: 18px;
        }
        .chat-close-btn {
            background: transparent;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            line-height: 30px;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #f8f9fa;
        }
        .chat-message {
            margin-bottom: 15px;
            padding: 12px 15px;
            border-radius: 12px;
            max-width: 85%;
            word-wrap: break-word;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            line-height: 1.5;
        }
        .chat-message.user {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            margin-left: auto;
            text-align: left;
            border-bottom-right-radius: 4px;
        }
        .chat-message.assistant {
            background: #ffffff;
            color: #2c3e50;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        .chat-message.error {
            background: #fee;
            color: #c33;
            border: 1px solid #fcc;
            border-bottom-left-radius: 4px;
        }
        .chat-message.loading {
            background: #f8f9fa;
            color: #7f8c8d;
            font-style: italic;
            border: 1px solid #e0e0e0;
        }
        .chat-message img {
            max-width: 100%;
            border-radius: 8px;
            margin-top: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            display: block;
        }
        .chat-message .chart-container {
            margin-top: 10px;
            text-align: center;
        }
        .chat-message .chart-container img {
            max-width: 100%;
            height: auto;
        }
        .chat-input-area {
            padding: 15px;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 10px;
        }
        .chat-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .chat-send-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        .chat-send-btn:hover {
            background: #2980b9;
        }
        .chat-send-btn:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }
        .param-confirmation {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        .param-confirmation h4 {
            margin-top: 0;
            color: #856404;
        }
        .param-confirmation-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        .param-confirm-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
        }
        .param-reject-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
        }
        .toggle-info {
            background: #16a085;
            color: white;
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin: 10px 0;
        }
        .toggle-info:hover {
            background: #138d75;
        }
        #indicatorInfo {
            display: none;
        }
    </style>
</head>
<body>
    <div class="main-wrapper">
    <div class="container" id="mainContainer">
        <h1>🤖 FinRobot - Market Analyst</h1>
        
        <button type="button" class="toggle-info" onclick="toggleInfo()">
            📚 Learn About Technical Indicators (Click to Expand)
        </button>
        
        <div id="indicatorInfo" class="info-panel">
            <h3>📊 Understanding Technical Indicators - A Beginner's Guide</h3>
            
            <h4>🎯 What Are Technical Indicators?</h4>
            <p>Technical indicators are mathematical calculations based on a stock's price and volume. Think of them as tools that help you understand market sentiment and predict potential price movements. They're like a weather forecast for stocks - not 100% accurate, but helpful for making informed decisions.</p>
            
            <h4>1. 📈 Moving Averages (MA)</h4>
            <p><strong>What it is:</strong> A moving average smooths out price data to show the average price over a specific period (like 20 or 50 days).</p>
            <p><strong>Simple Explanation:</strong> Imagine you're tracking your daily spending. A 7-day moving average would show your average spending over the last week, smoothing out daily ups and downs.</p>
            <ul>
                <li><strong>Short MA (20 days):</strong> Shows recent price trends - reacts quickly to price changes</li>
                <li><strong>Long MA (50 days):</strong> Shows longer-term trends - slower to react but shows the bigger picture</li>
                <li><strong>What to look for:</strong> When short MA crosses above long MA = BULLISH (price likely to go up). When short MA crosses below long MA = BEARISH (price likely to go down)</li>
            </ul>
            
            <h4>2. 📊 RSI (Relative Strength Index)</h4>
            <p><strong>What it is:</strong> Measures how fast and how much a stock's price is changing. It ranges from 0 to 100.</p>
            <p><strong>Simple Explanation:</strong> Like a speedometer for stock prices. If a car is going too fast (overbought) or too slow (oversold), you know it might need to adjust.</p>
            <ul>
                <li><strong>RSI below 30:</strong> Stock is OVERSOLD (like a car going too slow) - might be a good time to BUY as price could bounce back</li>
                <li><strong>RSI above 70:</strong> Stock is OVERBOUGHT (like a car going too fast) - might be a good time to SELL or wait for a pullback</li>
                <li><strong>RSI 30-70:</strong> Normal range - stock is moving at a healthy pace</li>
            </ul>
            
            <h4>3. 📉 MACD (Moving Average Convergence Divergence)</h4>
            <p><strong>What it is:</strong> Shows the relationship between two moving averages and helps identify momentum changes.</p>
            <p><strong>Simple Explanation:</strong> Like a traffic light for stock momentum. When MACD line crosses above the signal line, it's like a green light (momentum building up). When it crosses below, it's like a red light (momentum slowing down).</p>
            <ul>
                <li><strong>MACD Line:</strong> The difference between fast and slow moving averages</li>
                <li><strong>Signal Line:</strong> A smoothed version of the MACD line</li>
                <li><strong>Histogram:</strong> The difference between MACD and Signal - shows how strong the momentum is</li>
                <li><strong>BULLISH Signal:</strong> MACD crosses above Signal + Histogram is increasing = Good time to consider buying</li>
                <li><strong>BEARISH Signal:</strong> MACD crosses below Signal = Consider selling or waiting</li>
            </ul>
            
            <h4>4. 🎯 Bollinger Bands</h4>
            <p><strong>What it is:</strong> Three lines that form a "band" around the stock price, showing volatility and potential price boundaries.</p>
            <p><strong>Simple Explanation:</strong> Like a rubber band around the price. When the price touches the edges, it often bounces back toward the middle - like a rubber band snapping back.</p>
            <ul>
                <li><strong>Upper Band:</strong> Like a ceiling - price rarely goes above this</li>
                <li><strong>Middle Band:</strong> The average price (like the center of the rubber band)</li>
                <li><strong>Lower Band:</strong> Like a floor - price rarely goes below this</li>
                <li><strong>Price touches Lower Band:</strong> OVERSOLD - might bounce up (potential BUY signal)</li>
                <li><strong>Price touches Upper Band:</strong> OVERBOUGHT - might pull back (potential SELL signal)</li>
                <li><strong>%B:</strong> Shows where price is within the bands (0 = at lower band, 1 = at upper band, 0.5 = at middle)</li>
            </ul>
            
            <h4>5. 🛡️ ATR (Average True Range) - For Stop Loss</h4>
            <p><strong>What it is:</strong> Measures how much a stock's price typically moves (volatility).</p>
            <p><strong>Simple Explanation:</strong> Like measuring how bumpy a road is. A bumpy road (high volatility) needs more space, while a smooth road (low volatility) needs less.</p>
            <ul>
                <li><strong>High ATR:</strong> Stock moves a lot - set stop loss further away (more room for price swings)</li>
                <li><strong>Low ATR:</strong> Stock moves little - set stop loss closer (less room needed)</li>
                <li><strong>Why it matters:</strong> Helps set stop loss at the right distance - not too close (gets hit by normal swings) or too far (loses too much if wrong)</li>
            </ul>
            
            <h4>6. 📍 Support and Resistance Levels</h4>
            <p><strong>What it is:</strong> Price levels where the stock has historically had trouble moving past.</p>
            <p><strong>Simple Explanation:</strong> Like floors and ceilings in a building. Support is like a floor - price bounces up from here. Resistance is like a ceiling - price bounces down from here.</p>
            <ul>
                <li><strong>Support Level:</strong> A price level where buyers often step in (like a safety net) - good place to set stop loss</li>
                <li><strong>Resistance Level:</strong> A price level where sellers often step in (like a ceiling) - good place to set target price</li>
                <li><strong>How to use:</strong> Buy near support, sell near resistance. Set stop loss below support, set target near resistance</li>
            </ul>
            
            <h4>7. 💰 Risk-Reward Ratio</h4>
            <p><strong>What it is:</strong> Compares how much you could lose vs. how much you could gain.</p>
            <p><strong>Simple Explanation:</strong> Like betting odds. A 2:1 ratio means you risk $1 to potentially make $2. Only take trades where potential reward is greater than risk.</p>
            <ul>
                <li><strong>2:1 Ratio:</strong> Risk $1, potential to make $2 - Good ratio</li>
                <li><strong>3:1 Ratio:</strong> Risk $1, potential to make $3 - Excellent ratio</li>
                <li><strong>1:1 Ratio:</strong> Risk $1, potential to make $1 - Not ideal (equal risk/reward)</li>
                <li><strong>Why it matters:</strong> Even if you're wrong 50% of the time, a 2:1 ratio means you'll still profit overall</li>
            </ul>
            
            <h4>🎓 How to Use These Indicators Together</h4>
            <p><strong>Think of it like a weather forecast:</strong></p>
            <ul>
                <li><strong>One indicator says "rain" (bearish):</strong> Maybe it will rain, maybe not</li>
                <li><strong>Two indicators say "rain":</strong> More likely to rain - be cautious</li>
                <li><strong>Three+ indicators agree:</strong> Very likely to rain - strong signal!</li>
            </ul>
            <p><strong>Our system counts confirmations:</strong></p>
            <ul>
                <li><strong>STRONG Signal:</strong> 2+ indicators agree - Higher confidence trade</li>
                <li><strong>MODERATE Signal:</strong> Mixed signals - Proceed with caution</li>
                <li><strong>WEAK Signal:</strong> Indicators disagree - Wait for better setup</li>
            </ul>
            
            <h4>⚠️ Important Reminders</h4>
            <ul>
                <li><strong>No indicator is 100% accurate</strong> - They're tools, not crystal balls</li>
                <li><strong>Always use stop loss</strong> - Protects you from big losses</li>
                <li><strong>Don't risk more than you can afford to lose</strong> - Only trade with money you can lose</li>
                <li><strong>Multiple confirmations are better</strong> - Wait for 2+ indicators to agree</li>
                <li><strong>Practice with paper trading first</strong> - Learn without risking real money</li>
            </ul>
        </div>
        
        <form id="analysisForm" onsubmit="event.preventDefault(); event.stopPropagation(); handleFormSubmit(event); return false;">
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
                <label for="analysisType">Analysis Type:</label>
                <select id="analysisType" name="analysisType">
                    <option value="market">Market Analysis (AI-Powered)</option>
                    <option value="trading">Trading Strategy (Entry/Stop/Target)</option>
                    <option value="comprehensive">Comprehensive Analysis (Recommended)</option>
                </select>
            </div>
            
            <div class="form-group" id="queryGroup">
                <label for="query">Custom Query (Optional):</label>
                <textarea id="query" name="query" rows="3" placeholder="Leave empty for default analysis"></textarea>
            </div>
            
            <div class="form-group" id="tradingParams" style="display: none;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <label for="riskReward">Risk-Reward Ratio:</label>
                        <input type="number" id="riskReward" name="riskReward" value="2.0" step="0.1" min="1.0" max="5.0">
                    </div>
                    <div>
                        <label for="stopLossMethod">Stop Loss Method:</label>
                        <select id="stopLossMethod" name="stopLossMethod">
                            <option value="atr">ATR (Volatility-Based)</option>
                            <option value="percentage">Percentage</option>
                            <option value="support">Support Level</option>
                        </select>
                    </div>
                    <div>
                        <label for="period">Analysis Period:</label>
                        <select id="period" name="period">
                            <option value="1mo">1 Month</option>
                            <option value="3mo">3 Months</option>
                            <option value="6mo" selected>6 Months</option>
                            <option value="1y">1 Year</option>
                            <option value="2y">2 Years</option>
                        </select>
                    </div>
                    <div>
                        <label for="stopLossPct">Stop Loss % (if using percentage):</label>
                        <input type="number" id="stopLossPct" name="stopLossPct" value="2.0" step="0.1" min="0.5" max="10.0">
                    </div>
                    <div style="grid-column: 1 / -1;">
                        <label style="display: flex; align-items: center; gap: 10px;">
                            <input type="checkbox" id="runBacktest" name="runBacktest" style="width: auto;">
                            <span>Run Backtest (Test strategy on historical data)</span>
                        </label>
                    </div>
                </div>
            </div>
            
            <div class="form-group" id="comprehensiveParams" style="display: none;">
                <div style="background: #e8f4f8; border-left: 4px solid #3498db; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
                    <strong>📊 Comprehensive Analysis Parameters Guide</strong>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #555;">
                        These parameters help customize your analysis. Hover over each field for detailed explanations.
                    </p>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <label for="compRiskReward" title="Risk-Reward Ratio: How much you could gain vs. how much you could lose. Recommended: 2.0-3.0. Example: 2.0 means you risk $1 to potentially make $2.">
                            Risk-Reward Ratio: <span style="color: #3498db; cursor: help;" title="Recommended: 2.0-3.0. This is the ratio of potential profit to potential loss. A 2.0 ratio means you risk $1 to make $2. Higher ratios (3.0+) are better but harder to achieve.">ℹ️</span>
                        </label>
                        <input type="number" id="compRiskReward" name="compRiskReward" value="2.0" step="0.1" min="1.0" max="5.0" title="Recommended: 2.0-3.0. Lower values (1.0-1.5) are risky. Higher values (3.0+) are ideal but may be harder to achieve.">
                        <small style="color: #666; display: block; margin-top: 5px;">Recommended: 2.0-3.0 | Range: 1.0-5.0</small>
                        <small style="color: #888; display: block; margin-top: 2px;">What to expect: Higher ratios = better risk management. The analysis will calculate target price based on this ratio.</small>
                    </div>
                    <div>
                        <label for="compStopLossMethod" title="Stop Loss Method: How to calculate your safety net (stop loss price). ATR adapts to volatility, Percentage is fixed, Support uses price levels.">
                            Stop Loss Method: <span style="color: #3498db; cursor: help;" title="ATR adapts to stock volatility (best for most stocks). Percentage is simple but may be too tight/loose. Support uses historical price levels.">ℹ️</span>
                        </label>
                        <select id="compStopLossMethod" name="compStopLossMethod" title="ATR is recommended for most stocks as it adapts to volatility. Percentage is simpler but less flexible. Support uses historical price levels.">
                            <option value="atr">ATR (Volatility-Based) - Recommended</option>
                            <option value="percentage">Percentage - Simple</option>
                            <option value="support">Support Level - Advanced</option>
                        </select>
                        <small style="color: #666; display: block; margin-top: 5px;">Recommended: ATR (adapts to stock volatility)</small>
                        <small style="color: #888; display: block; margin-top: 2px;">What to expect: ATR gives tighter stops for stable stocks, wider for volatile ones. More accurate than fixed percentages.</small>
                    </div>
                    <div>
                        <label for="compPeriod" title="Analysis Period: How far back to look at price data. Longer periods show bigger trends but may miss recent changes.">
                            Analysis Period: <span style="color: #3498db; cursor: help;" title="6 months is recommended for most analysis. Shorter periods (1-3mo) show recent trends. Longer periods (1-2y) show major trends but may miss recent changes.">ℹ️</span>
                        </label>
                        <select id="compPeriod" name="compPeriod" title="6 months is recommended - balances recent trends with historical context. Use shorter for day trading, longer for long-term investing.">
                            <option value="1mo">1 Month - Very Recent</option>
                            <option value="3mo">3 Months - Short Term</option>
                            <option value="6mo" selected>6 Months - Recommended</option>
                            <option value="1y">1 Year - Long Term</option>
                            <option value="2y">2 Years - Very Long Term</option>
                        </select>
                        <small style="color: #666; display: block; margin-top: 5px;">Recommended: 6 Months (balances recent and historical data)</small>
                        <small style="color: #888; display: block; margin-top: 2px;">What to expect: Shorter = more sensitive to recent changes. Longer = more stable but may miss recent trends.</small>
                    </div>
                    <div>
                        <label for="compStopLossPct" title="Stop Loss Percentage: Only used if 'Percentage' method is selected. This is the % drop from entry price where you'll exit.">
                            Stop Loss % (if using percentage): <span style="color: #3498db; cursor: help;" title="Only used if Stop Loss Method is 'Percentage'. This is how much % drop from entry price triggers your stop loss. 2% is typical for stable stocks, 3-5% for volatile stocks.">ℹ️</span>
                        </label>
                        <input type="number" id="compStopLossPct" name="compStopLossPct" value="2.0" step="0.1" min="0.5" max="10.0" title="Only used if Stop Loss Method is 'Percentage'. 2% for stable stocks, 3-5% for volatile stocks.">
                        <small style="color: #666; display: block; margin-top: 5px;">Recommended: 2.0% (stable stocks) or 3-5% (volatile stocks) | Range: 0.5-10.0%</small>
                        <small style="color: #888; display: block; margin-top: 2px;">What to expect: Lower % = tighter stop (exits faster). Higher % = wider stop (more room for price swings). Only used with Percentage method.</small>
                    </div>
                    <div>
                        <label for="accountValue" title="Account Value: Your total trading/investment account balance. Used to calculate how many shares you can safely buy.">
                            Account Value ($): <span style="color: #3498db; cursor: help;" title="Your total account balance. The analysis will calculate position size based on this. Enter your actual account value for accurate recommendations.">ℹ️</span>
                        </label>
                        <input type="number" id="accountValue" name="accountValue" value="10000" step="100" min="100" title="Your total account balance. Used to calculate safe position size. Enter your actual account value.">
                        <small style="color: #666; display: block; margin-top: 5px;">Recommended: Your actual account balance | Minimum: $100</small>
                        <small style="color: #888; display: block; margin-top: 2px;">What to expect: The analysis will tell you exactly how many shares to buy based on this value and your risk tolerance.</small>
                    </div>
                    <div>
                        <label for="riskPerTrade" title="Risk per Trade: What % of your account you're willing to risk on this single trade. Lower is safer. Professional traders use 1-2%.">
                            Risk per Trade (%): <span style="color: #3498db; cursor: help;" title="What percentage of your account you're willing to risk on this trade. 1% is conservative (recommended for beginners), 2% is moderate, 3-5% is aggressive. Never risk more than 5% on a single trade.">ℹ️</span>
                        </label>
                        <input type="number" id="riskPerTrade" name="riskPerTrade" value="1.0" step="0.1" min="0.1" max="5.0" title="1% is conservative (recommended), 2% is moderate, 3-5% is aggressive. Never exceed 5%.">
                        <small style="color: #666; display: block; margin-top: 5px;">Recommended: 1.0% (conservative) or 2.0% (moderate) | Range: 0.1-5.0%</small>
                        <small style="color: #888; display: block; margin-top: 2px;">What to expect: Lower % = smaller position size = less risk. With 1% risk on $10,000 account, you risk $100 max on this trade.</small>
                    </div>
                    <div style="grid-column: 1 / -1;">
                        <label style="display: flex; align-items: center; gap: 10px;" title="Company Research: AI-powered analysis of why the stock is moving, company health, and key factors. Takes longer but provides valuable insights.">
                            <input type="checkbox" id="includeResearch" name="includeResearch" checked style="width: auto;">
                            <span>Include Company Research & Health Analysis (AI-Powered) <span style="color: #3498db; cursor: help;" title="When enabled, the AI will research the company, analyze why the stock is rising/falling, assess company health, and identify key positive/negative factors. This adds 30-60 seconds to analysis time but provides valuable fundamental insights.">ℹ️</span></span>
                        </label>
                        <small style="color: #666; display: block; margin-top: 5px; margin-left: 28px;">Recommended: Enabled (provides company health, reasons for price movement, and key factors)</small>
                        <small style="color: #888; display: block; margin-top: 2px; margin-left: 28px;">What to expect: AI will explain why stock is rising/falling, assess company health, and list 2-3 key positive developments and concerns. Adds 30-60 seconds to analysis.</small>
                    </div>
                </div>
            </div>
            
            <button type="submit" id="submitBtn">Analyze Stock</button>
        </form>
        
        <div id="result"></div>
    </div>
    </div>
    
    <!-- Chat functionality temporarily disabled -->
    <!-- Chat Toggle Button -->
    <!-- <button class="chat-toggle-btn" id="chatToggleBtn" onclick="toggleChatPanel()">
        💬 Chat with Analyst
    </button> -->
    
    <!-- Chat Panel -->
    <!-- <div class="chat-panel" id="chatPanel">
        <div class="chat-header">
            <h3>💬 Trading Analyst Chat</h3>
            <button class="chat-close-btn" onclick="toggleChatPanel()">×</button>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="chat-message assistant">
                👋 Hello! I'm your Trading Analyst Assistant. After you run an analysis, I can help you understand the results, explain technical indicators, generate charts, and answer any questions you have!
            </div>
        </div>
        <div class="chat-input-area">
            <input type="text" class="chat-input" id="chatInput" placeholder="Ask me anything about the analysis..." onkeypress="handleChatKeyPress(event)" oninput="validateChatInput()">
            <button class="chat-send-btn" id="chatSendBtn" onclick="sendChatMessage()" disabled>Send</button>
        </div>
    </div> -->
    
    <script>
        let currentSessionId = null;
        
        // Form submission handler - defined early to be available for inline handler
        async function handleFormSubmit(e) {
            try {
                if (e) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                console.log('Form submitted!');
                
                const submitBtn = document.getElementById('submitBtn');
                const resultDiv = document.getElementById('result');
                const analysisType = document.getElementById('analysisType').value;
                
                // Validate form
                if (!resultDiv) {
                    console.error('Result div not found!');
                    alert('Error: Result container not found. Please refresh the page.');
                    return false;
                }
                
                if (!submitBtn) {
                    console.error('Submit button not found!');
                    return false;
                }
                
                submitBtn.disabled = true;
                resultDiv.style.display = 'block';
                resultDiv.style.visibility = 'visible';
                resultDiv.innerHTML = '<div class="loading">⏳ Analyzing... This may take a minute.</div>';
                
                console.log('Starting analysis with type:', analysisType);
                
                const formData = {
                    ticker: document.getElementById('ticker').value,
                    model: document.getElementById('model').value,
                    analysisType: analysisType
                };
                
                if (analysisType === 'market') {
                    formData.query = document.getElementById('query').value;
                } else if (analysisType === 'trading') {
                    formData.riskReward = parseFloat(document.getElementById('riskReward').value);
                    formData.stopLossMethod = document.getElementById('stopLossMethod').value;
                    formData.period = document.getElementById('period').value;
                    formData.stopLossPct = parseFloat(document.getElementById('stopLossPct').value);
                    formData.runBacktest = document.getElementById('runBacktest').checked;
                } else if (analysisType === 'comprehensive') {
                    formData.riskReward = parseFloat(document.getElementById('compRiskReward').value);
                    formData.stopLossMethod = document.getElementById('compStopLossMethod').value;
                    formData.period = document.getElementById('compPeriod').value;
                    formData.stopLossPct = parseFloat(document.getElementById('compStopLossPct').value);
                    formData.accountValue = parseFloat(document.getElementById('accountValue').value);
                    formData.riskPerTrade = parseFloat(document.getElementById('riskPerTrade').value);
                    formData.includeResearch = document.getElementById('includeResearch').checked;
                }
                
                let endpoint = '/analyze';
                if (analysisType === 'trading') {
                    endpoint = '/trading-strategy';
                } else if (analysisType === 'comprehensive') {
                    endpoint = '/comprehensive-analysis';
                }
                
                console.log('Sending request to:', endpoint, 'with data:', formData);
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                console.log('Response status:', response.status);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('Response data:', data);
                
                if (data.success) {
                    // Ensure result div is visible and display results
                    resultDiv.style.display = 'block';
                    resultDiv.style.visibility = 'visible';
                    resultDiv.innerHTML = '<div class="result">' + escapeHtml(data.result) + '</div>';
                    
                    // Scroll to results
                    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    
                    // Chat functionality temporarily disabled - focus on getting analysis working first
                    // if (data.session_id) {
                    //     currentSessionId = data.session_id;
                    //     console.log('Session initialized:', currentSessionId);
                    // }
                } else {
                    resultDiv.style.display = 'block';
                    resultDiv.style.visibility = 'visible';
                    resultDiv.innerHTML = '<div class="error">Error: ' + escapeHtml(data.error || 'Unknown error') + '</div>';
                }
            } catch (error) {
                const resultDiv = document.getElementById('result');
                if (resultDiv) {
                    resultDiv.style.display = 'block';
                    resultDiv.style.visibility = 'visible';
                    resultDiv.innerHTML = '<div class="error">Error: ' + escapeHtml(error.message || 'Network error occurred') + '</div>';
                }
                console.error('Analysis error:', error);
            } finally {
                const submitBtn = document.getElementById('submitBtn');
                if (submitBtn) {
                    submitBtn.disabled = false;
                }
            }
            return false;
        }
        
        // Make handleFormSubmit globally accessible immediately
        window.handleFormSubmit = handleFormSubmit;
        
        // Chat functions temporarily disabled - focus on getting analysis working first
        // function validateChatInput() {
        //     const input = document.getElementById('chatInput');
        //     const sendBtn = document.getElementById('chatSendBtn');
        //     const message = input.value.trim();
        //     
        //     // Enable/disable send button based on whether there's content
        //     if (message.length > 0 && currentSessionId) {
        //         sendBtn.disabled = false;
        //     } else {
        //         sendBtn.disabled = true;
        //     }
        // }
        
        // Toggle indicator info panel
        function toggleInfo() {
            const infoPanel = document.getElementById('indicatorInfo');
            if (infoPanel) {
                if (infoPanel.style.display === 'none' || infoPanel.style.display === '') {
                    infoPanel.style.display = 'block';
                } else {
                    infoPanel.style.display = 'none';
                }
            }
        }
        
        // Make toggleInfo globally accessible
        window.toggleInfo = toggleInfo;
        
        
        // Toggle trading parameters based on analysis type
        function setupEventListeners() {
            const analysisTypeEl = document.getElementById('analysisType');
            const analysisFormEl = document.getElementById('analysisForm');
            
            if (!analysisTypeEl || !analysisFormEl) {
                console.error('Required form elements not found!');
                return;
            }
            
            analysisTypeEl.addEventListener('change', function() {
                const analysisType = this.value;
                const queryGroup = document.getElementById('queryGroup');
                const tradingParams = document.getElementById('tradingParams');
                const comprehensiveParams = document.getElementById('comprehensiveParams');
                const resultDiv = document.getElementById('result');
                
                // Clear previous results when changing analysis type
                if (resultDiv) {
                    resultDiv.innerHTML = '';
                }
                
                if (analysisType === 'trading') {
                    queryGroup.style.display = 'none';
                    tradingParams.style.display = 'block';
                    comprehensiveParams.style.display = 'none';
                } else if (analysisType === 'comprehensive') {
                    queryGroup.style.display = 'none';
                    tradingParams.style.display = 'none';
                    comprehensiveParams.style.display = 'block';
                } else {
                    queryGroup.style.display = 'block';
                    tradingParams.style.display = 'none';
                    comprehensiveParams.style.display = 'none';
                }
            });
            
            // Attach form submit handler (backup, inline handler should work)
            analysisFormEl.addEventListener('submit', function(e) {
                e.preventDefault();
                e.stopPropagation();
                handleFormSubmit(e);
            });
            console.log('Form event listener attached');
        }
        
        // Initialize form state on page load
        document.addEventListener('DOMContentLoaded', function() {
            // Setup event listeners
            setupEventListeners();
            // Set initial form state based on selected analysis type
            const analysisType = document.getElementById('analysisType');
            if (analysisType) {
                analysisType.dispatchEvent(new Event('change'));
            }
            
            // Ensure result div is visible
            const resultDiv = document.getElementById('result');
            if (resultDiv) {
                resultDiv.style.display = 'block';
                resultDiv.style.visibility = 'visible';
            }
            
            // Chat functionality temporarily disabled
            // const chatToggleBtn = document.getElementById('chatToggleBtn');
        });
        
        // Also try to setup listeners immediately (in case DOM is already loaded)
        if (document.readyState === 'loading') {
            // DOM is still loading, wait for DOMContentLoaded
        } else {
            // DOM is already loaded, setup immediately
            setupEventListeners();
        }
        
        // Chat Functions - temporarily disabled
        // All chat-related functions commented out to focus on getting analysis working first
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    response = make_response(render_template_string(HTML_TEMPLATE))
    # Disable caching to ensure fresh content
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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
        
        # Run analysis using initiate_chat directly so we can access messages before reset
        from autogen.cache import Cache
        
        result_text = "Analysis completed."
        
        try:
            # Use initiate_chat directly instead of chat() so we can access messages before reset
            with Cache.disk() as cache:
                assistant.user_proxy.initiate_chat(
                    assistant.assistant,
                    message=message,
                    cache=cache,
                )
            
            # Get the last message from the assistant BEFORE reset
            # The messages are stored in assistant.assistant.chat_messages[assistant.user_proxy]
            if assistant.assistant.chat_messages.get(assistant.user_proxy):
                messages = assistant.assistant.chat_messages[assistant.user_proxy]
                # Get the last message from the assistant (not user_proxy)
                for msg in reversed(messages):
                    if msg.get("role") == "assistant" or assistant.assistant.name in str(msg.get("name", "")):
                        result_text = msg.get("content", "Analysis completed.")
                        break
                # If no assistant message found, get the last message
                if result_text == "Analysis completed." and messages:
                    result_text = messages[-1].get("content", "Analysis completed.")
            
            # Now reset (like chat() does)
            assistant.reset()
            
            return jsonify({
                "success": True,
                "result": result_text
            })
        except Exception as chat_error:
            # Reset on error too
            try:
                assistant.reset()
            except:
                pass
            return jsonify({
                "success": False,
                "error": f"Error during analysis: {str(chat_error)}"
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/trading-strategy', methods=['POST'])
def trading_strategy():
    """Endpoint for trading strategy analysis (entry, stop loss, target price)"""
    try:
        data = request.json
        ticker = data.get('ticker', 'AAPL').upper()
        risk_reward = float(data.get('riskReward', 2.0))
        stop_loss_method = data.get('stopLossMethod', 'atr')
        period = data.get('period', '6mo')
        stop_loss_pct = float(data.get('stopLossPct', 2.0))
        run_backtest = data.get('runBacktest', False)
        
        # Call the trading strategy analyzer
        result = TradingStrategyAnalyzer.analyze_trading_opportunity(
            ticker_symbol=ticker,
            period=period,
            risk_reward_ratio=risk_reward,
            stop_loss_method=stop_loss_method,
            stop_loss_percentage=stop_loss_pct,
            atr_multiplier=2.0,
            use_advanced_indicators=True
        )
        
        # If backtesting is requested, extract prices and run backtest
        if run_backtest:
            try:
                # Parse entry, stop loss, and target prices from result
                import re
                entry_match = re.search(r'Entry Price: \$([\d.]+)', result)
                stop_match = re.search(r'Stop Loss: \$([\d.]+)', result)
                target_match = re.search(r'Target Price: \$([\d.]+)', result)
                
                if entry_match and stop_match and target_match:
                    entry_price = float(entry_match.group(1))
                    stop_loss = float(stop_match.group(1))
                    target_price = float(target_match.group(1))
                    
                    # Calculate backtest period (use last 6 months for backtest)
                    from datetime import datetime, timedelta
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=180)  # 6 months
                    
                    backtest_result = TradingStrategyAnalyzer.backtest_strategy_recommendations(
                        ticker_symbol=ticker,
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d'),
                        entry_price=entry_price,
                        stop_loss=stop_loss,
                        target_price=target_price,
                        use_advanced_indicators=True
                    )
                    
                    result += "\n\n" + "="*60 + "\n"
                    result += "BACKTESTING RESULTS\n"
                    result += "="*60 + "\n"
                    result += backtest_result
            except Exception as backtest_error:
                result += f"\n\n⚠️ Backtesting failed: {str(backtest_error)}"
        
        return jsonify({
            "success": True,
            "result": result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/comprehensive-analysis', methods=['POST'])
def comprehensive_analysis():
    """Endpoint for comprehensive analysis combining technical analysis, company research, and forecasts"""
    try:
        data = request.json
        ticker = data.get('ticker', 'AAPL').upper()
        risk_reward = float(data.get('riskReward', 2.0))
        stop_loss_method = data.get('stopLossMethod', 'atr')
        period = data.get('period', '6mo')
        stop_loss_pct = float(data.get('stopLossPct', 2.0))
        account_value = float(data.get('accountValue', 10000.0))
        risk_per_trade = float(data.get('riskPerTrade', 1.0))
        include_research = data.get('includeResearch', True)
        model_type = data.get('model', 'gemini')
        
        # Get company research if requested
        company_research = None
        if include_research:
            try:
                # Select config file based on model
                config_file = "GEMINI_CONFIG_LIST" if model_type == "gemini" else "OAI_CONFIG_LIST"
                model_filter = ["gemini-2.5-flash"] if model_type == "gemini" else ["gpt-4o"]
                
                if os.path.exists(config_file):
                    # Configure LLM
                    llm_config_obj = autogen.LLMConfig.from_json(
                        path=config_file,
                        filter_dict={"model": model_filter},
                    )
                    llm_config = {
                        "config_list": llm_config_obj.config_list,
                        "timeout": 120,
                        "temperature": 0,
                    }
                    
                    # Create agent for company research
                    assistant = SingleAssistant(
                        "Company_Researcher",
                        llm_config,
                        human_input_mode="NEVER",
                        max_consecutive_auto_reply=5,
                    )
                    
                    # Build research query
                    research_message = (
                        f"Use all the tools provided to retrieve information available for {ticker} "
                        f"upon {get_current_date()}. Analyze and explain:\n"
                        f"1. Why is the stock price rising or falling? (Based on recent news, earnings, and market conditions)\n"
                        f"2. Is the company healthy? (Analyze financial health, growth prospects, competitive position)\n"
                        f"3. What are the main positive developments? (2-3 key factors)\n"
                        f"4. What are the main concerns or risks? (2-3 key factors)\n"
                        f"Keep the analysis concise and focused on actionable insights. Most factors should be inferred from company-related news and financial data."
                    )
                    
                    # Run research
                    from autogen.cache import Cache
                    research_text = "Company research completed."
                    
                    try:
                        with Cache.disk() as cache:
                            assistant.user_proxy.initiate_chat(
                                assistant.assistant,
                                message=research_message,
                                cache=cache,
                            )
                        
                        # Get the last message from the assistant
                        if assistant.assistant.chat_messages.get(assistant.user_proxy):
                            messages = assistant.assistant.chat_messages[assistant.user_proxy]
                            for msg in reversed(messages):
                                if msg.get("role") == "assistant" or assistant.assistant.name in str(msg.get("name", "")):
                                    research_text = msg.get("content", "Company research completed.")
                                    break
                            if research_text == "Company research completed." and messages:
                                research_text = messages[-1].get("content", "Company research completed.")
                        
                        assistant.reset()
                        company_research = research_text
                    except Exception as research_error:
                        # If research fails, continue without it
                        company_research = f"⚠️ Company research unavailable: {str(research_error)}"
                        try:
                            assistant.reset()
                        except:
                            pass
            except Exception as e:
                # If research setup fails, continue without it
                company_research = f"⚠️ Company research unavailable: {str(e)}"
        
        # Call comprehensive analysis
        result = TradingStrategyAnalyzer.comprehensive_analysis(
            ticker_symbol=ticker,
            period=period,
            risk_reward_ratio=risk_reward,
            stop_loss_method=stop_loss_method,
            stop_loss_percentage=stop_loss_pct,
            account_value=account_value,
            risk_per_trade_pct=risk_per_trade,
            company_research=company_research
        )
        
        # Initialize or update session
        session = get_or_create_session()
        session["ticker"] = ticker
        session["analysis_params"] = {
            "risk_reward": risk_reward,
            "stop_loss_method": stop_loss_method,
            "period": period,
            "stop_loss_pct": stop_loss_pct,
            "account_value": account_value,
            "risk_per_trade": risk_per_trade
        }
        session["last_analysis"] = result
        session["conversation_history"] = []
        
        return jsonify({
            "success": True,
            "result": result,
            "session_id": session["session_id"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/static/charts/<path:filename>')
def serve_chart(filename):
    """Serve generated charts."""
    try:
        # Ensure the file exists
        file_path = os.path.join(CHARTS_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "Chart not found"}), 404
        return send_from_directory(CHARTS_DIR, filename)
    except Exception as e:
        # Return 404 if chart not found
        return jsonify({"error": f"Chart not found: {str(e)}"}), 404

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from the trading agent."""
    try:
        cleanup_old_sessions()  # Clean up old sessions periodically
        
        data = request.json
        session_id = data.get('session_id')
        message = data.get('message', '')
        
        if not session_id or session_id not in sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or expired session. Please run an analysis first."
            })
        
        session = sessions[session_id]
        
        if not session.get('ticker'):
            return jsonify({
                "success": False,
                "error": "No analysis found in session. Please run an analysis first."
            })
        
        # Add user message to conversation history
        session["conversation_history"].append({"role": "user", "content": message})
        
        # Get model type (default to gemini)
        model_type = "gemini"  # Could be stored in session if needed
        config_file = "GEMINI_CONFIG_LIST" if model_type == "gemini" else "OAI_CONFIG_LIST"
        model_filter = ["gemini-2.5-flash"] if model_type == "gemini" else ["gpt-4o"]
        
        if not os.path.exists(config_file):
            return jsonify({
                "success": False,
                "error": f"Config file {config_file} not found"
            })
        
        # Configure LLM
        llm_config_obj = autogen.LLMConfig.from_json(
            path=config_file,
            filter_dict={"model": model_filter},
        )
        llm_config = {
            "config_list": llm_config_obj.config_list,
            "timeout": 120,
            "temperature": 0.7,  # Slightly higher for more conversational responses
        }
        
        # Initialize agent_context if not exists
        if "agent_context" not in session:
            session["agent_context"] = {}
        
        # Create or reuse trading chat agent
        if "agent" not in session["agent_context"]:
            agent = create_trading_chat_agent(
                llm_config=llm_config,
                ticker=session["ticker"],
                analysis_params=session["analysis_params"],
                last_analysis=session["last_analysis"][:1000],  # First 1000 chars for context
                conversation_history=session["conversation_history"][-10:]  # Last 10 messages
            )
            session["agent_context"]["agent"] = agent
        else:
            agent = session["agent_context"]["agent"]
        
        # Process message through agent
        response = process_chat_message(agent, message, use_cache=False)
        
        # Add assistant response to conversation history
        session["conversation_history"].append({"role": "assistant", "content": response})
        
        # Check if response contains chart request or parameter change
        response_type = "text"
        chart_url = None
        confirmation_data = None
        
        # Check for chart generation requests (simple pattern matching)
        if "chart" in message.lower() or "plot" in message.lower() or "graph" in message.lower() or "show me" in message.lower():
            # Try to generate a chart
            try:
                chart_url = generate_chart(
                    ticker=session["ticker"],
                    period=session["analysis_params"].get("period", "6mo"),
                    chart_type="candle",
                    mav=[20, 50]  # Default moving averages
                )
                if chart_url:
                    response_type = "chart"
                    response = "Here's the chart you requested:"
                else:
                    # Chart generation failed
                    response = "I apologize, but I couldn't generate the chart at this time. This may be due to Yahoo Finance API limitations. Please try again in a few minutes."
            except Exception as chart_error:
                response = f"I encountered an error while generating the chart: {str(chart_error)}. Please try again later."
        
        # Check for parameter change suggestions (simple pattern matching - could be enhanced)
        # This is a basic implementation - the agent should explicitly suggest changes
        if "suggest" in response.lower() and ("risk" in response.lower() or "parameter" in response.lower()):
            # Extract suggested changes (this is simplified - in production, use structured output)
            confirmation_id = str(uuid.uuid4())
            session["agent_context"]["pending_confirmations"] = session["agent_context"].get("pending_confirmations", {})
            session["agent_context"]["pending_confirmations"][confirmation_id] = {
                "suggestion": response,
                "timestamp": datetime.now()
            }
            response_type = "parameter_confirmation"
            confirmation_data = {
                "confirmation_id": confirmation_id,
                "confirmation_title": "Parameter Change Suggestion",
                "confirmation_message": response
            }
        
        result = {
            "success": True,
            "message": response,
            "response_type": response_type
        }
        
        if chart_url:
            result["chart_url"] = chart_url
        
        if confirmation_data:
            result.update(confirmation_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/chat/confirm-params', methods=['POST'])
def confirm_params():
    """Handle parameter change confirmations."""
    try:
        data = request.json
        session_id = data.get('session_id')
        confirmation_id = data.get('confirmation_id')
        accepted = data.get('accepted', False)
        
        if not session_id or session_id not in sessions:
            return jsonify({
                "success": False,
                "error": "Invalid session"
            })
        
        session = sessions[session_id]
        
        if accepted:
            # Get pending confirmation
            pending = session["agent_context"].get("pending_confirmations", {}).get(confirmation_id)
            if pending:
                # In a real implementation, parse the suggestion and update parameters
                # For now, we'll just re-run the analysis with current parameters
                # (In production, parse the agent's suggestion and extract new parameter values)
                
                # Re-run comprehensive analysis
                result = TradingStrategyAnalyzer.comprehensive_analysis(
                    ticker_symbol=session["ticker"],
                    period=session["analysis_params"].get("period", "6mo"),
                    risk_reward_ratio=session["analysis_params"].get("risk_reward", 2.0),
                    stop_loss_method=session["analysis_params"].get("stop_loss_method", "atr"),
                    stop_loss_percentage=session["analysis_params"].get("stop_loss_pct", 2.0),
                    account_value=session["analysis_params"].get("account_value", 10000.0),
                    risk_per_trade_pct=session["analysis_params"].get("risk_per_trade", 1.0),
                    company_research=None  # Could be cached
                )
                
                session["last_analysis"] = result
                
                # Remove confirmation
                if confirmation_id in session["agent_context"].get("pending_confirmations", {}):
                    del session["agent_context"]["pending_confirmations"][confirmation_id]
                
                return jsonify({
                    "success": True,
                    "updated_analysis": result
                })
        
        # Remove confirmation even if rejected
        if confirmation_id in session["agent_context"].get("pending_confirmations", {}):
            del session["agent_context"]["pending_confirmations"][confirmation_id]
        
        return jsonify({
            "success": True
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
    print("🛑 Press Ctrl+C to stop the server")
    print("💡 TIP: If you see old UI, do a hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)\n")
    app.run(host='0.0.0.0', port=port, debug=True)  # Enable debug mode for auto-reload

