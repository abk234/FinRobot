# FinnHub API Key Setup Guide

## Current Status

Your `config_api_keys` file currently has:
```json
{
    "FINNHUB_API_KEY": "YOUR_FINNHUB_API_KEY"
}
```

This is a placeholder - you need to add your actual API key.

## Is FinnHub Free?

**Yes!** FinnHub offers a **free tier** with generous limits:

### Free Tier Limits
- **60 API calls per minute**
- **Basic financial data access**
- **Company profiles**
- **Stock quotes**
- **Company news**
- **Basic financials**

**Note**: Some advanced features require paid plans, but the free tier is sufficient for most FinRobot use cases.

## How to Get Your Free FinnHub API Key

### Step 1: Sign Up
1. Go to: **https://finnhub.io/register**
2. Sign up with your email (or use Google/GitHub login)
3. Verify your email if required

### Step 2: Get Your API Key
1. After logging in, go to: **https://finnhub.io/dashboard**
2. You'll see your API key on the dashboard
3. Copy the API key (it looks like: `c1234567890abcdefghij`)

### Step 3: Add to Config
1. Open `config_api_keys` file
2. Replace `YOUR_FINNHUB_API_KEY` with your actual key:
   ```json
   {
       "FINNHUB_API_KEY": "c1234567890abcdefghij",
       "FMP_API_KEY": "YOUR_FMP_API_KEY",
       "SEC_API_KEY": "YOUR_SEC_API_KEY"
   }
   ```

## What FinnHub Provides

FinnHub gives FinRobot access to:
- ✅ **Company Profiles**: Company information, industry, market cap
- ✅ **Company News**: Recent news articles about companies
- ✅ **Basic Financials**: Key financial metrics
- ✅ **Stock Quotes**: Real-time and historical prices
- ✅ **Market Data**: Exchange information, market status

## Is It Required?

**No, FinnHub is optional!** FinRobot can work without it:
- ✅ **Yahoo Finance** (yfinance) works without API keys - already working!
- ✅ **Stock data** can be retrieved from Yahoo Finance
- ⚠️ **Company news** and **profiles** work better with FinnHub

## Current Status

Looking at your earlier run, you saw:
```
Error: FinnhubAPIException(status_code: 401): Invalid API key
```

This means:
- ✅ FinRobot is trying to use FinnHub
- ❌ The API key is not configured (or invalid)
- ✅ But **Yahoo Finance is working** - you got stock data successfully!

## Recommendation

1. **Get a free FinnHub key** (takes 2 minutes)
2. **Add it to `config_api_keys`**
3. **You'll get richer data** (news, company profiles, etc.)

But you can also **continue without it** - FinRobot works fine with just Yahoo Finance!

## Quick Setup

```bash
# 1. Get key from https://finnhub.io/register
# 2. Edit config_api_keys
# 3. Replace YOUR_FINNHUB_API_KEY with your actual key
# 4. Restart the application
```

## Free Tier Details

- **No credit card required**
- **No billing setup needed**
- **60 calls/minute** (plenty for personal use)
- **Basic features** (sufficient for FinRobot)

## Next Steps

1. Visit: https://finnhub.io/register
2. Sign up (free)
3. Copy your API key from dashboard
4. Update `config_api_keys` file
5. Restart your application

That's it! 🚀

