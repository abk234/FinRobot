# Functional Modules Guide

This guide documents the functional modules in FinRobot that provide analysis, visualization, and processing capabilities.

## Overview

Functional modules are organized in `finrobot/functional/`:

- **analyzer.py**: Financial statement analysis
- **charting.py**: Stock charts and visualizations
- **coding.py**: Code execution utilities
- **quantitative.py**: Quantitative analysis and backtesting
- **rag.py**: Retrieval-Augmented Generation
- **reportlab.py**: PDF report generation
- **text.py**: Text processing utilities

## Analyzer Module

### ReportAnalysisUtils

Provides utilities for analyzing financial statements with context from 10-K reports.

#### analyze_income_stmt(ticker, fyear, save_path)

Analyze income statement with 10-K context.

```python
from finrobot.functional import ReportAnalysisUtils

result = ReportAnalysisUtils.analyze_income_stmt(
    "MSFT",
    "2023",
    "analysis/income_stmt_analysis.txt"
)
```

**Workflow**:
1. Retrieves income statement from YFinance
2. Gets relevant 10-K section (MD&A)
3. Combines with analysis instructions
4. Saves to file for LLM processing

**Returns**: Confirmation message with file path

#### analyze_balance_sheet(ticker, fyear, save_path)

Analyze balance sheet with 10-K context.

```python
result = ReportAnalysisUtils.analyze_balance_sheet(
    "MSFT",
    "2023",
    "analysis/balance_sheet_analysis.txt"
)
```

#### analyze_cash_flow(ticker, fyear, save_path)

Analyze cash flow statement with 10-K context.

```python
result = ReportAnalysisUtils.analyze_cash_flow(
    "MSFT",
    "2023",
    "analysis/cash_flow_analysis.txt"
)
```

### Usage in Agents

```python
agent_config = {
    "toolkits": [
        ReportAnalysisUtils.analyze_income_stmt,
        ReportAnalysisUtils.analyze_balance_sheet,
        ReportAnalysisUtils.analyze_cash_flow,
    ],
}
```

## Charting Module

### MplFinanceUtils

Stock chart generation using mplfinance.

#### plot_stock_price_chart(ticker, start_date, end_date, save_path, ...)

Create stock price charts (candlestick, OHLC, line, etc.).

```python
from finrobot.functional import MplFinanceUtils

MplFinanceUtils.plot_stock_price_chart(
    ticker_symbol="AAPL",
    start_date="2023-01-01",
    end_date="2023-12-31",
    save_path="charts/aapl_chart.png",
    type="candle",  # 'candle', 'ohlc', 'line', etc.
    style="default",
    mav=(10, 20, 50),  # Moving averages
)
```

**Parameters**:
- `ticker_symbol`: Stock ticker
- `start_date`, `end_date`: Date range
- `save_path`: Where to save chart
- `type`: Chart type ('candle', 'ohlc', 'line', 'renko', 'pnf')
- `style`: Chart style
- `mav`: Moving average windows (int, list, or tuple)
- `show_nontrading`: Show non-trading days

**Returns**: Confirmation message

#### plot_technical_indicators(ticker, start_date, end_date, save_path, indicators)

Plot technical indicators on stock chart.

```python
MplFinanceUtils.plot_technical_indicators(
    "AAPL",
    "2023-01-01",
    "2023-12-31",
    "charts/aapl_indicators.png",
    indicators=["RSI", "MACD", "Bollinger"]
)
```

### ReportChartUtils

Report-specific charting utilities.

#### plot_pe_ratio(ticker, start_date, end_date, save_path)

Plot P/E ratio over time.

```python
from finrobot.functional import ReportChartUtils

ReportChartUtils.plot_pe_ratio(
    "AAPL",
    "2023-01-01",
    "2023-12-31",
    "charts/pe_ratio.png"
)
```

#### plot_eps(ticker, start_date, end_date, save_path)

Plot Earnings Per Share over time.

```python
ReportChartUtils.plot_eps(
    "AAPL",
    "2023-01-01",
    "2023-12-31",
    "charts/eps.png"
)
```

### Usage Example

```python
# Create candlestick chart with moving averages
MplFinanceUtils.plot_stock_price_chart(
    "AAPL",
    "2023-01-01",
    "2023-12-31",
    "charts/aapl_candle.png",
    type="candle",
    mav=[20, 50, 200],
)

# Create P/E ratio chart for report
ReportChartUtils.plot_pe_ratio(
    "AAPL",
    "2023-01-01",
    "2023-12-31",
    "report/pe_ratio.png"
)
```

## Coding Module

### CodingUtils

Utilities for code manipulation and file operations.

#### list_dir(path)

List files in a directory.

```python
from finrobot.functional import CodingUtils

files = CodingUtils.list_dir("coding/")
# Returns string listing of files
```

#### see_file(path)

Read file contents.

```python
content = CodingUtils.see_file("coding/analysis.py")
# Returns file contents as string
```

#### modify_code(old_code, new_code, file_path)

Replace code in a file.

```python
CodingUtils.modify_code(
    old_code="def old_function():",
    new_code="def new_function():",
    file_path="coding/script.py"
)
```

#### create_file_with_code(code, file_path)

Create a new file with code.

```python
CodingUtils.create_file_with_code(
    code="print('Hello, World!')",
    file_path="coding/hello.py"
)
```

### IPythonUtils

IPython/Jupyter notebook utilities.

#### display_image(path)

Display image in IPython notebook.

```python
from finrobot.functional import IPythonUtils

IPythonUtils.display_image("charts/aapl_chart.png")
```

### Usage in Agents

These tools are automatically available when agents execute code:

```python
# Agent can use these tools to:
# - List files in work directory
# - Read existing code
# - Modify code
# - Create new files
```

## Quantitative Module

### BackTraderUtils

Backtesting framework integration.

**Note**: See `finrobot/functional/quantitative.py` for available methods.

**Usage**: Strategy backtesting and performance analysis.

## RAG Module

### get_rag_function(retrieve_config, rag_description)

Set up RAG (Retrieval-Augmented Generation) functionality.

```python
from finrobot.functional import get_rag_function
from autogen import register_function

retrieve_config = {
    "task": "qa",
    "docs_path": "earnings_calls/",
    "collection_name": "earnings_collection",
    "chunk_token_size": 1000,
    "model": "gpt-4",
}

rag_func, rag_assistant = get_rag_function(
    retrieve_config,
    rag_description="Search earnings call transcripts"
)

# Register with agent
register_function(
    rag_func,
    caller=assistant.assistant,
    executor=assistant.user_proxy,
    description=rag_description,
)
```

**Configuration**:
- `task`: Task type ("qa", "code", etc.)
- `docs_path`: Directory containing documents
- `collection_name`: Vector database collection name
- `chunk_token_size`: Size of document chunks
- `model`: LLM model to use

**Returns**: 
- `rag_func`: Function to call for retrieval
- `rag_assistant`: Assistant agent for RAG

## ReportLab Module

### ReportLabUtils

PDF report generation utilities.

#### build_annual_report(content_dict, save_path)

Build formatted annual report PDF.

```python
from finrobot.functional import ReportLabUtils

content = {
    "title": "Annual Report 2023",
    "company": "Microsoft Corporation",
    "sections": [
        {"title": "Executive Summary", "content": "..."},
        {"title": "Financial Analysis", "content": "..."},
        # ... more sections
    ],
    "charts": ["charts/pe_ratio.png", "charts/eps.png"],
}

ReportLabUtils.build_annual_report(
    content,
    "report/annual_report_2023.pdf"
)
```

**Content Dictionary Structure**:
```python
{
    "title": "Report Title",
    "company": "Company Name",
    "sections": [
        {"title": "Section Title", "content": "Section content"},
    ],
    "charts": ["path/to/chart1.png", ...],
}
```

**Features**:
- Custom styling
- Multi-section layout
- Chart integration
- Professional formatting

### Usage Example

```python
# Generate analysis
income_analysis = ReportAnalysisUtils.analyze_income_stmt(...)
balance_analysis = ReportAnalysisUtils.analyze_balance_sheet(...)

# Create charts
ReportChartUtils.plot_pe_ratio(...)
ReportChartUtils.plot_eps(...)

# Build report
content = {
    "title": "Financial Analysis Report",
    "company": "Microsoft",
    "sections": [
        {"title": "Income Statement", "content": income_analysis},
        {"title": "Balance Sheet", "content": balance_analysis},
    ],
    "charts": ["charts/pe_ratio.png", "charts/eps.png"],
}

ReportLabUtils.build_annual_report(content, "report/analysis.pdf")
```

## Text Module

### TextUtils

Text processing utilities.

#### check_text_length(text)

Check if text meets length requirements.

```python
from finrobot.functional import TextUtils

result = TextUtils.check_text_length(
    "Your text content here..."
)
# Returns validation message
```

**Use Case**: Ensure report sections meet word count requirements.

### Usage Example

```python
# Validate text before including in report
text = "Your analysis text..."
validation = TextUtils.check_text_length(text)

if "valid" in validation.lower():
    # Include in report
    pass
```

## Module Integration Patterns

### Pattern 1: Analysis → Visualization → Report

```python
# 1. Analyze
income = ReportAnalysisUtils.analyze_income_stmt(...)

# 2. Visualize
ReportChartUtils.plot_pe_ratio(...)

# 3. Generate Report
ReportLabUtils.build_annual_report({
    "sections": [{"title": "Analysis", "content": income}],
    "charts": ["charts/pe_ratio.png"],
}, "report.pdf")
```

### Pattern 2: Data → Code → Execution

```python
# 1. Get data
data = YFinanceUtils.get_stock_data(...)

# 2. Agent writes analysis code
# (uses CodingUtils to create/modify files)

# 3. Code executes automatically
# (via UserProxyAgent)
```

### Pattern 3: RAG → Analysis → Report

```python
# 1. Set up RAG
rag_func, _ = get_rag_function(...)

# 2. Query documents
context = rag_func("What was Q4 revenue?")

# 3. Analyze with context
analysis = analyze_with_context(context)

# 4. Generate report
ReportLabUtils.build_annual_report(...)
```

## Best Practices

1. **Save Intermediate Results**: Use `save_path` parameters
2. **Validate Inputs**: Check data before processing
3. **Error Handling**: Handle file I/O errors
4. **Resource Cleanup**: Remove temporary files
5. **Chart Formatting**: Use consistent styles
6. **Report Structure**: Follow standard report formats

## Creating Custom Functional Modules

### Template

```python
from typing import Annotated
from ..data_source import YFinanceUtils

class MyFunctionalUtils:
    
    @staticmethod
    def my_analysis(
        symbol: Annotated[str, "Ticker symbol"],
        param: Annotated[str, "Parameter"],
    ) -> str:
        """
        Perform custom analysis.
        
        Returns:
            Analysis result as string
        """
        # Fetch data
        data = YFinanceUtils.get_stock_data(symbol, ...)
        
        # Perform analysis
        result = analyze(data, param)
        
        # Format output
        return format_result(result)
```

### Adding to Package

1. Create `finrobot/functional/my_module.py`
2. Add to `finrobot/functional/__init__.py`:

```python
from .my_module import MyFunctionalUtils
```

## Next Steps

- See [[04-Development-Guide]] for creating custom modules
- Read [[05-Data-Sources]] for data source integration
- Check `tutorials_advanced/` for advanced usage examples

