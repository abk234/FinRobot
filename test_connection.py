#!/usr/bin/env python3
"""
Simple test script to diagnose connection issues
"""
import json
import sys
import warnings
warnings.filterwarnings("ignore")

print("Testing FinRobot Connection...")
print("=" * 60)

# Load config
try:
    with open('OAI_CONFIG_LIST') as f:
        config_list = json.load(f)
    print("✓ OAI_CONFIG_LIST loaded")
except Exception as e:
    print(f"✗ Error loading config: {e}")
    sys.exit(1)

# Check API key
api_key = config_list[0].get('api_key', '')
if not api_key or api_key.startswith('<'):
    print("✗ API key not configured")
    sys.exit(1)

print(f"✓ API key found (length: {len(api_key)})")

# Test with autogen
try:
    import autogen
    llm_config = {
        "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST"),
        "timeout": 30,
    }
    print("✓ LLM config created")
    
    # Try a simple test
    print("\nTesting API connection...")
    test_config = {
        "config_list": [config_list[0]],
        "timeout": 30,
    }
    
    # Create wrapper
    wrapper = autogen.oai.OpenAIWrapper(**test_config)
    print("✓ OpenAIWrapper created")
    
    # Try a minimal API call
    print("\nAttempting test API call...")
    response = wrapper.create(
        messages=[{"role": "user", "content": "Say 'test'"}],
        model="gpt-4-0125-preview",
        max_tokens=5,
    )
    print("✓ API call successful!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    error_type = type(e).__name__
    error_msg = str(e)
    print(f"\n✗ Error: {error_type}")
    print(f"  Message: {error_msg}")
    
    if "Bad file descriptor" in error_msg or "Errno 9" in error_msg:
        print("\n  This appears to be a system-level networking issue.")
        print("  Possible causes:")
        print("  - Python environment issue")
        print("  - SSL/TLS library conflict")
        print("  - System resource limits")
        print("\n  Try:")
        print("  1. Restart your terminal")
        print("  2. Recreate virtual environment")
        print("  3. Check system logs")
    elif "Connection" in error_msg:
        print("\n  Network connectivity issue detected.")
    elif "401" in error_msg or "authentication" in error_msg.lower():
        print("\n  API key authentication failed.")
        print("  Verify your API key is valid.")
    else:
        print(f"\n  Unexpected error: {error_type}")

