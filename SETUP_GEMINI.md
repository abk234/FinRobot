# Setting Up Google Gemini for FinRobot

## Why Use Gemini?

- ✅ **No billing required** for free tier
- ✅ **Free API access** with generous limits
- ✅ **High-quality models** (Gemini 1.5 Pro, Flash)
- ✅ **Fast responses** with Gemini Flash

## Step 1: Get Your Gemini API Key

1. **Go to Google AI Studio**:
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with your Google account

2. **Create API Key**:
   - Click "Create API Key"
   - Select or create a Google Cloud project
   - Copy your API key

3. **Note**: Gemini API is free to use with generous rate limits!

## Step 2: Configure FinRobot

1. **Update GEMINI_CONFIG_LIST**:
   - Open `GEMINI_CONFIG_LIST` file
   - Replace `YOUR_GEMINI_API_KEY_HERE` with your actual API key

2. **Example**:
   ```json
   [
       {
           "model": "gemini-1.5-flash",
           "api_key": "YOUR_ACTUAL_API_KEY_HERE",
           "api_type": "google",
           "base_url": "https://generativelanguage.googleapis.com/v1beta"
       }
   ]
   ```

## Step 3: Run the Demo

```bash
cd /Users/lxupkzwjs/Developer/eval/FinRobot
source venv/bin/activate
python start_demo_gemini.py
```

## Available Gemini Models

- **gemini-1.5-flash**: Fast, efficient (recommended for quick responses)
- **gemini-1.5-pro**: More capable, better for complex tasks
- **gemini-2.0-flash-exp**: Experimental, latest features

## Comparison: OpenAI vs Gemini

| Feature | OpenAI | Gemini |
|---------|--------|--------|
| Billing Required | Yes | No (free tier) |
| Free Tier | Limited | Generous |
| Model Quality | Excellent | Excellent |
| Speed | Fast | Fast (Flash) |
| Setup | Complex | Simple |

## Troubleshooting

### Error: "Invalid API key"
- Check that you copied the full API key
- Verify the key is active in Google AI Studio
- Make sure there are no extra spaces

### Error: "Module not found"
```bash
pip install google-generativeai
```

### Error: "Rate limit exceeded"
- Wait a few minutes
- Gemini has generous free limits, but they reset periodically

## Benefits of Using Gemini

1. **No Credit Card Required**: Free tier is truly free
2. **Easy Setup**: Just get an API key and go
3. **Good Performance**: Gemini models are competitive with GPT-4
4. **Fast**: Gemini Flash is very fast for quick responses

## Next Steps

1. Get your API key from https://makersuite.google.com/app/apikey
2. Update `GEMINI_CONFIG_LIST` with your key
3. Run `python start_demo_gemini.py`
4. Enjoy free AI-powered financial analysis!

