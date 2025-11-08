# Quick Start Guide - How to Use FinRobot

## 🎯 Three Ways to Use FinRobot

### 1. 🌐 Web Interface (Easiest - Recommended!)

**Start the web server:**
```bash
cd /Users/lxupkzwjs/Developer/eval/FinRobot
source venv/bin/activate
python web_interface.py
```

**Or specify a custom port:**
```bash
python web_interface.py 5001  # Use port 5001
python web_interface.py 3000  # Use port 3000
```

**Then open your browser:**
- Default: **http://localhost:8080**
- Or use the port you specified
- Enter a stock ticker (e.g., AAPL, TSLA, MSFT)
- Click "Analyze Stock"
- See the results in the browser!

**Features:**
- ✅ Easy-to-use web interface
- ✅ No command line needed
- ✅ Visual results
- ✅ Choose between Gemini (free) or OpenAI

### 2. 💻 Command Line Script

**Run the demo:**
```bash
cd /Users/lxupkzwjs/Developer/eval/FinRobot
source venv/bin/activate
python start_demo_gemini.py
```

**What it does:**
- Analyzes AAPL stock by default
- Prints results to terminal
- Good for automation/scripts

### 3. 📓 Jupyter Notebooks (Interactive)

**Start Jupyter:**
```bash
cd /Users/lxupkzwjs/Developer/eval/FinRobot
source venv/bin/activate
pip install jupyter
jupyter notebook
```

**Then open:**
- `tutorials_beginner/agent_fingpt_forecaster.ipynb`
- `tutorials_beginner/agent_annual_report.ipynb`

## 🚀 Recommended: Web Interface

The web interface is the easiest way to use FinRobot:

1. **Start it:**
   ```bash
   python web_interface.py
   ```

2. **Open browser:**
   - Go to: http://localhost:5000

3. **Use it:**
   - Enter any stock ticker
   - Choose Gemini (free) or OpenAI
   - Get instant analysis!

## 📝 Example Usage

### Web Interface
1. Run `python web_interface.py`
2. Open http://localhost:5000
3. Enter "TSLA" in the ticker field
4. Click "Analyze Stock"
5. Wait for results (30-60 seconds)
6. See the analysis!

### Command Line
```bash
python start_demo_gemini.py
# Change ticker in the script if needed
```

### Custom Script
```python
from finrobot.agents.workflow import SingleAssistant
import autogen

llm_config = {
    "config_list": autogen.config_list_from_json("GEMINI_CONFIG_LIST"),
}

assistant = SingleAssistant("Market_Analyst", llm_config)
assistant.chat("Analyze TSLA stock")
```

## 🎨 What You Can Do

- **Stock Analysis**: Analyze any stock ticker
- **Market Predictions**: Get price movement predictions
- **Financial Reports**: Generate comprehensive reports
- **Document Analysis**: Analyze SEC filings, earnings calls
- **Portfolio Optimization**: Optimize investment portfolios

## 🔧 Troubleshooting

**Web interface won't start?**
- Make sure Flask is installed: `pip install flask`
- Check port 5000 is available

**Want to change the port?**
- Edit `web_interface.py`
- Change `port=5000` to any port you want

**Want to analyze different stocks?**
- Web interface: Just change the ticker in the form
- Script: Edit the `company` variable in the script

## 📚 Next Steps

1. **Try the web interface** - Easiest way to get started
2. **Explore notebooks** - Learn more advanced features
3. **Create custom scripts** - Build your own analysis tools

Enjoy using FinRobot! 🚀

