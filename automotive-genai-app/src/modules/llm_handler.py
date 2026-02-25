from typing import Optional
from src.config import get_config

# Try importing OpenAI SDK; provide graceful fallback with clear error messages
try:
    from openai import OpenAI, APIError
    _OPENAI_AVAILABLE = True
except Exception:
    OpenAI = None
    APIError = Exception
    _OPENAI_AVAILABLE = False

class LLMHandler:
    """
    Handles all LLM interactions for narrative generation.
    Supports OpenAI API and can be extended for other providers.
    """
    
    def __init__(self):
        """Initialize LLM Handler with configuration"""
        self.config = get_config()
        # Create OpenAI client if API key is available
        self.client = None
        if _OPENAI_AVAILABLE and self.config.LLM_API_KEY:
            self.client = OpenAI(api_key=self.config.LLM_API_KEY)
        self.model = self.config.LLM_MODEL
        self.temperature = self.config.LLM_TEMPERATURE
        self.max_tokens = self.config.LLM_MAX_TOKENS
    
    def generate_narrative(self, prompt: str, context: Optional[str] = None) -> dict:
        """
        Generate a detailed automotive design narrative from a text prompt.
        
        Args:
            prompt: User's initial design concept description
            context: Optional additional context about the car design
        
        Returns:
            Dictionary containing narrative and metadata
        """
        # Ensure OpenAI library is available and API key is configured
        if not _OPENAI_AVAILABLE:
            return {
                "success": False,
                "error": "OpenAI Python package not installed. Install with: pip install -r requirements.txt",
                "narrative": None
            }
        
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API key not configured. Set LLM_API_KEY in .env file",
                "narrative": None
            }

        try:
            # Construct the system message for automotive design expertise
            system_message = """You are an expert automotive designer and concept visualizer. 
            You create detailed, vivid descriptions of automotive designs suitable for visualization.
            Focus on design philosophy, aesthetics, key features, materials, and visual characteristics.
            Be concise yet comprehensive."""
            
            # Build the full prompt
            full_prompt = prompt
            if context:
                full_prompt = f"{prompt}\n\nAdditional Context:\n{context}"
            
            # Call OpenAI API using the new client-based interface
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            narrative = response.choices[0].message.content
            
            return {
                "success": True,
                "narrative": narrative,
                "model": self.model,
                "tokens_used": response.usage.total_tokens,
                "prompt": prompt
            }
        
        except APIError as e:
            return {
                "success": False,
                "error": f"OpenAI API Error: {str(e)}",
                "narrative": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "narrative": None
            }
    
    def generate_image_prompt(self, narrative: str) -> dict:
        """
        Convert an automotive narrative into an optimized image generation prompt.
        
        Args:
            narrative: The detailed design narrative
        
        Returns:
            Dictionary containing optimized image prompt
        """
        if not _OPENAI_AVAILABLE:
            return {
                "success": False,
                "error": "OpenAI Python package not installed. Install with: pip install -r requirements.txt",
                "image_prompt": None
            }
        
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API key not configured. Set LLM_API_KEY in .env file",
                "image_prompt": None
            }

        try:
            system_message = """You are an expert prompt engineer specializing in automotive visualization.
            Convert detailed design narratives into concise, vivid prompts suitable for image generation models.
            Focus on visual elements, style, materials, lighting, and composition.
            Keep the prompt under 200 words but detailed and specific."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Convert this narrative into an image prompt:\n\n{narrative}"}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            image_prompt = response.choices[0].message.content
            
            return {
                "success": True,
                "image_prompt": image_prompt,
                "tokens_used": response.usage.total_tokens
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_prompt": None
            }
    
    def validate_api_key(self) -> bool:
        """Validate that the LLM API key is properly configured"""
        return bool(self.config.LLM_API_KEY and self.config.LLM_API_KEY != "your_openai_api_key_here") and _OPENAI_AVAILABLE

