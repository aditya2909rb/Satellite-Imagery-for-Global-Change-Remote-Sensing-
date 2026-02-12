"""
Simple FastAPI app for Satellite Smoke & Dust Detection
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from datetime import datetime
import psutil
import numpy as np

app = FastAPI(
    title="Satellite Smoke & Dust Detection API",
    description="Detect smoke and dust from satellite imagery",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Satellite data
SATELLITES = ["MODIS", "VIIRS", "GOES"]
PRODUCTS = {
    "MODIS": ["MOD09GA", "MOD09Q1"],
    "VIIRS": ["VNP09GA", "VNP09H1"],
    "GOES": ["ABI-L2-CMIPF", "ABI-L2-ACHAF"]
}

# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Satellite Smoke & Dust Detection API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "satellites": "/satellites",
            "status": "/status",
            "detect_smoke": "/detect/smoke",
            "detect_dust": "/detect/dust"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "API is running"
    }

@app.get("/satellites")
async def get_satellites():
    """Get supported satellites and products"""
    return {
        "satellites": SATELLITES,
        "products": PRODUCTS,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def get_status():
    """Get system status"""
    mem = psutil.virtual_memory()
    return {
        "api_status": "operational",
        "memory": {
            "total_gb": mem.total / (1024**3),
            "available_gb": mem.available / (1024**3),
            "percent_used": mem.percent
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/detect/smoke")
async def detect_smoke(
    satellite: str,
    product: str,
    date: str,
    coordinates: List[float],
    radius_km: float = 50.0,
    confidence: float = 0.7
):
    """
    Detect smoke in satellite imagery
    
    Args:
        satellite: MODIS, VIIRS, or GOES
        product: Satellite product code
        date: Date in YYYY-MM-DD format
        coordinates: [latitude, longitude]
        radius_km: Search radius in km
        confidence: Confidence threshold (0-1)
    """
    # Validate inputs
    if satellite not in SATELLITES:
        raise HTTPException(status_code=400, detail=f"Invalid satellite: {satellite}")
    
    if len(coordinates) != 2:
        raise HTTPException(status_code=400, detail="Coordinates must be [lat, lon]")
    
    lat, lon = coordinates
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    # Return mock detection
    return {
        "satellite": satellite,
        "product": product,
        "date": date,
        "coordinates": coordinates,
        "radius_km": radius_km,
        "detections": [
            {
                "confidence": 0.85,
                "bounding_box": [100, 100, 200, 200],
                "label": "Smoke",
                "area_km2": 25.5
            }
        ],
        "overlay_image": None,
        "timestamp": datetime.now().isoformat(),
        "note": "Mock detection - real models not available in Python 3.13"
    }

@app.post("/detect/dust")
async def detect_dust(
    satellite: str,
    product: str,
    date: str,
    coordinates: List[float],
    radius_km: float = 50.0,
    confidence: float = 0.7
):
    """
    Detect dust in satellite imagery
    
    Args:
        satellite: MODIS, VIIRS, or GOES
        product: Satellite product code
        date: Date in YYYY-MM-DD format
        coordinates: [latitude, longitude]
        radius_km: Search radius in km
        confidence: Confidence threshold (0-1)
    """
    # Validate inputs
    if satellite not in SATELLITES:
        raise HTTPException(status_code=400, detail=f"Invalid satellite: {satellite}")
    
    if len(coordinates) != 2:
        raise HTTPException(status_code=400, detail="Coordinates must be [lat, lon]")
    
    lat, lon = coordinates
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    # Return mock detection
    return {
        "satellite": satellite,
        "product": product,
        "date": date,
        "coordinates": coordinates,
        "radius_km": radius_km,
        "detections": [
            {
                "confidence": 0.78,
                "bounding_box": [50, 50, 150, 150],
                "label": "Dust",
                "area_km2": 15.3
            }
        ],
        "overlay_image": None,
        "timestamp": datetime.now().isoformat(),
        "note": "Mock detection - real models not available in Python 3.13"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
