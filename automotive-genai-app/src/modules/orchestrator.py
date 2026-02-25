from typing import Optional
from src.modules.llm_handler import LLMHandler
from src.modules.image_generator import ImageGenerator


class VisualizationOrchestrator:
    """
    Orchestrates the multimodal workflow combining LLM and Image Generation.
    Manages the complete pipeline from user prompt to final output.
    """
    
    def __init__(self, image_provider: str = "dalle"):
        """
        Initialize the orchestrator with required modules.
        
        Args:
            image_provider: Image generation provider to use
        """
        self.llm_handler = LLMHandler()
        self.image_generator = ImageGenerator(provider=image_provider)
    
    def create_automotive_visualization(
        self,
        design_prompt: str,
        context: Optional[str] = None,
        enhance_image: bool = False
    ) -> dict:
        """
        Complete workflow: Generate narrative and corresponding image.
        
        Args:
            design_prompt: Initial design concept description
            context: Optional additional context
            enhance_image: Whether to enhance the generated image
        
        Returns:
            Dictionary containing narrative, image, and metadata
        """
        result = {
            "success": False,
            "narrative": None,
            "image_data": None,
            "image_prompt": None,
            "error": None,
            "metadata": {}
        }
        
        # Step 1: Generate narrative
        narrative_result = self.llm_handler.generate_narrative(design_prompt, context)
        
        if not narrative_result.get("success"):
            result["error"] = narrative_result.get("error", "Failed to generate narrative")
            return result
        
        narrative = narrative_result.get("narrative")
        result["narrative"] = narrative
        result["metadata"]["llm_tokens"] = narrative_result.get("tokens_used", 0)
        
        # Step 2: Generate optimized image prompt
        image_prompt_result = self.llm_handler.generate_image_prompt(narrative)
        
        if not image_prompt_result.get("success"):
            result["error"] = image_prompt_result.get("error", "Failed to generate image prompt")
            return result
        
        image_prompt = image_prompt_result.get("image_prompt")
        result["image_prompt"] = image_prompt
        result["metadata"]["image_prompt_tokens"] = image_prompt_result.get("tokens_used", 0)
        
        # Step 3: Generate image
        image_result = self.image_generator.generate_image(image_prompt)
        
        if not image_result.get("success"):
            result["error"] = image_result.get("error", "Failed to generate image")
            return result
        
        result["image_data"] = image_result.get("image_data")
        result["metadata"]["image_model"] = image_result.get("model")
        result["metadata"]["image_provider"] = image_result.get("provider")
        
        # Step 4: Optional image enhancement
        if enhance_image and result["image_data"]:
            enhanced_result = self.image_generator.enhance_image(
                result["image_data"],
                "upscale"
            )
            if enhanced_result.get("success"):
                result["image_data"] = enhanced_result.get("enhanced_image")
                result["metadata"]["image_enhanced"] = True
        
        result["success"] = True
        return result
    
    def batch_create_visualizations(
        self,
        prompts: list,
        context: Optional[str] = None
    ) -> list:
        """
        Create multiple visualizations in batch.
        
        Args:
            prompts: List of design prompts
            context: Optional shared context
        
        Returns:
            List of visualization results
        """
        results = []
        for prompt in prompts:
            result = self.create_automotive_visualization(prompt, context)
            results.append(result)
        
        return results
    
    def validate_configuration(self) -> dict:
        """
        Validate that all required APIs are properly configured.
        
        Returns:
            Dictionary with validation status
        """
        validation = {
            "llm_configured": self.llm_handler.validate_api_key(),
            "image_api_configured": self.image_generator.validate_api_key(),
            "all_configured": False,
            "message": ""
        }
        
        if not validation["llm_configured"]:
            validation["message"] += "LLM API not configured. "
        
        if not validation["image_api_configured"]:
            validation["message"] += "Image API not configured. "
        
        if validation["llm_configured"] and validation["image_api_configured"]:
            validation["all_configured"] = True
            validation["message"] = "All APIs configured successfully!"
        
        return validation
