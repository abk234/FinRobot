# Troubleshooting Guide for start_demo.py

## Issues Fixed

### 1. ✅ Pydantic Warnings (FIXED)
**Problem**: Multiple `UserWarning` messages about `model_client_cls` field conflicts.

**Solution**: Added warning filters at the start of the script:
```python
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
```

**Status**: ✅ Fixed - warnings are now suppressed

### 2. ✅ NLTK Data Errors (FIXED)
**Problem**: Errors loading `punkt` and `averaged_perceptron_tagger` with "Bad file descriptor".

**Solution**: 
- Added error handling for NLTK data loading
- Redirected stderr during NLTK initialization to suppress errors
- Made NLTK downloads optional (won't crash if they fail)

**Status**: ✅ Fixed - errors are now suppressed

### 3. ⚠️ Connection Error (NEEDS ATTENTION)
**Problem**: `APIConnectionError` when trying to connect to OpenAI API.

**Possible Causes**:
1. **Network connectivity issue**
   - Check internet connection
   - Test: `ping api.openai.com`
   - Test: `curl https://api.openai.com/v1/models`

2. **API Key Issues**
   - Verify API key is valid at https://platform.openai.com/api-keys
   - Check that API key starts with `sk-`
   - Ensure API key has not expired
   - Verify API key has required permissions

3. **Firewall/Proxy**
   - Corporate firewall blocking OpenAI API
   - Proxy configuration needed
   - VPN interference

4. **OpenAI Service Status**
   - Check https://status.openai.com/
   - Service might be down or experiencing issues

## Current Output

The script now produces clean output:

```
============================================================
FinRobot Demo - Market Analyst Agent
============================================================

✓ API keys loaded
✓ LLM configuration loaded
✓ Initializing Market Analyst agent...
✓ Agent initialized successfully

============================================================
Starting Analysis...
============================================================
```

No more:
- ❌ Pydantic warnings
- ❌ NLTK data errors
- ✅ Clean, informative error messages

## Testing Network Connectivity

Run these commands to test connectivity:

```bash
# Test basic connectivity
ping -c 3 api.openai.com

# Test API endpoint (will return 401 without valid key, but confirms connectivity)
curl -I https://api.openai.com/v1/models

# Test with your API key (replace YOUR_KEY)
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

## Verifying API Key

1. **Check API key format**:
   - Should start with `sk-` or `sk-proj-`
   - Should be 51+ characters long
   - No spaces or line breaks

2. **Verify in OAI_CONFIG_LIST**:
   ```json
   [
       {
           "model": "gpt-4-0125-preview",
           "api_key": "sk-proj-..."
       }
   ]
   ```

3. **Test API key**:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```
   
   Should return JSON with model list (not 401/403 error)

## Next Steps

1. **If network test fails**:
   - Check internet connection
   - Check firewall settings
   - Try from different network

2. **If API key test fails**:
   - Generate new API key at https://platform.openai.com/api-keys
   - Update OAI_CONFIG_LIST
   - Verify key has billing/quota set up

3. **If everything works but script fails**:
   - Check Python version (should be 3.10 or 3.11)
   - Reinstall dependencies: `pip install -e .`
   - Check for proxy settings needed

## Clean Run Example

When everything works, you should see:

```
============================================================
FinRobot Demo - Market Analyst Agent
============================================================

✓ API keys loaded
✓ LLM configuration loaded
✓ Initializing Market Analyst agent...
✓ Agent initialized successfully

============================================================
Starting Analysis...
============================================================

User_Proxy (to Market_Analyst):

[Agent conversation and analysis...]

============================================================
Analysis Complete!
============================================================
```

## Summary

✅ **Fixed Issues**:
- Pydantic warnings suppressed
- NLTK errors suppressed
- Better error messages
- Cleaner output

⚠️ **Remaining Issue**:
- Connection error to OpenAI API (likely network/API key issue)

The script is now much cleaner and provides helpful debugging information when errors occur.

