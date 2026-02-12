#!/usr/bin/env python3
"""
Satellite Detection API - Standalone Server
Directly runs the FastAPI application without subprocess
"""

import os
import sys

# Navigate to project directory
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

print("\n" + "="*70)
print("SATELLITE DETECTION API - STARTING SERVER")
print("="*70)
print()

try:
    # Try to import and run
    print("Loading dependencies...")
    import uvicorn
    from api.main import app
    
    print("Dependencies loaded successfully")
    print()
    print("Starting FastAPI server...")
    print()
    print("API Server:     http://localhost:8000")
    print("API Docs:       http://localhost:8000/docs")
    print("ReDoc:          http://localhost:8000/redoc")
    print()
    print("🔌 Endpoints:")
    print("   GET  /health           - Health check")
    print("   GET  /satellites       - List satellites")
    print("   GET  /status           - System status")
    print("   POST /detect/smoke     - Detect smoke")
    print("   POST /detect/dust      - Detect dust")
    print()
    print("Press CTRL+C to stop the server")
    print("-"*70)
    print()
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

except ImportError as e:
    print(f"Import Error: {e}")
    print()
    print("You need to install dependencies first:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
