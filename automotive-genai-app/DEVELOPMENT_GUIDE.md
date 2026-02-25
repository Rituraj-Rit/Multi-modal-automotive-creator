# Development Setup Guide

## Prerequisites
- Python 3.8+
- Git
- Virtual environment support (venv or conda)

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd automotive-genai-app
```

### 2. Create Virtual Environment

#### Using venv (Recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### Using conda
```bash
conda create -n automotive-genai python=3.12
conda activate automotive-genai
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install pytest pytest-cov  # For testing
```

### 4. Configure Environment
```bash
# Copy example environment
cp .env.example .env

# Edit .env with your API keys
# Required:
# - LLM_API_KEY (OpenAI)
# - IMAGE_API_KEY (OpenAI or Stability AI)
```

### 5. Run Application

#### Development Mode
```bash
python run_server.py
# or
python src/app.py
```

#### Production Mode (with Gunicorn)
```bash
gunicorn --bind 127.0.0.1:5000 --workers 4 src.app:create_app()
```

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
# View: htmlcov/index.html
```

### Run Specific Tests
```bash
pytest tests/test_api.py::TestFlaskApp -v
```

## Project Structure

```
automotive-genai-app/
├── src/
│   ├── __init__.py
│   ├── app.py                 # Flask factory
│   ├── config.py              # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoints
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── llm_handler.py     # LLM interactions
│   │   ├── image_generator.py # Image generation
│   │   └── orchestrator.py    # Main orchestration
│   └── utils/
│       ├── __init__.py
│       └── helpers.py         # Utility functions
├── frontend/
│   ├── templates/
│   │   └── index.html         # Web UI
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── tests/
│   ├── __init__.py
│   └── test_api.py            # Test suite
├── config/                    # Configuration files
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
├── run_server.py             # Server runner
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose
└── README.md                 # This file
```

## API Endpoints

### Health Check
```bash
GET /api/health
# Response: 200 or 206 (Degraded)
```

### Generate Visualization
```bash
POST /api/generate
{
  "design_prompt": "A sleek electric sports car",
  "context": "luxury automotive brand",
  "enhance_image": false
}
# Response: { success, narrative, image_data, ... }
```

### Batch Generation
```bash
POST /api/batch
{
  "prompts": ["Prompt 1", "Prompt 2"],
  "context": "optional context"
}
```

### Get Configuration
```bash
GET /api/config
# Response: { llm_model, image_provider, validation }
```

## Code Style and Quality

### Code Formatting
```bash
# Using black (optional)
pip install black
black src/
```

### Linting
```bash
# Using pylint (optional)
pip install pylint
pylint src/
```

### Type Checking
```bash
# Using mypy (optional)
pip install mypy
mypy src/
```

## Common Development Tasks

### Add New Environment Variable
1. Add to `.env.example`
2. Update `src/config.py`
3. Document in README

### Add New API Endpoint
1. Add route in `src/api/routes.py`
2. Add handler in appropriate module
3. Add tests in `tests/test_api.py`

### Add New Test
1. Create test method in `tests/test_api.py`
2. Follow existing test patterns
3. Run: `pytest tests/test_api.py::TestClass::test_method -v`

### Debug Issues
```bash
# Verbose output
python -c "import src.app; print(src.app.create_app())"

# Check imports
python -c "from src.modules import llm_handler; print('OK')"

# Test API directly
python test_api_direct.py
```

## Performance Optimization

### Profile Application
```bash
pip install py-spy
py-spy record -o profile.svg -- python run_server.py
```

### Monitor Memory
```bash
pip install memory-profiler
python -m memory_profiler run_server.py
```

## Troubleshooting

### Module Not Found
```bash
# Ensure __init__.py exists in directories
find . -type d -name src -o -name modules -o -name api | xargs -I {} touch {}/__init__.py
```

### API Key Issues
```bash
# Verify environment variables
python -c "from src.config import get_config; c=get_config(); print(f'LLM: {bool(c.LLM_API_KEY)}, Image: {bool(c.IMAGE_API_KEY)}')"
```

### Port Already in Use
```bash
# Change port in .env
APP_PORT=5001

# or kill existing process (Linux/macOS)
lsof -ti :5000 | xargs kill -9
```

## Contributing

### Branch Naming
- Feature: `feature/description`
- Bug fix: `bugfix/description`
- Docs: `docs/description`

### Commit Messages
- Use clear, descriptive messages
- Reference issues: `Fixes #123`
- Format: `type: description`

### Pull Requests
1. Create feature branch
2. Make changes and test
3. Run full test suite
4. Submit PR with description

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenAI API Docs](https://platform.openai.com/docs/)
- [Python Testing Best Practices](https://docs.pytest.org/)
- [Docker Documentation](https://docs.docker.com/)

## Getting Help

1. Check existing documentation
2. Review test cases for examples
3. Check GitHub issues
4. Contact development team
