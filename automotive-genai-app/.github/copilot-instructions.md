# Automotive GenAI Visualization - Project Instructions

## Project Overview
This is a multimodal GenAI application that integrates LLMs with Image Generation models to create automotive concept visualizations. The system translates textual prompts into both descriptive narratives and high-fidelity visual representations.

## Architecture
- **Backend**: Flask API with LLM and Image Generation integrations
- **Frontend**: HTML/CSS/JavaScript web UI
- **Core Modules**: LLM Handler, Image Generator, Orchestrator
- **Configuration**: Environment-based settings for API credentials

## Setup Instructions
1. Install Python dependencies: `pip install -r requirements.txt`
2. Configure environment variables in `.env` file
3. Run the Flask application: `python src/app.py`
4. Access the UI at `http://localhost:5000`

## API Integrations
- **LLM API**: OpenAI or similar (for text narrative generation)
- **Image Generation API**: DALL-E, Midjourney, or Stable Diffusion API
