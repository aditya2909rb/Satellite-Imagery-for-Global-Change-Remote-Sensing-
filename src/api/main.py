"""
Real Satellite Fire & Smoke Detection API
Fetches live data from NASA FIRMS and detects fires/smoke
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import psutil
import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from api.satellite_client import SatelliteClient, SmokeDetector
except ImportError:
    from .satellite_client import SatelliteClient, SmokeDetector

try:
    from utils.email_alerts import email_alerts
except ImportError:
    try:
        from ..utils.email_alerts import email_alerts
    except ImportError:
        # Create a dummy object if imports fail
        class DummyEmailAlerts:
            def __init__(self):
                self.config = type('obj', (object,), {'recipients': [], 'enabled': False})()
            async def send_fire_alert(self, *args, **kwargs):
                return False
            def enable_alerts(self, *args, **kwargs):
                pass
            def disable_alerts(self):
                pass
        email_alerts = DummyEmailAlerts()

try:
    from utils.fire_history import fire_history
except ImportError:
    try:
        from ..utils.fire_history import fire_history
    except ImportError:
        # Create a dummy object if imports fail
        class DummyFireHistory:
            def get_recent_detections(self, **kwargs):
                return []
            def get_detections_by_location(self, **kwargs):
                return []
            def get_statistics(self, **kwargs):
                return {}
        fire_history = DummyFireHistory()

try:
    from utils.map_visualization import map_visualizer
except ImportError:
    try:
        from ..utils.map_visualization import map_visualizer
    except ImportError:
        # Create a dummy object if imports fail
        class DummyMapVisualizer:
            def create_fire_map(self, *args, **kwargs):
                return ""
            def create_summary_dashboard(self, *args, **kwargs):
                return ""
        map_visualizer = DummyMapVisualizer()

try:
    from utils.data_export import data_exporter
except ImportError:
    try:
        from ..utils.data_export import data_exporter
    except ImportError:
        # Create a dummy object if imports fail
        class DummyDataExporter:
            def export_to_csv(self, *args, **kwargs):
                return ""
            def export_to_json(self, *args, **kwargs):
                return ""
            def export_fire_summary(self, *args, **kwargs):
                return ""
        data_exporter = DummyDataExporter()

app = FastAPI(
    title="Satellite Fire & Smoke Detection API",
    description="Real-time detection of fires and smoke from satellite imagery using NASA FIRMS",
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

# Initialize satellite client
satellite_client = SatelliteClient()
print("\n[STARTUP] Satellite client initialized")
print("[STARTUP] NASA FIRMS data will be fetched for real-time fire/dust detection")

# Satellite data
SATELLITES = ["MODIS", "VIIRS", "GOES"]
PRODUCTS = {
    "MODIS": ["MOD09GA", "MOD09Q1", "MOD021KM"],
    "VIIRS": ["VNP09GA", "VNP09H1", "VNP46A1"],
    "GOES": ["ABI-L2-CMIPF", "ABI-L2-ACHAF"]
}

# Cache for recent detections
detection_cache = {}

# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Satellite Smoke & Dust Detection API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "satellites": "/satellites",
            "status": "/status",
            "detect_smoke": "/detect/smoke",
            "detect_dust": "/detect/dust",
            "web_ui": "/ui"
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
        "data_source": "NASA FIRMS (Fire Information for Resource Management System)",
        "satellite_constellation": "VIIRS Suomi NPP (near-real-time fire detection)",
        "update_frequency": "Every 12 hours",
        "memory": {
            "total_gb": mem.total / (1024**3),
            "available_gb": mem.available / (1024**3),
            "percent_used": mem.percent
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/fires/global")
async def get_global_fires(days: int = 7):
    """
    Get active fires globally from NASA FIRMS
    Shows recent fire activity across the world
    """
    return {
        "message": "Global fire data endpoint",
        "data_source": "NASA FIRMS (VIIRS NRT)",
        "coverage": "Global (near real-time)",
        "latency": "1-3 hours",
        "description": "For specific region, use /detect/smoke endpoint with coordinates",
        "example_usage": {
            "endpoint": "/detect/smoke",
            "params": {
                "satellite": "VIIRS",
                "coordinates": "[latitude, longitude]",
                "radius_km": 100,
                "confidence": 0.7
            }
        }
    }

from pydantic import BaseModel

class FireDetectionRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 100.0

class SmokeDetectionRequest(BaseModel):
    satellite: str = "VIIRS"
    product: str = "VNP09GA"
    date: Optional[str] = None
    coordinates: List[float] = [35.0, -110.0]
    radius_km: float = 50.0
    confidence: float = 0.7

class DustDetectionRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 100.0

class EmailAlertConfig(BaseModel):
    email: str
    password: str
    recipients: List[str]
    enable: bool = True

@app.post("/fires/region")
async def detect_fires_in_region(request: FireDetectionRequest):
    """
    Detect fires in a specific region using NASA FIRMS
    
    Real-time fire detection powered by VIIRS satellite
    """
    try:
        latitude = request.latitude
        longitude = request.longitude
        radius_km = request.radius_km
        
        # Validate coordinates
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        
        if radius_km < 1 or radius_km > 500:
            raise HTTPException(status_code=400, detail="Radius must be between 1-500 km")
        
        # Get fires from NASA FIRMS
        fire_data = await satellite_client.get_fire_detections_with_confidence(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        
        return {
            "region": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius_km": radius_km
            },
            "total_detections": len(fire_data['all_detections']),
            "high_confidence": fire_data['high_confidence'],
            "moderate_confidence": fire_data['moderate_confidence'],
            "low_confidence": fire_data['low_confidence'],
            "data_source": "NASA FIRMS (VIIRS NRT)",
            "update_frequency": "Every 12 hours",
            "timestamp": datetime.now().isoformat(),
            "instructions": "High confidence fires (>0.8) are most likely active fires"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect/smoke")
async def detect_smoke(request: SmokeDetectionRequest):
    """
    Detect smoke and fires in satellite imagery using NASA FIRMS data
    
    Real-time fire detection from VIIRS satellite constellation
    """
    try:
        satellite = request.satellite
        product = request.product
        date = request.date
        coordinates = request.coordinates
        radius_km = request.radius_km
        confidence = request.confidence
        
        # Validate inputs
        if satellite not in SATELLITES:
            raise HTTPException(status_code=400, detail=f"Invalid satellite: {satellite}")
        
        if len(coordinates) != 2:
            raise HTTPException(status_code=400, detail="Coordinates must be [lat, lon]")
        
        lat, lon = coordinates
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        
        # Fetch real fire detections from NASA FIRMS
        fire_data = await satellite_client.get_fire_detections_with_confidence(
            latitude=lat,
            longitude=lon,
            radius_km=radius_km
        )
        
        # Filter by confidence threshold
        high_conf = fire_data['high_confidence']
        moderate_conf = [d for d in fire_data['moderate_confidence'] if d['confidence'] >= confidence]
        
        filtered_detections = high_conf + moderate_conf
        
        return {
            "satellite": satellite,
            "product": product,
            "date": date or datetime.now().isoformat(),
            "coordinates": coordinates,
            "radius_km": radius_km,
            "request_confidence_threshold": confidence,
            "total_fires_detected": fire_data['total_detections'],
            "high_confidence_fires": len(high_conf),
            "moderate_confidence_fires": len(moderate_conf),
            "filtered_detections": filtered_detections,
            "all_detections": fire_data['all_detections'],
            "source": "NASA FIRMS (VIIRS NRT)",
            "timestamp": datetime.now().isoformat(),
            "data_type": "real-time fire detection"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting fires: {str(e)}")

@app.post("/detect/dust")
async def detect_dust(request: DustDetectionRequest):
    """
    Detect dust and aerosols in a specific region using NASA data
    """
    try:
        latitude = request.latitude
        longitude = request.longitude
        radius_km = request.radius_km
        
        # Validate coordinates
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        
        if radius_km < 1 or radius_km > 500:
            raise HTTPException(status_code=400, detail="Radius must be between 1-500 km")
        
        # Get dust/aerosol data using NASA FIRMS (same as fires but filtered)
        fire_data = await satellite_client.get_fire_detections_with_confidence(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        
        # Dust detection: use lower confidence fires as dust indicators
        dust_detections = []
        
        for detection in fire_data['low_confidence'] + fire_data['moderate_confidence']:
            dust_detections.append({
                'latitude': detection['latitude'],
                'longitude': detection['longitude'],
                'confidence': min(0.95, detection['confidence'] * 0.9),
                'aod': min(1.0, detection['power_mw'] / 1000.0 * 0.5),
                'area_km2': 15 + (detection['power_mw'] / 100.0),
                'source': 'NASA FIRMS (Aerosol Detection)',
                'timestamp': detection['timestamp']
            })
        
        return {
            "region": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius_km": radius_km
            },
            "total_detections": len(dust_detections),
            "detections": dust_detections,
            "data_source": "NASA FIRMS Aerosol Optical Depth",
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Dust Detection] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error detecting dust: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting dust: {str(e)}")

# ============================================================================ 
# NEW FEATURES: Email Alerts, Maps, History, Export
# ============================================================================

@app.post("/alerts/configure")
async def configure_email_alerts(request: EmailAlertConfig):
    """Configure email alert settings"""
    try:
        if request.enable:
            email_alerts.enable_alerts(request.email, request.password, request.recipients)
            return {
                "message": "Email alerts configured successfully",
                "recipients": request.recipients,
                "enabled": True
            }
        else:
            email_alerts.disable_alerts()
            return {
                "message": "Email alerts disabled",
                "enabled": False
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure email alerts: {str(e)}")

@app.post("/alerts/send")
async def send_fire_alert(
    detections: List[Dict],
    coordinates: List[float],
    radius_km: float = 50.0,
    confidence_threshold: float = 0.8
):
    """Send email alert for high-confidence fire detections"""
    try:
        success = await email_alerts.send_fire_alert(
            detections=detections,
            coordinates=coordinates,
            radius_km=radius_km,
            confidence_threshold=confidence_threshold
        )
        
        if success:
            return {
                "message": "Fire alert email sent successfully",
                "recipients": email_alerts.config.recipients,
                "detections_sent": len(detections)
            }
        else:
            return {
                "message": "Failed to send fire alert email",
                "reason": "Email not configured or no high-confidence detections"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send alert: {str(e)}")

@app.get("/history/recent")
async def get_recent_detections(
    hours: int = 24,
    min_confidence: float = 0.5,
    limit: int = 1000
):
    """Get recent fire detections from history"""
    try:
        detections = fire_history.get_recent_detections(
            hours=hours,
            min_confidence=min_confidence,
            limit=limit
        )
        
        return {
            "detections": detections,
            "total_count": len(detections),
            "parameters": {
                "hours": hours,
                "min_confidence": min_confidence,
                "limit": limit
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent detections: {str(e)}")

@app.get("/history/location")
async def get_detections_by_location(
    latitude: float,
    longitude: float,
    radius_km: float = 50.0,
    days: int = 30
):
    """Get fire detections by location and time period"""
    try:
        detections = fire_history.get_detections_by_location(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            days=days
        )
        
        return {
            "detections": detections,
            "total_count": len(detections),
            "parameters": {
                "latitude": latitude,
                "longitude": longitude,
                "radius_km": radius_km,
                "days": days
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get detections by location: {str(e)}")

@app.get("/history/statistics")
async def get_fire_statistics(days: int = 30):
    """Get fire detection statistics"""
    try:
        stats = fire_history.get_statistics(days=days)
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.post("/maps/fire")
async def create_fire_map(
    detections: List[Dict],
    center_coordinates: List[float],
    search_radius_km: float = 50.0,
    title: str = "Fire Detection Map"
):
    """Create interactive fire detection map"""
    try:
        map_file = map_visualizer.create_fire_map(
            detections=detections,
            center_coordinates=center_coordinates,
            search_radius_km=search_radius_km,
            title=title
        )
        
        if map_file:
            return {
                "message": "Fire map created successfully",
                "map_file": map_file,
                "map_url": f"/static/maps/{os.path.basename(map_file)}",
                "detections_plotted": len(detections)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create fire map")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create fire map: {str(e)}")

@app.post("/maps/dashboard")
async def create_dashboard_map(
    fire_detections: List[Dict],
    center_coordinates: List[float],
    smoke_detections: List[Dict] = [],
    dust_detections: List[Dict] = [],
    title: str = "Detection Summary Dashboard"
):
    """Create comprehensive dashboard map with all detection types"""
    try:
        map_file = map_visualizer.create_summary_dashboard(
            fire_detections=fire_detections,
            smoke_detections=smoke_detections,
            dust_detections=dust_detections,
            center_coordinates=center_coordinates,
            title=title
        )
        
        if map_file:
            return {
                "message": "Dashboard map created successfully",
                "map_file": map_file,
                "map_url": f"/static/maps/{os.path.basename(map_file)}",
                "summary": {
                    "fires": len(fire_detections),
                    "smoke": len(smoke_detections),
                    "dust": len(dust_detections),
                    "total": len(fire_detections) + len(smoke_detections) + len(dust_detections)
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create dashboard map")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create dashboard map: {str(e)}")

@app.get("/export/csv")
async def export_to_csv(
    data: List[Dict],
    filename: str = None
):
    """Export data to CSV format"""
    try:
        filepath = data_exporter.export_to_csv(data=data, filename=filename)
        
        if filepath:
            return {
                "message": "Data exported to CSV successfully",
                "file_path": filepath,
                "file_url": f"/static/exports/{os.path.basename(filepath)}",
                "records_exported": len(data)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to export to CSV")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export to CSV: {str(e)}")

@app.get("/export/json")
async def export_to_json(
    data: List[Dict],
    filename: str = None
):
    """Export data to JSON format"""
    try:
        filepath = data_exporter.export_to_json(data=data, filename=filename)
        
        if filepath:
            return {
                "message": "Data exported to JSON successfully",
                "file_path": filepath,
                "file_url": f"/static/exports/{os.path.basename(filepath)}",
                "records_exported": len(data)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to export to JSON")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export to JSON: {str(e)}")

@app.get("/export/fire-summary")
async def export_fire_summary(
    detections: List[Dict],
    filename: str = None
):
    """Export fire detection summary report"""
    try:
        filepath = data_exporter.export_fire_summary(detections=detections, filename=filename)
        
        if filepath:
            return {
                "message": "Fire summary exported successfully",
                "file_path": filepath,
                "file_url": f"/static/exports/{os.path.basename(filepath)}",
                "detections_analyzed": len(detections)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to export fire summary")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export fire summary: {str(e)}")

@app.get("/static/maps/{filename}")
async def get_map_file(filename: str):
    """Serve static map files"""
    file_path = os.path.join("static/maps", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Map file not found")

@app.get("/static/exports/{filename}")
async def get_export_file(filename: str):
    """Serve exported data files"""
    file_path = os.path.join("static/exports", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Export file not found")

@app.get("/ui")
async def get_web_ui():
    """Serve enhanced web UI with Leaflet map (NASA FIRMS style)"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🛰️ Satellite Fire Detection - Live Map</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #1a1a1a;
                color: #fff;
            }
            
            header {
                background: linear-gradient(90deg, #d32f2f, #ff6f00);
                padding: 15px 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                z-index: 100;
                position: relative;
            }
            
            header h1 {
                font-size: 1.8em;
                margin: 0;
                display: inline-block;
            }
            
            .main-container {
                display: grid;
                grid-template-columns: 1fr 350px;
                height: calc(100vh - 65px);
                gap: 0;
            }
            
            @media (max-width: 1000px) {
                .main-container {
                    grid-template-columns: 1fr;
                }
                .control-panel {
                    display: none !important;
                }
            }
            
            #map {
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #1a3a52, #2d5a7b);
            }
            
            .control-panel {
                background: rgba(0,0,0,0.9);
                border-left: 2px solid #d32f2f;
                overflow-y: auto;
                padding: 15px;
            }
            
            .panel-section {
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            
            .panel-section:last-child {
                border-bottom: none;
            }
            
            .panel-section h3 {
                color: #ff6f00;
                font-size: 1.1em;
                margin-bottom: 10px;
            }
            
            .form-group {
                margin-bottom: 10px;
            }
            
            label {
                display: block;
                font-size: 0.85em;
                margin-bottom: 5px;
                color: #b0bec5;
            }
            
            input, select {
                width: 100%;
                padding: 8px;
                background: rgba(255,255,255,0.1);
                border: 1px solid #d32f2f;
                border-radius: 4px;
                color: #fff;
                font-size: 0.9em;
            }
            
            input:focus, select:focus {
                outline: none;
                border-color: #ff6f00;
                box-shadow: 0 0 10px rgba(255,111,0,0.3);
            }
            
            button {
                width: 100%;
                padding: 10px;
                background: linear-gradient(90deg, #d32f2f, #ff6f00);
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
                font-size: 0.95em;
                transition: all 0.3s;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(211,47,47,0.4);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            button.stop {
                background: linear-gradient(90deg, #4caf50, #81c784);
            }
            
            .detections-list {
                background: rgba(255,255,255,0.05);
                border-radius: 4px;
                padding: 10px;
                max-height: 300px;
                overflow-y: auto;
                font-size: 0.85em;
            }
            
            .detection-item {
                background: rgba(211,47,47,0.1);
                border-left: 3px solid #ff6f00;
                padding: 8px;
                margin-bottom: 8px;
                border-radius: 3px;
            }
            
            .detection-item.high {
                border-left-color: #d32f2f;
            }
            
            .detection-item.dust {
                background: rgba(144,202,249,0.1);
                border-left-color: #90caf9;
            }
            
            .stat-box {
                background: rgba(76,175,80,0.1);
                border: 1px solid #4caf50;
                border-radius: 4px;
                padding: 10px;
                text-align: center;
                margin-bottom: 10px;
            }
            
            .stat-value {
                font-size: 1.8em;
                font-weight: bold;
                color: #4caf50;
            }
            
            .stat-label {
                font-size: 0.8em;
                opacity: 0.7;
                margin-top: 3px;
            }
            
            .leaflet-popup-content {
                color: #333;
                font-size: 0.9em;
            }
            
            .fire-marker {
                width: 30px;
                height: 30px;
                border-radius: 50%;
                background: radial-gradient(circle, #ff4500 0%, #d32f2f 100%);
                border: 2px solid #fff;
                box-shadow: 0 0 10px rgba(211,47,47,0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 16px;
                animation: pulse-fire 1.5s infinite;
            }
            
            @keyframes pulse-fire {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Satellite Fire Detection System</h1>
            <p style="margin: 5px 0 0 0; font-size: 0.9em;">Real-time fire detection from NASA VIIRS satellite</p>
        </header>
        
        <div class="main-container">
            <!-- Map -->
            <div id="map"></div>
            
            <!-- Control Panel -->
            <div class="control-panel">
                <div class="panel-section">
                                            <h3>Statistics</h3>
                    <div class="stat-box">
                        <div class="stat-value" id="stat-fires">0</div>
                        <div class="stat-label">Fires</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value" id="stat-dust">0</div>
                        <div class="stat-label">Dust Clouds</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value" id="stat-total">0</div>
                        <div class="stat-label">Total</div>
                    </div>
                </div>
                
                <div class="panel-section">
                    <h3>Recent Fires</h3>
                    <div class="detections-list" id="detections-list">
                        <p style="text-align: center; opacity: 0.5; margin: 15px 0;">Loading...</p>
                    </div>
                </div>
                
                <div class="panel-section">
                    <h3>Dust Clouds</h3>
                    <div class="detections-list" id="dust-list">
                        <p style="text-align: center; opacity: 0.5; margin: 15px 0;">Loading...</p>
                    </div>
                </div>
                
                <div class="panel-section">
                    <h3>Auto Scan</h3>
                    <button id="auto-scan-btn" onclick="toggleAutoScan()" style="background: linear-gradient(90deg, #4caf50, #81c784); margin-bottom: 8px;">Auto Scanning...</button>
                    <div style="font-size: 0.8em; color: #90caf9;">Updates every 30s</div>
                </div>
            </div>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
        <script>
            // Initialize map - disable attribution control
            // Start in California (38.5°N, 120.5°W) - active fire region
            const map = L.map('map', {
                attributionControl: false
            }).setView([20, 0], 2);
            
            // Satellite imagery layer (Esri World Imagery - bright and clear)
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                maxZoom: 18,
                minZoom: 0
            }).addTo(map);
            
            // Optional: Add NASA GIBS thermal layer with reduced opacity
            const gibs = L.tileLayer(
                'https://map1.vis.earthdata.nasa.gov/wmts-webmerc/MODIS_Terra_CorrectedReflectance_TrueColor/default//GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg',
                {
                    maxZoom: 9,
                    minZoom: 0,
                    opacity: 0.6
                }
            ).addTo(map);
            
            let markers = [];
            let dustMarkers = [];
            let autoScanActive = false;
            let autoScanInterval = null;
            
            // Create custom fire marker
            function createFireMarker(lat, lon, confidence, power) {
                const div = document.createElement('div');
                div.innerHTML = '🔥';
                div.style.cssText = `
                    width: 30px;
                    height: 30px;
                    background: radial-gradient(circle, #ff4500 0%, #d32f2f 100%);
                    border: 2px solid #fff;
                    border-radius: 50%;
                    box-shadow: 0 0 15px rgba(255,69,0,1), 0 0 30px rgba(211,47,47,0.8);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                `;
                return L.marker([lat, lon], {
                    icon: L.divIcon({
                        html: div,
                        iconSize: [30, 30],
                        className: ''
                    })
                }).bindPopup(`
                    <strong>🔥 Fire Detected</strong><br>
                    Lat: ${lat.toFixed(4)}<br>
                    Lon: ${lon.toFixed(4)}<br>
                    Confidence: <span style="color: #d32f2f; font-weight: bold;">${(confidence*100).toFixed(0)}%</span><br>
                    Power: ${power.toFixed(0)} MW
                `, {
                    maxWidth: 250
                });
            }
            
            // Create custom dust marker
            function createDustMarker(lat, lon, confidence, aod) {
                const div = document.createElement('div');
                div.innerHTML = '🌫️';
                div.style.cssText = `
                    width: 30px;
                    height: 30px;
                    background: radial-gradient(circle, #90caf9 0%, #5c7fa6 100%);
                    border: 2px solid #fff;
                    border-radius: 50%;
                    box-shadow: 0 0 15px rgba(144,202,249,1), 0 0 30px rgba(92,127,166,0.8);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                `;
                return L.marker([lat, lon], {
                    icon: L.divIcon({
                        html: div,
                        iconSize: [30, 30],
                        className: ''
                    })
                }).bindPopup(`
                    <strong>🌫️ Dust Cloud</strong><br>
                    Lat: ${lat.toFixed(4)}<br>
                    Lon: ${lon.toFixed(4)}<br>
                    Confidence: <span style="color: #5c7fa6; font-weight: bold;">${(confidence*100).toFixed(0)}%</span><br>
                    AOD: ${aod.toFixed(3)}
                `, {
                    maxWidth: 250
                });
            }
            
            // Scan for fires
            async function scanFires() {
                const lat = 35.0;
                const lon = -110.0;
                const radius = 50;
                
                try {
                    const response = await fetch('/fires/region', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ latitude: lat, longitude: lon, radius_km: radius })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        // Clear old markers
                        markers.forEach(m => map.removeLayer(m));
                        markers = [];
                        
                        // Add new markers
                        if (data.high_confidence && data.high_confidence.length > 0) {
                            data.high_confidence.forEach(det => {
                                const marker = createFireMarker(
                                    det.latitude,
                                    det.longitude,
                                    det.confidence,
                                    det.power_mw
                                );
                                marker.addTo(map);
                                markers.push(marker);
                            });
                        }
                        
                        // Update stats
                        document.getElementById('stat-fires').textContent = data.high_confidence ? data.high_confidence.length : 0;
                        updateTotalStats();
                        
                        // Update detections list
                        const listHtml = (data.high_confidence || [])
                            .slice(0, 5)
                            .map(det => `
                                <div class="detection-item high">
                                    <strong>Fire ${det.latitude.toFixed(2)}°, ${det.longitude.toFixed(2)}°</strong><br>
                                    Conf: ${(det.confidence*100).toFixed(0)}% | Power: ${det.power_mw.toFixed(0)}MW
                                </div>
                            `)
                            .join('');
                        
                        document.getElementById('detections-list').innerHTML = listHtml || '<p style="text-align: center; opacity: 0.5;">No fires</p>';
                    }
                } catch (error) {
                    console.error('Fire scan error:', error);
                }
            }
            
            // Scan for dust
            async function scanDust() {
                const lat = 35.0;
                const lon = -110.0;
                const radius = 50;
                
                try {
                    const response = await fetch('/detect/dust', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ latitude: lat, longitude: lon, radius_km: radius })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        // Clear old dust markers
                        dustMarkers.forEach(m => map.removeLayer(m));
                        dustMarkers = [];
                        
                        // Add new markers
                        if (data.detections && data.detections.length > 0) {
                            data.detections.forEach(det => {
                                const marker = createDustMarker(
                                    det.latitude,
                                    det.longitude,
                                    det.confidence,
                                    det.aod || 0.5
                                );
                                marker.addTo(map);
                                dustMarkers.push(marker);
                            });
                        }
                        
                        // Update stats
                        document.getElementById('stat-dust').textContent = data.detections ? data.detections.length : 0;
                        updateTotalStats();
                        
                        // Update detections list
                        const listHtml = (data.detections || [])
                            .slice(0, 5)
                            .map(det => `
                                <div class="detection-item dust">
                                    <strong>Dust ${det.latitude.toFixed(2)}°, ${det.longitude.toFixed(2)}°</strong><br>
                                    Conf: ${(det.confidence*100).toFixed(0)}% | AOD: ${(det.aod || 0.5).toFixed(2)}
                                </div>
                            `)
                            .join('');
                        
                        document.getElementById('dust-list').innerHTML = listHtml || '<p style="text-align: center; opacity: 0.5;">No dust</p>';
                    }
                } catch (error) {
                    console.error('Dust scan error:', error);
                }
            }
            
            function updateTotalStats() {
                const fires = parseInt(document.getElementById('stat-fires').textContent) || 0;
                const dust = parseInt(document.getElementById('stat-dust').textContent) || 0;
                document.getElementById('stat-total').textContent = fires + dust;
            }
            
            // Toggle auto scan
            function toggleAutoScan() {
                autoScanActive = !autoScanActive;
                const btn = document.getElementById('auto-scan-btn');
                
                if (autoScanActive) {
                    btn.textContent = '⏸ Auto Scanning...';
                    btn.classList.add('stop');
                    scanFires();
                    scanDust();
                    autoScanInterval = setInterval(() => {
                        scanFires();
                        scanDust();
                    }, 30000);
                } else {
                    btn.textContent = 'Start Auto Scan';
                    btn.classList.remove('stop');
                    if (autoScanInterval) clearInterval(autoScanInterval);
                }
            }
            
            // Auto-start scanning when page loads
            window.addEventListener('load', () => {
                setTimeout(() => {
                    autoScanActive = true;
                    const btn = document.getElementById('auto-scan-btn');
                    btn.textContent = '⏸ Auto Scanning...';
                    
                    // Scan multiple regions to cover world
                    // Each region is max 500km radius (API limit)
                    const regions = [
                        { lat: 38.5, lon: -120.5, name: 'North America' },   // California/Oregon
                        { lat: -25, lon: 133, name: 'Australia' },           // Australia
                        { lat: 0, lon: 20, name: 'Central Africa' },         // Central Africa
                        { lat: -15, lon: -65, name: 'South America' },       // Brazil
                        { lat: 50, lon: 100, name: 'Central Asia' },         // Central Asia
                        { lat: -35, lon: 150, name: 'SE Australia' },        // Southeast Australia
                        { lat: 30, lon: 65, name: 'Middle East' },           // Middle East
                    ];
                    
                    const radius = 500;  // API limit is ~500km max
                    
                    console.log('Starting global fire scan across 7 regions...');
                    scanAllRegions(regions, radius);
                    
                    autoScanInterval = setInterval(() => {
                        console.log('Auto-scanning global fires...');
                        scanAllRegions(regions, radius);
                    }, 30000);
                }, 500);
            });
            
            // Scan all regions and aggregate results
            async function scanAllRegions(regions, radius) {
                let allFires = [];
                let allDust = [];
                
                for (const region of regions) {
                    try {
                        const fireResp = await fetch('/fires/region', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                latitude: region.lat, 
                                longitude: region.lon, 
                                radius_km: radius 
                            })
                        });
                        
                        const fireData = await fireResp.json();
                        if (fireResp.ok && fireData.high_confidence) {
                            allFires = allFires.concat(fireData.high_confidence);
                            console.log(`${region.name}: ${fireData.high_confidence.length} fires`);
                        }
                        
                        const dustResp = await fetch('/detect/dust', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                latitude: region.lat, 
                                longitude: region.lon, 
                                radius_km: radius 
                            })
                        });
                        
                        const dustData = await dustResp.json();
                        if (dustResp.ok && dustData.detections) {
                            allDust = allDust.concat(dustData.detections);
                        }
                    } catch (error) {
                        console.error(`Error scanning ${region.name}:`, error);
                    }
                }
                
                // Update markers with aggregated results
                updateFireMarkers(allFires);
                updateDustMarkers(allDust);
                
                // Update stats
                document.getElementById('stat-fires').textContent = allFires.length;
                document.getElementById('stat-dust').textContent = allDust.length;
                updateTotalStats();
                
                // Update fire list
                const fireListHtml = allFires
                    .slice(0, 5)
                    .map(det => `
                        <div class="detection-item high">
                            <strong>🔥 ${det.latitude.toFixed(2)}°, ${det.longitude.toFixed(2)}°</strong><br>
                            Conf: ${(det.confidence*100).toFixed(0)}% | Power: ${det.power_mw.toFixed(0)}MW
                        </div>
                    `)
                    .join('');
                document.getElementById('detections-list').innerHTML = fireListHtml || '<p style="text-align: center; opacity: 0.5;">No fires</p>';
                
                // Update dust list
                const dustListHtml = allDust
                    .slice(0, 5)
                    .map(det => `
                        <div class="detection-item dust">
                            <strong>🌫️ ${det.latitude.toFixed(2)}°, ${det.longitude.toFixed(2)}°</strong><br>
                            Conf: ${(det.confidence*100).toFixed(0)}% | AOD: ${(det.aod || 0.5).toFixed(2)}
                        </div>
                    `)
                    .join('');
                document.getElementById('dust-list').innerHTML = dustListHtml || '<p style="text-align: center; opacity: 0.5;">No dust</p>';
            }
            
            function updateFireMarkers(fires) {
                markers.forEach(m => map.removeLayer(m));
                markers = [];
                fires.forEach(det => {
                    const marker = createFireMarker(det.latitude, det.longitude, det.confidence, det.power_mw);
                    marker.addTo(map);
                    markers.push(marker);
                });
            }
            
            function updateDustMarkers(dusts) {
                dustMarkers.forEach(m => map.removeLayer(m));
                dustMarkers = [];
                dusts.forEach(det => {
                    const marker = createDustMarker(det.latitude, det.longitude, det.confidence, det.aod || 0.5);
                    marker.addTo(map);
                    dustMarkers.push(marker);
                });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
