# Starting the FinRobot Web Interface

## Quick Start

```bash
cd /Users/lxupkzwjs/Developer/eval/FinRobot
source venv/bin/activate
python web_interface.py
```

Then open: **http://localhost:8080**

## Port Options

### Default Port (8080)
```bash
python web_interface.py
```
Opens on: http://localhost:8080

### Custom Port
```bash
python web_interface.py 5001
```
Opens on: http://localhost:5001

### Other Common Ports
```bash
python web_interface.py 3000   # Port 3000
python web_interface.py 9000   # Port 9000
python web_interface.py 5001   # Port 5001
```

## Using the Web Interface

1. **Start the server** (see above)
2. **Open your browser** to the URL shown
3. **Enter a stock ticker** (e.g., AAPL, TSLA, MSFT)
4. **Choose AI model**:
   - Gemini 2.5 Flash (Free - Recommended)
   - OpenAI GPT-4 (Requires billing)
5. **Optional**: Enter a custom query
6. **Click "Analyze Stock"**
7. **Wait 30-60 seconds** for results
8. **View the analysis** in the browser

## Troubleshooting

### Port Already in Use?

If you get "Address already in use":
```bash
# Try a different port
python web_interface.py 5001
python web_interface.py 3000
python web_interface.py 9000
```

### Check What's Using Port 5000
```bash
lsof -i :5000
```

### Stop the Server
Press `Ctrl+C` in the terminal where it's running

## Features

- ✅ Easy-to-use web form
- ✅ Visual results display
- ✅ Choose between Gemini (free) or OpenAI
- ✅ Custom queries supported
- ✅ No command line needed after starting

## Example

```bash
# Terminal 1: Start server
python web_interface.py

# Browser: http://localhost:8080
# Enter: TSLA
# Click: Analyze Stock
# Result: Tesla stock analysis appears!
```

Enjoy! 🚀

