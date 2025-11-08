# Getting Started with FinRobot

This guide will help you set up FinRobot from scratch and run your first agent.

## Prerequisites

- **Python**: 3.10 or 3.11 (Python 3.12 is not yet supported)
- **Operating System**: macOS, Linux, or Windows
- **API Keys**: You'll need API keys for:
  - OpenAI (for LLM access)
  - FinnHub (optional, for market data)
  - Financial Modeling Prep (optional, for financial data)
  - SEC API (optional, for SEC filings)

## Installation Steps

### Step 1: Create Virtual Environment

**Using Conda (Recommended):**
```bash
conda create --name finrobot python=3.10
conda activate finrobot
```

**Using venv:**
```bash
python3.10 -m venv finrobot_env
source finrobot_env/bin/activate  # On Windows: finrobot_env\Scripts\activate
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/AI4Finance-Foundation/FinRobot.git
cd FinRobot
```

### Step 3: Install Dependencies

**Option A: Install from PyPI (Latest Release)**
```bash
pip install -U finrobot
```

**Option B: Install from Source (Development)**
```bash
pip install -e .
```

This will install all dependencies listed in `requirements.txt`.

### Step 4: Configure API Keys

#### 4.1 Configure OpenAI API Key

1. Copy the sample config file:
```bash
cp OAI_CONFIG_LIST_sample OAI_CONFIG_LIST
```

2. Edit `OAI_CONFIG_LIST` and remove the comment lines, then add your OpenAI API key:
```json
[
    {
        "model": "gpt-4-0125-preview",
        "api_key": "YOUR_OPENAI_API_KEY_HERE"
    }
]
```

#### 4.2 Configure Financial Data API Keys

1. Copy the sample config file:
```bash
cp config_api_keys_sample config_api_keys
```

2. Edit `config_api_keys` and add your API keys:
```json
{
    "FINNHUB_API_KEY": "YOUR_FINNHUB_API_KEY",
    "FMP_API_KEY": "YOUR_FMP_API_KEY",
    "SEC_API_KEY": "YOUR_SEC_API_KEY"
}
```

**Note**: Not all API keys are required. You only need the keys for the data sources you plan to use.

## Your First Agent: Market Analyst

Let's create a simple market analyst agent that predicts stock movements.

### Step 1: Create a Python Script

Create a file `my_first_agent.py`:

```python
import autogen
from finrobot.utils import get_current_date, register_keys_from_json
from finrobot.agents.workflow import SingleAssistant

# Load API keys
register_keys_from_json("config_api_keys")

# Configure LLM
llm_config = {
    "config_list": autogen.config_list_from_json(
        "OAI_CONFIG_LIST",
        filter_dict={"model": ["gpt-4-0125-preview"]},
    ),
    "timeout": 120,
    "temperature": 0,
}

# Create the agent
assistant = SingleAssistant(
    "Market_Analyst",
    llm_config,
    human_input_mode="NEVER",  # Set to "ALWAYS" for interactive mode
)

# Run the agent
company = "NVDA"
assistant.chat(
    f"Use all the tools provided to retrieve information available for {company} "
    f"upon {get_current_date()}. Analyze the positive developments and potential "
    f"concerns of {company} with 2-4 most important factors respectively and keep "
    f"them concise. Most factors should be inferred from company related news. "
    f"Then make a rough prediction (e.g. up/down by 2-3%) of the {company} stock "
    f"price movement for next week. Provide a summary analysis to support your prediction."
)
```

### Step 2: Run the Script

```bash
python my_first_agent.py
```

The agent will:
1. Retrieve company information from FinnHub
2. Get recent news about the company
3. Analyze financial data
4. Make a stock price prediction
5. Provide a summary

## Understanding the Code

### SingleAssistant Class

`SingleAssistant` is a wrapper that creates:
- **Assistant Agent**: The AI agent with tools and capabilities
- **User Proxy**: Handles code execution and tool calls

### Agent Configuration

The `"Market_Analyst"` string refers to a pre-defined agent in the agent library. It comes with:
- Pre-configured system prompt
- Pre-loaded tools (FinnHub, YFinance utilities)
- Optimized for market analysis tasks

### LLM Configuration

The `llm_config` dictionary specifies:
- **config_list**: Which LLM models to use
- **timeout**: Maximum time to wait for responses
- **temperature**: Controls randomness (0 = deterministic)

### Human Input Mode

- `"NEVER"`: Fully autonomous (no human interaction)
- `"ALWAYS"`: Requires human approval for each step
- `"TERMINATE"`: Only asks when task is complete

## Common Issues and Solutions

### Issue: "Module not found" errors

**Solution**: Make sure you've activated your virtual environment and installed the package:
```bash
pip install -e .
```

### Issue: "API key not found" errors

**Solution**: 
1. Check that `config_api_keys` file exists and has correct format
2. Verify API keys are valid
3. Ensure environment variables are set (if using `register_keys_from_json`)

### Issue: "Agent not found in library"

**Solution**: Check available agents in `finrobot/agents/agent_library.py` or use a custom agent configuration.

### Issue: Rate limiting errors

**Solution**: 
- Add delays between API calls
- Use caching: `assistant.chat(message, use_cache=True)`
- Check your API key limits

## Next Steps

1. **Explore Tutorials**: Check out `tutorials_beginner/` for more examples
2. **Read Architecture Docs**: See [[02-Architecture]] for system design
3. **Learn Agent Patterns**: Review [[03-Agent-Workflows]] for different agent types
4. **Develop Custom Agents**: Follow [[04-Development-Guide]] to create your own agents

## Additional Resources

- **Beginner Tutorials**: 
  - `tutorials_beginner/agent_annual_report.ipynb`
  - `tutorials_beginner/agent_fingpt_forecaster.ipynb`
- **Advanced Tutorials**:
  - `tutorials_advanced/agent_trade_strategist.ipynb`
  - `tutorials_advanced/lmm_agent_mplfinance.ipynb`
- **Examples**: Check `experiments/` folder for real-world use cases

## Getting Help

- **Discord**: Join the [FinRobot Discord](https://discord.gg/trsr8SXpW5)
- **GitHub Issues**: Report bugs or ask questions on GitHub
- **Documentation**: Read the full documentation in this folder

