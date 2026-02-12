#!/usr/bin/env python3
"""
Test script to verify the Satellite Fire Detection System works
"""

import sys
import os
import time

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        from api.main import app
        print("✅ Main API import successful")
        
        from utils.email_alerts import email_alerts
        print("✅ Email alerts import successful")
        
        from utils.fire_history import fire_history
        print("✅ Fire history import successful")
        
        from utils.map_visualization import map_visualizer
        print("✅ Map visualization import successful")
        
        from utils.data_export import data_exporter
        print("✅ Data export import successful")
        
        from config import AppConfig
        print("✅ Configuration import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_api_endpoints():
    """Test if API endpoints are properly defined"""
    print("\n🔍 Testing API endpoints...")
    
    try:
        from api.main import app
        
        # Get all routes
        routes = [route.path for route in app.routes]
        
        expected_endpoints = [
            '/health',
            '/satellites', 
            '/status',
            '/fires/global',
            '/fires/region',
            '/detect/smoke',
            '/detect/dust',
            '/alerts/configure',
            '/alerts/send',
            '/history/recent',
            '/history/location',
            '/history/statistics',
            '/maps/fire',
            '/maps/dashboard',
            '/export/csv',
            '/export/json',
            '/export/fire-summary',
            '/static/maps/{filename}',
            '/static/exports/{filename}',
            '/ui'
        ]
        
        missing_endpoints = []
        for endpoint in expected_endpoints:
            if endpoint not in routes:
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            print(f"❌ Missing endpoints: {missing_endpoints}")
            return False
        else:
            print(f"✅ All {len(expected_endpoints)} endpoints found")
            return True
            
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return False

def test_dependencies():
    """Test if required dependencies are available"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn', 
        'aiohttp',
        'folium',
        'sqlite3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {missing_packages}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ All required dependencies available")
        return True

def main():
    """Main test function"""
    print("🚀 Satellite Fire Detection System - Test Suite")
    print("=" * 60)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test API endpoints
    endpoints_ok = test_api_endpoints()
    
    # Test dependencies
    deps_ok = test_dependencies()
    
    print("\n" + "=" * 60)
    
    if imports_ok and endpoints_ok and deps_ok:
        print("🎉 All tests passed! The application is ready to run.")
        print("\n📋 To start the server:")
        print("   cd satellite-detection-project")
        print("   python start_server.py")
        print("\n🌐 Access points:")
        print("   Main API: http://localhost:8000")
        print("   Web UI: http://localhost:8000/ui")
        print("   API Docs: http://localhost:8000/docs")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)