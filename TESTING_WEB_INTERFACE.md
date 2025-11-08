# Testing the Web Interface - Comprehensive Analysis & Chat

## Quick Test Steps

1. **Start the server:**
   ```bash
   python web_interface.py
   ```

2. **Open browser:** http://localhost:8250

3. **Test Comprehensive Analysis:**
   - Select "Comprehensive Analysis (Recommended)" from Analysis Type dropdown
   - Enter a ticker (e.g., "AAPL")
   - Set parameters (or use defaults)
   - Click "Analyze Stock"
   - Wait for analysis to complete (may take 1-2 minutes)

4. **Verify Results Display:**
   - Results should appear in the gray box below the form
   - Results should scroll into view automatically
   - Check browser console (F12) for any errors

5. **Verify Chat Window:**
   - After analysis completes, chat toggle button should appear (bottom-right)
   - Button should say "💬 Chat Available" and have a blue pulsing animation
   - Click the button to open chat panel
   - Chat panel should appear on the right side
   - Welcome message should be visible

6. **Test Chat Functionality:**
   - Type a message in the chat input
   - Send button should be enabled (not grayed out)
   - Send a message (e.g., "Explain the RSI indicator")
   - Wait for response
   - Try requesting a chart: "Can you show me a chart?"

## What to Check

### Comprehensive Analysis Should Show:
- ✅ Company name and ticker
- ✅ Current market data (price, trend, signal strength)
- ✅ Moving averages, RSI, MACD, Bollinger Bands
- ✅ Trading recommendations (entry, stop loss, target)
- ✅ Position sizing recommendations
- ✅ Price forecast
- ✅ Kid-friendly explanation
- ✅ Summary with next steps

### Chat Window Should:
- ✅ Appear automatically after analysis (or be accessible via toggle button)
- ✅ Show welcome message
- ✅ Allow typing and sending messages
- ✅ Display assistant responses
- ✅ Show charts when requested
- ✅ Maintain conversation context

## Debugging

### Browser Console (F12 → Console)
Look for:
- `Session initialized: [session-id]` - Confirms session was created
- `Chat panel activated` - Confirms chat panel was shown
- Any error messages in red

### Common Issues

**Results not showing:**
- Check browser console for JavaScript errors
- Verify the result div exists: `document.getElementById('result')`
- Check network tab to see if request completed

**Chat not appearing:**
- Check if `session_id` is in the response (console log)
- Verify chat panel element exists
- Check CSS - chat panel should have `display: flex !important` when active

**Chart not generating:**
- Check for Yahoo Finance API errors (401 errors)
- Verify chart file was created in `static/charts/` directory
- Check browser console for chart loading errors

## Expected Behavior

1. **Form Submission:**
   - Button disables during analysis
   - Loading message appears
   - Results appear when complete
   - Button re-enables

2. **Chat Activation:**
   - Toggle button appears/updates after analysis
   - Chat panel can be opened/closed
   - Send button enables when there's text and a session

3. **Chat Interaction:**
   - Messages appear in chat bubbles
   - User messages on right (blue)
   - Assistant messages on left (white/gray)
   - Error messages in red
   - Charts display inline when generated

## Manual Testing Checklist

- [ ] Comprehensive analysis completes successfully
- [ ] Results display in the result box
- [ ] Chat toggle button appears after analysis
- [ ] Chat panel opens when button clicked
- [ ] Can send messages in chat
- [ ] Assistant responds to questions
- [ ] Charts can be requested and displayed
- [ ] Chat maintains conversation context
- [ ] Analysis type can be changed
- [ ] Form clears/resets when changing analysis type

