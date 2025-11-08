# How to Use FinRobot

## Understanding FinRobot

FinRobot is a **Python library/framework** - it's not a web application. You run it through:
- **Command line** (Python scripts)
- **Jupyter notebooks** (interactive)
- **Custom web interface** (if you build one)

## Current Setup

You have two ways to run FinRobot:

### 1. Command Line Script (What We Just Created)

```bash
cd /Users/lxupkzwjs/Developer/eval/FinRobot
source venv/bin/activate
python start_demo_gemini.py
```

This runs the Market Analyst agent and prints results to the terminal.

### 2. Jupyter Notebooks (Interactive)

The project includes interactive notebooks:

```bash
cd /Users/lxupkzwjs/Developer/eval/FinRobot
source venv/bin/activate
jupyter notebook tutorials_beginner/
```

Then open:
- `agent_fingpt_forecaster.ipynb` - Market forecasting
- `agent_annual_report.ipynb` - Report generation
- `agent_rag_qa.ipynb` - Document Q&A

## Ways to Access/Use FinRobot

### Option 1: Command Line (Current Method)

**Pros**: Simple, fast, good for automation
**Cons**: No visual interface

**Usage**:
```bash
python start_demo_gemini.py
```

### Option 2: Jupyter Notebooks

**Pros**: Interactive, visual, great for exploration
**Cons**: Requires Jupyter installation

**Setup**:
```bash
pip install jupyter
jupyter notebook
```

### Option 3: Create a Web Interface (I can help!)

I can create a simple web interface using:
- **Flask** (simple web server)
- **FastAPI** (modern API + web interface)
- **Streamlit** (easiest, most user-friendly)

Would you like me to create a web interface?

### Option 4: Python Scripts

Create your own scripts:

```python
from finrobot.agents.workflow import SingleAssistant
import autogen

llm_config = {
    "config_list": autogen.config_list_from_json("GEMINI_CONFIG_LIST"),
}

assistant = SingleAssistant("Market_Analyst", llm_config)
assistant.chat("Analyze TSLA stock")
```

## Quick Start Guide

### Run the Demo

```bash
# Activate environment
cd /Users/lxupkzwjs/Developer/eval/FinRobot
source venv/bin/activate

# Run Gemini demo
python start_demo_gemini.py

# Or run OpenAI demo (if billing is set up)
python start_demo.py
```

### Run Interactive Notebooks

```bash
# Install Jupyter
pip install jupyter

# Start Jupyter
jupyter notebook

# Browser will open automatically
# Navigate to tutorials_beginner/ or tutorials_advanced/
```

### Create Custom Scripts

1. Create a new Python file: `my_analysis.py`
2. Import FinRobot
3. Configure your agent
4. Run your analysis

## What Would You Like?

1. **Simple web interface** - I can create a Flask/Streamlit app
2. **API server** - REST API to call FinRobot
3. **More examples** - Different use cases
4. **Keep using command line** - Current method works fine

Let me know what you prefer!

