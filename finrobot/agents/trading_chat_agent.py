"""
Trading Chat Agent for Interactive Stock Analysis

This module provides a specialized agent configuration for interactive trading conversations
that can explain technical analysis, generate charts, update parameters, and provide
comprehensive forecasting information.
"""

from finrobot.agents.workflow import SingleAssistant
from finrobot.functional.quantitative import TradingStrategyAnalyzer
from finrobot.functional.charting import MplFinanceUtils
from finrobot.toolkits import register_toolkits
from typing import Dict, Any
import autogen


def create_trading_chat_agent(
    llm_config: Dict[str, Any],
    ticker: str,
    analysis_params: Dict[str, Any],
    last_analysis: str = "",
    conversation_history: list = None
) -> SingleAssistant:
    """
    Create a trading chat agent with specialized configuration for interactive conversations.
    
    Args:
        llm_config: LLM configuration dictionary
        ticker: Current stock ticker being analyzed
        analysis_params: Current analysis parameters (risk_reward, stop_loss_method, etc.)
        last_analysis: Last comprehensive analysis results
        conversation_history: Previous conversation messages
    
    Returns:
        Configured SingleAssistant agent
    """
    
    # Build system prompt with context
    context_info = f"""
Current Analysis Context:
- Ticker Symbol: {ticker}
- Risk-Reward Ratio: {analysis_params.get('risk_reward', 2.0)}
- Stop Loss Method: {analysis_params.get('stop_loss_method', 'atr')}
- Analysis Period: {analysis_params.get('period', '6mo')}
- Account Value: ${analysis_params.get('account_value', 10000):,.2f}
- Risk per Trade: {analysis_params.get('risk_per_trade', 1.0)}%
"""
    
    if last_analysis:
        context_info += f"\nLast Analysis Summary:\n{last_analysis[:500]}...\n"
    
    system_prompt = f"""You are an expert Trading Analyst Assistant helping users understand stock analysis and make informed trading decisions.

{context_info}

Your capabilities:
1. Explain technical indicators in detail (RSI, MACD, Bollinger Bands, Moving Averages, etc.)
2. Perform additional technical analysis when requested
3. Generate trading charts with various indicators
4. Ask clarifying questions about risk tolerance, account size, investment goals
5. Provide comprehensive forecasting information
6. Suggest parameter improvements when appropriate (but always ask for confirmation)

Guidelines:
- Be conversational, friendly, and educational
- Explain complex concepts in simple terms
- When suggesting parameter changes, clearly explain WHY the change would be beneficial
- Always ask for user confirmation before making any parameter changes
- If asked to generate a chart, use the plot_stock_price_chart function
- When explaining technical analysis, provide both the "what" and "why"
- Help users understand risk management concepts
- Answer follow-up questions about the analysis results

Available Tools:
- comprehensive_analysis: Run full comprehensive analysis with current parameters
- analyze_trading_opportunity: Perform technical analysis only
- calculate_position_size: Calculate how many shares to buy
- plot_stock_price_chart: Generate trading charts with indicators

When the user asks questions, be thorough but concise. If they want more detail, provide it.
When suggesting improvements, explain the reasoning clearly.

Reply TERMINATE when the conversation is complete or the user indicates they're done.
"""
    
    # Create agent configuration
    agent_config = {
        "name": "Trading_Chat_Assistant",
        "profile": system_prompt,
        "toolkits": [
            TradingStrategyAnalyzer.comprehensive_analysis,
            TradingStrategyAnalyzer.analyze_trading_opportunity,
            TradingStrategyAnalyzer.calculate_position_size,
            MplFinanceUtils.plot_stock_price_chart,
        ]
    }
    
    # Create and configure agent
    assistant = SingleAssistant(
        agent_config,
        llm_config=llm_config,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=15,
    )
    
    # Register toolkits
    register_toolkits(
        agent_config["toolkits"],
        caller=assistant.assistant,
        executor=assistant.user_proxy,
    )
    
    return assistant


def process_chat_message(
    agent: SingleAssistant,
    message: str,
    use_cache: bool = False
) -> str:
    """
    Process a chat message through the trading agent.
    
    Args:
        agent: The trading chat agent
        message: User's message
        use_cache: Whether to use cached responses
    
    Returns:
        Agent's response text
    """
    from autogen.cache import Cache
    
    result_text = "I'm here to help with your trading analysis questions!"
    
    try:
        with Cache.disk() as cache:
            agent.user_proxy.initiate_chat(
                agent.assistant,
                message=message,
                cache=cache if use_cache else None,
            )
        
        # Get the last message from the assistant
        if agent.assistant.chat_messages.get(agent.user_proxy):
            messages = agent.assistant.chat_messages[agent.user_proxy]
            # Get the last message from the assistant
            for msg in reversed(messages):
                if msg.get("role") == "assistant" or agent.assistant.name in str(msg.get("name", "")):
                    result_text = msg.get("content", result_text)
                    break
            # If no assistant message found, get the last message
            if result_text == "I'm here to help with your trading analysis questions!" and messages:
                result_text = messages[-1].get("content", result_text)
        
        # Don't reset here - we want to maintain context across messages
        # The agent will maintain conversation history in its chat_messages
        
    except Exception as e:
        result_text = f"Error processing message: {str(e)}"
        try:
            agent.reset()
        except:
            pass
    
    return result_text

