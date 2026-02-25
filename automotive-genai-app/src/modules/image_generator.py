import base64
import io
from typing import Optional, Tuple
from src.config import get_config

# External libraries may be optional in some environments; import safely
try:
    import requests
    _REQUESTS_AVAILABLE = True
except Exception:
    requests = None
    _REQUESTS_AVAILABLE = False

try:
    from PIL import Image
    _PIL_AVAILABLE = True
except Exception:
    Image = None
    _PIL_AVAILABLE = False

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except Exception:
    OpenAI = None
    _OPENAI_AVAILABLE = False


class ImageGenerator:
    """
    Handles image generation for automotive designs.
    Supports multiple image generation APIs (DALL-E, Stable Diffusion, etc.).
    """
    
    def __init__(self, provider: str = "dalle"):
        """
        Initialize Image Generator with specified provider.
        
        Args:
            provider: API provider ('dalle', 'stable_diffusion', 'midjourney')
        """
        self.config = get_config()
        self.provider = provider.lower()
        self.api_key = self.config.IMAGE_API_KEY
        self.model = self.config.IMAGE_MODEL
        self.quality = self.config.IMAGE_QUALITY
        self.size = self.config.IMAGE_SIZE
        # Initialize OpenAI client if API key is available
        self.client = None
        if _OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
    
    def generate_image(self, prompt: str) -> dict:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text prompt describing the image to generate
        
        Returns:
            Dictionary containing image data and metadata
        """
        if self.provider == "dalle":
            return self._generate_dalle_image(prompt)
        elif self.provider == "stable_diffusion":
            return self._generate_stable_diffusion_image(prompt)
        else:
            return {
                "success": False,
                "error": f"Unsupported provider: {self.provider}",
                "image_data": None
            }
    
    def _generate_dalle_image(self, prompt: str) -> dict:
        """Generate image using DALL-E API"""
        try:
            # Check if OpenAI SDK is available
            if not _OPENAI_AVAILABLE:
                return {
                    "success": False,
                    "error": "OpenAI Python package not installed. Install with: pip install -r requirements.txt",
                    "image_data": None
                }
            
            # Check if client is initialized with API key
            if not self.client:
                return {
                    "success": False,
                    "error": "Image API key not configured. Set IMAGE_API_KEY in .env file",
                    "image_data": None
                }

            # Call OpenAI Images API using the new client interface
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.size,
                quality=self.quality,
                n=1
            )

            image_url = response.data[0].url

            # Download and encode the image
            if not _REQUESTS_AVAILABLE:
                return {
                    "success": False,
                    "error": "`requests` package not installed. Install with: pip install -r requirements.txt",
                    "image_data": None
                }

            image_response = requests.get(image_url)
            image_data = base64.b64encode(image_response.content).decode()

            return {
                "success": True,
                "image_data": image_data,
                "image_url": image_url,
                "model": self.model,
                "prompt": prompt,
                "provider": "dalle"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"DALL-E API Error: {str(e)}",
                "image_data": None
            }
    
    def _generate_stable_diffusion_image(self, prompt: str) -> dict:
        """Generate image using Stable Diffusion API (e.g., via Replicate)"""
        try:
            # Example implementation for Stability AI API
            if not _REQUESTS_AVAILABLE:
                return {
                    "success": False,
                    "error": "`requests` package not installed. Install with: pip install -r requirements.txt",
                    "image_data": None
                }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7.5,
                "height": int(self.size.split("x")[1]),
                "width": int(self.size.split("x")[0]),
                "samples": 1,
                "steps": 30,
            }
            
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text}",
                    "image_data": None
                }
            
            data = response.json()
            image_data = base64.b64encode(
                base64.b64decode(data["artifacts"][0]["base64"])
            ).decode()
            
            return {
                "success": True,
                "image_data": image_data,
                "model": self.model,
                "prompt": prompt,
                "provider": "stable_diffusion"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Stable Diffusion API Error: {str(e)}",
                "image_data": None
            }
    
    def enhance_image(self, image_data: str, enhancement_type: str = "upscale") -> dict:
        """
        Enhance a generated image (upscale, denoise, etc.).
        
        Args:
            image_data: Base64 encoded image data
            enhancement_type: Type of enhancement ('upscale', 'denoise', etc.)
        
        Returns:
            Dictionary containing enhanced image data
        """
        try:
            # This is a placeholder for image enhancement
            # Implementation depends on the service used
            
            return {
                "success": True,
                "enhanced_image": image_data,
                "enhancement_type": enhancement_type
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "enhanced_image": None
            }
    
    def validate_api_key(self) -> bool:
        """Validate that the image generation API key is properly configured"""
        return bool(self.api_key and self.api_key != "your_image_api_key_here")
    
    def get_supported_sizes(self) -> list:
        """Get list of supported image sizes"""
        return ["256x256", "512x512", "1024x1024", "1024x1792", "1792x1024"]
    
    def get_supported_qualities(self) -> list:
        """Get list of supported quality levels"""
        return ["standard", "hd"]
