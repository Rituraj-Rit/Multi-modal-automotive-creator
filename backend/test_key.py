import os
from pathlib import Path

# Load .env from the backend directory
backend_dir = Path(__file__).parent

# Try to load the .env file
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

api_key = os.getenv("OPENAI_API_KEY", "")
print(f"API Key loaded: {api_key[:30] if api_key else 'EMPTY'}...")
print(f"Key length: {len(api_key) if api_key else 0}")
print(f"Full key (first 50): {api_key[:50] if api_key else 'EMPTY'}")

# Check if there are other env vars that might be interfering
print(f"\nAll env vars with 'OPENAI' or 'API':")
for key, value in os.environ.items():
    if 'OPENAI' in key.upper() or 'API' in key.upper():
        print(f"  {key}: {value[:20]}...")

from openai import OpenAI

client = OpenAI(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("\nSUCCESS! API key is valid.")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"\nERROR: {e}")
