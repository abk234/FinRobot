# Reddit API Setup - Step by Step

## You're on the Right Page! ✅

I can see you're on the Reddit "create application" page. Here's exactly what to fill in:

## Form Fields to Fill:

### 1. **name** field:
```
FinRobot
```
(Or any name you prefer - this is just for your reference)

### 2. **Application Type** (Radio Buttons):
**Select: "script"** ✅
- Click the "script" radio button
- Description: "Script for personal use. Will only have access to the developers accounts"
- This is the correct choice for FinRobot

### 3. **description** field (Optional):
```
Financial analysis tool using Reddit data for market sentiment
```
(Or leave blank - this is optional)

### 4. **about url** field (Optional):
```
http://localhost:8080
```
(Or leave blank - this is optional)

### 5. **redirect uri** field:
```
http://localhost:8080
```
(This is required - use any valid URL, localhost is fine)

### 6. **reCAPTCHA**:
- Check the "I'm not a robot" box
- Complete the reCAPTCHA challenge if it appears

### 7. **create app** button:
- Click the grey "create app" button at the bottom

## After Creating the App:

Once you click "create app", you'll see a page with:

1. **Client ID**: 
   - Looks like: `abc123def456ghi789`
   - This is the string shown under your app name
   - Copy this!

2. **Client Secret**:
   - Looks like: `xyz789_secret_key_here`
   - This is shown as "secret" on the page
   - Copy this!

## Then Update Your Config:

Open `config_api_keys` and replace:
```json
"REDDIT_CLIENT_ID": "YOUR_REDDIT_CLIENT_ID",
"REDDIT_CLIENT_SECRET": "YOUR_REDDIT_CLIENT_SECRET",
```

With your actual values:
```json
"REDDIT_CLIENT_ID": "",
"REDDIT_CLIENT_SECRET": "",
```

## Quick Checklist:

- [ ] Name: "FinRobot" (or any name)
- [ ] Type: Select **"script"** (important!)
- [ ] Description: Optional (can leave blank)
- [ ] About URL: Optional (can leave blank)
- [ ] Redirect URI: `http://localhost:8080`
- [ ] Complete reCAPTCHA
- [ ] Click "create app"
- [ ] Copy Client ID and Secret
- [ ] Add to config_api_keys file

That's it! Once you have the keys, let me know and I can help you add them to the config file.

