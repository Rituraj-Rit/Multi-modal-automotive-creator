import logging
from typing import Optional
import json


class Logger:
    """Custom logger for application"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level))
        
        # Console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def debug(self, message: str):
        self.logger.debug(message)


def validate_prompt(prompt: str, min_length: int = 10, max_length: int = 2000) -> tuple:
    """
    Validate user prompt input.
    
    Args:
        prompt: User input prompt
        min_length: Minimum prompt length
        max_length: Maximum prompt length
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not prompt or not prompt.strip():
        return False, "Prompt cannot be empty"
    
    if len(prompt) < min_length:
        return False, f"Prompt must be at least {min_length} characters"
    
    if len(prompt) > max_length:
        return False, f"Prompt cannot exceed {max_length} characters"
    
    return True, "Valid prompt"


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: User input text
    
    Returns:
        Sanitized text
    """
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    sanitized = text
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()


def parse_json_response(response_text: str) -> Optional[dict]:
    """
    Safely parse JSON response.
    
    Args:
        response_text: JSON text to parse
    
    Returns:
        Parsed dictionary or None if parsing fails
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
