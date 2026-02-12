#!/usr/bin/env python3
"""
Extract and Setup Script for PythonAnywhere
This script extracts your uploaded ZIP file and sets up the project automatically
"""

import os
import zipfile
import subprocess
import sys

def extract_zip_file():
    """Extract the uploaded ZIP file"""
    print("🔍 Looking for uploaded ZIP files...")
    
    # Look for ZIP files in the current directory
    zip_files = [f for f in os.listdir('.') if f.endswith('.zip')]
    
    if not zip_files:
        print("❌ No ZIP files found in current directory")
        print("Please upload your project ZIP file to PythonAnywhere first")
        return False
    
    print(f"📦 Found ZIP files: {zip_files}")
    
    # Use the first ZIP file found
    zip_file = zip_files[0]
    print(f"📂 Extracting {zip_file}...")
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # Extract to current directory
            zip_ref.extractall('.')
            print(f"✅ Successfully extracted {zip_file}")
            
            # List extracted contents
            extracted_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.')]
            print(f"📁 Extracted directories: {extracted_dirs}")
            
            return True
            
    except Exception as e:
        print(f"❌ Failed to extract ZIP file: {e}")
        return False

def find_project_directory():
    """Find the extracted project directory"""
    print("\n🔍 Finding project directory...")
    
    # Look for directories that might contain our project
    potential_dirs = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and not item.startswith('.'):
            # Check if it contains our key files
            if os.path.exists(os.path.join(item, 'app.py')) or \
               os.path.exists(os.path.join(item, 'app_lightweight.py')) or \
               os.path.exists(os.path.join(item, 'setup_lightweight.py')):
                potential_dirs.append(item)
    
    if potential_dirs:
        print(f"📁 Found project directories: {potential_dirs}")
        return potential_dirs[0]  # Return the first one found
    else:
        print("❌ No project directory found")
        return None

def run_setup():
    """Run the setup process"""
    print("\n🚀 Starting automated setup...")
    
    # Step 1: Extract ZIP
    if not extract_zip_file():
        return False
    
    # Step 2: Find project directory
    project_dir = find_project_directory()
    if not project_dir:
        print("❌ Could not find project directory")
        return False
    
    print(f"📁 Working in directory: {project_dir}")
    
    # Step 3: Change to project directory
    os.chdir(project_dir)
    print(f"✅ Changed to directory: {os.getcwd()}")
    
    # Step 4: Create virtual environment
    print("\n🔧 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Virtual environment created")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False
    
    # Step 5: Activate virtual environment and install dependencies
    print("\n📦 Installing dependencies...")
    
    # For PythonAnywhere, we need to use the full path to pip
    venv_pip = os.path.join('venv', 'bin', 'pip')
    
    try:
        # Install essential packages for lightweight version
        packages = [
            'fastapi>=0.104.1',
            'uvicorn>=0.24.0',
            'aiohttp>=3.9.1', 
            'pillow>=11.0.0',
            'numpy>=2.0.0',
            'beautifulsoup4>=4.12.2',
            'requests>=2.31.0',
            'psutil>=5.9.6',
            'mangum>=0.18.0',
            'pytest>=7.4.3',
            'pytest-asyncio>=0.21.1'
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            subprocess.run([venv_pip, 'install', package], check=True)
        
        print("✅ All essential packages installed")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False
    
    # Step 6: Create necessary directories
    directories = ['logs', 'exports', 'data']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    # Step 7: Test the lightweight application
    print("\n🧪 Testing application...")
    try:
        # Try to import the lightweight app
        result = subprocess.run([
            sys.executable, '-c', 
            'import sys; sys.path.insert(0, "."); from app_lightweight import app; print("✅ App imported successfully")'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Application test successful!")
            print(result.stdout)
        else:
            print("⚠️  Application test had issues:")
            print(result.stderr)
            
    except Exception as e:
        print(f"⚠️  Application test failed: {e}")
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print(f"📁 Project location: {os.getcwd()}")
    print("🔧 Virtual environment: venv/")
    print("📦 Dependencies installed (lightweight version)")
    print("\n📋 NEXT STEPS:")
    print("1. Go to PythonAnywhere Web tab")
    print("2. Add new web app (choose Flask)")
    print(f"3. Set WSGI file: {os.getcwd()}/pythonanywhere_wsgi.py")
    print(f"4. Set virtualenv: {os.getcwd()}/venv")
    print("5. Click Reload")
    print("6. Visit your app URL")
    print("\n📖 For detailed instructions, see PYTHONANYWHERE_GUIDE.md")
    
    return True

if __name__ == "__main__":
    print("🚀 PythonAnywhere Extract and Setup Script")
    print("="*50)
    print("This script will:")
    print("1. Extract your uploaded ZIP file")
    print("2. Find the project directory")
    print("3. Create virtual environment")
    print("4. Install dependencies")
    print("5. Test the application")
    print("="*50)
    
    success = run_setup()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("Your application is ready for PythonAnywhere deployment!")
    else:
        print("\n❌ Setup failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)