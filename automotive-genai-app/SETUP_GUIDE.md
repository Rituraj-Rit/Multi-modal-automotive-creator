# SETUP_GUIDE.md - Complete Installation Instructions

## 🎯 Quick Start Guide

This guide walks you through setting up and running the Automotive GenAI Visualization application.

---

## ✅ Pre-Installation Checklist

- [ ] Python 3.8 or higher installed
- [ ] pip package manager available
- [ ] OpenAI API key obtained
- [ ] Image generation API key (optional but recommended)
- [ ] Git (optional, for version control)

### Getting API Keys

#### OpenAI API Key

1. Visit https://platform.openai.com/
2. Sign up or log in to your account
3. Go to **API Keys** section
4. Click **Create new secret key**
5. Copy the key (you won't see it again!)
6. Save it securely

#### Image Generation API Key (Optional)

**Option A: DALL-E 3 (via OpenAI)**
- Use the same OpenAI API key

**Option B: Stable Diffusion (via Stability AI)**
1. Visit https://platform.stability.ai/
2. Create account and log in
3. Go to API Keys section
4. Create new key
5. Copy and save securely

---

## 📦 Installation Steps

### Step 1: Navigate to Project Directory

```bash
cd c:\Users\BRICS\Desktop\LLM\automotive-genai-app
```

### Step 2: Create Python Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Wait for all packages to install successfully. This installs:
- Flask (web framework)
- OpenAI (API client)
- python-dotenv (environment management)
- requests (HTTP library)
- Pillow (image processing)
- And other required packages

### Step 4: Configure Environment Variables

**Copy the example file:**

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

**Edit the .env file with your API keys:**

```bash
# Windows (Notepad)
notepad .env

# Windows (PowerShell)
code .env

# macOS/Linux
nano .env
```

**Minimum required configuration:**

```env
LLM_API_KEY=sk-...your_openai_key_here...
LLM_MODEL=gpt-4
IMAGE_API_KEY=sk-...your_image_api_key...
IMAGE_MODEL=dall-e-3
FLASK_ENV=development
FLASK_DEBUG=True
APP_PORT=5000
```

### Step 5: Verify Installation

Run the health check:

```bash
python src/app.py
```

You should see output like:
```
WARNING in app.py: This is a development server. Do not use it in production...
Running on http://127.0.0.1:5000
```

---

## 🚀 Running the Application

### Start the Server

```bash
python src/app.py
```

Or with Gunicorn for production:

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 src.app:app
```

### Access the Web Interface

Open your browser and navigate to:

```
http://localhost:5000
```

You should see the Automotive GenAI Visualizer interface.

---

## 🧪 Testing the Application

### 1. Test via Web Interface

1. Visit http://localhost:5000
2. Enter a design prompt in the text area
3. Click "Generate Visualization"
4. Wait for results (may take 30-60 seconds)

**Example test prompt:**
```
A sleek futuristic sports car with aggressive angular lines, 
low profile, glowing neon accents, and minimalist interior design.
```

### 2. Test via API (Using PowerShell)

```powershell
# Test health endpoint
Invoke-WebRequest -Uri "http://localhost:5000/api/health" | ConvertTo-Json

# Test narrative generation
$body = @{
    prompt = "A luxury electric sedan"
    context = "Year 2026, eco-friendly"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/narrative" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### 3. Test via API (Using cURL)

```bash
# Health check
curl http://localhost:5000/api/health

# Generate visualization
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"design_prompt\": \"A futuristic sports car\", \"enhance_image\": false}"
```

### 4. Test via Python

```python
import requests

# Test API
response = requests.post(
    "http://localhost:5000/api/generate",
    json={
        "design_prompt": "A futuristic hypercar with sleek design",
        "context": "Year 2030, sustainable materials",
        "enhance_image": False
    }
)

result = response.json()
print("Success:", result['success'])
print("Narrative:", result['narrative'][:100] + "...")
```

---

## 🔧 Configuration Guide

### Environment Variables Explained

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `LLM_API_KEY` | OpenAI API authentication | Required | `sk-...` |
| `LLM_MODEL` | GPT model version | `gpt-4` | `gpt-4`, `gpt-4-turbo` |
| `LLM_TEMPERATURE` | Model creativity (0-1) | `0.7` | `0.5` (conservative), `0.9` (creative) |
| `LLM_MAX_TOKENS` | Response length limit | `1000` | `500`, `2000` |
| `IMAGE_API_KEY` | Image generation API key | Required | `sk-...` |
| `IMAGE_MODEL` | Image model | `dall-e-3` | `dall-e-3`, `dall-e-2` |
| `IMAGE_QUALITY` | Image quality level | `hd` | `standard`, `hd` |
| `IMAGE_SIZE` | Output image dimensions | `1024x1024` | `512x512`, `1024x1792` |
| `FLASK_ENV` | Environment mode | `development` | `production` |
| `FLASK_DEBUG` | Debug mode | `True` | `False` for production |
| `APP_PORT` | Server port | `5000` | Any available port |

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```bash
# Ensure virtual environment is activated
# Then reinstall requirements
pip install -r requirements.txt --upgrade
```

### Problem: "API Key Not Found"

**Solution:**
1. Verify `.env` file exists in project root
2. Check key names are exact (case-sensitive)
3. Ensure no extra quotes or spaces in keys
4. Restart the application after saving `.env`

### Problem: "OpenAI API Error 401 Unauthorized"

**Solution:**
- API key is invalid or expired
- Try creating a new key from https://platform.openai.com/api-keys
- Verify account has API access enabled
- Check for billing/quota issues

### Problem: "Port 5000 already in use"

**Solution:**
```bash
# Change port in .env
APP_PORT=5001

# Or kill process using port (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Problem: "Slow response times"

**Solutions:**
- Reduce `LLM_MAX_TOKENS` for faster generation
- Lower `LLM_TEMPERATURE` for simpler responses
- Check API rate limits
- Monitor system resources (CPU, RAM)

### Problem: "Generated images are low quality"

**Solutions:**
- Set `IMAGE_QUALITY=hd`
- Increase image prompt detail
- Use `enhance_image: true` option
- Try different models

---

## 📊 File Structure Explanation

```
automotive-genai-app/
│
├── src/
│   ├── modules/              # Core AI modules
│   │   ├── llm_handler.py    # Text generation logic
│   │   ├── image_generator.py # Image generation logic
│   │   └── orchestrator.py   # Workflow management
│   │
│   ├── api/
│   │   └── routes.py         # REST API endpoints
│   │
│   ├── utils/
│   │   └── helpers.py        # Utility functions
│   │
│   ├── app.py                # Flask application entry
│   └── config.py             # Configuration loader
│
├── frontend/
│   ├── templates/
│   │   └── index.html        # Web page
│   └── static/
│       ├── css/style.css     # Styling
│       └── js/app.js         # Frontend logic
│
├── config/                   # Configuration files
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── README.md                # Main documentation
├── EXAMPLES.md              # Usage examples
└── SETUP_GUIDE.md           # This file
```

---

## 🚀 Advanced Setup

### Using Docker

**Create Dockerfile:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENV FLASK_APP=src/app.py

CMD ["python", "src/app.py"]
```

**Build and run:**

```bash
docker build -t automotive-genai .
docker run -p 5000:5000 --env-file .env automotive-genai
```

### Using Nginx as Reverse Proxy

**nginx.conf example:**

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /app/frontend/static/;
    }
}
```

### Production Deployment Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS/SSL
- [ ] Set up proper logging
- [ ] Configure rate limiting
- [ ] Enable CORS only for trusted origins
- [ ] Monitor API usage and costs
- [ ] Set up error alerts
- [ ] Regular security audits

---

## 📈 Performance Tips

1. **Cache Results**: Store responses for identical prompts
2. **Optimize Prompts**: Shorter prompts with better descriptions
3. **Use Batch Processing**: Generate multiple concepts together
4. **Monitor Tokens**: Track API usage to control costs
5. **Upgrade Model**: Use faster models if speed is priority
6. **Implement CDN**: For static assets in production

---

## 🔒 Security Reminders

⚠️ **IMPORTANT:**

- Never commit `.env` file to version control
- Don't share API keys in public repositories
- Rotate keys periodically
- Use environment variables for all secrets
- Validate and sanitize user inputs
- Enable logging for audit trails
- Use HTTPS in production
- Implement authentication for API endpoints

---

## 📞 Getting Help

If you encounter issues:

1. **Check the logs**: Look for error messages
2. **Review README.md**: Full documentation
3. **Check EXAMPLES.md**: Usage examples
4. **Verify API keys**: Most issues are key-related
5. **Test endpoints**: Use curl or Postman
6. **Check internet connection**: Ensure API connectivity

---

## ✨ Next Steps

After successful installation:

1. Explore the web interface at http://localhost:5000
2. Test with provided example prompts (see EXAMPLES.md)
3. Experiment with different design concepts
4. Review API documentation for integration
5. Customize configuration for your needs
6. Deploy to production when ready

---

**Congratulations! Your Automotive GenAI application is ready to use! 🎉**

For detailed usage information, see **README.md**
For example prompts and API tests, see **EXAMPLES.md**
