# FinRobot Architecture

This document provides a detailed overview of FinRobot's architecture, components, and how they interact.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              Application Layer (Your Code)               │
│  SingleAssistant | MultiAssistant | Custom Agents       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Agent Workflow Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ FinRobot     │  │ SingleAsst   │  │ MultiAsst    │  │
│  │ (Base Agent) │  │ (Workflow)   │  │ (Workflow)   │  │
│  └──────┬───────┘  └──────┬────────┘  └──────┬───────┘  │
│         │                │                    │          │
│  ┌──────▼────────────────▼────────────────────▼──────┐  │
│  │         AutoGen Framework (Microsoft)            │  │
│  │  AssistantAgent | UserProxyAgent | GroupChat    │  │
│  └──────────────────────┬──────────────────────────┘  │
└──────────────────────────┼──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│              Toolkit Registration Layer                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Data Sources │  │ Functional   │  │ Custom Tools │  │
│  │   Utils      │  │   Modules    │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Agent Layer (`finrobot/agents/`)

#### 1.1 FinRobot Class (`workflow.py`)

The base agent class that extends AutoGen's `AssistantAgent`.

**Key Features:**
- Loads agent configurations from library or custom dict
- Registers toolkits automatically
- Preprocesses system prompts with role/responsibility templates
- Supports shadow agents for reflection

**Key Methods:**
```python
class FinRobot(AssistantAgent):
    def __init__(agent_config, system_message, toolkits, proxy, **kwargs)
    def register_proxy(proxy)  # Register tools with proxy
    def _preprocess_config(config)  # Format prompts
```

#### 1.2 SingleAssistant (`workflow.py`)

Simplest workflow: one agent + one user proxy.

**Use Cases:**
- Simple analysis tasks
- Single-agent workflows
- Quick prototypes

**Example:**
```python
assistant = SingleAssistant("Market_Analyst", llm_config)
assistant.chat("Analyze AAPL stock")
```

#### 1.3 SingleAssistantRAG (`workflow.py`)

Single agent with RAG (Retrieval-Augmented Generation) capabilities.

**Use Cases:**
- Document analysis
- Earnings call Q&A
- SEC filing analysis

**Features:**
- Integrates with retrieval system
- Can query document databases
- Enhanced context for LLM

#### 1.4 SingleAssistantShadow (`workflow.py`)

Single agent with a shadow agent for self-reflection.

**Use Cases:**
- Complex analysis requiring self-review
- Quality assurance
- Multi-step reasoning

**How it works:**
- Main agent performs tasks
- Shadow agent reviews and provides feedback
- Uses nested chats for communication

#### 1.5 MultiAssistant (`workflow.py`)

Multiple agents working together in a group chat.

**Use Cases:**
- Complex multi-step analysis
- Collaborative problem solving
- Division of labor

**Features:**
- GroupChatManager orchestrates conversations
- Custom speaker selection
- Agents can call each other

#### 1.6 MultiAssistantWithLeader (`workflow.py`)

Hierarchical structure with a leader agent delegating to worker agents.

**Use Cases:**
- Structured workflows
- Task delegation
- Coordinated analysis

**Structure:**
```
Leader Agent
  ├── Agent 1 (via nested chat)
  ├── Agent 2 (via nested chat)
  └── Agent 3 (via nested chat)
```

### 2. Agent Library (`agent_library.py`)

Pre-defined agent configurations with:
- **Name**: Unique identifier
- **Profile**: System message/role description
- **Toolkits**: List of tools available to the agent
- **Description**: Human-readable description

**Available Agents:**
- `Market_Analyst`: Market analysis and predictions
- `Expert_Investor`: Financial report generation
- `Financial_Analyst`: Financial data analysis
- `Software_Developer`: Code writing and execution
- `Data_Analyst`: Data analysis tasks
- And more...

**Adding Custom Agents:**
```python
custom_agent = {
    "name": "My_Custom_Agent",
    "profile": "You are a custom agent that...",
    "toolkits": [MyCustomTool.function1, MyCustomTool.function2],
}
```

### 3. Toolkit System (`toolkits.py`)

Registers functions as tools that agents can use.

#### 3.1 register_toolkits()

Main function for registering tools.

**Supports:**
- Functions: `register_toolkits([my_function], caller, executor)`
- Classes: `register_toolkits([MyClass], caller, executor)`
- Dictionaries: `register_toolkits([{"function": func, "name": "custom_name"}], ...)`

#### 3.2 Tool Registration Flow

```
Tool Function → stringify_output() → register_function() → AutoGen
```

**stringify_output()**: Converts pandas DataFrames to strings for LLM consumption.

### 4. Data Source Layer (`finrobot/data_source/`)

Wrapper classes for financial data APIs.

#### 4.1 FinnHubUtils

**Methods:**
- `get_company_profile(symbol)`: Company information
- `get_company_news(symbol)`: Recent news
- `get_basic_financials(symbol)`: Financial metrics

**Initialization:**
- Requires `FINNHUB_API_KEY` environment variable
- Auto-initializes client on first use

#### 4.2 YFinanceUtils

**Methods:**
- `get_stock_data(symbol, start_date, end_date)`: Historical prices
- `get_income_stmt(symbol)`: Income statement
- `get_balance_sheet(symbol)`: Balance sheet
- `get_cash_flow(symbol)`: Cash flow statement
- `get_company_info(symbol)`: Company information

**Features:**
- Uses `@decorate_all_methods(init_ticker)` pattern
- Automatically initializes yf.Ticker

#### 4.3 FMPUtils (Financial Modeling Prep)

**Methods:**
- `get_sec_report(ticker, report_type, year)`: SEC filing URLs
- Financial data retrieval

#### 4.4 SECUtils

**Methods:**
- `get_10k_section(ticker, year, section)`: Extract 10-K sections
- SEC filing processing

#### 4.5 RedditUtils

**Methods:**
- Reddit data retrieval for sentiment analysis

### 5. Functional Modules (`finrobot/functional/`)

#### 5.1 Analyzer (`analyzer.py`)

**ReportAnalysisUtils**: Financial statement analysis

**Methods:**
- `analyze_income_stmt(ticker, fyear, save_path)`
- `analyze_balance_sheet(ticker, fyear, save_path)`
- `analyze_cash_flow(ticker, fyear, save_path)`

**Workflow:**
1. Retrieves financial statement
2. Gets relevant 10-K section
3. Combines with analysis instructions
4. Saves to file for LLM processing

#### 5.2 Charting (`charting.py`)

**MplFinanceUtils**: Stock chart generation
- `plot_stock_price_chart()`: Candlestick/OHLC charts
- `plot_technical_indicators()`: Technical analysis charts

**ReportChartUtils**: Report-specific charts
- `plot_pe_ratio()`: P/E ratio visualization
- `plot_eps()`: Earnings per share charts

#### 5.3 Coding (`coding.py`)

**CodingUtils**: Code manipulation tools
- `list_dir(path)`: List directory contents
- `see_file(path)`: Read file contents
- `modify_code(old, new, file_path)`: Replace code
- `create_file_with_code(code, file_path)`: Create files

**IPythonUtils**: IPython integration
- `display_image(path)`: Display images in notebooks

#### 5.4 Quantitative (`quantitative.py`)

**BackTraderUtils**: Backtesting framework
- Strategy backtesting
- Performance analysis

#### 5.5 RAG (`rag.py`)

**get_rag_function()**: Sets up RAG capabilities
- Document retrieval
- Vector database integration
- Context injection

#### 5.6 ReportLab (`reportlab.py`)

**ReportLabUtils**: PDF report generation
- `build_annual_report()`: Creates formatted PDF reports
- Custom styling and layout

#### 5.7 Text (`text.py`)

**TextUtils**: Text processing
- `check_text_length(text)`: Validate text length
- Text formatting utilities

## Data Flow

### Single Agent Workflow

```
User Message
    ↓
UserProxyAgent (receives message)
    ↓
AssistantAgent (processes with LLM)
    ↓
Tool Call (if needed)
    ↓
UserProxyAgent (executes tool)
    ↓
Tool Result
    ↓
AssistantAgent (processes result)
    ↓
Response (or next tool call)
    ↓
TERMINATE (when done)
```

### Multi-Agent Workflow

```
User Message
    ↓
GroupChatManager
    ↓
Select Next Speaker (custom logic)
    ↓
Agent 1 → Tool Call → Result
    ↓
Agent 2 → Analysis → Result
    ↓
Agent 3 → Synthesis → Final Response
    ↓
TERMINATE
```

### Leader-Worker Workflow

```
User Message
    ↓
Leader Agent (receives task)
    ↓
Leader analyzes → Delegates to Worker 1
    ↓
Nested Chat: Leader → Worker 1
    ↓
Worker 1 Result
    ↓
Leader synthesizes → Delegates to Worker 2
    ↓
...
    ↓
Leader generates final response
```

## Configuration System

### LLM Configuration

```python
llm_config = {
    "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST"),
    "timeout": 120,
    "temperature": 0,
}
```

### Agent Configuration

```python
agent_config = {
    "name": "Agent_Name",
    "profile": "System message...",
    "toolkits": [function1, function2, Class1],
    "description": "Human-readable description",
}
```

### Code Execution Configuration

```python
code_execution_config = {
    "work_dir": "coding",
    "use_docker": False,
}
```

## Extension Points

### Adding New Data Sources

1. Create utility class in `data_source/`
2. Use `@decorate_all_methods()` if needed
3. Add to `data_source/__init__.py`
4. Register in agent toolkits

### Adding New Functional Modules

1. Create module in `functional/`
2. Define utility class with static methods
3. Add type annotations for AutoGen
4. Export in `functional/__init__.py`

### Creating Custom Agents

1. Define agent config (name, profile, toolkits)
2. Add to agent library or use directly
3. Create workflow instance
4. Use in your application

## Best Practices

1. **Type Annotations**: Always use `Annotated` types for tool parameters
2. **Error Handling**: Wrap API calls in try-except blocks
3. **Caching**: Use `use_cache=True` for expensive operations
4. **Resource Management**: Clean up files and connections
5. **Documentation**: Document all tool functions with docstrings

## Next Steps

- See [[03-Agent-Workflows]] for workflow patterns
- Read [[04-Development-Guide]] for development practices
- Check [[05-Data-Sources]] for data source details
- Review [[06-Functional-Modules]] for functional module usage

