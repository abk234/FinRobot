# Deployment Guide

This guide covers deploying FinRobot applications to production environments.

## Deployment Considerations

### Environment Requirements

- **Python**: 3.10 or 3.11
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: Sufficient space for data and cache
- **Network**: Stable internet for API calls
- **API Keys**: Valid keys for all required services

### Security Considerations

1. **API Key Management**: Never commit keys to version control
2. **Environment Variables**: Use secure environment variable management
3. **Rate Limiting**: Implement rate limiting for API calls
4. **Error Handling**: Don't expose sensitive information in errors
5. **Access Control**: Restrict access to deployment

## Deployment Options

### Option 1: Local Deployment

#### Setup

```bash
# Clone repository
git clone https://github.com/AI4Finance-Foundation/FinRobot.git
cd FinRobot

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure API keys
cp config_api_keys_sample config_api_keys
# Edit config_api_keys with your keys

cp OAI_CONFIG_LIST_sample OAI_CONFIG_LIST
# Edit OAI_CONFIG_LIST with your OpenAI key
```

#### Running

```bash
python your_script.py
```

### Option 2: Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install package
RUN pip install -e .

# Set environment variables (use secrets in production)
ENV FINNHUB_API_KEY=""
ENV FMP_API_KEY=""
ENV SEC_API_KEY=""

# Run application
CMD ["python", "your_script.py"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  finrobot:
    build: .
    environment:
      - FINNHUB_API_KEY=${FINNHUB_API_KEY}
      - FMP_API_KEY=${FMP_API_KEY}
      - SEC_API_KEY=${SEC_API_KEY}
    volumes:
      - ./data:/app/data
      - ./reports:/app/reports
    env_file:
      - .env
```

#### Building and Running

```bash
# Build image
docker build -t finrobot:latest .

# Run container
docker run -d \
  --name finrobot \
  -e FINNHUB_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  finrobot:latest

# Or use docker-compose
docker-compose up -d
```

### Option 3: Cloud Deployment

#### AWS Lambda

**Note**: Lambda has limitations (timeout, memory) that may affect agent workflows.

```python
# lambda_function.py
import json
from finrobot.agents.workflow import SingleAssistant
import autogen

def lambda_handler(event, context):
    llm_config = {
        "config_list": autogen.config_list_from_json(
            "OAI_CONFIG_LIST",
            filter_dict={"model": ["gpt-4"]},
        ),
    }
    
    assistant = SingleAssistant("Market_Analyst", llm_config)
    
    query = event.get("query", "")
    assistant.chat(query)
    
    return {
        "statusCode": 200,
        "body": json.dumps("Analysis complete")
    }
```

#### Google Cloud Functions

```python
# main.py
from finrobot.agents.workflow import SingleAssistant
import autogen

def analyze_stock(request):
    llm_config = {
        "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST"),
    }
    
    assistant = SingleAssistant("Market_Analyst", llm_config)
    query = request.json.get("query")
    
    assistant.chat(query)
    
    return {"status": "complete"}
```

#### Azure Functions

```python
# __init__.py
import azure.functions as func
from finrobot.agents.workflow import SingleAssistant
import autogen

def main(req: func.HttpRequest) -> func.HttpResponse:
    llm_config = {
        "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST"),
    }
    
    assistant = SingleAssistant("Market_Analyst", llm_config)
    query = req.params.get("query")
    
    assistant.chat(query)
    
    return func.HttpResponse("Analysis complete")
```

### Option 4: Web Application

#### Flask API

```python
# app.py
from flask import Flask, request, jsonify
from finrobot.agents.workflow import SingleAssistant
import autogen

app = Flask(__name__)

llm_config = {
    "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST"),
}

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    symbol = data.get('symbol')
    
    assistant = SingleAssistant("Market_Analyst", llm_config)
    assistant.chat(f"Analyze {symbol} stock")
    
    return jsonify({"status": "complete"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### FastAPI

```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from finrobot.agents.workflow import SingleAssistant
import autogen

app = FastAPI()

llm_config = {
    "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST"),
}

class AnalysisRequest(BaseModel):
    symbol: str
    query: str

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    assistant = SingleAssistant("Market_Analyst", llm_config)
    assistant.chat(f"Analyze {request.symbol}: {request.query}")
    return {"status": "complete"}
```

## Configuration Management

### Environment Variables

```bash
# .env file
FINNHUB_API_KEY=your_key_here
FMP_API_KEY=your_key_here
SEC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### Using python-dotenv

```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("FINNHUB_API_KEY")
```

### Secret Management

#### AWS Secrets Manager

```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

secrets = get_secret("finrobot/api-keys")
os.environ["FINNHUB_API_KEY"] = secrets["finnhub_key"]
```

#### HashiCorp Vault

```python
import hvac

client = hvac.Client(url='https://vault.example.com')
client.token = os.getenv('VAULT_TOKEN')

secret = client.secrets.kv.v2.read_secret_version(path='finrobot/keys')
os.environ["FINNHUB_API_KEY"] = secret['data']['data']['finnhub_key']
```

## Monitoring and Logging

### Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('finrobot.log', maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Application Monitoring

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"{func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            raise
    return wrapper

@monitor_performance
def analyze_stock(symbol):
    # Analysis code
    pass
```

### Error Tracking

#### Sentry Integration

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

## Performance Optimization

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_company_profile(symbol):
    return FinnHubUtils.get_company_profile(symbol)
```

### Async Operations

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def analyze_multiple_stocks(symbols):
    with ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [
            executor.submit(analyze_stock, symbol)
            for symbol in symbols
        ]
        results = [task.result() for task in tasks]
    return results
```

### Rate Limiting

```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=100, period=60)  # 100 calls per minute
def api_call():
    # API call
    pass
```

## Scaling Considerations

### Horizontal Scaling

- Use load balancers for multiple instances
- Implement session management for stateful agents
- Use message queues for task distribution

### Vertical Scaling

- Increase memory for large data processing
- Use faster CPUs for computation-intensive tasks
- Optimize database queries

### Database Integration

```python
# Store analysis results
import sqlite3

def save_analysis(symbol, analysis_result):
    conn = sqlite3.connect('analyses.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO analyses (symbol, result, timestamp) VALUES (?, ?, ?)",
        (symbol, analysis_result, datetime.now())
    )
    conn.commit()
    conn.close()
```

## Backup and Recovery

### Data Backup

```python
import shutil
from datetime import datetime

def backup_data():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backups/backup_{timestamp}"
    shutil.copytree("data", backup_path)
    return backup_path
```

### Configuration Backup

```bash
# Backup configuration
tar -czf config_backup.tar.gz config_api_keys OAI_CONFIG_LIST
```

## Security Best Practices

1. **Never commit secrets**: Use .gitignore
2. **Use HTTPS**: Encrypt all communications
3. **Validate inputs**: Sanitize user inputs
4. **Limit access**: Use authentication and authorization
5. **Regular updates**: Keep dependencies updated
6. **Audit logs**: Log all important operations

## Troubleshooting

### Common Issues

#### Issue: Out of Memory

**Solution**: 
- Reduce batch sizes
- Use streaming for large datasets
- Increase memory allocation

#### Issue: API Rate Limits

**Solution**:
- Implement rate limiting
- Use caching
- Distribute requests over time

#### Issue: Timeout Errors

**Solution**:
- Increase timeout values
- Optimize queries
- Use async operations

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable verbose output
assistant = SingleAssistant(
    "Market_Analyst",
    llm_config,
    verbose=True,
)
```

## Production Checklist

- [ ] API keys configured securely
- [ ] Logging configured
- [ ] Error handling implemented
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Security measures implemented
- [ ] Performance tested
- [ ] Documentation updated
- [ ] Deployment process documented
- [ ] Rollback plan prepared

## Next Steps

- See [[01-Getting-Started]] for basic setup
- Read [[04-Development-Guide]] for development practices
- Check [[07-Testing-Guide]] for testing strategies

