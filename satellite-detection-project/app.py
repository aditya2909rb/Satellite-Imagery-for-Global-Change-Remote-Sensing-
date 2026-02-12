#!/usr/bin/env python3
"""
Direct app runner - imports and runs the FastAPI app
"""
import sys
import os

# Add src to path FIRST
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

print("\n" + "="*80)
print("SATELLITE DETECTION API - STARTING NOW")
print("="*80 + "\n")

try:
    print("Loading FastAPI and dependencies...")
    import uvicorn
    from api.extended_main import app
    
    print("Dependencies loaded!\n")
    print("-"*80)
    print()
    print("SERVER STARTING...")
    print()
    print("Dashboard:         http://localhost:8000")
    print("Interactive Docs:  http://localhost:8000/docs")
    print("ReDoc:             http://localhost:8000/redoc")
    print()
    print("Available Features:")
    print("  * Email Alerts      - Configure notifications")
    print("  * Maps              - Interactive fire maps")
    print("  * History           - Past detections")
    print("  * Export            - CSV/JSON downloads")
    print("  * Detect            - Run fire detection")
    print()
    print("Press CTRL+C to stop")
    print("-"*80)
    print()
    
    # Run server (no reload for direct execution)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False, log_level="info")
    
except ImportError as e:
    print(f"\nError: Missing required module: {e}")
    print("\nPlease install dependencies first:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n\nServer stopped by user (CTRL+C)")
    sys.exit(0)
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
