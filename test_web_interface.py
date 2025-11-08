#!/usr/bin/env python3
"""
Test script to verify web interface endpoints work correctly
"""
import requests
import json
import time

BASE_URL = "http://localhost:8250"

def test_comprehensive_analysis():
    """Test the comprehensive analysis endpoint"""
    print("Testing Comprehensive Analysis Endpoint...")
    print("=" * 60)
    
    test_data = {
        "ticker": "AAPL",
        "model": "gemini",
        "analysisType": "comprehensive",
        "riskReward": 2.0,
        "stopLossMethod": "atr",
        "period": "6mo",
        "stopLossPct": 2.0,
        "accountValue": 10000.0,
        "riskPerTrade": 1.0,
        "includeResearch": False  # Skip research for faster testing
    }
    
    try:
        print(f"Sending request to {BASE_URL}/comprehensive-analysis...")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/comprehensive-analysis",
            json=test_data,
            timeout=180  # 3 minutes timeout
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success', False)}")
            
            if data.get('success'):
                print(f"✓ Analysis completed successfully!")
                print(f"✓ Session ID: {data.get('session_id', 'Not provided')}")
                result = data.get('result', '')
                print(f"✓ Result length: {len(result)} characters")
                print(f"\nFirst 500 characters of result:")
                print("-" * 60)
                print(result[:500])
                print("-" * 60)
                
                # Check if session_id is present
                if data.get('session_id'):
                    print("\n✓ Session ID is present - Chat should be enabled!")
                else:
                    print("\n⚠ Warning: Session ID not found - Chat may not work!")
            else:
                print(f"✗ Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"✗ HTTP Error {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out (analysis taking too long)")
    except requests.exceptions.ConnectionError:
        print("✗ Connection error - Is the server running on port 8250?")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

def test_chat_endpoint():
    """Test the chat endpoint (requires a session)"""
    print("\n\nTesting Chat Endpoint...")
    print("=" * 60)
    print("Note: This requires running comprehensive analysis first to get a session_id")
    print("Skipping chat test - run comprehensive analysis first to get session_id")

if __name__ == "__main__":
    print("FinRobot Web Interface Test")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}\n")
    
    # Test comprehensive analysis
    test_comprehensive_analysis()
    
    # Note about chat
    test_chat_endpoint()
    
    print("\n" + "=" * 60)
    print("Test completed!")

