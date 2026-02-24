from openai import OpenAI
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Client for interacting with OpenAI API for text generation."""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def generate_narrative(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an automotive description/narrative based on the prompt.
        
        Args:
            prompt: The user's prompt describing the car concept
            context: Optional context from previous conversations
            
        Returns:
            Dictionary containing the generated narrative and metadata
        """
        system_prompt = """You are an expert automotive designer and storyteller. 
Your task is to create compelling, detailed descriptions of automotive concepts.
Describe the vehicle's design philosophy, key features, visual elements, and the 
emotion it evokes. Use vivid, professional language suitable for presentations 
and marketing materials."""
        
        if context:
            system_prompt += f"\n\nPrevious context: {context}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            return {
                "success": True,
                "narrative": response.choices[0].message.content,
                "model": "gpt-4",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            }
        except Exception as e:
            logger.error(f"Error generating narrative: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "narrative": None
            }
    
    def generate_chat_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generate a chat response for automotive-related queries.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Dictionary containing the response and metadata
        """
        system_prompt = """You are an AI assistant specialized in automotive design and technology.
Provide helpful, informative responses about car design, automotive history, 
emerging technologies, and concept vehicles."""
        
        try:
            all_messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=all_messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model": "gpt-4",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            }
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    def enhance_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """
        Enhance a user prompt for better image generation results.
        
        Args:
            user_prompt: The original user prompt
            
        Returns:
            Dictionary containing the enhanced prompt
        """
        system_prompt = """You are an expert at crafting prompts for AI image generation.
Your task is to enhance user prompts for DALL-E image generation, especially for
automotive concepts. Add detailed visual descriptions, lighting, perspective,
and style elements. Keep the prompt concise but descriptive."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Enhance this prompt for image generation: {user_prompt}"}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return {
                "success": True,
                "enhanced_prompt": response.choices[0].message.content
            }
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "enhanced_prompt": user_prompt
            }
