from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import uvicorn
import logging
import sys
import os
import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config
from utils.nasa_api import NASAImageFetcher

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.AppConfig.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create main FastAPI app
app = FastAPI(
    title="Satellite Smoke & Dust Detection System",
    description="Comprehensive system for detecting smoke from wildfires and atmospheric dust using satellite imagery",
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

# Include API routes
app.include_router(api_app, prefix="/api", tags=["api"])

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Satellite Smoke & Dust Detection System")

    # Initialize NASA image fetcher
    try:
        nasa_fetcher = NASAImageFetcher(config)
        await nasa_fetcher.initialize()
        logger.info("NASA API client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize NASA API client: {e}")

    # Check system resources
    system_info = get_system_info()
    logger.info(f"System Info: {system_info}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Satellite Smoke & Dust Detection System")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Satellite Smoke & Dust Detection System",
        "version": "1.0.0",
        "description": "Comprehensive system for detecting smoke from wildfires and atmospheric dust using satellite imagery",
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
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/status")
async def get_status():
    """Get system status and performance metrics"""
    return {
        "system": get_system_info(),
        "models": {
            "smoke_detector": "loaded",
            "dust_detector": "loaded"
        },
        "timestamp": datetime.now().isoformat()
    }

def get_system_info() -> Dict:
    """Get system information"""
    import psutil
    import torch

    return {
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "gpu_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        "torch_version": torch.__version__,
        "python_version": sys.version,
        "platform": sys.platform
    }

def main():
    """Main entry point"""
    # Set environment variables
    os.environ.setdefault("NASA_API_KEY", "DEMO_KEY")  # Default demo key

    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))

    # Run the application from the correct path
    logger.info(f"Starting server on port {port}")
    import uvicorn
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()