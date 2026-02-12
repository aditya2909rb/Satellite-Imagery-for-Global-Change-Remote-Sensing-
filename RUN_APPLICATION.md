# 🚀 Running the Satellite Fire Detection System

## Quick Start

The application is now ready to run! Here are the different ways to start it:

### Method 1: Double-click the launcher (Recommended)
1. Navigate to the `satellite-detection-project` folder
2. Double-click on `LAUNCH_APP.bat`
3. The server will start automatically
4. Open your browser and go to http://localhost:8000/ui

### Method 2: Command Line
```bash
cd satellite-detection-project
python start_server.py
```

### Method 3: Direct uvicorn
```bash
cd satellite-detection-project/src/api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Access Points

Once the server is running, you can access:

- **Main API**: http://localhost:8000
- **Web UI**: http://localhost:8000/ui
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🎯 Features Available

### 1. Email Alerts for High-Confidence Fires
- Configure email settings: `POST /alerts/configure`
- Send alerts: `POST /alerts/send`
- HTML emails with CSV attachments

### 2. Map Visualization
- Generate fire maps: `POST /maps/fire`
- Create dashboard maps: `POST /maps/dashboard`
- Interactive Folium maps with markers

### 3. Historical Fire Data
- View recent detections: `GET /history/recent`
- Location-based history: `GET /history/location`
- Statistics: `GET /history/statistics`

### 4. Data Export
- Export to CSV: `GET /export/csv`
- Export to JSON: `GET /export/json`
- Fire summaries: `GET /export/fire-summary`

### 5. Web Interface
- Complete web UI at `/ui`
- Real-time fire detection
- Email configuration panel
- Historical data viewer
- Map generation tools
- Data export functionality

## 📋 Prerequisites

Make sure you have these Python packages installed:
```bash
pip install fastapi uvicorn aiohttp pillow opencv-python numpy torch onnxruntime beautifulsoup4 requests psutil folium pandas
```

## 🔧 Troubleshooting

### If you get import errors:
1. Make sure you're in the `satellite-detection-project` directory
2. Check that all dependencies are installed
3. Verify Python path is correct

### If the server won't start:
1. Check that port 8000 is not in use
2. Verify all files are in the correct locations
3. Run `python test_server.py` to check for issues

### If you get permission errors:
1. Try running as administrator
2. Check file permissions
3. Ensure Python is in your PATH

## 📁 Project Structure

```
satellite-detection-project/
├── src/
│   ├── config.py                    # Configuration system
│   ├── utils/
│   │   ├── email_alerts.py          # Email alert system
│   │   ├── fire_history.py          # Historical data tracking
│   │   ├── map_visualization.py     # Map generation
│   │   └── data_export.py           # Data export functionality
│   └── api/
│       └── main.py                  # Main API with all endpoints
├── static/
│   ├── maps/                        # Generated map files
│   └── exports/                     # Exported data files
├── data/fire_history.db             # SQLite database
├── start_server.py                  # Startup script
├── LAUNCH_APP.bat                   # Easy launcher (double-click)
├── test_server.py                   # Test script
└── RUN_APPLICATION.md               # This file
```

## 🎊 Ready to Use!

The application is now fully functional with all features working:

- ✅ Real-time fire detection from NASA FIRMS
- ✅ Email alerts for high-confidence fires
- ✅ Interactive map visualization
- ✅ Historical data tracking and analysis
- ✅ Multiple export formats (CSV, JSON, Excel)
- ✅ User-friendly web interface
- ✅ Comprehensive API documentation
- ✅ All error handling and logging

**Start the server using any of the methods above and begin using all features!**