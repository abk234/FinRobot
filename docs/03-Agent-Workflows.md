# Agent Workflows and Patterns

This guide explains the different agent workflow patterns available in FinRobot and when to use each one.

## Workflow Types Overview

FinRobot provides several workflow patterns:

1. **SingleAssistant**: Single agent with user proxy
2. **SingleAssistantRAG**: Single agent with RAG capabilities
3. **SingleAssistantShadow**: Single agent with self-reflection
4. **MultiAssistant**: Multiple agents in group chat
5. **MultiAssistantWithLeader**: Hierarchical leader-worker pattern

## 1. SingleAssistant

The simplest workflow pattern - one agent working with a user proxy.

### When to Use

- Simple, straightforward tasks
- Single-step analysis
- Quick prototypes
- Tasks that don't require collaboration

### Example: Market Analysis

```python
from finrobot.agents.workflow import SingleAssistant
import autogen

llm_config = {
    "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST"),
    "temperature": 0,
}

assistant = SingleAssistant(
    "Market_Analyst",
    llm_config,
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
)

assistant.chat("Analyze AAPL stock and predict next week's movement")
```

### Configuration Options

```python
SingleAssistant(
    agent_config,              # Agent name or config dict
    llm_config,                # LLM configuration
    is_termination_msg=...,    # Custom termination condition
    human_input_mode="NEVER",  # "NEVER", "ALWAYS", "TERMINATE"
    max_consecutive_auto_reply=10,  # Max auto-replies
    code_execution_config={...},   # Code execution settings
)
```

### Termination

By default, agents terminate when they output "TERMINATE". You can customize:

```python
def custom_termination(msg):
    return "DONE" in msg.get("content", "")

assistant = SingleAssistant(
    "Market_Analyst",
    llm_config,
    is_termination_msg=custom_termination,
)
```

## 2. SingleAssistantRAG

Single agent enhanced with Retrieval-Augmented Generation for document analysis.

### When to Use

- Document Q&A
- Earnings call analysis
- SEC filing analysis
- Any task requiring document retrieval

### Example: Earnings Call Analysis

```python
from finrobot.agents.workflow import SingleAssistantRAG
import autogen

llm_config = {
    "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST"),
    "temperature": 0,
}

retrieve_config = {
    "task": "qa",
    "docs_path": "earnings_calls/",
    "collection_name": "earnings_calls_collection",
}

assistant = SingleAssistantRAG(
    "Financial_Analyst",
    llm_config,
    retrieve_config=retrieve_config,
    rag_description="Search earnings call transcripts for information",
)

assistant.chat("What did the CEO say about Q4 revenue guidance?")
```

### RAG Configuration

```python
retrieve_config = {
    "task": "qa",                    # Task type
    "docs_path": "path/to/docs",    # Document directory
    "collection_name": "my_collection",  # Vector DB collection
    "chunk_token_size": 1000,        # Chunk size
    "model": "gpt-4",                # Embedding model
}
```

### How RAG Works

1. User asks question
2. RAG function searches document database
3. Retrieves relevant chunks
4. Injects context into LLM prompt
5. LLM generates answer with context

## 3. SingleAssistantShadow

Single agent with a shadow agent for self-reflection and quality assurance.

### When to Use

- Complex analysis requiring review
- Quality-critical tasks
- Multi-step reasoning
- Tasks needing self-correction

### Example: Report Generation with Review

```python
from finrobot.agents.workflow import SingleAssistantShadow
import autogen

llm_config = {
    "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST"),
    "temperature": 0.5,
}

assistant = SingleAssistantShadow(
    "Expert_Investor",
    llm_config,
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=None,  # No limit
)

assistant.chat(
    "Write an annual report for Microsoft 2023. "
    "Review each section before finalizing.",
    max_turns=50,
)
```

### How Shadow Works

1. Main agent performs task
2. Shadow agent reviews output
3. Shadow provides feedback via nested chat
4. Main agent incorporates feedback
5. Process repeats until quality threshold

### Shadow Agent Behavior

- Shadow agent has NO tools (toolkits=[])
- Only provides feedback and suggestions
- Uses reflection prompts
- Silent by default (summary_method="last_msg")

## 4. MultiAssistant

Multiple agents collaborating in a group chat.

### When to Use

- Complex multi-step tasks
- Division of labor
- Collaborative problem solving
- Tasks requiring different expertise

### Example: Investment Analysis Team

```python
from finrobot.agents.workflow import MultiAssistant
import autogen

llm_config = {
    "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST"),
    "temperature": 0,
}

group_config = {
    "name": "Investment_Team",
    "agents": [
        "Financial_Analyst",
        "Data_Analyst",
        "Statistician",
    ],
}

team = MultiAssistant(
    group_config,
    llm_config=llm_config,
    human_input_mode="NEVER",
)

team.chat(
    "Analyze NVDA stock from multiple perspectives: "
    "financial metrics, statistical trends, and market sentiment. "
    "Provide a comprehensive investment recommendation."
)
```

### Custom Agent Configurations

```python
group_config = {
    "name": "Custom_Team",
    "agents": [
        {
            "name": "Analyst_1",
            "profile": "You are a financial analyst specializing in tech stocks...",
            "toolkits": [FinnHubUtils.get_company_profile],
        },
        {
            "name": "Analyst_2",
            "profile": "You are a quantitative analyst...",
            "toolkits": [YFinanceUtils.get_stock_data],
        },
    ],
}
```

### Speaker Selection

The default speaker selection logic:
1. First message: First agent
2. After user message: Last agent who spoke
3. After tool call: User proxy
4. Otherwise: Next agent in rotation

You can customize this in `MultiAssistant._get_representative()`.

## 5. MultiAssistantWithLeader

Hierarchical structure with a leader delegating to workers.

### When to Use

- Structured workflows
- Task delegation
- Coordinated analysis
- Clear hierarchy needed

### Example: Research Team with Manager

```python
from finrobot.agents.workflow import MultiAssistantWithLeader
import autogen

llm_config = {
    "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST"),
    "temperature": 0,
}

group_config = {
    "leader": {
        "title": "Research_Manager",
        "responsibilities": [
            "Coordinate research team",
            "Synthesize findings",
            "Generate final report",
        ],
    },
    "agents": [
        {
            "title": "Financial_Analyst",
            "responsibilities": [
                "Analyze financial statements",
                "Calculate financial ratios",
            ],
        },
        {
            "title": "Market_Researcher",
            "responsibilities": [
                "Research market trends",
                "Analyze competitor data",
            ],
        },
    ],
}

team = MultiAssistantWithLeader(
    group_config,
    llm_config=llm_config,
)

team.chat(
    "Conduct a comprehensive analysis of AAPL. "
    "The Financial Analyst should analyze financials, "
    "and the Market Researcher should analyze market position. "
    "The Research Manager should synthesize everything into a report."
)
```

### Leader-Worker Communication

The leader communicates with workers via nested chats:

```python
# Leader triggers worker with pattern: [Worker_Name]
# Example: "[Financial_Analyst] Analyze the income statement"
```

### Nested Chat Configuration

```python
{
    "sender": user_proxy,
    "recipient": worker_agent,
    "message": order_message,           # Message formatter
    "summary_method": "reflection_with_llm",  # How to summarize
    "max_turns": 10,                    # Max conversation turns
    "max_consecutive_auto_reply": 3,    # Max auto-replies
}
```

## Workflow Comparison

| Pattern | Complexity | Use Case | Collaboration |
|---------|-----------|----------|---------------|
| SingleAssistant | Low | Simple tasks | None |
| SingleAssistantRAG | Medium | Document analysis | None |
| SingleAssistantShadow | Medium | Quality-critical | Self-reflection |
| MultiAssistant | High | Complex tasks | Peer-to-peer |
| MultiAssistantWithLeader | High | Structured workflows | Hierarchical |

## Advanced Patterns

### Pattern 1: Sequential Workflow

Use multiple SingleAssistant instances in sequence:

```python
# Step 1: Data collection
data_agent = SingleAssistant("Data_Analyst", llm_config)
data_agent.chat("Collect AAPL stock data for last year")

# Step 2: Analysis
analysis_agent = SingleAssistant("Financial_Analyst", llm_config)
analysis_agent.chat("Analyze the collected data")

# Step 3: Reporting
report_agent = SingleAssistant("Expert_Investor", llm_config)
report_agent.chat("Generate report from analysis")
```

### Pattern 2: Conditional Workflow

Use human input mode to add conditionals:

```python
assistant = SingleAssistant(
    "Market_Analyst",
    llm_config,
    human_input_mode="TERMINATE",  # Ask before finishing
)

# Human can review and provide feedback before termination
```

### Pattern 3: Caching for Performance

Use caching to speed up repeated queries:

```python
assistant.chat("Analyze AAPL", use_cache=True)
```

### Pattern 4: Custom Termination

Implement custom termination logic:

```python
def is_complete(msg):
    content = msg.get("content", "")
    return (
        "TERMINATE" in content or
        "Analysis complete" in content or
        len(content) > 5000  # Very long response
    )

assistant = SingleAssistant(
    "Market_Analyst",
    llm_config,
    is_termination_msg=is_complete,
)
```

## Best Practices

1. **Choose the Right Pattern**: Match workflow complexity to task complexity
2. **Set Appropriate Limits**: Use `max_consecutive_auto_reply` to prevent loops
3. **Use Caching**: Enable caching for expensive operations
4. **Monitor Costs**: Track API usage, especially with multi-agent setups
5. **Error Handling**: Wrap agent calls in try-except blocks
6. **Logging**: Enable logging to debug agent conversations
7. **Resource Cleanup**: Reset agents between tasks

## Debugging Workflows

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Agent Messages

```python
# After chat completes
print(assistant.assistant.chat_messages)
print(assistant.user_proxy.chat_messages)
```

### Check Tool Calls

```python
# Messages include tool_calls
for msg in assistant.assistant.chat_messages[assistant.user_proxy]:
    if "tool_calls" in msg:
        print(msg["tool_calls"])
```

## Next Steps

- See [[04-Development-Guide]] for creating custom workflows
- Read [[02-Architecture]] for system architecture details
- Check examples in `tutorials_advanced/` for real-world patterns

