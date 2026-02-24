from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend directory FIRST
# override=True ensures we use .env values instead of system env vars
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path, override=True)

class Settings(BaseModel):
    """Application settings loaded from .env file only - no system env vars."""
    
    model_config = {
        "extra": "ignore"
    }
    
    # Stability AI API Configuration - PRIMARY for image generation
    stability_api_key: str = ""
    
    # OpenAI API Configuration - for text generation only
    openai_api_key: str = ""
    
    # Groq API Configuration - for text generation
    groq_api_key: str = ""
    
    # Ollama Configuration (Local LLM) - PRIMARY for text
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    
    # Preferred text provider (ollama, openai, groq)
    preferred_provider: str = "ollama"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # ChromaDB Configuration
    chroma_persist_dir: str = "./chroma_data"
    
    # Application Configuration
    app_name: str = "Automotive Image Generator"
    debug: bool = True
    
    # Generation Settings
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    
    # Image Generation Settings
    image_width: int = 1024
    image_height: int = 1024
    image_num_inference_steps: int = 30
    image_guidance_scale: float = 7.5
    
    @classmethod
    def from_env(cls):
        """Create settings from .env file only."""
        return cls(
            stability_api_key=os.getenv("STABILITY_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "mistral"),
            preferred_provider=os.getenv("PREFERRED_PROVIDER", "ollama"),
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            chroma_persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./chroma_data"),
            debug=True
        )

# Create settings from .env only
settings = Settings.from_env()

# Log what was loaded (masked)
print(f"Config loaded:")
print(f"  stability_api_key: '{settings.stability_api_key[:10] if settings.stability_api_key else 'EMPTY'}...'")
print(f"  openai_api_key: '{settings.openai_api_key[:10] if settings.openai_api_key else 'EMPTY'}...'")
print(f"  groq_api_key: '{settings.groq_api_key[:10] if settings.groq_api_key else 'EMPTY'}...'")
print(f"  preferred_provider: {settings.preferred_provider}")
print(f"  ollama_model: {settings.ollama_model}")
