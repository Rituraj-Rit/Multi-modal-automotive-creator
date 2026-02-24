"""
Ollama Client for Local LLM Inference.

This module provides a local LLM interface using Ollama server.
"""

import logging
import requests
import json
from typing import Optional, List, Dict, Any

from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Client for Ollama local LLM server.
    """
    
    DEFAULT_MODEL = "mistral"
    
    def __init__(self, base_url: str = None, model: str = None):
        """
        Initialize the Ollama client.
        
        Args:
            base_url: Base URL for Ollama server (default: http://localhost:11434)
            model: Model name to use (default: mistral)
        """
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model or self.DEFAULT_MODEL
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
        self.top_p = settings.top_p
        self.timeout = 120
        
        logger.info(f"Ollama client initialized")
        logger.info(f"Ollama base URL: {self.base_url}")
        logger.info(f"Ollama model: {self.model}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Content-Type": "application/json"
        }
    
    def _make_request(self, payload: Dict[str, Any]) -> str:
        """
        Make a request to the Ollama API.
        """
        url = f"{self.base_url}/api/generate"
        
        try:
            logger.info(f"Making request to Ollama: {self.model}")
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
        except requests.exceptions.Timeout:
            raise Exception("Ollama request timeout")
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")
    
    def generate(self, prompt: str) -> str:
        """
        Generate text from prompt.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": min(self.max_tokens, 512),
                "temperature": self.temperature,
                "top_p": self.top_p,
            }
        }
        
        return self._make_request(payload)
    
    def chat(self, messages: List[Dict[str, str]], context: str = None) -> str:
        """
        Generate a chat response.
        """
        logger.info(f"Generating chat response ({len(messages)} messages)")
        
        # Build conversation context
        conversation = "You are a helpful automotive expert assistant.\n\n"
        if context:
            conversation += f"Context: {context}\n\n"
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            conversation += f"{role.capitalize()}: {content}\n"
        
        conversation += "Assistant:"
        
        return self.generate(conversation)
    
    def generate_narrative(self, prompt: str, context: str = None) -> str:
        """
        Generate an automotive narrative.
        """
        logger.info(f"Generating narrative with prompt: {prompt[:50]}...")
        
        system_prompt = """You are an expert automotive designer and storyteller. 
Create vivid, detailed descriptions of futuristic vehicle concepts. 
Focus on innovative design elements, cutting-edge technology, and sustainable materials.
Make descriptions inspiring and technically accurate."""

        if context:
            full_prompt = f"{system_prompt}\n\nContext: {context}\n\nPrompt: {prompt}"
        else:
            full_prompt = f"{system_prompt}\n\nPrompt: {prompt}"
        
        return self.generate(full_prompt)
    
    def enhance_prompt(self, prompt: str) -> str:
        """
        Enhance a prompt for better image generation.
        """
        logger.info(f"Enhancing prompt: {prompt[:50]}...")
        
        enhancement_prompt = f"""Enhance the following prompt for ultra-realistic, 
photorealistic image generation. Add quality modifiers like:
cinematic quality, 8k resolution, highly detailed, professional photography, 
natural lighting, sharp focus, modern automotive design.

Original prompt: {prompt}

Enhanced prompt:"""

        enhanced = self.generate(enhancement_prompt)
        return enhanced.strip()


# For backwards compatibility
Client = OllamaClient
