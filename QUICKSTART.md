# SATELLITE DETECTION PROJECT - QUICK START GUIDE

## 🚀 Getting Started

### Step 1: Install Dependencies (One-Time Only)
```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (API framework)
- OpenCV & Pillow (image processing)
- NumPy (numerical computing)
- PyTorch & ONNX Runtime (ML inference)
- Requests & BeautifulSoup (web scraping)
- And more...

### Step 2: Validate Installation
```bash
python validate.py
```

Expected output:
```
============================================================
Satellite Detection Project - Validation Tests
============================================================
✓ PASS: Imports
✓ PASS: Web Scraper
✓ PASS: Image Cache
✓ PASS: Satellite Image Fetcher
✓ PASS: Coordinate Validation
✓ PASS: Async Fetch

Total: 6/6 tests passed
```

### Step 3: Run Examples
```bash
python example_usage.py
```

This demonstrates:
- Fetching satellite images
- Using the web scraper
- Working with multiple locations
- Testing different satellite products
- Coordinate validation

### Step 4: Start the API Server
```bash
cd src/api
python -m uvicorn main:app --reload
```

Server will start at: `http://localhost:8000`

### Step 5: Test the API

**Health Check:**
```bash
curl http://localhost:8000/health
```

**List Satellites:**
```bash
curl http://localhost:8000/satellites
```

**Detect Smoke:**
```bash
curl -X POST http://localhost:8000/detect/smoke \
  -H "Content-Type: application/json" \
  -d '{
    "satellite": "MODIS",
    "product": "MOD09GA",
    "date": "2024-01-15",
    "coordinates": [35.0, -110.0],
    "radius_km": 50.0
  }'
```

**System Status:**
```bash
curl http://localhost:8000/status
```

## 📁 Quick File Reference

| File | Purpose |
|------|---------|
| `validate.py` | Run validation tests |
| `example_usage.py` | See usage examples |
| `src/api/main.py` | API server |
| `src/utils/web_scraper.py` | NASA Worldview scraper |
| `src/utils/nasa_api.py` | Image fetcher with caching |
| `requirements.txt` | Dependencies |
| `README.md` | Full documentation |

## 🔧 Quick Troubleshooting

**Problem: ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**Problem: Port 8000 already in use**
```bash
python -m uvicorn main:app --port 8001
```

**Problem: Import errors with relative paths**
- Make sure to run scripts from project root directory
- Virtual environment should be activated

**Problem: Network errors fetching images**
- NASA Worldview may be temporarily unavailable
- Check internet connectivity
- The code has automatic retries built-in

## 📊 Project Architecture

```
API Request
    ↓
FastAPI Endpoint
    ↓
fetch_satellite_image()
    ├→ Check cache (disk-based LRU)
    ├→ If not cached, fetch from NASA Worldview
    │  ├→ Try Layer 1 (MODIS Terra)
    │  ├→ Try Layer 2 (MODIS Aqua)  
    │  └→ Try Layer 3 (VIIRS SNPP)
    │     With retry logic (3 attempts)
    ├→ Cache result for future use
    └→ Return image
    ↓
Preprocess Image
    ↓
Run ML Model (Smoke/Dust Detection)
    ↓
Create Overlay Visualization
    ↓
Return JSON Response with:
    - Detections (locations, confidence)
    - Base64-encoded overlay image
    - Timestamp
```

## 🎯 Key Features Implemented

✅ **Web Scraping**
- Fetches images from NASA Worldview
- Supports multiple satellite layers
- Automatic layer fallback

✅ **Error Handling**
- Exponential backoff retry logic
- Network timeout handling
- Graceful error messages

✅ **Performance**
- Image caching (disk-based LRU)
- Async/await throughout
- GPU acceleration ready

✅ **API**
- 5 RESTful endpoints
- Async request handling
- CORS enabled

✅ **Documentation**
- Comprehensive README
- API endpoint docs
- Usage examples
- Validation tests

## 📚 Documentation Links

- **Full README**: See README.md for complete documentation
- **API Endpoints**: README.md → "API Endpoints" section
- **Configuration**: README.md → "Configuration" section
- **Troubleshooting**: README.md → "Troubleshooting" section

## ✨ Next Steps

1. **Development:**
   - Modify detection models in `src/models/detection.py`
   - Add new API endpoints in `src/api/main.py`
   - Customize config in `src/config.py`

2. **Production:**
   - Set appropriate log levels
   - Configure rate limiting
   - Enable authentication if needed
   - Use production ASGI server (Gunicorn + Uvicorn)

3. **Integration:**
   - Connect to your own models
   - Integrate with external systems
   - Add database persistence
   - Deploy to cloud platform

## 📞 Support

For detailed information, see README.md in the project root.

---
Last Updated: 2024-01-15
Version: 1.0.0
