# Complete API Keys Guide for FinRobot

## Overview

Your `config_api_keys` file contains 6 different API keys. Here's everything you need to know about each one:

## Current Status

✅ **FinnHub API Key**: Already configured! (`d47i62pr01qtk51q850gd47i62pr01qtk51q8510`)
❌ **FMP API Key**: Not configured (placeholder)
❌ **SEC API Key**: Not configured (placeholder)
❌ **Reddit Client ID**: Not configured (placeholder)
❌ **Reddit Client Secret**: Not configured (placeholder)
❌ **Twitter Bearer Token**: Not configured (placeholder)

---

## 1. FINNHUB_API_KEY ✅ (Already Set!)

### Status: **CONFIGURED** ✅

### Is it Free?
**YES!** Free tier available

### Free Tier Limits:
- **60 API calls per minute**
- **Basic financial data**
- **Company profiles**
- **Company news**
- **Stock quotes**
- **No credit card required**

### How to Get:
1. Go to: https://finnhub.io/register
2. Sign up (free)
3. Get API key from dashboard: https://finnhub.io/dashboard
4. Already done! ✅

### What It Provides:
- Company profiles and information
- Recent company news
- Basic financial metrics
- Market data

### Required?
**Optional** - FinRobot works without it (uses Yahoo Finance), but FinnHub provides richer data.

---

## 2. FMP_API_KEY (Financial Modeling Prep)

### Status: **NOT CONFIGURED** ❌

### Is it Free?
**YES!** Free tier available

### Free Tier Limits:
- **250 API calls per day**
- **Basic financial data**
- **Stock quotes**
- **Company profiles**
- **No credit card required**

### How to Get:
1. Go to: https://site.financialmodelingprep.com/developer/docs/
2. Sign up for free account
3. Get API key from dashboard
4. Add to `config_api_keys`:
   ```json
   "FMP_API_KEY": "your_actual_key_here"
   ```

### What It Provides:
- SEC filing URLs and dates
- Financial statements
- Company financial data
- Stock market data

### Required?
**Optional** - Only needed for SEC report retrieval features.

### Paid Plans:
- Free: 250 calls/day
- Starter: $14/month - 750 calls/day
- Professional: $29/month - Unlimited

---

## 3. SEC_API_KEY (SEC-API.com)

### Status: **NOT CONFIGURED** ❌

### Is it Free?
**Limited free tier** - Most features require paid plan

### Free Tier Limits:
- **Very limited** - Mostly for testing
- **Basic SEC filing access**
- **May require paid plan for production use**

### How to Get:
1. Go to: https://sec-api.io/
2. Sign up for account
3. Get API key from dashboard
4. Add to `config_api_keys`:
   ```json
   "SEC_API_KEY": "your_actual_key_here"
   ```

### What It Provides:
- SEC filing retrieval
- 10-K, 10-Q document parsing
- Section extraction from filings

### Required?
**Optional** - Only needed for advanced SEC filing analysis.

### Paid Plans:
- Free: Very limited
- Starter: $49/month
- Professional: $199/month

---

## 4. REDDIT_CLIENT_ID & REDDIT_CLIENT_SECRET

### Status: **NOT CONFIGURED** ❌

### Is it Free?
**YES!** Completely free

### Free Tier Limits:
- **60 requests per minute**
- **No daily limit**
- **No credit card required**

### How to Get:
1. Go to: https://www.reddit.com/prefs/apps
2. Scroll down and click **"create another app..."** or **"create application"**
3. Fill in:
   - **Name**: FinRobot (or any name)
   - **Type**: Select **"script"**
   - **Description**: Financial analysis tool (optional)
   - **About URL**: Leave blank or add your website
   - **Redirect URI**: `http://localhost:8080` (or any URL)
4. Click **"create app"**
5. You'll see:
   - **Client ID**: The string under your app name (looks like: `abc123def456`)
   - **Client Secret**: The "secret" field (looks like: `xyz789_secret_key`)
6. Add both to `config_api_keys`:
   ```json
   "REDDIT_CLIENT_ID": "your_client_id_here",
   "REDDIT_CLIENT_SECRET": "your_client_secret_here"
   ```

### What It Provides:
- Reddit post data
- Social sentiment analysis
- Market discussion threads
- Stock-related discussions

### Required?
**Optional** - Only needed for Reddit sentiment analysis features.

### Rate Limits:
- 60 requests per minute
- No daily limit
- Completely free forever

---

## 5. TWITTER_BEARER_TOKEN (X/Twitter API)

### Status: **NOT CONFIGURED** ❌

### Is it Free?
**Limited** - Twitter/X API has changed significantly

### Free Tier Limits:
- **Very limited** - Mostly requires paid plan now
- **Basic read access** (if available)
- **May require Twitter Developer account approval**

### How to Get:
1. Go to: https://developer.twitter.com/
2. Apply for Twitter Developer account (may take time for approval)
3. Create an app
4. Generate Bearer Token
5. Add to `config_api_keys`:
   ```json
   "TWITTER_BEARER_TOKEN": "your_bearer_token_here"
   ```

### What It Provides:
- Twitter/X posts about stocks
- Social sentiment
- Market discussions

### Required?
**Optional** - Only needed for Twitter sentiment analysis.

### Current Status:
Twitter/X API has become more restrictive. Free tier is very limited or may not be available.

### Paid Plans:
- Basic: $100/month
- Pro: $5,000/month

**Note**: Twitter/X API access has become expensive and restrictive. Consider skipping this unless you specifically need Twitter data.

---

## Summary Table

| API Key | Free? | Limits | Required? | Difficulty |
|---------|-------|--------|-----------|------------|
| **FinnHub** | ✅ Yes | 60/min | Optional | ⭐ Easy (Already done!) |
| **FMP** | ✅ Yes | 250/day | Optional | ⭐ Easy |
| **SEC API** | ⚠️ Limited | Very limited | Optional | ⭐⭐ Medium |
| **Reddit** | ✅ Yes | 60/min | Optional | ⭐ Easy |
| **Twitter** | ❌ Very Limited | Very limited | Optional | ⭐⭐⭐ Hard |

---

## Recommended Setup Priority

### Essential (Already Working):
1. ✅ **FinnHub** - Already configured!
2. ✅ **Gemini API** - Already configured in GEMINI_CONFIG_LIST

### Nice to Have:
3. **Reddit** - Easy to get, free, useful for sentiment
4. **FMP** - Easy to get, free tier, good for SEC filings

### Optional (Can Skip):
5. **SEC API** - Limited free tier, mostly paid
6. **Twitter** - Very expensive, limited free access

---

## Minimum Required Setup

**FinRobot works with just:**
- ✅ Gemini API (already configured)
- ✅ Yahoo Finance (no API key needed - already working!)

**Everything else is optional!**

---

## Quick Setup Guide

### 1. Reddit (Recommended - Easy & Free)

1. Go to: https://www.reddit.com/prefs/apps
2. Click "create another app"
3. Type: "script"
4. Copy Client ID and Secret
5. Add to `config_api_keys`

### 2. FMP (Recommended - Easy & Free)

1. Go to: https://site.financialmodelingprep.com/developer/docs/
2. Sign up (free)
3. Get API key
4. Add to `config_api_keys`

### 3. SEC API (Optional - Limited Free)

1. Go to: https://sec-api.io/
2. Sign up
3. Get API key (may need paid plan for real usage)
4. Add to `config_api_keys`

### 4. Twitter (Not Recommended - Expensive)

- Skip unless you specifically need Twitter data
- Very expensive ($100+/month)
- Limited free access

---

## Current Configuration Status

```json
{
    "FINNHUB_API_KEY": "d47i62pr01qtk51q850gd47i62pr01qtk51q8510", ✅
    "FMP_API_KEY": "YOUR_FMP_API_KEY", ❌
    "SEC_API_KEY": "YOUR_SEC_API_KEY", ❌
    "REDDIT_CLIENT_ID": "YOUR_REDDIT_CLIENT_ID", ❌
    "REDDIT_CLIENT_SECRET": "YOUR_REDDIT_CLIENT_SECRET", ❌
    "TWITTER_BEARER_TOKEN": "YOUR_TWITTER_BEARER_TOKEN" ❌
}
```

---

## What You Can Do Right Now

**With current setup:**
- ✅ Analyze stocks (using Gemini + Yahoo Finance)
- ✅ Get stock price data
- ✅ Get company information
- ✅ Make predictions

**After adding Reddit:**
- ✅ Get social sentiment
- ✅ Analyze Reddit discussions

**After adding FMP:**
- ✅ Get SEC filing URLs
- ✅ Access more financial data

---

## Recommendation

**Start with:**
1. ✅ FinnHub (already done!)
2. ✅ Gemini (already done!)
3. ⭐ Reddit (easy, free, useful)
4. ⭐ FMP (easy, free, useful)

**Skip for now:**
- SEC API (limited free tier)
- Twitter (expensive)

You have everything you need to use FinRobot effectively! 🚀

