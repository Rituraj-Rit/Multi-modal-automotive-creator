"""
Stability AI Image Generation Client

This module provides a clean interface to Stability AI API for image generation.
Uses the Stable Diffusion XL 1.0 (SDXL) model.

API Documentation: https://platform.stability.ai/docs/api
"""

import logging
import time
import base64
import requests
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class StabilityAIImageClient:
    """
    Client for Stability AI image generation API.
    Provides robust error handling, timeout, retries, and logging.
    """
    
    MODEL_NAME = "stable-diffusion-xl-1024-v1-0"
    
    API_URL = "https://api.stability.ai/v2beta/image/text-to-image"
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        out_dir: str = "./generated_images", 
        timeout: int = 180, 
        retries: int = 3
    ):
        self.api_key = api_key.strip() if api_key else None
        self.out_path = Path(out_dir)
        self.timeout_val = timeout
        self.max_retry_cnt = retries
        self.out_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"StabilityAIImageClient initialized with model: {self.MODEL_NAME}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _make_request(self, url: str, payload: Dict[str, Any], retry_count: int = 0) -> requests.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            url: API endpoint URL
            payload: Request payload
            retry_count: Current retry attempt
            
        Returns:
            Response object
            
        Raises:
            Exception: If request fails after all retries
        """
        try:
            response = requests.post(
                url, 
                headers=self.get_headers(), 
                json=payload, 
                timeout=self.timeout_val
            )
            
            if response.status_code == 200:
                return response
            elif response.status_code == 429 and retry_count < self.max_retry_cnt - 1:
                # Rate limited - wait and retry
                wait_time = (retry_count + 1) * 10
                logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                return self._make_request(url, payload, retry_count + 1)
            elif response.status_code >= 500 and retry_count < self.max_retry_cnt - 1:
                # Server error - wait and retry
                wait_time = (retry_count + 1) * 5
                logger.warning(f"Server error {response.status_code}. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                return self._make_request(url, payload, retry_count + 1)
            else:
                error_msg = f"API error {response.status_code}: {response.text[:200]}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            if retry_count < self.max_retry_cnt - 1:
                wait_time = (retry_count + 1) * 5
                logger.warning(f"Timeout. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                return self._make_request(url, payload, retry_count + 1)
            raise Exception("Request timeout after all retries")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    def generate_image(
        self, 
        prompt: str, 
        width: int = 1024, 
        height: int = 1024, 
        num_inference_steps: int = 30, 
        guidance_scale: float = 7.5,
        negative_prompt: Optional[str] = None,
        style_preset: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate image using Stability AI Stable Diffusion XL.
        
        Args:
            prompt: Text description of the image to generate
            width: Image width (default: 1024)
            height: Image height (default: 1024)
            num_inference_steps: Number of inference steps (default: 30)
            guidance_scale: Guidance scale for generation (default: 7.5)
            negative_prompt: Things to avoid in the image
            style_preset: Style preset (e.g., "photorealistic", "anime", "cinematic")
            
        Returns:
            Dict with success status, image_url, and optional error
        """
        if not self.api_key:
            logger.error("STABILITY_API_KEY not configured")
            return {
                "success": False, 
                "error": "STABILITY_API_KEY not configured", 
                "image_url": None
            }
        
        # Build request payload according to Stability AI API
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1.0
                }
            ],
            "cfg_scale": guidance_scale,
            "height": min(height, 1024),
            "width": min(width, 1024),
            "steps": min(num_inference_steps, 50),
            "samples": 1
        }
        
        # Add negative prompt if provided
        if negative_prompt:
            payload["text_prompts"].append({
                "text": negative_prompt,
                "weight": -1.0
            })
        
        # Add style preset if provided
        if style_preset:
            payload["style_preset"] = style_preset
        
        try:
            logger.info(f"Generating image with Stability AI: {prompt[:50]}...")
            
            response = self._make_request(self.API_URL, payload)
            
            # Parse the response
            result = response.json()
            
            if "artifacts" in result and len(result["artifacts"]) > 0:
                # Extract base64 image from first artifact
                artifact = result["artifacts"][0]
                if artifact.get("base64"):
                    img_b64 = artifact["base64"]
                    image_url = f"data:image/png;base64,{img_b64}"
                    
                    logger.info(f"Image generated successfully: {len(img_b64)} bytes (base64)")
                    
                    return {
                        "success": True,
                        "image_url": image_url,
                        "error": None,
                        "metadata": {
                            "model": self.MODEL_NAME,
                            "prompt": prompt,
                            "width": payload["width"],
                            "height": payload["height"],
                            "steps": payload["steps"],
                            "cfg_scale": payload["cfg_scale"]
                        }
                    }
                else:
                    raise Exception("No base64 image data in response")
            else:
                error_msg = result.get("message", "Unknown error in response")
                logger.error(f"API returned error: {error_msg}")
                raise Exception(f"API error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return {
                "success": False, 
                "error": str(e), 
                "image_url": None
            }


def generate_image(
    prompt: str, 
    api_token: Optional[str] = None,
    width: int = 1024,
    height: int = 1024,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for image generation.
    
    Args:
        prompt: Text description of the image
        api_token: Stability AI API key (optional, uses env if not provided)
        width: Image width
        height: Image height
        **kwargs: Additional parameters for generate_image
        
    Returns:
        Dict with success status, image_url, and optional error
    """
    from app.config import settings
    
    token = api_token or getattr(settings, 'stability_api_key', None)
    if not token:
        return {
            "success": False, 
            "error": "STABILITY_API_KEY not configured", 
            "image_url": None
        }
    
    client = StabilityAIImageClient(api_key=token)
    return client.generate_image(prompt, width=width, height=height, **kwargs)
