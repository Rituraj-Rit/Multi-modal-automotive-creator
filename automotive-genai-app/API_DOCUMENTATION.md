# API Documentation

## Base URL

```
http://localhost:5000/api
```

---

## Endpoints Overview

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check API health and configuration |
| `/generate` | POST | Generate visualization (narrative + image) |
| `/narrative` | POST | Generate design narrative only |
| `/image-prompt` | POST | Optimize narrative into image prompt |
| `/batch` | POST | Batch generate multiple visualizations |
| `/config` | GET | Get current configuration |

---

## Endpoint Details

### 1. Health Check

**GET** `/api/health`

Check if all required APIs are configured.

**Response:**

```json
{
  "status": "healthy",
  "configuration": {
    "llm_configured": true,
    "image_api_configured": true,
    "all_configured": true,
    "message": "All APIs configured successfully!"
  }
}
```

**Status Codes:**
- `200`: All systems healthy
- `206`: Partial configuration (degraded)
- `500`: Configuration error

---

### 2. Generate Full Visualization

**POST** `/api/generate`

Generate both narrative and image from design prompt.

**Request Body:**

```json
{
  "design_prompt": "A sleek electric sports car with aggressive angular lines...",
  "context": "Year 2026, luxury segment, eco-friendly",
  "enhance_image": false
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `design_prompt` | string | Yes | Design concept description (10-2000 chars) |
| `context` | string | No | Additional context or constraints |
| `enhance_image` | boolean | No | Whether to upscale generated image (default: false) |

**Response (Success):**

```json
{
  "success": true,
  "narrative": "A stunning automotive design concept that represents the pinnacle of modern...",
  "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "image_prompt": "A sleek electric sports car, aggressive angular design, metallic blue...",
  "metadata": {
    "llm_tokens": 487,
    "image_model": "dall-e-3",
    "image_provider": "dalle",
    "image_enhanced": false
  }
}
```

**Response (Error):**

```json
{
  "success": false,
  "error": "Failed to generate narrative",
  "narrative": null,
  "image_data": null
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (missing/invalid parameters)
- `500`: Server error

**Timing:** Typically 30-60 seconds

---

### 3. Generate Narrative Only

**POST** `/api/narrative`

Generate only the design narrative without image.

**Request Body:**

```json
{
  "prompt": "A futuristic autonomous taxi",
  "context": "Urban mobility, sustainable, year 2030"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Design prompt |
| `context` | string | No | Additional context |

**Response:**

```json
{
  "success": true,
  "narrative": "This autonomous taxi concept represents...",
  "model": "gpt-4",
  "tokens_used": 342,
  "prompt": "A futuristic autonomous taxi"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request
- `500`: Server error

**Timing:** 5-15 seconds

---

### 4. Generate Image Prompt

**POST** `/api/image-prompt`

Convert design narrative into optimized image generation prompt.

**Request Body:**

```json
{
  "narrative": "This luxury sedan features a low, sleek profile with dramatic curves..."
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `narrative` | string | Yes | Design narrative to optimize |

**Response:**

```json
{
  "success": true,
  "image_prompt": "Luxury sedan, sleek low profile, dramatic curves, ambient LED lighting...",
  "tokens_used": 156
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request
- `500`: Server error

---

### 5. Batch Generation

**POST** `/api/batch`

Generate visualizations for multiple design prompts.

**Request Body:**

```json
{
  "prompts": [
    "A rugged off-road SUV with aggressive styling",
    "A luxury electric sedan with minimalist design",
    "A compact city car for urban commuting"
  ],
  "context": "Year 2026, sustainable materials, advanced technology"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompts` | array | Yes | Array of design prompts (min 1, max 10) |
| `context` | string | No | Shared context for all prompts |

**Response:**

```json
{
  "success": true,
  "count": 3,
  "results": [
    {
      "success": true,
      "narrative": "...",
      "image_data": "...",
      "image_prompt": "..."
    },
    {...},
    {...}
  ]
}
```

**Notes:**
- Processes sequentially (slower for many prompts)
- Each result has same structure as `/generate` endpoint
- Failed individual prompts don't stop batch processing

**Status Codes:**
- `200`: Batch submitted successfully
- `400`: Bad request (invalid prompts array)
- `500`: Server error

**Timing:** (30-60 seconds) × number of prompts

---

### 6. Configuration

**GET** `/api/config`

Get current application configuration (sanitized).

**Response:**

```json
{
  "image_provider": "dalle",
  "image_model": "dall-e-3",
  "llm_model": "gpt-4",
  "validation": {
    "llm_configured": true,
    "image_api_configured": true,
    "all_configured": true,
    "message": "All APIs configured successfully!"
  }
}
```

**Status Codes:**
- `200`: Success

---

## Error Handling

### Error Response Format

All error responses follow this format:

```json
{
  "success": false,
  "error": "Description of what went wrong"
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing required field: 'design_prompt'` | Required field not provided | Include design_prompt in request |
| `Design prompt cannot be empty` | Empty or whitespace-only prompt | Provide meaningful design description |
| `OpenAI API Error: Invalid API key` | API key invalid or expired | Verify API key in .env file |
| `API Error: 429` | Rate limit exceeded | Wait before retrying |
| `Server error` | Internal server error | Check logs, verify configuration |

---

## Usage Examples

### Using cURL

**Generate Visualization:**

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "design_prompt": "A sleek sports car with neon accents",
    "enhance_image": false
  }'
```

**Health Check:**

```bash
curl http://localhost:5000/api/health
```

**Batch Generation:**

```bash
curl -X POST http://localhost:5000/api/batch \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": ["Car design 1", "Car design 2"],
    "context": "Luxury segment"
  }'
```

### Using Python (requests library)

```python
import requests
import base64

# Generate visualization
response = requests.post(
    "http://localhost:5000/api/generate",
    json={
        "design_prompt": "A futuristic hypercar with gull-wing doors",
        "context": "High-performance, year 2030",
        "enhance_image": True
    }
)

result = response.json()

if result['success']:
    # Save image
    image_bytes = base64.b64decode(result['image_data'])
    with open('car_design.png', 'wb') as f:
        f.write(image_bytes)
    
    print("Narrative:")
    print(result['narrative'])
    print("\nImage Prompt:")
    print(result['image_prompt'])
else:
    print(f"Error: {result['error']}")
```

### Using JavaScript (Fetch API)

```javascript
const generateVisualization = async () => {
    const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            design_prompt: "A luxury SUV with premium materials",
            context: "Executive transportation",
            enhance_image: false
        })
    });

    const result = await response.json();

    if (result.success) {
        console.log('Narrative:', result.narrative);
        
        // Display image
        const img = new Image();
        img.src = `data:image/png;base64,${result.image_data}`;
        document.body.appendChild(img);
    } else {
        console.error('Error:', result.error);
    }
};
```

---

## Rate Limiting & Quotas

**Recommended Practices:**

- Limit requests to prevent quota exhaustion
- Cache results for identical prompts
- Monitor token usage
- Use batch processing for multiple requests
- Implement exponential backoff for retries

**Token Estimation:**

- Average narrative: 400-600 tokens
- Average image prompt: 100-200 tokens
- Total per visualization: 500-800 tokens

---

## Response Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Use returned data |
| 206 | Partial Success | Check configuration status |
| 400 | Bad Request | Fix request parameters |
| 404 | Not Found | Check endpoint URL |
| 500 | Server Error | Check logs, retry later |
| 503 | Service Unavailable | External API down, retry later |

---

## CORS & Security

**CORS Configuration:**

- Allowed origins: * (can be restricted)
- Allowed methods: GET, POST
- Allowed headers: Content-Type

**Security Headers (Production):**

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

---

## Performance Metrics

**Typical Response Times:**

- Health check: < 100ms
- Narrative generation: 5-15 seconds
- Image prompt generation: 2-5 seconds
- Image generation: 20-45 seconds
- Full pipeline: 30-60 seconds

**Optimization Tips:**

1. Reduce `LLM_MAX_TOKENS` for faster responses
2. Use shorter, more concise prompts
3. Disable image enhancement if not needed
4. Batch related requests
5. Cache repeated requests

---

## Webhook Integration (Future)

Planned for v1.1:

```javascript
// Future: Async processing with webhooks
POST /api/generate-async
{
  "design_prompt": "...",
  "webhook_url": "https://yourapp.com/callback",
  "webhook_secret": "your_secret"
}

// Webhook payload:
{
  "request_id": "req_123456",
  "success": true,
  "data": {...}
}
```

---

## API Changelog

### v1.0 (Current)

- Basic generate endpoint
- Narrative generation
- Image generation (DALL-E 3)
- Batch processing
- Configuration endpoint

### Planned Features

- Async processing with webhooks
- Design history tracking
- Collaborative features
- Additional image providers
- Premium upscaling
- Style transfer options

---

**For detailed usage examples, see EXAMPLES.md**

**For setup instructions, see SETUP_GUIDE.md**

**For general information, see README.md**
