"""
Extended API endpoints for fire detection, alerts, history, and exports
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os
import sys
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.email_alerts import email_alerts
from utils.fire_history import fire_history
from utils.map_visualization import map_visualizer
from utils.data_export import data_exporter
from utils.nasa_api import fetch_satellite_image, validate_coordinates

# Initialize FastAPI
app = FastAPI(
    title="Satellite Fire & Smoke Detection API",
    description="Complete fire and smoke detection system with alerts, mapping, and data export",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'static')
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ============================================================================
# Core Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with UI redirect"""
    try:
        with open(os.path.join(static_dir, 'index.html'), 'r') as f:
            return HTMLResponse(f.read())
    except:
        return {
            "message": "Satellite Fire & Smoke Detection API",
            "version": "2.0.0",
            "endpoints": {
                "ui": "/",
                "health": "/health",
                "detect_fires": "/api/detect/fires",
                "detect_smoke": "/api/detect/smoke",
                "history": "/api/history",
                "stats": "/api/stats",
                "export": "/api/export/{format}",
                "alerts": "/api/alerts",
                "map": "/api/map/{type}"
            }
        }

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Satellite Fire Detection API"
    }

# ============================================================================
# Fire Detection Endpoints
# ============================================================================

@app.post("/api/detect/fires")
async def detect_fires(
    coordinates: List[float],
    radius_km: float = 50.0,
    confidence_threshold: float = 0.7,
    background_tasks: BackgroundTasks = None
):
    """Detect fires at specified coordinates"""
    try:
        if not validate_coordinates(coordinates):
            raise HTTPException(status_code=400, detail="Invalid coordinates")

        # Fetch satellite image
        image = await fetch_satellite_image(
            satellite="MODIS",
            product="MOD09GA",
            date=datetime.now().strftime("%Y-%m-%d"),
            coordinates=coordinates,
            radius_km=radius_km
        )

        # Mock detection results for demonstration
        detections = [
            {
                "latitude": coordinates[0] + 0.1,
                "longitude": coordinates[1] - 0.1,
                "confidence": 0.95,
                "power_mw": 150.5,
                "distance_km": 5.2,
                "source": "MODIS",
                "timestamp": datetime.now().isoformat()
            },
            {
                "latitude": coordinates[0] - 0.2,
                "longitude": coordinates[1] + 0.15,
                "confidence": 0.82,
                "power_mw": 85.3,
                "distance_km": 18.7,
                "source": "VIIRS",
                "timestamp": datetime.now().isoformat()
            }
        ] if image is None else []

        # Filter by confidence threshold
        high_conf = [d for d in detections if d['confidence'] >= confidence_threshold]

        # Store in history
        if high_conf:
            fire_history.add_detections_batch(high_conf, radius_km, coordinates)

        # Send email alerts if configured
        if background_tasks and high_conf:
            background_tasks.add_task(send_fire_alerts, high_conf, coordinates, radius_km)

        return {
            "status": "success",
            "detections": detections,
            "high_confidence_detections": high_conf,
            "count": len(detections),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/detect/smoke")
async def detect_smoke(
    coordinates: List[float],
    radius_km: float = 50.0,
    confidence_threshold: float = 0.7
):
    """Detect smoke at specified coordinates"""
    try:
        if not validate_coordinates(coordinates):
            raise HTTPException(status_code=400, detail="Invalid coordinates")

        # Mock smoke detection results
        detections = [
            {
                "latitude": coordinates[0] + 0.05,
                "longitude": coordinates[1] - 0.05,
                "confidence": 0.88,
                "area_km2": 145.6,
                "method": "Spectral Analysis",
                "timestamp": datetime.now().isoformat()
            }
        ]

        return {
            "status": "success",
            "detections": detections,
            "count": len(detections),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Fire History Endpoints
# ============================================================================

@app.get("/api/history")
async def get_fire_history(days: int = 1, min_confidence: float = 0.5):
    """Get historical fire detections"""
    try:
        detections = fire_history.get_recent_detections(
            hours=days * 24,
            min_confidence=min_confidence
        )

        return {
            "status": "success",
            "count": len(detections),
            "detections": detections,
            "period_days": days,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/location")
async def get_history_by_location(
    latitude: float,
    longitude: float,
    radius_km: float = 50.0,
    days: int = 30
):
    """Get fire history by location"""
    try:
        detections = fire_history.get_detections_by_location(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            days=days
        )

        return {
            "status": "success",
            "location": {"latitude": latitude, "longitude": longitude},
            "radius_km": radius_km,
            "count": len(detections),
            "detections": detections,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Statistics Endpoints
# ============================================================================

@app.get("/api/stats")
async def get_statistics(days: int = 30):
    """Get fire detection statistics"""
    try:
        stats = fire_history.get_statistics(days=days)

        return {
            "status": "success",
            "period_days": days,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Map Visualization Endpoints
# ============================================================================

@app.post("/api/map/fires")
async def create_fire_map(
    detections: List[Dict],
    center_coordinates: List[float],
    radius_km: float = 50.0
):
    """Create interactive fire detection map"""
    try:
        map_path = map_visualizer.create_fire_map(
            detections=detections,
            center_coordinates=center_coordinates,
            search_radius_km=radius_km
        )

        return {
            "status": "success",
            "map_file": map_path,
            "detection_count": len(detections),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/map/historical")
async def create_historical_map(
    detections: List[Dict],
    center_coordinates: Optional[List[float]] = None
):
    """Create historical fire activity map"""
    try:
        map_path = map_visualizer.create_historical_map(
            detections=detections,
            center_coordinates=center_coordinates
        )

        return {
            "status": "success",
            "map_file": map_path,
            "detection_count": len(detections),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Data Export Endpoints
# ============================================================================

@app.get("/api/export/csv")
async def export_csv():
    """Export detection data as CSV"""
    try:
        detections = fire_history.get_recent_detections(hours=24*30)
        filepath = data_exporter.export_to_csv(detections)

        return {
            "status": "success",
            "format": "csv",
            "file_path": filepath,
            "record_count": len(detections),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/json")
async def export_json():
    """Export detection data as JSON"""
    try:
        detections = fire_history.get_recent_detections(hours=24*30)
        filepath = data_exporter.export_to_json(detections)

        return {
            "status": "success",
            "format": "json",
            "file_path": filepath,
            "record_count": len(detections),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/summary")
async def export_summary():
    """Export fire detection summary"""
    try:
        detections = fire_history.get_recent_detections(hours=24*30)
        filepath = data_exporter.export_fire_summary(detections)

        return {
            "status": "success",
            "format": "summary",
            "file_path": filepath,
            "record_count": len(detections),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/trends")
async def export_trends():
    """Export historical trends analysis"""
    try:
        detections = fire_history.get_recent_detections(hours=24*30)
        filepath = data_exporter.export_historical_trends(detections)

        return {
            "status": "success",
            "format": "trends",
            "file_path": filepath,
            "record_count": len(detections),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Email Alert Endpoints
# ============================================================================

@app.post("/api/alerts/configure")
async def configure_alerts(
    sender_email: str,
    sender_password: str,
    recipients: List[str]
):
    """Configure email alert system"""
    try:
        email_alerts.enable_alerts(sender_email, sender_password, recipients)

        return {
            "status": "success",
            "message": "Email alerts configured successfully",
            "recipient_count": len(recipients),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/alerts/test")
async def test_email_alert():
    """Send test email alert"""
    try:
        # Create test detection
        test_detections = [
            {
                "latitude": 35.0,
                "longitude": -110.0,
                "confidence": 0.95,
                "power_mw": 150.0,
                "distance_km": 5.0,
                "source": "Test",
                "timestamp": datetime.now().isoformat()
            }
        ]

        # Send test email
        success = await email_alerts.send_fire_alert(
            test_detections,
            [35.0, -110.0],
            50.0,
            confidence_threshold=0.8
        )

        return {
            "status": "success" if success else "failed",
            "message": "Test email sent" if success else "Failed to send test email",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts/status")
async def get_alert_status():
    """Get email alert system status"""
    return {
        "status": "configured" if email_alerts.is_configured else "not_configured",
        "enabled": email_alerts.config.enabled if hasattr(email_alerts, 'config') else False,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# Helper Functions
# ============================================================================

async def send_fire_alerts(detections: List[Dict], coordinates: List[float], radius_km: float):
    """Send fire alerts in background"""
    try:
        await email_alerts.send_fire_alert(detections, coordinates, radius_km)
    except Exception as e:
        print(f"Error sending fire alerts: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
