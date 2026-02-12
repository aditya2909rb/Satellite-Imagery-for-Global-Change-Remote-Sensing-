#!/usr/bin/env python3
"""
Simple startup script for the Satellite Fire Detection System
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Import the app from the correct location
    from api.main import app
    import uvicorn
    
    print("Starting Satellite Fire Detection System...")
    print("Server will be available at: http://localhost:8000")
    print("Web UI available at: http://localhost:8000/ui")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
    
except ImportError as e:
    print(f"Import Error: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install fastapi uvicorn aiohttp pillow opencv-python numpy torch onnxruntime beautifulsoup4 requests psutil folium pandas")
    sys.exit(1)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)
