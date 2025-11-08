# Starting Jupyter Notebooks for FinRobot

## Quick Start

```bash
cd /Users/lxupkzwjs/Developer/eval/FinRobot
source venv/bin/activate
jupyter notebook
```

This will:
- Start Jupyter server (usually on port 8888)
- Open your browser automatically
- Show the file browser

## Access Jupyter

Once started, open in your browser:
- **http://localhost:8888**

## Available Notebooks

### Beginner Tutorials (Start Here!)

1. **`tutorials_beginner/agent_fingpt_forecaster.ipynb`** ⭐
   - Market forecasting
   - Stock predictions
   - Best for learning

2. **`tutorials_beginner/agent_annual_report.ipynb`**
   - Generate annual reports
   - PDF creation

3. **`tutorials_beginner/agent_rag_qa.ipynb`**
   - Document Q&A
   - RAG functionality

### Advanced Tutorials

- `tutorials_advanced/agent_trade_strategist.ipynb`
- `tutorials_advanced/lmm_agent_mplfinance.ipynb`
- `tutorials_advanced/lmm_agent_opt_smacross.ipynb`

## Using Notebooks

1. **Navigate** to `tutorials_beginner/` folder
2. **Click** on any `.ipynb` file
3. **Run cells** with `Shift + Enter`
4. **Modify code** to customize
5. **See results** inline

## Configuration

Before running, update notebook cells:

### For Gemini (Free):
```python
llm_config = {
    "config_list": autogen.config_list_from_json(
        "../GEMINI_CONFIG_LIST",  # Use Gemini
        filter_dict={"model": ["gemini-2.5-flash"]},
    ),
}
```

### For OpenAI:
```python
llm_config = {
    "config_list": autogen.config_list_from_json(
        "../OAI_CONFIG_LIST",  # Use OpenAI
        filter_dict={"model": ["gpt-4o"]},
    ),
}
```

## Tips

- **Run cells in order** - They build on each other
- **Read markdown cells** - They explain what's happening
- **Modify ticker symbols** - Change `"AAPL"` to any stock
- **Experiment** - Try different configurations

Enjoy interactive FinRobot development! 🚀

