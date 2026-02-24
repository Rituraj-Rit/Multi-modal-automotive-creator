"""
Groq API Client for text generation.
Fast LLM inference with low latency.
"""
from typing import Optional, Dict, Any, List
import logging
import requests
import time

logger = logging.getLogger(__name__)


class GroqClient:
    """Client for interacting with Groq API for text generation."""
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", 
                 max_tokens: int = 2048, temperature: float = 0.7):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key
            model: Model to use (default: llama-3.3-70b-versatile)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.base_url = "https://api.groq.com/openai/v1"
        self.timeout = 60  # seconds
        
        # Verify API key is set
        if not api_key:
            raise ValueError("Groq API key is required")
    
    def _call_api(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make API call to Groq with retries.
        
        Args:
            endpoint: API endpoint
            payload: Request payload
            
        Returns:
            Response JSON
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Groq API call attempt {attempt + 1}/{max_retries}: {endpoint}")
                
                response = requests.post(
                    url, 
                    json=payload, 
                    headers=headers, 
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limited
                    logger.warning(f"Groq rate limited, attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    raise Exception(f"Groq rate limit exceeded: {response.text}")
                elif response.status_code == 401:
                    raise Exception(f"Groq authentication failed: {response.text}")
                else:
                    raise Exception(f"Groq API error {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Groq timeout, attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise Exception("Groq request timeout")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Groq request error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise Exception(f"Groq request failed: {str(e)}")
        
        raise Exception("Groq max retries exceeded")
    
    def generate_chat_response(self, messages: List[Dict[str, str]], 
                                context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate chat response using Groq.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            context: Optional context to prepend
            
        Returns:
            Dict with success status and response
        """
        try:
            # Build system message with context
            system_content = "You are a helpful automotive AI assistant."
            if context:
                system_content += f"\n\nContext: {context}"
            
            # Build messages for API
            api_messages = [{"role": "system", "content": system_content}]
            
            # Add user messages (limit to last 10 for context window)
            for msg in messages[-10:]:
                api_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            payload = {
                "model": self.model,
                "messages": api_messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": False
            }
            
            result = self._call_api("chat/completions", payload)
            
            # Extract response
            choices = result.get("choices", [])
            if choices:
                response_text = choices[0].get("message", {}).get("content", "")
                return {
                    "success": True,
                    "response": response_text,
                    "model": self.model,
                    "usage": result.get("usage", {})
                }
            else:
                return {
                    "success": False,
                    "error": "No response from Groq",
                    "response": ""
                }
                
        except Exception as e:
            logger.error(f"Groq chat error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": ""
            }
    
    def generate_narrative(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an automotive narrative.
        
        Args:
            prompt: The prompt for narrative generation
            context: Optional context
            
        Returns:
            Dict with success status and narrative
        """
        # Build the full prompt for narrative
        full_prompt = f"""Generate a detailed automotive narrative or description based on the following:
        
{prompt}

Provide an engaging, descriptive narrative about the vehicle or concept."""
        
        if context:
            full_prompt += f"\n\nAdditional context: {context}"
        
        messages = [{"role": "user", "content": full_prompt}]
        
        return self.generate_chat_response(messages, context=None)
    
    def enhance_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Enhance a prompt for better image generation.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Dict with success status and enhanced prompt
        """
        enhancement_prompt = f"""Enhance the following prompt for AI image generation. 
Make it more detailed, vivid, and descriptive while keeping the core concept.

Original prompt: {prompt}

Provide an enhanced version that includes:
- Visual details (colors, lighting, textures)
- Style (photorealistic, cinematic, etc.)
- Technical specifications
- Composition guidance

Enhanced prompt:"""
        
        messages = [{"role": "user", "content": enhancement_prompt}]
        result = self.generate_chat_response(messages)
        
        if result.get("success"):
            return {
                "success": True,
                "enhanced_prompt": result.get("response", prompt)
            }
        else:
            return {
                "success": False,
                "error": result.get("error"),
                "enhanced_prompt": prompt
            }


def get_groq_client(api_key: Optional[str] = None) -> Optional[GroqClient]:
    """
    Get Groq client instance.
    
    Args:
        api_key: Optional API key (will use from settings if not provided)
        
    Returns:
        GroqClient instance or None if no API key
    """
    from app.config import settings
    
    if not api_key:
        api_key = getattr(settings, 'groq_api_key', None)
    
    if not api_key:
        logger.warning("No Groq API key available")
        return None
    
    try:
        return GroqClient(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to create Groq client: {e}")
        return None
