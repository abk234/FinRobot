# How to Fix "Insufficient Quota" Error

## What This Error Means

The error "You exceeded your current quota" means:
- ✅ Your API key is **valid** and working
- ✅ Your connection is **working**
- ❌ Your OpenAI account has **no available credits/quota**

This is a **billing/account issue**, not a code problem.

## Why This Happens

OpenAI requires you to:
1. **Add a payment method** to your account
2. **Set up billing** (even for free tier in some cases)
3. **Have available credits** in your account

Even if you have a free tier or credits, you need to:
- Complete the billing setup
- Add a payment method (even if you won't be charged immediately)
- Verify your account

## How to Fix It

### Step 1: Check Your OpenAI Account

1. Go to: https://platform.openai.com/account/billing
2. Log in with your OpenAI account
3. Check if you have:
   - A payment method added
   - Available credits/quota
   - Active billing plan

### Step 2: Add Payment Method (If Needed)

1. Go to: https://platform.openai.com/account/billing
2. Click "Add payment method"
3. Enter your credit card details
4. **Note**: You may have free credits that don't require immediate charges

### Step 3: Check Your Usage Limits

1. Go to: https://platform.openai.com/usage
2. Check:
   - Your current usage
   - Your rate limits
   - Available credits

### Step 4: Verify Account Status

1. Go to: https://platform.openai.com/account
2. Make sure your account is:
   - Verified (check email verification)
   - Not restricted
   - Has billing enabled

## Common Scenarios

### Scenario 1: New Account
- **Problem**: New accounts often need billing setup even for free tier
- **Solution**: Add payment method at https://platform.openai.com/account/billing

### Scenario 2: Free Credits Exhausted
- **Problem**: You've used all your free credits
- **Solution**: Add payment method to continue using the API

### Scenario 3: Rate Limits
- **Problem**: You're hitting rate limits (too many requests)
- **Solution**: Wait a bit, or upgrade your plan for higher limits

### Scenario 4: Account Restrictions
- **Problem**: Account might be restricted or flagged
- **Solution**: Check account status and contact OpenAI support if needed

## Quick Checklist

- [ ] Payment method added to OpenAI account
- [ ] Billing enabled in account settings
- [ ] Account is verified (email confirmed)
- [ ] Available credits/quota in account
- [ ] Not hitting rate limits
- [ ] API key is from the correct account

## Testing After Fix

Once you've set up billing, test again:

```bash
cd /Users/lxupkzwjs/Developer/eval/FinRobot
source venv/bin/activate
python start_demo.py
```

## Still Having Issues?

If you've completed all steps and still get the error:

1. **Wait a few minutes** - Sometimes changes take time to propagate
2. **Check API key** - Make sure you're using the key from the account with billing set up
3. **Check usage dashboard** - See if there are any restrictions
4. **Contact OpenAI Support** - If everything looks correct but still not working

## Alternative: Use a Different Model

If you want to test without setting up billing, you could:
- Use a local model (if available)
- Use a different API provider
- Wait for free tier credits (if available)

But for OpenAI's API, billing setup is typically required.

## Summary

**The error means**: Your account needs billing setup or has no quota
**The fix**: Add payment method and enable billing at https://platform.openai.com/account/billing
**Your code is fine**: The application is working correctly!

