# Docker Deployment Guide

## Overview
This guide covers deploying the Automotive GenAI application using Docker and Docker Compose.

## Prerequisites
- Docker (v20.10+)
- Docker Compose (v1.29+)
- OpenAI API key (for LLM_API_KEY)
- Image generation API key (for IMAGE_API_KEY)

## Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd automotive-genai-app
cp .env.example .env
```

### 2. Configure Environment Variables
Edit `.env` and add your API keys:
```bash
LLM_API_KEY=your_openai_key_here
IMAGE_API_KEY=your_image_api_key_here
```

### 3. Build and Run with Docker Compose
```bash
docker-compose up --build
```

The application will be available at `http://localhost:5000`

## Docker Commands

### Build Image
```bash
docker build -t automotive-genai:latest .
```

### Run Container
```bash
docker run -d \
  -p 5000:5000 \
  -e LLM_API_KEY=your_key \
  -e IMAGE_API_KEY=your_key \
  --name automotive-genai \
  automotive-genai:latest
```

### View Logs
```bash
docker logs -f automotive-genai
```

### Stop Container
```bash
docker stop automotive-genai
docker rm automotive-genai
```

## Docker Compose Commands

### Start Services
```bash
docker-compose up
```

### Start in Background
```bash
docker-compose up -d
```

### Rebuild Images
```bash
docker-compose up --build
```

### Stop Services
```bash
docker-compose down
```

### Remove All (including volumes)
```bash
docker-compose down -v
```

## Production Deployment

### Environment Setup
For production, create a `.env.production` file with:
```bash
FLASK_ENV=production
FLASK_DEBUG=False
LLM_API_KEY=<your-prod-key>
IMAGE_API_KEY=<your-prod-key>
```

### Scaling with Multiple Workers
Edit `Dockerfile` to adjust worker count:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", ...]
```

### Using External Database (Optional)
Modify `docker-compose.yml` to add persistent storage:
```yaml
volumes:
  data:
    driver: local
```

## Monitoring

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Docker Health Status
```bash
docker ps --filter "name=automotive-genai"
```

## Troubleshooting

### Container Won't Start
```bash
docker-compose logs automotive-genai
```

### Port Already in Use
```bash
docker-compose down
# or change port in docker-compose.yml
```

### API Key Issues
Verify environment variables:
```bash
docker exec automotive-genai env | grep API_KEY
```

## Performance Optimization

1. **Multi-stage builds** - Reduce image size
2. **Caching** - Leverage Docker layer caching
3. **Resource limits** - Add to docker-compose.yml:
```yaml
services:
  automotive-genai:
    mem_limit: 2g
    cpus: '2'
```

## Security Best Practices

1. **Don't commit `.env`** - Only commit `.env.example`
2. **Use secrets management** - For production, use Docker Swarm Secrets or Kubernetes
3. **Regular updates** - Keep base image and dependencies updated
4. **Network isolation** - Use Docker networks for inter-service communication

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Build and push Docker image
  run: |
    docker build -t automotive-genai:${{ github.sha }} .
    docker tag automotive-genai:${{ github.sha }} automotive-genai:latest
```
