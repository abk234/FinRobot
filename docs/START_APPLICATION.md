# Starting the FinRobot Application

## Current Status

I've created a demo script (`start_demo.py`) to run FinRobot, but there's a Python version compatibility issue:

- **Your System**: Python 3.14.0
- **FinRobot Requirement**: Python 3.10 or 3.11 (not 3.12+)

## Solutions

### Option 1: Install Python 3.11 via Homebrew (Recommended)

```bash
# Install Python 3.11
brew install python@3.11

# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install FinRobot
pip install -e .
```

### Option 2: Use Conda

```bash
# Create conda environment with Python 3.11
conda create --name finrobot python=3.11
conda activate finrobot

# Install FinRobot
pip install -e .
```

### Option 3: Use pyenv

```bash
# Install pyenv (if not installed)
brew install pyenv

# Install Python 3.11
pyenv install 3.11.9

# Set local Python version
cd /Users/lxupkzwjs/Developer/eval/FinRobot
pyenv local 3.11.9

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install FinRobot
pip install -e .
```

## After Installing Python 3.11

Once you have Python 3.11 set up:

1. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Verify API keys are configured**:
   - Check `OAI_CONFIG_LIST` has your OpenAI API key
   - Check `config_api_keys` has your FinnHub API key (optional)

3. **Run the demo**:
   ```bash
   python start_demo.py
   ```

## Quick Start Script

I've created `start_demo.py` which will:
- Load API keys
- Initialize a Market Analyst agent
- Analyze a stock (default: AAPL)
- Provide market insights and predictions

You can modify the `company` variable in the script to analyze different stocks.

## Alternative: Run Existing Demos

You can also run the existing demo scripts:

```bash
# Agent builder demo
python agent_builder_demo.py

# Or use Jupyter notebooks
jupyter notebook tutorials_beginner/agent_fingpt_forecaster.ipynb
```

## Troubleshooting

### API Key Issues

If you get API key errors:
1. Ensure `OAI_CONFIG_LIST` has a valid OpenAI API key
2. For market data, ensure `config_api_keys` has FinnHub API key
3. Remove placeholder text like `<your OpenAI API key here>`

### Module Not Found

If you get import errors:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -e .
```

### Network Issues

If API calls fail:
- Check your internet connection
- Verify API keys are valid
- Check rate limits on your API accounts

## Next Steps

1. Install Python 3.11 using one of the methods above
2. Set up your API keys
3. Run `python start_demo.py`
4. Explore the tutorials in `tutorials_beginner/` for more examples

For detailed documentation, see the `docs/` folder.

