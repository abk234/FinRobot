#!/usr/bin/env python3
"""
Simple FinRobot Demo - Market Analyst Agent

This script demonstrates a basic FinRobot agent that analyzes a stock
and provides market insights.
"""

import warnings
import sys
import os

# Suppress pydantic warnings (known issue with autogen)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Suppress NLTK download messages and errors
import nltk
import sys
from io import StringIO

# Redirect stderr temporarily to suppress NLTK errors
_stderr = sys.stderr
sys.stderr = StringIO()

try:
    nltk.data.find('tokenizers/punkt')
except (LookupError, OSError):
    try:
        nltk.download('punkt', quiet=True)
    except Exception:
        pass  # Will fail silently if network issue

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except (LookupError, OSError):
    try:
        nltk.download('averaged_perceptron_tagger', quiet=True)
    except Exception:
        pass  # Will fail silently if network issue

# Restore stderr
sys.stderr = _stderr

import autogen
from finrobot.utils import get_current_date, register_keys_from_json
from finrobot.agents.workflow import SingleAssistant

def main():
    print("=" * 60)
    print("FinRobot Demo - Market Analyst Agent")
    print("=" * 60)
    print()
    
    # Load API keys
    try:
        register_keys_from_json("config_api_keys")
        print("✓ API keys loaded")
    except Exception as e:
        print(f"⚠ Warning: Could not load API keys: {e}")
        print("  Continuing with OpenAI config only...")
    
    # Configure LLM
    try:
        # Use new LLMConfig API (replaces deprecated config_list_from_json)
        llm_config_obj = autogen.LLMConfig.from_json(
            path="OAI_CONFIG_LIST",
            filter_dict={"model": ["gpt-4o"]},
        )
        llm_config = {
            "config_list": llm_config_obj.config_list,
            "timeout": 120,
            "temperature": 0,
        }
        
        # Validate API key format
        if llm_config["config_list"]:
            api_key = llm_config["config_list"][0].get("api_key", "")
            if not api_key or api_key.startswith("<your") or len(api_key) < 20:
                print("✗ Error: Invalid or missing OpenAI API key in OAI_CONFIG_LIST")
                print("  Please update OAI_CONFIG_LIST with a valid API key")
                return
            if not api_key.startswith("sk-"):
                print("⚠ Warning: API key doesn't start with 'sk-'. It may not be a valid OpenAI key.")
        
        print("✓ LLM configuration loaded")
    except Exception as e:
        print(f"✗ Error loading LLM config: {e}")
        print("  Please ensure OAI_CONFIG_LIST file exists and is properly configured.")
        return
    
    # Create the agent
    print("✓ Initializing Market Analyst agent...")
    try:
        assistant = SingleAssistant(
            "Market_Analyst",
            llm_config,
            human_input_mode="NEVER",  # Set to "ALWAYS" for interactive mode
            max_consecutive_auto_reply=10,
        )
        print("✓ Agent initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing agent: {e}")
        print("  This might be due to:")
        print("  - Invalid API key format")
        print("  - Missing dependencies")
        print("  - Network connectivity issues")
        return
    
    # Run the agent
    print()
    print("=" * 60)
    print("Starting Analysis...")
    print("=" * 60)
    print()
    
    company = "AAPL"  # You can change this to any stock ticker
    
    message = (
        f"Use all the tools provided to retrieve information available for {company} "
        f"upon {get_current_date()}. Analyze the positive developments and potential "
        f"concerns of {company} with 2-4 most important factors respectively and keep "
        f"them concise. Most factors should be inferred from company related news. "
        f"Then make a rough prediction (e.g. up/down by 2-3%) of the {company} stock "
        f"price movement for next week. Provide a summary analysis to support your prediction."
    )
    
    try:
        assistant.chat(message)
        print()
        print("=" * 60)
        print("Analysis Complete!")
        print("=" * 60)
    except KeyboardInterrupt:
        print("\n\n⚠ Analysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"\n✗ Error during analysis: {error_msg}")
        print(f"  Error type: {error_type}")
        print("\n  Possible causes:")
        if "Connection" in error_msg or "timeout" in error_msg.lower() or "APIConnectionError" in error_type:
            print("  - Network connectivity issue")
            print("  - API endpoint unreachable")
            print("  - Firewall blocking connection")
            print("  - Check your internet connection")
            print("  - Try: ping api.openai.com")
        elif "API key" in error_msg or "authentication" in error_msg.lower() or "InvalidAPIKey" in error_type:
            print("  - Invalid or expired API key")
            print("  - API key doesn't have required permissions")
            print("  - Check OAI_CONFIG_LIST file")
        elif "rate limit" in error_msg.lower():
            print("  - API rate limit exceeded")
            print("  - Too many requests, please wait and try again")
        else:
            print("  - Check your API keys and network connection")
            print("  - Verify OpenAI service status")
            print(f"  - Unexpected error: {error_type}")
        
        # Additional debugging info
        print("\n  Debugging steps:")
        print("  1. Verify API key is valid at https://platform.openai.com/api-keys")
        print("  2. Check network: curl https://api.openai.com/v1/models")
        print("  3. Verify OAI_CONFIG_LIST has correct format")
        print(f"\n  Full error details: {error_type}: {error_msg}")

if __name__ == "__main__":
    # Redirect stderr to suppress warnings during execution
    # (warnings are already filtered, but this provides extra safety)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        main()
