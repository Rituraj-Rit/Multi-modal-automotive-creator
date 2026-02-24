from typing import Optional, Dict, Any, List
import logging
import re

# Stability AI for image generation (PRIMARY)
from app.services.stabilityai_client import StabilityAIImageClient, generate_image as stability_generate_image

# Text generation clients
from app.services.groq_client import GroqClient
from app.services.openai_client import OpenAIClient
from app.services.ollama_client import OllamaClient
from app.config import settings

logger = logging.getLogger(__name__)


def is_quota_error(error: Exception) -> bool:
    """
    Check if the error is a quota/rate-limit error (429, 403, or resource exhausted).
    """
    error_str = str(error).lower()
    
    # Check for 429 (rate limit) errors
    if "429" in error_str:
        return True
    
    # Check for quota exceeded messages
    if "quota" in error_str and ("exceeded" in error_str or "exhausted" in error_str):
        return True
    
    # Check for resource exhausted
    if "resource_exhausted" in error_str:
        return True
    
    # Check for 403 forbidden (API key issues)
    if "403" in error_str:
        return True
    
    # Check for billing/quota related messages
    if "billing" in error_str or "plan" in error_str:
        return True
    
    return False


def is_retryable_error(error: Exception) -> bool:
    """
    Check if the error is retryable (temporary failure, not permanent).
    """
    error_str = str(error).lower()
    
    # Quota errors are retryable (with different provider)
    if is_quota_error(error):
        return True
    
    # Timeout errors are retryable
    if "timeout" in error_str or "timed out" in error_str:
        return True
    
    # Service unavailable
    if "503" in error_str or "unavailable" in error_str:
        return True
    
    # Rate limiting
    if "rate limit" in error_str:
        return True
    
    # Connection errors for local Ollama
    if "cannot connect" in error_str or "connection" in error_str:
        return True
    
    return False


class UnifiedClient:
    """
    Unified client for text and image generation.
    - Text chat: Uses Ollama (local) as primary
    - Image generation: Uses Stability AI (PRIMARY)
    """
    
    def __init__(self):
        # Text generation clients
        self.openai_client = None
        self.ollama_client = None
        self.groq_client = None
        
        # Image generation client
        self.stability_client = None
        
        # Initialize Ollama client (local, no API key needed) - PRIMARY for text
        try:
            self.ollama_client = OllamaClient()
            logger.info("Ollama client initialized (PRIMARY for text)")
        except Exception as e:
            logger.warning(f"Ollama client not available: {e}")
        
        # Initialize OpenAI if API key available (for text only)
        if settings.openai_api_key:
            try:
                self.openai_client = OpenAIClient(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized (text only)")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Initialize Groq if API key available (fallback for text)
        if settings.groq_api_key:
            try:
                self.groq_client = GroqClient(api_key=settings.groq_api_key)
                logger.info("Groq client initialized (fallback for text)")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        
        # Initialize Stability AI for image generation - PRIMARY
        if settings.stability_api_key:
            try:
                self.stability_client = StabilityAIImageClient(api_key=settings.stability_api_key)
                logger.info("Stability AI client initialized (PRIMARY for images)")
            except Exception as e:
                logger.error(f"Failed to initialize Stability AI client: {e}")
        else:
            logger.warning("STABILITY_API_KEY not configured - image generation will not work")
    
    def _extract_response(self, result: Any, method_name: str) -> Any:
        """
        Extract the actual response from provider results, handling different formats.
        """
        # Handle None
        if result is None:
            return None
        
        # If it's a string, return it directly
        if isinstance(result, str):
            return result
        
        # If it's a dict, extract the appropriate field
        if isinstance(result, dict):
            # Check for success field
            if not result.get("success", True):
                error_msg = result.get("error", "Unknown error")
                raise Exception(error_msg)
            
            # Try to extract the response based on method name
            if method_name == "chat":
                return result.get("response", "")
            elif method_name == "generate_narrative":
                return result.get("narrative", "")
            elif method_name == "enhance_prompt":
                return result.get("enhanced_prompt", "")
            elif method_name == "generate_image":
                return result.get("image_url", "")
            else:
                # Return the whole dict if we can't determine the type
                return result
        
        # Return as-is for other types
        return result
    
    def _try_text_providers(self, method_name: str, *args, **kwargs) -> Any:
        """
        Try each text provider in order until one succeeds.
        Falls back to next provider on quota/rate-limit errors.
        """
        errors = []
        
        # Get preferred provider from settings
        preferred = getattr(settings, 'preferred_provider', 'ollama').lower()
        logger.info(f"Preferred text provider: {preferred}")
        
        # Define provider order for text - OLLAMA is PRIMARY, GROQ is fallback
        provider_order = []
        if preferred == "ollama":
            provider_order = ["ollama", "openai", "groq"]
        elif preferred == "openai":
            provider_order = ["openai", "groq", "ollama"]
        elif preferred == "groq":
            provider_order = ["groq", "ollama", "openai"]
        else:
            # Default: Ollama first, then Groq
            provider_order = ["ollama", "groq", "openai"]
        
        logger.info(f"Text provider order: {provider_order}")
        
        for provider in provider_order:
            try:
                result = None
                
                if provider == "openai" and self.openai_client:
                    # Map method names for OpenAI
                    mapped_method = method_name
                    if method_name == "chat":
                        mapped_method = "generate_chat_response"
                    client_method = getattr(self.openai_client, mapped_method, None)
                    if client_method:
                        logger.info(f"Trying {provider} for {method_name}")
                        # Only pass the first argument (messages for chat)
                        if mapped_method == "generate_chat_response":
                            result = client_method(args[0] if args else [])
                        elif mapped_method == "generate_narrative":
                            result = client_method(args[0] if args else "", kwargs.get("context"))
                        elif mapped_method == "enhance_prompt":
                            result = client_method(args[0] if args else "")
                        else:
                            result = client_method(*args, **kwargs)
                        
                        # Extract response from OpenAI format
                        extracted = self._extract_response(result, method_name)
                        logger.info(f"{provider} succeeded for {method_name}")
                        return extracted
                
                elif provider == "ollama" and self.ollama_client:
                    client_method = getattr(self.ollama_client, method_name, None)
                    if client_method:
                        logger.info(f"Trying {provider} for {method_name}")
                        result = client_method(*args, **kwargs)
                        # Ollama returns raw string, just return it
                        logger.info(f"{provider} succeeded for {method_name}")
                        return result
                
                elif provider == "groq" and self.groq_client:
                    # Map method names for Groq
                    mapped_method = method_name
                    if method_name == "chat":
                        mapped_method = "generate_chat_response"
                    client_method = getattr(self.groq_client, mapped_method, None)
                    if client_method:
                        logger.info(f"Trying {provider} for {method_name}")
                        # Only pass the first argument (messages for chat)
                        if mapped_method == "generate_chat_response":
                            result = client_method(args[0] if args else [])
                        elif mapped_method == "generate_narrative":
                            result = client_method(args[0] if args else "", kwargs.get("context"))
                        elif mapped_method == "enhance_prompt":
                            result = client_method(args[0] if args else "")
                        else:
                            result = client_method(*args, **kwargs)
                        
                        # Extract response from Groq format
                        extracted = self._extract_response(result, method_name)
                        logger.info(f"{provider} succeeded for {method_name}")
                        return extracted
                        
            except Exception as e:
                error_msg = str(e)
                is_quota = is_quota_error(e)
                is_retryable = is_retryable_error(e)
                
                logger.warning(f"{provider} failed for {method_name}: {error_msg}")
                
                if is_quota:
                    logger.warning(f"Quota/rate-limit error detected for {provider}. Will try next provider.")
                elif not is_retryable:
                    logger.warning(f"Non-retryable error from {provider}. Will try next provider.")
                
                errors.append(f"{provider}: {error_msg}")
                
                # Continue to next provider
                continue
        
        # All providers failed
        error_msg = f"All providers failed for {method_name}: {'; '.join(errors)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def generate_narrative(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate an automotive narrative using Groq only.
        
        Args:
            prompt: The prompt for narrative generation
            context: Optional context
            
        Returns:
            Generated narrative text
        """
        # Use Groq directly for narrative generation - no fallback to Ollama
        if not self.groq_client:
            raise Exception("Groq API key not configured. Please set GROQ_API_KEY in .env")
        
        try:
            logger.info(f"Generating narrative with Groq: {prompt[:50]}...")
            result = self.groq_client.generate_narrative(prompt, context)
            
            if result.get("success"):
                narrative = result.get("response", "")
                logger.info(f"Narrative generated successfully: {len(narrative)} chars")
                return narrative
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"Groq narrative generation failed: {error}")
                raise Exception(error)
                
        except Exception as e:
            logger.error(f"Narrative generation error: {str(e)}")
            raise Exception(f"Narrative generation failed: {str(e)}")
    
    def generate_image(self, prompt: str, size: str = "1024x1024", 
                      quality: str = "standard", style: str = "vivid") -> str:
        """
        Generate an image using Stability AI.
        
        Args:
            prompt: The text description of the image
            size: Image size (passed for compatibility)
            quality: Image quality (passed for compatibility)
            style: Image style (passed for compatibility)
            
        Returns:
            Image URL or error message
        """
        try:
            logger.info(f"Generating image with Stability AI: {prompt[:50]}...")
            
            # Parse size to width/height
            width, height = 1024, 1024
            if size and "x" in size:
                try:
                    width, height = map(int, size.split("x"))
                except:
                    pass
            
            # Use Stability AI for image generation
            result = stability_generate_image(
                prompt=prompt,
                width=width,
                height=height
            )
            
            if result.get("success"):
                image_url = result.get("image_url")
                logger.info(f"Image generated successfully")
                return image_url
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"Stability AI image generation failed: {error}")
                raise Exception(error)
                
        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            raise Exception(f"Image generation failed: {str(e)}")
    
    def enhance_prompt(self, prompt: str) -> str:
        """Enhance a prompt."""
        # Use local enhancement if no API keys available
        if not self.openai_client and not self.ollama_client and not self.groq_client:
            return self._local_enhance(prompt)
        
        return self._try_text_providers("enhance_prompt", prompt)
    
    def _local_enhance(self, prompt: str) -> str:
        """Local prompt enhancement without API calls."""
        enhancements = [
            "ultra-realistic, photorealistic",
            "cinematic quality, 8k resolution",
            "highly detailed, professional photography",
            "natural lighting, sharp focus",
            "modern automotive design",
            "sleek aerodynamic body",
            "studio lighting, reflections",
            "carbon fiber accents",
            "metallic paint finish",
            "luxury interior"
        ]
        
        # Add random enhancements
        import random
        selected = random.sample(enhancements, min(5, len(enhancements)))
        
        return f"{prompt}, {', '.join(selected)}"
    
    def chat(self, messages: List[Dict[str, str]], context: Optional[str] = None) -> str:
        """Chat with the AI."""
        return self._try_text_providers("chat", messages, context=context)
