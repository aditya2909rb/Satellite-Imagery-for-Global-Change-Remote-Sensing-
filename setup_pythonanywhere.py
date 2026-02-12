#!/usr/bin/env python3
"""
PythonAnywhere Setup Script
This script automates the setup process for your satellite imagery detection project on PythonAnywhere
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print the result"""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print("✅ SUCCESS!")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED!")
        print("Error:", e.stderr)
        return False

def main():
    print("🚀 PythonAnywhere Setup for Satellite Imagery Detection Project")
    print("="*70)
    
    # Step 1: Check Python version
    print(f"Python version: {sys.version}")
    
    # Step 2: Install required packages
    packages = [
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0", 
        "aiohttp>=3.9.1",
        "pillow>=11.0.0",
        "opencv-python>=4.8.1.78",
        "numpy>=2.0.0",
        "beautifulsoup4>=4.12.2",
        "requests>=2.31.0",
        "psutil>=5.9.6",
        "mangum>=0.18.0",  # For FastAPI on PythonAnywhere
        "pytest>=7.4.3",
        "pytest-asyncio>=0.21.1"
    ]
    
    for package in packages:
        success = run_command(f"pip install {package}", f"Installing {package}")
        if not success:
            print(f"⚠️  Warning: Failed to install {package}, continuing...")
    
    # Step 3: Create necessary directories
    directories = ['logs', 'exports', 'data']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    # Step 4: Set up database if needed
    print("\n" + "="*60)
    print("STEP: Setting up database")
    print("="*60)
    
    # Check if we need to initialize the database
    if os.path.exists('data/fire_history.db'):
        print("✅ Database already exists")
    else:
        print("⚠️  Database file not found, it will be created when the app runs")
    
    # Step 5: Test the application
    print("\n" + "="*60)
    print("STEP: Testing application import")
    print("="*60)
    
    try:
        import app
        print("✅ Application imports successfully!")
        
        # Test if FastAPI app is created
        if hasattr(app, 'app'):
            print("✅ FastAPI app object found!")
        else:
            print("⚠️  FastAPI app object not found in app.py")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This might be normal if dependencies aren't fully installed yet")
    
    # Step 6: Create a simple test script
    test_script = '''#!/usr/bin/env python3
"""
Simple test script to verify the application works
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("✅ Application imported successfully!")
    print("✅ FastAPI app is ready!")
    
    # Try to get the app info
    if hasattr(app, '__name__'):
        print(f"App module: {app.__name__}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
'''
    
    with open('test_app_import.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created test script: test_app_import.py")
    
    print("\n" + "="*70)
    print("🎉 SETUP COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Upload your project files to PythonAnywhere")
    print("2. Run this setup script on PythonAnywhere")
    print("3. Configure your web app in PythonAnywhere dashboard")
    print("4. Set the WSGI file path to: /home/aditya2909rb/Satellite-Imagery-for-Global-Change-Remote-Sensing-/pythonanywhere_wsgi.py")
    print("5. Restart your web app")
    print("\nFor detailed instructions, see PYTHONANYWHERE_GUIDE.md")

if __name__ == "__main__":
    main()