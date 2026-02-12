# Satellite Fire Detection System - New Features Guide

This document provides a comprehensive guide to all the new features implemented in the Satellite Fire Detection System.

## 🚀 New Features Overview

The system now includes the following advanced capabilities:

1. **📧 Email Alerts for High-Confidence Fires**
2. **🗺️ Map Visualization Endpoint**
3. **📊 Historical Fire Data Tracking**
4. **📤 Export Data to CSV/JSON**
5. **🌐 Simple Web UI for Easy Access**

## 📧 Email Alerts System

### Configuration
```python
# Configure email alerts
POST /alerts/configure
{
    "email": "your-email@example.com",
    "password": "your-app-password",
    "recipients": ["admin@example.com", "emergency@example.com"],
    "enable": true
}
```

### Send Alerts
```python
# Send fire alert for high-confidence detections
POST /alerts/send
{
    "detections": [...],
    "coordinates": [35.0, -110.0],
    "radius_km": 50.0,
    "confidence_threshold": 0.8
}
```

### Features
- ✅ HTML email format with detailed fire information
- ✅ CSV attachment with detection data
- ✅ Automatic filtering for high-confidence fires (>80%)
- ✅ Configurable recipient lists
- ✅ Error handling and logging

## 🗺️ Map Visualization

### Fire Detection Map
```python
# Create interactive fire detection map
POST /maps/fire
{
    "detections": [...],
    "center_coordinates": [35.0, -110.0],
    "search_radius_km": 50.0,
    "title": "Fire Detection Map"
}
```

### Dashboard Map
```python
# Create comprehensive dashboard with all detection types
POST /maps/dashboard
{
    "fire_detections": [...],
    "smoke_detections": [...],
    "dust_detections": [...],
    "center_coordinates": [35.0, -110.0],
    "title": "Detection Summary Dashboard"
}
```

### Features
- ✅ Interactive Folium maps with markers
- ✅ Color-coded confidence levels
- ✅ Search radius visualization
- ✅ Popups with detailed information
- ✅ Legend and statistics
- ✅ Multiple map types (fire, smoke, dust, dashboard)

## 📊 Historical Fire Data Tracking

### Add Detections to History
```python
# Automatically done when detecting fires
# Or manually add detections
fire_history.add_detection(detection, search_radius_km, center_coordinates)
```

### Get Recent Detections
```python
# Get recent fire detections
GET /history/recent?hours=24&min_confidence=0.5&limit=100
```

### Get Detections by Location
```python
# Get detections by geographic area
GET /history/location?latitude=35.0&longitude=-110.0&radius_km=50&days=30
```

### Get Statistics
```python
# Get fire detection statistics
GET /history/statistics?days=30
```

### Features
- ✅ SQLite database for persistent storage
- ✅ Automatic cleanup of old records
- ✅ Geographic and temporal filtering
- ✅ Comprehensive statistics
- ✅ Alert tracking and management

## 📤 Data Export System

### Export to CSV
```python
# Export data to CSV format
GET /export/csv
{
    "data": [...],
    "filename": "export.csv"
}
```

### Export to JSON
```python
# Export data to JSON format
GET /export/json
{
    "data": [...],
    "filename": "export.json"
}
```

### Fire Summary Export
```python
# Export comprehensive fire detection summary
GET /export/fire-summary
{
    "detections": [...],
    "filename": "summary.json"
}
```

### Batch Export
```python
# Export to multiple formats at once
data_exporter.batch_export(data, formats=['csv', 'json', 'excel'])
```

### Features
- ✅ CSV, JSON, and Excel export formats
- ✅ Fire detection summary reports
- ✅ Alert report generation
- ✅ Historical trends analysis
- ✅ Configurable file naming and formatting

## 🌐 Simple Web UI

### Access the UI
Navigate to: `http://localhost:8000/ui`

### UI Features
- 🔍 **Fire Detection**: Real-time fire detection with coordinates
- 📧 **Email Configuration**: Easy setup of email alerts
- 📊 **Historical Data**: View and export historical fire data
- 🗺️ **Map Generation**: Create interactive maps with one click
- 📤 **Data Export**: Export data in multiple formats

### UI Components
1. **Fire Detection Panel**
   - Input latitude/longitude
   - Set search radius
   - View detection results
   - Send alerts and generate maps

2. **Email Configuration Panel**
   - Configure SMTP settings
   - Set recipient lists
   - Enable/disable alerts

3. **Historical Data Panel**
   - Filter by time period
   - Set confidence thresholds
   - View statistics
   - Export data

4. **Map Generation Panel**
   - Create fire detection maps
   - Generate dashboard maps
   - Customize map titles
   - View and download maps

## 🔧 Configuration System

### Email Configuration
```python
from config import AppConfig

AppConfig.update_email_config({
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "alerts@example.com",
    "recipients": ["admin@example.com"],
    "enabled": True
})
```

### Database Configuration
```python
AppConfig.update_database_config({
    "db_path": "data/fire_history.db",
    "max_history_days": 365,
    "backup_interval_hours": 24
})
```

### Export Configuration
```python
AppConfig.update_export_config({
    "export_dir": "exports",
    "csv_delimiter": ",",
    "json_indent": 2
})
```

### Map Configuration
```python
AppConfig.update_map_config({
    "default_zoom": 8,
    "map_tile_provider": "OpenStreetMap",
    "fire_marker_color": "red"
})
```

## 🚀 Quick Start

### 1. Start the API Server
```bash
cd satellite-detection-project/src/api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Access the Web UI
Open your browser and navigate to: `http://localhost:8000/ui`

### 3. Configure Email Alerts
Use the Email Configuration panel in the UI or call:
```bash
curl -X POST "http://localhost:8000/alerts/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-app-password",
    "recipients": ["admin@example.com"],
    "enable": true
  }'
```

### 4. Detect Fires
```bash
curl -X POST "http://localhost:8000/fires/region" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 35.0,
    "longitude": -110.0,
    "radius_km": 50.0
  }'
```

### 5. View Historical Data
```bash
curl "http://localhost:8000/history/recent?hours=24&min_confidence=0.5"
```

### 6. Generate Maps
```bash
curl -X POST "http://localhost:8000/maps/fire" \
  -H "Content-Type: application/json" \
  -d '{
    "detections": [...],
    "center_coordinates": [35.0, -110.0],
    "search_radius_km": 50.0,
    "title": "Fire Detection Map"
  }'
```

## 📁 File Structure

```
satellite-detection-project/
├── src/
│   ├── config.py                    # Configuration system
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── email_alerts.py          # Email alert system
│   │   ├── fire_history.py          # Historical data tracking
│   │   ├── map_visualization.py     # Map generation
│   │   └── data_export.py           # Data export functionality
│   └── api/
│       ├── main.py                  # Updated API with new endpoints
│       └── ...
├── static/
│   ├── maps/                        # Generated map files
│   └── exports/                     # Exported data files
├── data/
│   └── fire_history.db              # SQLite database
├── test_new_features.py             # Test script
└── NEW_FEATURES_GUIDE.md            # This file
```

## 🔍 API Endpoints Summary

### Email Alerts
- `POST /alerts/configure` - Configure email settings
- `POST /alerts/send` - Send fire alerts

### Historical Data
- `GET /history/recent` - Get recent detections
- `GET /history/location` - Get detections by location
- `GET /history/statistics` - Get detection statistics

### Map Visualization
- `POST /maps/fire` - Create fire detection maps
- `POST /maps/dashboard` - Create dashboard maps
- `GET /static/maps/{filename}` - Serve map files

### Data Export
- `GET /export/csv` - Export to CSV
- `GET /export/json` - Export to JSON
- `GET /export/fire-summary` - Export fire summary
- `GET /static/exports/{filename}` - Serve export files

### Web Interface
- `GET /ui` - Simple web UI

## 🛠️ Dependencies

New dependencies required for the features:
- `folium` - Map visualization
- `pandas` - Excel export (optional)
- `sqlite3` - Database (built-in)
- `smtplib` - Email sending (built-in)

## 📝 Notes

- All new features are backward compatible
- Email functionality requires valid SMTP credentials
- Map files are saved in the `static/maps/` directory
- Export files are saved in the `static/exports/` directory
- Historical data is stored in SQLite database
- The system includes comprehensive error handling and logging

## 🎉 Conclusion

The Satellite Fire Detection System now provides a complete solution for fire detection and monitoring with:

- **Real-time detection** with NASA FIRMS integration
- **Email alerts** for high-confidence fires
- **Interactive maps** for visualization
- **Historical tracking** for trend analysis
- **Data export** for further analysis
- **Simple web UI** for easy access

All features are designed to work together seamlessly and provide a comprehensive fire monitoring solution.