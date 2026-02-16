#!/usr/bin/env python
"""Test the /api/generate endpoint"""
import requests
import json

url = 'http://127.0.0.1:5000/api/generate'
payload = {
    'design_prompt': 'Design a futuristic electric SUV with sleek aerodynamics and LED headlights',
    'context': 'next-generation luxury vehicle for 2030'
}

try:
    r = requests.post(url, json=payload)
    print(f'Status: {r.status_code}')
    print('Response:')
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f'Error: {e}')
