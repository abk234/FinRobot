# Data Sources Guide

This guide documents all available data sources in FinRobot and how to use them.

## Overview

FinRobot integrates with multiple financial data providers:

- **FinnHub**: Market data, news, company profiles
- **Yahoo Finance (yfinance)**: Stock prices, financial statements
- **Financial Modeling Prep (FMP)**: SEC filings, financial data
- **SEC API**: SEC filing retrieval and parsing
- **Reddit (PRAW)**: Social sentiment data
- **FinNLP** (optional): Financial NLP utilities

## FinnHub Utils

### Setup

Requires `FINNHUB_API_KEY` environment variable:

```python
from finrobot.utils import register_keys_from_json
register_keys_from_json("config_api_keys")
```

### Available Methods

#### get_company_profile(symbol)

Get comprehensive company profile information.

```python
from finrobot.data_source import FinnHubUtils

profile = FinnHubUtils.get_company_profile("AAPL")
# Returns formatted string with company info
```

**Returns**: Formatted string with:
- Company name and industry
- Market capitalization
- IPO date
- Exchange information

#### get_company_news(symbol)

Get recent company news.

```python
news = FinnHubUtils.get_company_news("AAPL")
# Returns formatted news articles
```

**Returns**: Formatted string with recent news articles

#### get_basic_financials(symbol)

Get basic financial metrics.

```python
financials = FinnHubUtils.get_basic_financials("AAPL")
# Returns key financial metrics
```

**Returns**: Formatted string with financial metrics

### Usage in Agents

```python
agent_config = {
    "name": "Market_Analyst",
    "toolkits": [
        FinnHubUtils.get_company_profile,
        FinnHubUtils.get_company_news,
        FinnHubUtils.get_basic_financials,
    ],
}
```

## YFinance Utils

### Setup

No API key required - uses public Yahoo Finance API.

### Available Methods

#### get_stock_data(symbol, start_date, end_date)

Get historical stock price data.

```python
from finrobot.data_source import YFinanceUtils

data = YFinanceUtils.get_stock_data(
    "AAPL",
    "2023-01-01",
    "2023-12-31"
)
# Returns pandas DataFrame
```

**Parameters**:
- `symbol`: Ticker symbol (e.g., "AAPL")
- `start_date`: Start date in "YYYY-MM-DD" format
- `end_date`: End date in "YYYY-MM-DD" format
- `save_path`: Optional path to save CSV

**Returns**: pandas DataFrame with OHLCV data

#### get_income_stmt(symbol)

Get income statement.

```python
income_stmt = YFinanceUtils.get_income_stmt("AAPL")
# Returns pandas DataFrame
```

**Returns**: DataFrame with income statement data

#### get_balance_sheet(symbol)

Get balance sheet.

```python
balance_sheet = YFinanceUtils.get_balance_sheet("AAPL")
# Returns pandas DataFrame
```

**Returns**: DataFrame with balance sheet data

#### get_cash_flow(symbol)

Get cash flow statement.

```python
cash_flow = YFinanceUtils.get_cash_flow("AAPL")
# Returns pandas DataFrame
```

**Returns**: DataFrame with cash flow data

#### get_company_info(symbol)

Get company information.

```python
info = YFinanceUtils.get_company_info("AAPL")
# Returns pandas DataFrame
```

**Returns**: DataFrame with company information

#### get_stock_info(symbol)

Get latest stock information.

```python
info = YFinanceUtils.get_stock_info("AAPL")
# Returns dictionary
```

**Returns**: Dictionary with stock information

### Usage Example

```python
from finrobot.data_source import YFinanceUtils

# Get stock data
stock_data = YFinanceUtils.get_stock_data("AAPL", "2023-01-01", "2023-12-31")

# Get financial statements
income = YFinanceUtils.get_income_stmt("AAPL")
balance = YFinanceUtils.get_balance_sheet("AAPL")
cashflow = YFinanceUtils.get_cash_flow("AAPL")
```

## FMP Utils (Financial Modeling Prep)

### Setup

Requires `FMP_API_KEY` environment variable.

### Available Methods

#### get_sec_report(ticker, report_type, year)

Get SEC report URL and filing date.

```python
from finrobot.data_source import FMPUtils

report = FMPUtils.get_sec_report("MSFT", "10-K", "2023")
# Returns formatted string with report URL and date
```

**Parameters**:
- `ticker`: Stock ticker symbol
- `report_type`: "10-K", "10-Q", "8-K", etc.
- `year`: Fiscal year

**Returns**: Formatted string with report information

### Usage in Agents

```python
agent_config = {
    "toolkits": [FMPUtils.get_sec_report],
}
```

## SEC Utils

### Setup

Requires `SEC_API_KEY` environment variable (for SEC API integration).

### Available Methods

#### get_10k_section(ticker, year, section)

Extract specific section from 10-K report.

```python
from finrobot.data_source import SECUtils

section_text = SECUtils.get_10k_section("MSFT", "2023", 7)
# Returns text from section 7 (MD&A)
```

**Parameters**:
- `ticker`: Stock ticker symbol
- `year`: Fiscal year
- `section`: Section number (1-15)

**Common Sections**:
- 1: Business
- 2: Properties
- 3: Legal Proceedings
- 7: Management's Discussion and Analysis (MD&A)
- 8: Financial Statements

**Returns**: Text content of the section

### Usage Example

```python
# Get MD&A section
mda = SECUtils.get_10k_section("MSFT", "2023", 7)

# Get Business section
business = SECUtils.get_10k_section("MSFT", "2023", 1)
```

## Reddit Utils

### Setup

Requires Reddit API credentials (client_id, client_secret, user_agent).

### Available Methods

Reddit utilities for sentiment analysis and social data.

**Note**: See `finrobot/data_source/reddit_utils.py` for available methods.

## FinNLP Utils (Optional)

### Setup

Requires `finnlp` package installation:

```bash
pip install finnlp
```

### Available Methods

Financial NLP utilities for text analysis.

**Note**: Automatically imported if `finnlp` is available.

## Data Source Patterns

### Pattern 1: Decorator Pattern

Many data sources use the decorator pattern for initialization:

```python
@decorate_all_methods(init_api_client)
class DataSourceUtils:
    @staticmethod
    def method():
        # API client is automatically initialized
        pass
```

### Pattern 2: Save Path Parameter

Many methods support optional `save_path`:

```python
data = YFinanceUtils.get_stock_data(
    "AAPL",
    "2023-01-01",
    "2023-12-31",
    save_path="data/aapl_stock.csv"
)
```

### Pattern 3: DataFrame to String

DataFrames are automatically converted to strings for LLM consumption:

```python
# Returns DataFrame
df = YFinanceUtils.get_stock_data(...)

# When used as tool, automatically stringified
# LLM receives: df.to_string()
```

## Error Handling

### API Key Errors

```python
# Check if API key is set
import os
if not os.environ.get("FINNHUB_API_KEY"):
    print("Please set FINNHUB_API_KEY")
```

### Rate Limiting

Implement rate limiting for API calls:

```python
from time import sleep

def safe_api_call():
    try:
        result = api_call()
        return result
    except RateLimitError:
        sleep(60)  # Wait 1 minute
        return safe_api_call()
```

### Data Validation

```python
def validate_symbol(symbol):
    if not symbol or len(symbol) > 5:
        raise ValueError(f"Invalid symbol: {symbol}")
    return symbol.upper()
```

## Creating Custom Data Sources

### Template

```python
import os
from typing import Annotated
from functools import wraps
from ..utils import decorate_all_methods, SavePathType

def init_my_api(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global api_client
        if not os.environ.get("MY_API_KEY"):
            raise ValueError("MY_API_KEY not set")
        api_client = MyAPIClient(os.environ["MY_API_KEY"])
        return func(*args, **kwargs)
    return wrapper

@decorate_all_methods(init_my_api)
class MyDataSourceUtils:
    
    @staticmethod
    def get_data(
        symbol: Annotated[str, "Ticker symbol"],
        save_path: SavePathType = None,
    ) -> str:
        """
        Get data from My API.
        
        Returns:
            Formatted data string
        """
        data = api_client.fetch(symbol)
        
        if save_path:
            pd.DataFrame(data).to_csv(save_path)
        
        return format_data(data)
```

### Adding to Package

1. Create `finrobot/data_source/my_source_utils.py`
2. Add to `finrobot/data_source/__init__.py`:

```python
from .my_source_utils import MyDataSourceUtils
__all__.append("MyDataSourceUtils")
```

## Best Practices

1. **Cache API Calls**: Use caching to reduce API calls
2. **Handle Errors**: Always handle API errors gracefully
3. **Rate Limiting**: Respect API rate limits
4. **Data Validation**: Validate inputs before API calls
5. **Type Annotations**: Use Annotated types for all parameters
6. **Documentation**: Document all methods with docstrings

## API Key Management

### Environment Variables

```python
# Set in config file
{
    "FINNHUB_API_KEY": "your_key",
    "FMP_API_KEY": "your_key",
    "SEC_API_KEY": "your_key",
}

# Load
from finrobot.utils import register_keys_from_json
register_keys_from_json("config_api_keys")
```

### Security

- **Never commit API keys** to version control
- Use `.gitignore` for config files
- Use environment variables in production
- Rotate keys regularly

## Next Steps

- See [[04-Development-Guide]] for creating custom data sources
- Read [[06-Functional-Modules]] for using data in analysis
- Check examples in `tutorials_beginner/` for usage patterns

