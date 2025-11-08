# Using Jupyter Notebooks with FinRobot

## What are Jupyter Notebooks?

Jupyter Notebooks are interactive documents that combine code, text, and visualizations. They're perfect for:
- **Learning** FinRobot step-by-step
- **Experimenting** with different agents and configurations
- **Visualizing** results with charts and graphs
- **Documenting** your analysis workflow

## Available Notebooks

### Beginner Tutorials (`tutorials_beginner/`)

1. **`agent_fingpt_forecaster.ipynb`** ⭐ Recommended to start
   - Market forecasting agent
   - Predicts stock movements
   - Uses Gemini or OpenAI

2. **`agent_annual_report.ipynb`**
   - Generates annual reports
   - Analyzes 10-K filings
   - Creates PDF reports

3. **`agent_rag_qa.ipynb`**
   - Document Q&A with RAG
   - Earnings call analysis
   - SEC filing questions

4. **`agent_rag_earnings_call_sec_filings.ipynb`**
   - Earnings call transcripts
   - SEC filing analysis
   - RAG-powered queries

5. **`ollama stock chart.ipynb`**
   - Stock chart visualization
   - Using Ollama models

### Advanced Tutorials (`tutorials_advanced/`)

1. **`agent_trade_strategist.ipynb`**
   - Trading strategy development
   - Backtesting strategies
   - Advanced analysis

2. **`agent_fingpt_forecaster.ipynb`** (Advanced version)
   - More configuration options
   - Custom agent setups

3. **`lmm_agent_mplfinance.ipynb`**
   - Advanced charting with mplfinance
   - Technical indicators
   - Custom visualizations

4. **`lmm_agent_opt_smacross.ipynb`**
   - Strategy optimization
   - Moving average crossovers
   - Parameter tuning

## Installation

### Step 1: Install Jupyter

```bash
cd /Users/lxupkzwjs/Developer/eval/FinRobot
source venv/bin/activate
pip install jupyter
```

### Step 2: Start Jupyter

```bash
jupyter notebook
```

This will:
- Start a local server (usually on port 8888)
- Open your browser automatically
- Show the Jupyter file browser

### Step 3: Navigate to Tutorials

In the Jupyter interface:
1. Click on `tutorials_beginner/` folder
2. Open any `.ipynb` file
3. Start running cells!

## Using the Notebooks

### Basic Workflow

1. **Open a notebook** (e.g., `agent_fingpt_forecaster.ipynb`)
2. **Read the cells** - They contain explanations
3. **Run cells** - Click "Run" or press `Shift + Enter`
4. **Modify code** - Edit cells to customize
5. **See results** - Output appears below each cell

### Cell Types

- **Markdown cells**: Documentation and explanations
- **Code cells**: Python code to execute
- **Output cells**: Results, charts, text

### Keyboard Shortcuts

- `Shift + Enter`: Run cell and move to next
- `Ctrl + Enter`: Run cell and stay
- `A`: Insert cell above
- `B`: Insert cell below
- `DD`: Delete cell (press D twice)

## Recommended Starting Point

### For Beginners:

1. **Start with**: `tutorials_beginner/agent_fingpt_forecaster.ipynb`
   ```bash
   jupyter notebook tutorials_beginner/agent_fingpt_forecaster.ipynb
   ```

2. **What it does**:
   - Shows how to set up a Market Analyst agent
   - Demonstrates stock analysis
   - Makes price predictions

3. **Follow along**:
   - Read each cell
   - Run them in order
   - Modify the ticker symbol to analyze different stocks

### Configuration

Before running notebooks, make sure:

1. **API keys are configured**:
   - `GEMINI_CONFIG_LIST` has your Gemini key (for free tier)
   - Or `OAI_CONFIG_LIST` has OpenAI key (requires billing)

2. **Update paths in notebooks**:
   - Some notebooks reference `../OAI_CONFIG_LIST`
   - Update to `../GEMINI_CONFIG_LIST` if using Gemini
   - Or adjust paths as needed

## Example: Running Your First Notebook

### Step-by-Step:

```bash
# 1. Activate environment
cd /Users/lxupkzwjs/Developer/eval/FinRobot
source venv/bin/activate

# 2. Install Jupyter (if not installed)
pip install jupyter

# 3. Start Jupyter
jupyter notebook

# 4. Browser opens automatically
# 5. Navigate to: tutorials_beginner/
# 6. Open: agent_fingpt_forecaster.ipynb
# 7. Run cells one by one
```

### In the Notebook:

1. **First cell**: Usually imports and setup
2. **Second cell**: Configuration (update API key path if needed)
3. **Third cell**: Create agent
4. **Fourth cell**: Run analysis
5. **Results**: Appear below cells

## Customizing Notebooks

### Change Stock Ticker

In any notebook, find:
```python
company = "AAPL"
```

Change to:
```python
company = "TSLA"  # Or any ticker you want
```

### Switch to Gemini

If notebook uses OpenAI, change:
```python
llm_config = {
    "config_list": autogen.config_list_from_json(
        "../OAI_CONFIG_LIST",  # Change this
        ...
    ),
}
```

To:
```python
llm_config = {
    "config_list": autogen.config_list_from_json(
        "../GEMINI_CONFIG_LIST",  # Use Gemini instead
        filter_dict={"model": ["gemini-2.5-flash"]},
    ),
}
```

## Benefits of Jupyter Notebooks

✅ **Interactive**: Run code step-by-step
✅ **Visual**: See charts and graphs inline
✅ **Educational**: Learn by doing
✅ **Experimentation**: Try different configurations easily
✅ **Documentation**: Code and explanations together

## Troubleshooting

### Jupyter won't start?
```bash
pip install --upgrade jupyter
jupyter notebook --port 8889  # Try different port
```

### Import errors?
```bash
# Make sure you're in the virtual environment
source venv/bin/activate
pip install -e .
```

### Notebook can't find config files?
- Check file paths in notebook cells
- Update `../OAI_CONFIG_LIST` to correct path
- Make sure config files exist

### Kernel dies?
- Check you have enough memory
- Restart kernel: Kernel → Restart
- Check for errors in previous cells

## Next Steps

1. **Install Jupyter**: `pip install jupyter`
2. **Start Jupyter**: `jupyter notebook`
3. **Open**: `tutorials_beginner/agent_fingpt_forecaster.ipynb`
4. **Run cells** and explore!

Enjoy interactive FinRobot development! 🚀

