# Updating Notebooks to Use New AutoGen API

## Deprecation Warning

AutoGen has deprecated `autogen.config_list_from_json()` in favor of `autogen.LLMConfig.from_json()`.

## How to Update Notebooks

### Old Code (Deprecated):
```python
llm_config = {
    "config_list": autogen.config_list_from_json(
        "../OAI_CONFIG_LIST",
        filter_dict={"model": ["gpt-4o"]},
    ),
    "timeout": 120,
    "temperature": 0,
}
```

### New Code (Recommended):
```python
# Use new LLMConfig API
llm_config_obj = autogen.LLMConfig.from_json(
    path="../OAI_CONFIG_LIST",
    filter_dict={"model": ["gpt-4o"]},
)
llm_config = {
    "config_list": llm_config_obj.config_list,
    "timeout": 120,
    "temperature": 0,
}
```

## For Gemini Notebooks

### Old:
```python
llm_config = {
    "config_list": autogen.config_list_from_json(
        "../GEMINI_CONFIG_LIST",
        filter_dict={"model": ["gemini-2.5-flash"]},
    ),
    "timeout": 120,
    "temperature": 0,
}
```

### New:
```python
llm_config_obj = autogen.LLMConfig.from_json(
    path="../GEMINI_CONFIG_LIST",
    filter_dict={"model": ["gemini-2.5-flash"]},
)
llm_config = {
    "config_list": llm_config_obj.config_list,
    "timeout": 120,
    "temperature": 0,
}
```

## Quick Fix for All Notebooks

1. **Open the notebook** in Jupyter
2. **Find cells** with `autogen.config_list_from_json`
3. **Replace** with the new pattern above
4. **Run the cell** to verify it works

## Files Already Updated

✅ `start_demo.py` - Updated
✅ `start_demo_gemini.py` - Updated  
✅ `web_interface.py` - Updated

## Notebooks to Update

The following notebooks still use the old API:
- `tutorials_beginner/agent_fingpt_forecaster.ipynb`
- `tutorials_beginner/agent_annual_report.ipynb`
- `tutorials_beginner/agent_rag_qa.ipynb`
- `tutorials_beginner/agent_rag_qa_up.ipynb`
- `tutorials_advanced/agent_fingpt_forecaster.ipynb`
- `tutorials_advanced/agent_annual_report.ipynb`
- `tutorials_advanced/agent_trade_strategist.ipynb`
- `tutorials_advanced/lmm_agent_mplfinance.ipynb`
- `tutorials_advanced/lmm_agent_opt_smacross.ipynb`

## Why This Change?

- **Better type safety**: LLMConfig is a proper class
- **Future-proof**: Old API will be removed in AutoGen 0.11.0
- **No warnings**: Cleaner output without deprecation messages

## Testing

After updating, test by running the notebook cell. You should see:
- ✅ No deprecation warnings
- ✅ Same functionality
- ✅ Cleaner code

