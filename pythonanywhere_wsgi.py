#!/usr/bin/env python3
"""
WSGI configuration for PythonAnywhere deployment
This file configures your FastAPI application to run on PythonAnywhere
"""

import sys
import os

# Add the project directory to the Python path
project_home = '/home/aditya2909rb/Satellite-Imagery-for-Global-Change-Remote-Sensing-'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set the Django/Flask settings module (if needed)
os.environ['DJANGO_SETTINGS_MODULE'] = 'Satellite-Imagery-for-Global-Change-Remote-Sensing-.settings'

# Import your FastAPI application (use the lightweight version first)
try:
    from app_lightweight import app as application
    print("✅ Successfully imported app_lightweight")
except ImportError as e:
    print(f"❌ Failed to import app_lightweight: {e}")
    print("Falling back to app_simple...")
    try:
        from app_simple import app as application
        print("✅ Successfully imported app_simple")
    except ImportError as e2:
        print(f"❌ Failed to import app_simple: {e2}")
        print("Falling back to app.py...")
        try:
            from app import app as application
            print("✅ Successfully imported app")
        except ImportError as e3:
            print(f"❌ Failed to import app: {e3}")
            sys.exit(1)

# For FastAPI on PythonAnywhere, we need to wrap it with a WSGI adapter
from mangum import Mangum

# Create a Mangum handler for FastAPI
handler = Mangum(application)

if __name__ == "__main__":
    # This allows you to run the app locally for testing
    import uvicorn
    uvicorn.run("app_simple:app", host="0.0.0.0", port=8000, reload=True)
