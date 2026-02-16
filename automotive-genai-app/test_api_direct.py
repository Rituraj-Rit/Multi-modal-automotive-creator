#!/usr/bin/env python
"""Direct test of the API without network calls"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import create_app

app = create_app()

# Create a test client
with app.test_client() as client:
    print("Testing /api/health endpoint:")
    response = client.get('/api/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}\n")
    
    print("Testing /api/generate endpoint:")
    response = client.post('/api/generate', json={
        'design_prompt': 'Design a futuristic electric SUV with sleek aerodynamics'
    })
    print(f"Status: {response.status_code}")
    data = response.get_json()
    print(f"Success: {data.get('success')}")
    print(f"Error (if any): {data.get('error')}\n")
    
    print("Testing /api/config endpoint:")
    response = client.get('/api/config')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")
