# FinRobot Documentation

Welcome to the FinRobot documentation! This comprehensive guide will help you understand, develop, test, and deploy FinRobot applications.

## Documentation Index

### Getting Started
- [[00-Project-Overview]] - Introduction to FinRobot, architecture, and key concepts
- [[01-Getting-Started]] - Installation, setup, and your first agent

### Core Documentation
- [[02-Architecture]] - Detailed system architecture and component design
- [[03-Agent-Workflows]] - Agent workflow patterns and when to use them
- [[04-Development-Guide]] - Creating custom agents, tools, and modules

### Reference Guides
- [[05-Data-Sources]] - All available data sources and how to use them
- [[06-Functional-Modules]] - Functional modules for analysis, visualization, and reporting
- [[07-Testing-Guide]] - Testing strategies, examples, and best practices
- [[08-Deployment-Guide]] - Deployment options, configuration, and production considerations

## Quick Start

1. **New to FinRobot?** Start with [[00-Project-Overview]] and [[01-Getting-Started]]
2. **Want to understand the system?** Read [[02-Architecture]]
3. **Ready to build?** Check [[04-Development-Guide]]
4. **Need reference?** See [[05-Data-Sources]] and [[06-Functional-Modules]]

## Documentation Structure

```
docs/
├── README.md                    # This file
├── 00-Project-Overview.md       # Introduction and overview
├── 01-Getting-Started.md        # Setup and installation
├── 02-Architecture.md           # System architecture
├── 03-Agent-Workflows.md        # Workflow patterns
├── 04-Development-Guide.md     # Development practices
├── 05-Data-Sources.md           # Data source reference
├── 06-Functional-Modules.md     # Functional module reference
├── 07-Testing-Guide.md          # Testing guide
└── 08-Deployment-Guide.md       # Deployment guide
```

## Key Concepts

### AI Agents
AI Agents in FinRobot are intelligent entities that:
- Use LLMs as their "brain"
- Perceive financial data from multiple sources
- Make decisions and execute actions
- Work independently or collaboratively

### Workflow Patterns
- **SingleAssistant**: Simple single-agent workflows
- **SingleAssistantRAG**: Document analysis with RAG
- **SingleAssistantShadow**: Self-reflection and quality assurance
- **MultiAssistant**: Collaborative multi-agent workflows
- **MultiAssistantWithLeader**: Hierarchical leader-worker pattern

### Data Sources
- **FinnHub**: Market data, news, company profiles
- **Yahoo Finance**: Stock prices, financial statements
- **Financial Modeling Prep**: SEC filings, financial data
- **SEC API**: SEC filing retrieval and parsing

### Functional Modules
- **Analyzer**: Financial statement analysis
- **Charting**: Stock charts and visualizations
- **Coding**: Code execution utilities
- **Quantitative**: Backtesting and quantitative analysis
- **RAG**: Retrieval-Augmented Generation
- **ReportLab**: PDF report generation

## Common Tasks

### Running Your First Agent

```python
from finrobot.agents.workflow import SingleAssistant
import autogen

llm_config = {
    "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST"),
}

assistant = SingleAssistant("Market_Analyst", llm_config)
assistant.chat("Analyze AAPL stock")
```

### Creating a Custom Agent

```python
custom_agent = {
    "name": "My_Analyst",
    "profile": "You are a custom financial analyst...",
    "toolkits": [MyCustomTool.function],
}

assistant = SingleAssistant(custom_agent, llm_config)
```

### Adding a New Tool

```python
from typing import Annotated

def my_tool(
    param: Annotated[str, "Parameter description"]
) -> str:
    """Tool description"""
    return "result"

# Register in agent
agent_config = {
    "toolkits": [my_tool],
}
```

## Resources

### Tutorials
- **Beginner**: `tutorials_beginner/` - Start here if you're new
- **Advanced**: `tutorials_advanced/` - Advanced patterns and techniques

### Examples
- **Experiments**: `experiments/` - Real-world use cases
- **Demos**: See README.md for demo examples

### Community
- **Discord**: [Join the FinRobot Discord](https://discord.gg/trsr8SXpW5)
- **GitHub**: [FinRobot Repository](https://github.com/AI4Finance-Foundation/FinRobot)
- **Issues**: Report bugs or ask questions on GitHub

## Contributing

See [[04-Development-Guide]] for:
- Code style guidelines
- Testing requirements
- Contribution process
- Best practices

## Support

- **Documentation Issues**: Open an issue on GitHub
- **Questions**: Ask on Discord or GitHub Discussions
- **Bugs**: Report on GitHub Issues

## License

FinRobot is released under the Apache-2.0 license. See LICENSE file for details.

---

**Note**: This documentation is designed for Obsidian. The `[[links]]` format creates internal links between documents. If viewing in a different system, you may need to adjust the links.

