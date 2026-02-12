#!/usr/bin/env python3
"""
Lightweight version of the application for PythonAnywhere deployment
This version avoids heavy dependencies like OpenCV and uses simpler imports
"""

import sys
import os
from pathlib import Path

# Add the current directory and src to Python path
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / "src"

# Add to Python path
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import what we can without heavy dependencies
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from typing import List, Dict, Optional
    import logging
    import datetime
    
    # Import from src directory - but handle OpenCV issues gracefully
    try:
        from src.config import AppConfig
        print("✅ Config loaded successfully")
    except ImportError as e:
        print(f"⚠️  Config import issue: {e}")
        # Create a basic config if the real one fails
        class BasicConfig:
            log_level = "INFO"
        AppConfig = BasicConfig()
    
    try:
        from src.api.main import app as api_app
        print("✅ API loaded successfully")
    except ImportError as e:
        print(f"⚠️  API import issue: {e}")
        # Create a basic API if the real one fails
        from fastapi import APIRouter
        api_app = APIRouter()
        @api_app.get("/test")
        async def test_endpoint():
            return {"message": "Basic API working"}
    
    try:
        # Try to import NASA API but don't fail if it doesn't work
        from src.utils.nasa_api import NASAImageFetcher
        print("✅ NASA API loaded successfully")
    except ImportError as e:
        print(f"⚠️  NASA API import issue: {e}")
        NASAImageFetcher = None
    
    print("✅ All imports successful!")
    
except ImportError as e:
    print(f"❌ Critical import error: {e}")
    print("This might be due to missing dependencies.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=getattr(logging, getattr(AppConfig, 'log_level', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create main FastAPI app
app = FastAPI(
    title="Satellite Smoke & Dust Detection System (Lightweight)",
    description="Lightweight version for PythonAnywhere - basic satellite imagery detection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API routes (if available)
try:
    app.include_router(api_app, prefix="/api", tags=["api"])
    print("✅ API routes included")
except Exception as e:
    print(f"⚠️  API route inclusion issue: {e}")

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Lightweight Satellite Detection System")

    # Initialize NASA image fetcher if available
    if NASAImageFetcher:
        try:
            nasa_fetcher = NASAImageFetcher(AppConfig)
            await nasa_fetcher.initialize()
            logger.info("NASA API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NASA API client: {e}")
    else:
        logger.warning("NASA API not available in lightweight version")

    # Check system resources
    system_info = get_system_info()
    logger.info(f"System Info: {system_info}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Lightweight Satellite Detection System")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Satellite Smoke & Dust Detection System (Lightweight)",
        "version": "1.0.0",
        "description": "Lightweight version for PythonAnywhere deployment",
        "note": "Some features may be limited due to storage constraints",
        "endpoints": {
            "api": "/api",
            "health": "/health",
            "status": "/status"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0",
        "note": "Lightweight version - some features may be limited"
    }

@app.get("/status")
async def get_status():
    """Get system status and performance metrics"""
    return {
        "system": get_system_info(),
        "models": {
            "smoke_detector": "limited (no OpenCV)",
            "dust_detector": "limited (no OpenCV)"
        },
        "features": {
            "api_endpoints": "available",
            "image_processing": "limited",
            "nasa_integration": "available" if NASAImageFetcher else "not available"
        },
        "timestamp": datetime.datetime.now().isoformat()
    }

def get_system_info() -> Dict:
    """Get system information"""
    try:
        import psutil
        
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "gpu_available": False,  # OpenCV not available
            "cuda_version": None,
            "torch_version": "not installed (OpenCV conflict)",
            "python_version": sys.version,
            "platform": sys.platform,
            "storage_warning": "Running in lightweight mode due to storage constraints"
        }
    except ImportError:
        return {
            "cpu_count": "unknown",
            "memory_total": "unknown", 
            "memory_available": "unknown",
            "gpu_available": False,
            "cuda_version": None,
            "torch_version": "not installed",
            "python_version": sys.version,
            "platform": sys.platform,
            "storage_warning": "Limited system info available"
        }

def main():
    """Main entry point"""
    # Set environment variables
    os.environ.setdefault("NASA_API_KEY", "DEMO_KEY")  # Default demo key

    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))

    # Run the application
    logger.info(f"Starting lightweight server on port {port}")
    import uvicorn
    uvicorn.run(
        "app_lightweight:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()