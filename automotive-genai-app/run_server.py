#!/usr/bin/env python
"""Start Flask server and keep it running"""
import sys
import os

# Add parent directory to path so src module is found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import create_app

if __name__ == '__main__':
    app = create_app()
    print("\n✓ Flask app created successfully")
    print("Starting server on http://127.0.0.1:5000")
    print("Press CTRL+C to stop\n")
    
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped")
        sys.exit(0)
