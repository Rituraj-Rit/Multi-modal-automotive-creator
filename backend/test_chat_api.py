import requests

# Test the chat API
url = "http://localhost:8000/api/chat"
data = {"messages": [{"role": "user", "content": "Hello"}]}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
