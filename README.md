# Multimodal Automotive Creator

A multimodal GenAI application for Automotive concept visualization that integrates LLMs with Image Generation models to translate textual prompts into both descriptive narratives and high-fidelity visual representations.

## Features

- **Text-to-Text**: Generate detailed automotive descriptions with GPT-4
- **Text-to-Image**: Create stunning car designs with DALL-E 3
- **Chat Interface**: Interact with an AI assistant specialized in automotive design
- **History & Search**: Store, retrieve, and search through your generated concepts
- **Vector Storage**: ChromaDB for semantic search and history management

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite + Tailwind CSS
- **LLM**: OpenAI GPT-4
- **Image Generation**: DALL-E 3
- **Vector Database**: ChromaDB

## Prerequisites

- Python 3.8+
- Node.js 18+
- OpenAI API Key

## Installation

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
pip install -r requirements.txt
```

### Frontend

```
bash
cd frontend
npm install
```

## Running the Application

### Start Backend

```
bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Start Frontend

```
bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

## API Endpoints

- `POST /api/generate/narrative` - Generate automotive descriptions
- `POST /api/generate/image` - Generate car design images
- `POST /api/generate/both` - Generate both narrative and image
- `POST /api/chat` - Chat with automotive AI assistant
- `POST /api/prompt/enhance` - Enhance prompts for better image generation
- `GET /api/history` - Get generation history
- `POST /api/search` - Search similar generations

## Usage

1. Open the application in your browser
2. Go to Settings and enter your OpenAI API key
3. Use the Create panel to:
   - Enter a description of your desired car
   - Select generation mode (Narrative, Image, or Both)
   - Configure image settings (size, quality, style)
   - Click Generate to create your automotive concept
4. View and manage your generated concepts in the History panel
5. Chat with the AI assistant for automotive design advice
