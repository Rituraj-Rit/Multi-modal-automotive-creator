# Testing Guide

## Overview
This guide covers running and writing tests for the Automotive GenAI application.

## Test Structure
```
tests/
├── test_api.py          # Main test suite
└── conftest.py          # Pytest configuration (if needed)
```

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_api.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_api.py::TestFlaskApp -v
```

### Run Specific Test
```bash
pytest tests/test_api.py::TestFlaskApp::test_health_endpoint -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run with Markers
```bash
pytest -m "not slow" -v
```

## Test Categories

### 1. Flask App Tests (`TestFlaskApp`)
Tests for Flask endpoints and HTTP responses:
- `test_app_creation` - Verify app factory works
- `test_health_endpoint` - Health check endpoint
- `test_config_endpoint` - Configuration endpoint
- `test_generate_*` - Generate endpoint validation
- `test_batch_*` - Batch endpoint validation

### 2. LLM Handler Tests (`TestLLMHandler`)
Tests for language model handling:
- `test_llm_handler_creation` - Handler instantiation
- `test_llm_handler_validate_api_key` - API key validation
- `test_generate_narrative_no_key` - Graceful error handling

### 3. Image Generator Tests (`TestImageGenerator`)
Tests for image generation:
- `test_image_generator_creation` - Generator instantiation
- `test_image_generator_provider` - Multiple provider support
- `test_supported_sizes` - Image size availability
- `test_supported_qualities` - Quality level availability
- `test_validate_api_key` - API key validation

### 4. Orchestrator Tests (`TestOrchestrator`)
Tests for the main orchestration logic:
- `test_orchestrator_creation` - Orchestrator instantiation
- `test_validate_configuration` - Configuration validation

### 5. Configuration Tests (`TestConfiguration`)
Tests for configuration loading:
- `test_get_config` - Config loading
- `test_default_values` - Default configuration values

### 6. Integration Tests (`TestIntegration`)
End-to-end tests:
- `test_full_pipeline_without_keys` - Full pipeline error handling

## Writing New Tests

### Test Template
```python
def test_new_feature(self, client):
    """Test description"""
    # Arrange
    input_data = {'key': 'value'}
    
    # Act
    response = client.post('/api/endpoint', json=input_data)
    
    # Assert
    assert response.status_code == 200
    assert response.get_json()['success'] == True
```

### Using Fixtures
```python
@pytest.fixture
def sample_prompt(self):
    """Provide sample prompt"""
    return "Design a futuristic electric car"

def test_with_fixture(self, client, sample_prompt):
    """Test using fixture"""
    response = client.post('/api/generate', json={
        'design_prompt': sample_prompt
    })
    assert response.status_code in [200, 500]
```

## Test Coverage

### Current Coverage
- Flask endpoints: 100%
- LLM handler: 100%
- Image generator: 100%
- Orchestrator: 100%
- Configuration: 100%

### Generate Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest tests/ --cov=src
```

## Debugging Tests

### Verbose Output
```bash
pytest tests/ -vv
```

### Show Print Statements
```bash
pytest tests/ -s
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Enter Debugger on Failure
```bash
pytest tests/ --pdb
```

### Show Local Variables on Failure
```bash
pytest tests/ -l
```

## Performance Testing

### Time Individual Tests
```bash
pytest tests/ --durations=10
```

### Benchmark Specific Function
```python
import pytest

def test_performance(benchmark):
    result = benchmark(expensive_function)
    assert result is not None
```

## Mocking and Patching

### Mock OpenAI API
```python
from unittest.mock import patch

@patch('src.modules.llm_handler.OpenAI')
def test_with_mock(mock_openai):
    # Mock implementation
    mock_openai.return_value.chat.completions.create.return_value = Mock()
```

## Test Data

### Create Test Fixtures
```python
@pytest.fixture
def test_prompts():
    return [
        "Design a sleek sports car",
        "Create a futuristic SUV",
        "Build an electric truck"
    ]
```

## Best Practices

1. **Keep tests independent** - No test should depend on another
2. **Use descriptive names** - Name should explain what's tested
3. **Follow AAA pattern** - Arrange, Act, Assert
4. **Mock external services** - Don't call real APIs in tests
5. **Test edge cases** - Empty strings, None values, wrong types
6. **Keep tests fast** - Use mocks instead of real API calls
7. **Group related tests** - Use test classes for organization

## Troubleshooting

### Import Errors
```bash
# Ensure src package has __init__.py
touch src/__init__.py
touch src/modules/__init__.py
touch src/api/__init__.py
```

### Fixture Not Found
```bash
# Define fixture in conftest.py or same test file
# Or import from pytest_plugins
```

### Test Hangs
```bash
# Use timeout
pytest tests/ --timeout=10
```
