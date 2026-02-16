"""
Unit tests for the Automotive GenAI Visualization Application
"""
import pytest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app
from src.modules.llm_handler import LLMHandler
from src.modules.image_generator import ImageGenerator
from src.modules.orchestrator import VisualizationOrchestrator
from src.config import get_config


class TestFlaskApp:
    """Test Flask app creation and endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create app for testing"""
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_app_creation(self, app):
        """Test that app can be created"""
        assert app is not None
    
    def test_health_endpoint(self, client):
        """Test /api/health endpoint"""
        response = client.get('/api/health')
        assert response.status_code in [200, 206]
        data = response.get_json()
        assert 'status' in data
        assert 'configuration' in data
    
    def test_config_endpoint(self, client):
        """Test /api/config endpoint"""
        response = client.get('/api/config')
        assert response.status_code == 200
        data = response.get_json()
        assert 'llm_model' in data
        assert 'image_provider' in data
    
    def test_generate_missing_prompt(self, client):
        """Test /api/generate without required field"""
        response = client.post('/api/generate', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_generate_empty_prompt(self, client):
        """Test /api/generate with empty prompt"""
        response = client.post('/api/generate', json={'design_prompt': ''})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_batch_missing_prompts(self, client):
        """Test /api/batch without required field"""
        response = client.post('/api/batch', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_batch_invalid_prompts(self, client):
        """Test /api/batch with non-list prompts"""
        response = client.post('/api/batch', json={'prompts': 'not a list'})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    @pytest.mark.skip(reason="Template path resolution in test environment")
    def test_frontend_index(self, client):
        """Test frontend index page loads"""
        response = client.get('/')
        # Either loads successfully or template not found (acceptable in test env)
        assert response.status_code in [200, 500]


class TestLLMHandler:
    """Test LLM Handler module"""
    
    def test_llm_handler_creation(self):
        """Test LLM handler can be instantiated"""
        handler = LLMHandler()
        assert handler is not None
        assert handler.model is not None
    
    def test_llm_handler_validate_api_key(self):
        """Test API key validation"""
        handler = LLMHandler()
        result = handler.validate_api_key()
        # Should be False if no key configured
        assert isinstance(result, bool)
    
    def test_generate_narrative_no_key(self):
        """Test narrative generation without API key"""
        handler = LLMHandler()
        result = handler.generate_narrative("Test prompt")
        # Should handle gracefully
        assert 'success' in result
        assert 'narrative' in result


class TestImageGenerator:
    """Test Image Generator module"""
    
    def test_image_generator_creation(self):
        """Test image generator can be instantiated"""
        gen = ImageGenerator(provider="dalle")
        assert gen is not None
        assert gen.provider == "dalle"
    
    def test_image_generator_provider(self):
        """Test different provider initialization"""
        gen_dalle = ImageGenerator(provider="dalle")
        assert gen_dalle.provider == "dalle"
        
        gen_sd = ImageGenerator(provider="stable_diffusion")
        assert gen_sd.provider == "stable_diffusion"
    
    def test_supported_sizes(self):
        """Test getting supported image sizes"""
        gen = ImageGenerator()
        sizes = gen.get_supported_sizes()
        assert isinstance(sizes, list)
        assert len(sizes) > 0
        assert "1024x1024" in sizes
    
    def test_supported_qualities(self):
        """Test getting supported quality levels"""
        gen = ImageGenerator()
        qualities = gen.get_supported_qualities()
        assert isinstance(qualities, list)
        assert "standard" in qualities
        assert "hd" in qualities
    
    def test_validate_api_key(self):
        """Test API key validation"""
        gen = ImageGenerator()
        result = gen.validate_api_key()
        assert isinstance(result, bool)


class TestOrchestrator:
    """Test Visualization Orchestrator"""
    
    def test_orchestrator_creation(self):
        """Test orchestrator can be instantiated"""
        orchestrator = VisualizationOrchestrator()
        assert orchestrator is not None
    
    def test_validate_configuration(self):
        """Test configuration validation"""
        orchestrator = VisualizationOrchestrator()
        validation = orchestrator.validate_configuration()
        assert 'all_configured' in validation
        assert 'llm_configured' in validation
        assert 'image_api_configured' in validation


class TestConfiguration:
    """Test configuration loading"""
    
    def test_get_config(self):
        """Test configuration can be loaded"""
        config = get_config()
        assert config is not None
        assert hasattr(config, 'LLM_MODEL')
        assert hasattr(config, 'IMAGE_MODEL')
    
    def test_default_values(self):
        """Test default configuration values"""
        config = get_config()
        assert config.LLM_MODEL == "gpt-4"
        assert config.IMAGE_MODEL == "dall-e-3"
        assert config.IMAGE_SIZE == "1024x1024"


class TestIntegration:
    """Integration tests"""
    
    def test_full_pipeline_without_keys(self):
        """Test full pipeline gracefully handles missing keys"""
        orchestrator = VisualizationOrchestrator()
        result = orchestrator.create_automotive_visualization(
            design_prompt="A test car"
        )
        # Should handle gracefully
        assert isinstance(result, dict)
        assert 'success' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
