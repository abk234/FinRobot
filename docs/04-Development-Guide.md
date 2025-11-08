# Development Guide

This guide helps you extend FinRobot by creating custom agents, tools, and workflows.

## Table of Contents

1. [Creating Custom Agents](#creating-custom-agents)
2. [Adding New Tools](#adding-new-tools)
3. [Creating Data Source Utilities](#creating-data-source-utilities)
4. [Building Functional Modules](#building-functional-modules)
5. [Testing Your Code](#testing-your-code)
6. [Code Style and Best Practices](#code-style-and-best-practices)

## Creating Custom Agents

### Method 1: Using Agent Library

Add your agent to `finrobot/agents/agent_library.py`:

```python
library = {
    # ... existing agents ...
    "My_Custom_Agent": {
        "name": "My_Custom_Agent",
        "profile": dedent(
            """
            You are a custom agent specialized in [your domain].
            Your responsibilities include:
            - Task 1
            - Task 2
            - Task 3
            """
        ),
        "toolkits": [
            MyCustomTool.function1,
            MyCustomTool.function2,
        ],
    },
}
```

Then use it:

```python
assistant = SingleAssistant("My_Custom_Agent", llm_config)
```

### Method 2: Inline Configuration

Define agent config directly:

```python
custom_agent_config = {
    "name": "Custom_Analyst",
    "profile": "You are a custom financial analyst...",
    "toolkits": [
        FinnHubUtils.get_company_profile,
        YFinanceUtils.get_stock_data,
        MyCustomFunction,
    ],
}

assistant = SingleAssistant(custom_agent_config, llm_config)
```

### Method 3: Extending FinRobot Class

For advanced customization:

```python
from finrobot.agents.workflow import FinRobot

class MyCustomAgent(FinRobot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom initialization
    
    def custom_method(self):
        # Custom agent behavior
        pass
```

## Adding New Tools

### Tool Function Requirements

Tools must:
1. Have type annotations using `Annotated`
2. Have docstrings describing their purpose
3. Return strings or DataFrames (will be stringified)

### Example: Simple Tool

```python
from typing import Annotated

def calculate_pe_ratio(
    price: Annotated[float, "Current stock price"],
    earnings: Annotated[float, "Earnings per share"],
) -> str:
    """
    Calculate the Price-to-Earnings (P/E) ratio.
    
    Args:
        price: Current stock price
        earnings: Earnings per share
        
    Returns:
        P/E ratio as a formatted string
    """
    pe_ratio = price / earnings if earnings > 0 else "N/A"
    return f"P/E Ratio: {pe_ratio:.2f}"
```

### Example: Tool with DataFrame

```python
import pandas as pd
from typing import Annotated

def get_stock_comparison(
    symbols: Annotated[list, "List of ticker symbols"],
    metric: Annotated[str, "Metric to compare (e.g., 'price', 'volume')"],
) -> pd.DataFrame:
    """
    Compare stocks by a given metric.
    
    Returns:
        DataFrame with comparison data
    """
    data = []
    for symbol in symbols:
        # Fetch data for each symbol
        data.append({"symbol": symbol, metric: fetch_metric(symbol, metric)})
    
    return pd.DataFrame(data)
```

**Note**: DataFrames are automatically converted to strings by `stringify_output()`.

### Registering Tools

#### Option 1: In Agent Config

```python
agent_config = {
    "name": "My_Agent",
    "toolkits": [
        calculate_pe_ratio,
        get_stock_comparison,
    ],
}
```

#### Option 2: Register After Creation

```python
from finrobot.toolkits import register_toolkits
from autogen import register_function

assistant = SingleAssistant("Market_Analyst", llm_config)

# Register additional tools
register_toolkits(
    [calculate_pe_ratio, get_stock_comparison],
    caller=assistant.assistant,
    executor=assistant.user_proxy,
)
```

#### Option 3: Register Class Methods

```python
class MyToolClass:
    @staticmethod
    def method1(param: Annotated[str, "Parameter"]) -> str:
        """Tool method 1"""
        return "result"
    
    @staticmethod
    def method2(param: Annotated[int, "Number"]) -> str:
        """Tool method 2"""
        return "result"

# Register all public methods
register_toolkits(
    [MyToolClass],
    caller=assistant.assistant,
    executor=assistant.user_proxy,
)
```

### Tool with Custom Name/Description

```python
register_toolkits(
    [{
        "function": calculate_pe_ratio,
        "name": "calculate_valuation_metric",
        "description": "Calculates P/E ratio for stock valuation",
    }],
    caller=assistant.assistant,
    executor=assistant.user_proxy,
)
```

## Creating Data Source Utilities

### Template for Data Source Class

```python
import os
from typing import Annotated
from functools import wraps
from ..utils import decorate_all_methods, SavePathType

def init_api_client(func):
    """Decorator to initialize API client"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        global api_client
        if os.environ.get("MY_API_KEY") is None:
            print("Please set MY_API_KEY environment variable")
            return None
        api_client = MyAPIClient(api_key=os.environ["MY_API_KEY"])
        return func(*args, **kwargs)
    return wrapper

@decorate_all_methods(init_api_client)
class MyDataSourceUtils:
    
    @staticmethod
    def get_data(
        symbol: Annotated[str, "Ticker symbol"],
        save_path: SavePathType = None,
    ) -> str:
        """
        Retrieve data for the given symbol.
        
        Args:
            symbol: Stock ticker symbol
            save_path: Optional path to save data
            
        Returns:
            Formatted data string
        """
        data = api_client.fetch_data(symbol)
        
        if save_path:
            pd.DataFrame(data).to_csv(save_path)
        
        return format_data(data)
```

### Adding to Package

1. Create file: `finrobot/data_source/my_source_utils.py`
2. Add to `finrobot/data_source/__init__.py`:

```python
from .my_source_utils import MyDataSourceUtils
__all__.append("MyDataSourceUtils")
```

3. Use in agents:

```python
agent_config = {
    "toolkits": [MyDataSourceUtils.get_data],
}
```

## Building Functional Modules

### Template for Functional Module

```python
from typing import Annotated
from ..data_source import YFinanceUtils

class MyFunctionalUtils:
    
    @staticmethod
    def analyze_metric(
        symbol: Annotated[str, "Ticker symbol"],
        metric: Annotated[str, "Metric name"],
    ) -> str:
        """
        Analyze a specific metric for a stock.
        
        Returns:
            Analysis result as string
        """
        # Fetch data
        data = YFinanceUtils.get_stock_data(symbol, ...)
        
        # Perform analysis
        result = perform_analysis(data, metric)
        
        # Format output
        return format_analysis(result)
```

### Adding to Package

1. Create file: `finrobot/functional/my_module.py`
2. Add to `finrobot/functional/__init__.py`:

```python
from .my_module import MyFunctionalUtils
```

3. Use in agents:

```python
agent_config = {
    "toolkits": [MyFunctionalUtils.analyze_metric],
}
```

## Testing Your Code

### Unit Testing Tools

```python
import unittest
from finrobot.data_source.yfinance_utils import YFinanceUtils

class TestYFinanceUtils(unittest.TestCase):
    
    def test_get_stock_data(self):
        data = YFinanceUtils.get_stock_data(
            "AAPL",
            "2023-01-01",
            "2023-12-31"
        )
        self.assertIsNotNone(data)
        self.assertGreater(len(data), 0)
```

### Testing Agents

```python
def test_market_analyst():
    llm_config = {
        "config_list": [{"model": "gpt-4", "api_key": "test"}],
    }
    
    assistant = SingleAssistant("Market_Analyst", llm_config)
    
    # Test with simple query
    assistant.chat("Get AAPL company profile")
    
    # Check that tools were called
    assert len(assistant.assistant.chat_messages) > 0
```

### Integration Testing

```python
def test_full_workflow():
    # Test complete workflow
    assistant = SingleAssistant("Expert_Investor", llm_config)
    
    result = assistant.chat(
        "Analyze MSFT and generate a brief report"
    )
    
    # Verify output
    assert "Microsoft" in str(result)
```

### Mocking API Calls

```python
from unittest.mock import patch, MagicMock

@patch('finnhub.Client')
def test_finnhub_utils(mock_client):
    mock_client.return_value.company_profile2.return_value = {
        "name": "Test Company",
        "ticker": "TEST",
    }
    
    result = FinnHubUtils.get_company_profile("TEST")
    assert "Test Company" in result
```

## Code Style and Best Practices

### Type Annotations

**Always use Annotated types for tool parameters:**

```python
# Good
def my_function(
    symbol: Annotated[str, "Ticker symbol"],
    date: Annotated[str, "Date in YYYY-MM-DD format"],
) -> str:
    pass

# Bad
def my_function(symbol: str, date: str) -> str:
    pass
```

### Docstrings

**Always include docstrings for tools:**

```python
def my_tool(param: Annotated[str, "Parameter"]) -> str:
    """
    Brief description of what the tool does.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Example:
        >>> my_tool("AAPL")
        "Result..."
    """
    pass
```

### Error Handling

**Handle errors gracefully:**

```python
def safe_api_call(symbol: Annotated[str, "Symbol"]) -> str:
    try:
        result = api_client.fetch(symbol)
        return format_result(result)
    except APIError as e:
        return f"Error fetching data: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
```

### Resource Management

**Clean up resources:**

```python
def process_data(file_path: Annotated[str, "File path"]) -> str:
    try:
        data = load_file(file_path)
        result = process(data)
        return result
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)
```

### Logging

**Use logging for debugging:**

```python
import logging

logger = logging.getLogger(__name__)

def my_function(param):
    logger.debug(f"Processing {param}")
    try:
        result = process(param)
        logger.info(f"Successfully processed {param}")
        return result
    except Exception as e:
        logger.error(f"Error processing {param}: {e}")
        raise
```

### Code Organization

**Follow the existing structure:**

```
finrobot/
├── data_source/     # Data source utilities
├── functional/      # Functional modules
├── agents/          # Agent definitions
└── utils.py         # Shared utilities
```

**Keep functions focused:**

```python
# Good: Single responsibility
def get_stock_price(symbol):
    return fetch_price(symbol)

def calculate_return(price1, price2):
    return (price2 - price1) / price1

# Bad: Multiple responsibilities
def get_stock_and_calculate_return(symbol, date1, date2):
    price1 = fetch_price(symbol, date1)
    price2 = fetch_price(symbol, date2)
    return (price2 - price1) / price1
```

## Contributing Guidelines

### Before Submitting

1. **Test your code**: Write unit tests
2. **Follow style**: Use type annotations and docstrings
3. **Update docs**: Document new features
4. **Check dependencies**: Ensure new dependencies are in requirements.txt

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit pull request

### Code Review Checklist

- [ ] Type annotations present
- [ ] Docstrings included
- [ ] Error handling implemented
- [ ] Tests written
- [ ] Documentation updated
- [ ] No hardcoded API keys
- [ ] Follows existing patterns

## Debugging Tips

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Agent State

```python
# Check agent messages
print(assistant.assistant.chat_messages)

# Check registered tools
print(assistant.assistant._function_map)

# Check system message
print(assistant.assistant.system_message)
```

### Test Tools Independently

```python
# Test tool without agent
result = MyTool.my_function("AAPL")
print(result)
```

## Next Steps

- See [[05-Data-Sources]] for data source details
- Read [[06-Functional-Modules]] for functional module patterns
- Check `tutorials_advanced/` for advanced examples
- Review existing code in `finrobot/` for patterns

