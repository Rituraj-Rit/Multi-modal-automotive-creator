from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any
import logging
import os
from pathlib import Path

from app.config import settings
from app.models import (
    GenerateNarrativeRequest, GenerateImageRequest, GenerateBothRequest,
    ChatRequest, SearchRequest, EnhancePromptRequest,
    NarrativeResponse, ImageResponse, GenerationResponse, ChatResponse,
    HistoryResponse, SearchResponse, EnhancePromptResponse, HealthResponse
)
from app.services import UnifiedClient, VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A GenAI application for Automotive concept visualization using Stability AI for image generation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
unified_client: UnifiedClient = None
vector_store: VectorStore = None

# Collection name for history
HISTORY_COLLECTION = "automotive_generations"


def get_unified_client() -> UnifiedClient:
    """Dependency to get unified client."""
    global unified_client
    if not unified_client:
        unified_client = UnifiedClient()
    return unified_client


def get_vector_store() -> VectorStore:
    """Dependency to get vector store."""
    global vector_store
    if not vector_store:
        vector_store = VectorStore(settings.chroma_persist_dir)
    return vector_store


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global unified_client, vector_store
    
    logger.info("Starting Automotive Image Generator...")
    
    # Initialize vector store
    vector_store = VectorStore(settings.chroma_persist_dir)
    logger.info("Vector store initialized")
    
    # Initialize unified client
    unified_client = UnifiedClient()
    logger.info("Unified client initialized")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Automotive Image Generator API", "version": "1.0.0"}


@app.get("/api/health", tags=["Health"], response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        services={
            "unified_client": "configured",
            "vector_store": "ready"
        }
    )


@app.post("/api/narrative", tags=["Narrative"], response_model=NarrativeResponse)
async def generate_narrative(
    request: GenerateNarrativeRequest,
    client: UnifiedClient = Depends(get_unified_client)
):
    """
    Generate an automotive narrative/description.
    """
    try:
        result = client.generate_narrative(
            prompt=request.prompt,
            context=request.context
        )
        
        return NarrativeResponse(
            success=True,
            narrative=result
        )
            
    except Exception as e:
        logger.error(f"Error generating narrative: {str(e)}")
        return NarrativeResponse(success=False, error=str(e))


@app.post("/api/image", tags=["Image"], response_model=ImageResponse)
async def generate_image(
    request: GenerateImageRequest,
    client: UnifiedClient = Depends(get_unified_client)
):
    """
    Generate a car image using Stability AI.
    """
    try:
        # Enhance prompt if requested
        final_prompt = request.prompt
        if request.enhance_prompt:
            enhanced = client.enhance_prompt(request.prompt)
            final_prompt = enhanced
        
        result = client.generate_image(
            prompt=final_prompt,
            size=request.size,
            quality=request.quality,
            style=request.style
        )
        
        if result:
            return ImageResponse(
                success=True,
                image_url=result,
                revised_prompt=final_prompt
            )
        else:
            return ImageResponse(
                success=False,
                error="Image generation failed"
            )
            
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        return ImageResponse(success=False, error=str(e))


@app.post("/api/generate", tags=["Generation"], response_model=GenerationResponse)
async def generate_both(
    request: GenerateBothRequest,
    client: UnifiedClient = Depends(get_unified_client),
    store: VectorStore = Depends(get_vector_store)
):
    """
    Generate both narrative and image.
    """
    try:
        # Generate narrative
        narrative = client.generate_narrative(
            prompt=request.prompt,
            context=request.context
        )
        
        # Generate image
        final_prompt = request.prompt
        if request.enhance_prompt:
            final_prompt = client.enhance_prompt(request.prompt)
        
        image_url = client.generate_image(
            prompt=final_prompt,
            size=request.image_size,
            quality=request.image_quality,
            style=request.image_style
        )
        
        # Save to history if requested
        record_id = None
        if request.save_to_history and image_url:
            record_id = store.add_generation(
                collection_name=HISTORY_COLLECTION,
                prompt=request.prompt,
                narrative=narrative,
                image_url=image_url
            )
        
        return GenerationResponse(
            success=True,
            prompt=request.prompt,
            narrative=narrative,
            image_url=image_url,
            revised_prompt=final_prompt,
            record_id=record_id
        )
        
    except Exception as e:
        logger.error(f"Error in generate both: {str(e)}")
        return GenerationResponse(success=False, prompt=request.prompt, error=str(e))


@app.post("/api/chat", tags=["Chat"], response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    client: UnifiedClient = Depends(get_unified_client)
):
    """
    Chat with the AI about automotive concepts.
    """
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        response = client.chat(
            messages=messages,
            context=request.context
        )
        
        return ChatResponse(
            success=True,
            response=response
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return ChatResponse(success=False, response="", error=str(e))


@app.post("/api/prompt/enhance", tags=["Tools"], response_model=EnhancePromptResponse)
async def enhance_prompt(
    request: EnhancePromptRequest,
    client: UnifiedClient = Depends(get_unified_client)
):
    """
    Enhance a prompt for better image generation results.
    """
    try:
        enhanced = client.enhance_prompt(request.prompt)
        
        return EnhancePromptResponse(
            success=True,
            enhanced_prompt=enhanced
        )
            
    except Exception as e:
        logger.error(f"Error in enhance_prompt: {str(e)}")
        return EnhancePromptResponse(success=False, enhanced_prompt=request.prompt, error=str(e))


@app.get("/api/history", tags=["History"], response_model=HistoryResponse)
async def get_history(
    limit: int = 20,
    store: VectorStore = Depends(get_vector_store)
):
    """
    Get generation history.
    """
    try:
        history = store.get_history(HISTORY_COLLECTION, limit)
        
        history_items = []
        for item in history:
            meta = item.get("metadata", {})
            history_items.append(HistoryItem(
                id=item.get("id"),
                prompt=meta.get("prompt", ""),
                narrative=meta.get("narrative", ""),
                image_url=meta.get("image_url", ""),
                created_at=meta.get("created_at", "")
            ))
        
        return HistoryResponse(
            success=True,
            history=history_items,
            count=len(history_items)
        )
        
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return HistoryResponse(success=False, history=[], count=0)


@app.post("/api/search", tags=["Search"], response_model=SearchResponse)
async def search_similar(
    request: SearchRequest,
    store: VectorStore = Depends(get_vector_store)
):
    """
    Search for similar generations based on a query.
    """
    try:
        results = store.search_similar(
            collection_name=HISTORY_COLLECTION,
            query=request.query,
            n_results=request.n_results
        )
        
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                id=result.get("id"),
                document=result.get("document"),
                metadata=result.get("metadata"),
                distance=result.get("distance")
            ))
        
        return SearchResponse(
            success=True,
            results=search_results,
            count=len(search_results)
        )
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return SearchResponse(success=False, results=[], count=0)


@app.delete("/api/history/{record_id}", tags=["History"])
async def delete_history_item(
    record_id: str,
    store: VectorStore = Depends(get_vector_store)
):
    """
    Delete a history item.
    """
    try:
        success = store.delete_record(HISTORY_COLLECTION, record_id)
        if success:
            return {"success": True, "message": "Record deleted"}
        else:
            raise HTTPException(status_code=404, detail="Record not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting record: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
