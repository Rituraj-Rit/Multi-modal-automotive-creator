# Examples and Test Cases

## Example 1: Classic Sports Car

**Input Prompt:**
```
A mid-engine sports car with an aggressive aerodynamic design, featuring 
low-slung body, large rear wing, integrated air intakes, and sleek LED 
headlights. The car should have vibrant red metallic paint with black 
racing stripes, widebody kit, and premium lightweight alloy wheels.
```

**Expected Narrative:**
The LLM will generate a detailed narrative describing the design philosophy, 
aerodynamic features, material choices, and visual characteristics of the sports car.

**Image Prompt Generated:**
```
A stunning mid-engine sports car, aggressive low-slung design, vibrant metallic 
red with black racing stripes, large rear wing, aerodynamic curves, LED headlights, 
widebody kit, premium alloy wheels, dynamic motion pose, studio lighting, 
professional automotive photography style.
```

---

## Example 2: Luxury SUV

**Input Prompt:**
```
A large luxury SUV with a commanding presence, featuring a bold chrome grille,
panoramic sunroof, sophisticated LED daytime running lights, and sleek body lines.
Premium leather interior visible through windows, elevated seating position,
all-terrain capability with refined luxury aesthetic.
```

**Context (Optional):**
```
Year 2026, eco-friendly hybrid powertrain, sustainable premium materials,
suitable for executive transportation and family adventures.
```

---

## Example 3: Electric City Car

**Input Prompt:**
```
A compact electric city car designed for urban commuting. Features minimal
design language, rounded forms, efficient battery-integrated floor, smart
LED lighting system, and modular interior. Color-option variations include
sky blue, forest green, and pearl white with matte finishes.
```

---

## API Testing Examples

### Using cURL

```bash
# Test Health Endpoint
curl http://localhost:5000/api/health

# Full Visualization Generation
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "design_prompt": "A futuristic hypercar with gull-wing doors and glowing accents",
    "context": "High-performance, year 2030, sustainable materials",
    "enhance_image": true
  }'
```

### Using Python

```python
import requests
import json

API_URL = "http://localhost:5000/api"

# Generate Visualization
payload = {
    "design_prompt": "A luxury electric sedan with minimalist design",
    "context": "Premium segment, sustainable, executive vehicle",
    "enhance_image": False
}

response = requests.post(
    f"{API_URL}/generate",
    json=payload
)

result = response.json()

if result['success']:
    print("Narrative:", result['narrative'])
    print("Image Prompt:", result['image_prompt'])
    # Save image
    with open('car_design.png', 'wb') as f:
        import base64
        f.write(base64.b64decode(result['image_data']))
else:
    print("Error:", result['error'])
```

### Using JavaScript/Fetch

```javascript
const payload = {
    design_prompt: "A rugged off-road SUV with aggressive styling",
    context: "All-terrain capability, adventure-focused, modern tech",
    enhance_image: false
};

fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
})
.then(res => res.json())
.then(data => {
    if (data.success) {
        console.log("Design Narrative:", data.narrative);
        console.log("Image Prompt:", data.image_prompt);
        // Display image
        const img = new Image();
        img.src = `data:image/png;base64,${data.image_data}`;
        document.body.appendChild(img);
    }
});
```

---

## Design Prompt Tips

### DO's ✅

- **Be Descriptive**: Include specific design elements, colors, and materials
- **Define Context**: Mention time period, vehicle segment, use case
- **Use Adjectives**: Sleek, aggressive, elegant, rugged, minimalist, etc.
- **Reference Inspirations**: "Inspired by nature," "retro-futuristic," etc.
- **Specify Materials**: Carbon fiber, leather, matte finish, chrome accents
- **Detail Lighting**: LED, neon, glowing accents, ambient lighting

### DON'Ts ❌

- Avoid vague descriptions: "Cool car" vs "Sleek electric sports car"
- Don't mix conflicting styles: Ultra-luxury + extreme off-road rarely match
- Avoid overly technical specs without visual description
- Don't request dangerous, illegal, or inappropriate designs
- Avoid excessive length (keep under 200-300 words for optimal results)

---

## Batch Processing Example

```bash
curl -X POST http://localhost:5000/api/batch \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [
      "A sleek city taxi with autonomous capabilities",
      "A rugged adventure SUV for off-road exploration",
      "A luxury sedan with premium materials"
    ],
    "context": "Year 2026, electric or hybrid powertrains"
  }'
```

---

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 src.app:app
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.app:app"]
```

Build and run:

```bash
docker build -t automotive-genai .
docker run -p 5000:5000 --env-file .env automotive-genai
```

---

## Monitoring & Logging

Enable detailed logging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Monitor:
- API response times
- Token usage and costs
- Error rates
- User input patterns

---

**For more examples and advanced usage, check the main README.md**
