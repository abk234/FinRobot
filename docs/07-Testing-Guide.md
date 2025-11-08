# Testing Guide

This guide covers testing strategies, best practices, and examples for FinRobot.

## Testing Philosophy

FinRobot testing should cover:
1. **Unit Tests**: Individual functions and classes
2. **Integration Tests**: Component interactions
3. **Agent Tests**: Agent behavior and workflows
4. **End-to-End Tests**: Complete workflows

## Test Structure

### Recommended Structure

```
tests/
├── unit/
│   ├── test_data_sources.py
│   ├── test_functional.py
│   └── test_utils.py
├── integration/
│   ├── test_agent_workflows.py
│   └── test_tool_integration.py
├── e2e/
│   └── test_complete_workflows.py
└── fixtures/
    └── sample_data.py
```

## Unit Testing

### Testing Data Sources

```python
import unittest
from unittest.mock import patch, MagicMock
from finrobot.data_source.yfinance_utils import YFinanceUtils

class TestYFinanceUtils(unittest.TestCase):
    
    @patch('yfinance.Ticker')
    def test_get_stock_data(self, mock_ticker):
        # Setup mock
        mock_ticker.return_value.history.return_value = pd.DataFrame({
            'Open': [100, 101],
            'Close': [101, 102],
        })
        
        # Test
        result = YFinanceUtils.get_stock_data(
            "AAPL",
            "2023-01-01",
            "2023-12-31"
        )
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
    
    def test_get_stock_data_invalid_symbol(self):
        with self.assertRaises(Exception):
            YFinanceUtils.get_stock_data(
                "INVALID",
                "2023-01-01",
                "2023-12-31"
            )
```

### Testing Functional Modules

```python
import unittest
from unittest.mock import patch
from finrobot.functional.charting import MplFinanceUtils

class TestChartingUtils(unittest.TestCase):
    
    @patch('mplfinance.plot')
    @patch('finrobot.data_source.yfinance_utils.YFinanceUtils.get_stock_data')
    def test_plot_stock_price_chart(self, mock_get_data, mock_plot):
        # Setup
        mock_get_data.return_value = pd.DataFrame({
            'Open': [100], 'High': [101],
            'Low': [99], 'Close': [100.5],
        })
        
        # Test
        result = MplFinanceUtils.plot_stock_price_chart(
            "AAPL",
            "2023-01-01",
            "2023-12-31",
            "test_chart.png"
        )
        
        # Assert
        self.assertIn("saved", result.lower())
        mock_plot.assert_called_once()
```

### Testing Utilities

```python
import unittest
from finrobot.utils import get_current_date, save_output
import pandas as pd
import os
import tempfile

class TestUtils(unittest.TestCase):
    
    def test_get_current_date(self):
        date = get_current_date()
        self.assertRegex(date, r'\d{4}-\d{2}-\d{2}')
    
    def test_save_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({'A': [1, 2]})
            save_path = os.path.join(tmpdir, "test.csv")
            
            save_output(df, "Test", save_path)
            
            self.assertTrue(os.path.exists(save_path))
            loaded = pd.read_csv(save_path)
            self.assertEqual(len(loaded), 2)
```

## Integration Testing

### Testing Agent Workflows

```python
import unittest
from unittest.mock import patch, MagicMock
from finrobot.agents.workflow import SingleAssistant
import autogen

class TestAgentWorkflows(unittest.TestCase):
    
    @patch('autogen.AssistantAgent')
    @patch('autogen.UserProxyAgent')
    def test_single_assistant_initialization(self, mock_proxy, mock_assistant):
        llm_config = {
            "config_list": [{"model": "gpt-4", "api_key": "test"}],
        }
        
        assistant = SingleAssistant("Market_Analyst", llm_config)
        
        self.assertIsNotNone(assistant.assistant)
        self.assertIsNotNone(assistant.user_proxy)
    
    def test_agent_reset(self):
        llm_config = {
            "config_list": [{"model": "gpt-4", "api_key": "test"}],
        }
        
        assistant = SingleAssistant("Market_Analyst", llm_config)
        assistant.reset()
        
        # Verify reset (check message history cleared)
        self.assertEqual(len(assistant.assistant.chat_messages), 0)
```

### Testing Tool Registration

```python
import unittest
from unittest.mock import patch
from finrobot.toolkits import register_toolkits
from autogen import ConversableAgent

class TestToolRegistration(unittest.TestCase):
    
    def test_register_single_tool(self):
        def test_tool(param: str) -> str:
            return f"Result: {param}"
        
        caller = MagicMock(spec=ConversableAgent)
        executor = MagicMock(spec=ConversableAgent)
        
        register_toolkits([test_tool], caller, executor)
        
        # Verify function was registered
        # (Check caller's function map)
        self.assertTrue(hasattr(caller, '_function_map'))
    
    def test_register_class_tools(self):
        class TestTools:
            @staticmethod
            def tool1(param: str) -> str:
                return "result1"
            
            @staticmethod
            def tool2(param: int) -> str:
                return "result2"
        
        caller = MagicMock(spec=ConversableAgent)
        executor = MagicMock(spec=ConversableAgent)
        
        register_toolkits([TestTools], caller, executor)
        
        # Verify all methods registered
        # (Implementation specific)
```

## End-to-End Testing

### Testing Complete Workflows

```python
import unittest
from unittest.mock import patch
from finrobot.agents.workflow import SingleAssistant
import autogen

class TestE2EWorkflows(unittest.TestCase):
    
    @patch('autogen.UserProxyAgent.initiate_chat')
    def test_market_analysis_workflow(self, mock_chat):
        llm_config = {
            "config_list": [{"model": "gpt-4", "api_key": "test"}],
        }
        
        assistant = SingleAssistant("Market_Analyst", llm_config)
        assistant.chat("Analyze AAPL stock")
        
        # Verify chat was initiated
        mock_chat.assert_called_once()
    
    def test_multi_agent_workflow(self):
        # Test multi-agent collaboration
        # (Mock agent interactions)
        pass
```

## Mocking Strategies

### Mocking API Calls

```python
from unittest.mock import patch, MagicMock

@patch('finnhub.Client')
def test_finnhub_utils(mock_client_class):
    # Setup mock client
    mock_client = MagicMock()
    mock_client.company_profile2.return_value = {
        "name": "Test Company",
        "ticker": "TEST",
    }
    mock_client_class.return_value = mock_client
    
    # Test
    from finrobot.data_source import FinnHubUtils
    result = FinnHubUtils.get_company_profile("TEST")
    
    # Assert
    assert "Test Company" in result
    mock_client.company_profile2.assert_called_once_with(symbol="TEST")
```

### Mocking LLM Responses

```python
from unittest.mock import patch, MagicMock

@patch('autogen.AssistantAgent.generate_reply')
def test_agent_with_mocked_llm(mock_generate):
    # Setup mock LLM response
    mock_generate.return_value = {
        "content": "TERMINATE",
        "role": "assistant",
    }
    
    # Test agent
    # ...
```

### Mocking File Operations

```python
from unittest.mock import patch, mock_open

@patch('builtins.open', new_callable=mock_open)
def test_file_operations(mock_file):
    # Test file operations
    # ...
    mock_file.assert_called_with("path/to/file", "w")
```

## Test Fixtures

### Sample Data Fixtures

```python
# tests/fixtures/sample_data.py
import pandas as pd

def sample_stock_data():
    return pd.DataFrame({
        'Open': [100, 101, 102],
        'High': [101, 102, 103],
        'Low': [99, 100, 101],
        'Close': [100.5, 101.5, 102.5],
        'Volume': [1000000, 1100000, 1200000],
    }, index=pd.date_range('2023-01-01', periods=3))

def sample_income_stmt():
    return pd.DataFrame({
        'Revenue': [1000000, 1100000],
        'Cost of Revenue': [600000, 650000],
        'Net Income': [200000, 250000],
    })
```

### Using Fixtures

```python
from tests.fixtures.sample_data import sample_stock_data

def test_with_fixture():
    data = sample_stock_data()
    # Use fixture data in test
    assert len(data) == 3
```

## Test Configuration

### pytest Configuration

Create `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_data_sources.py

# Run with coverage
pytest --cov=finrobot --cov-report=html

# Run with verbose output
pytest -v
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=finrobot
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Dependencies**: Don't make real API calls in tests
3. **Use Fixtures**: Reuse test data and setup
4. **Test Edge Cases**: Test error conditions and boundaries
5. **Fast Tests**: Keep unit tests fast (< 1 second each)
6. **Clear Assertions**: Use descriptive assertion messages
7. **Test Coverage**: Aim for >80% code coverage
8. **Documentation**: Document complex test scenarios

## Testing Agents

### Testing Agent Behavior

```python
def test_agent_termination():
    llm_config = {
        "config_list": [{"model": "gpt-4", "api_key": "test"}],
    }
    
    assistant = SingleAssistant(
        "Market_Analyst",
        llm_config,
        is_termination_msg=lambda x: "DONE" in x.get("content", ""),
    )
    
    # Test termination logic
    assert assistant.user_proxy.is_termination_msg({"content": "DONE"})
```

### Testing Tool Calls

```python
def test_agent_tool_usage():
    # Verify agent can call registered tools
    # (Implementation specific)
    pass
```

## Debugging Tests

### Using pytest Debugger

```python
import pytest

def test_with_debugger():
    # Set breakpoint
    import pdb; pdb.set_trace()
    
    # Test code
    result = function_under_test()
    
    assert result == expected
```

### Verbose Output

```bash
# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Show full traceback
pytest --tb=long
```

## Next Steps

- See [[04-Development-Guide]] for development practices
- Check existing tests in the codebase for patterns
- Review pytest documentation for advanced features

