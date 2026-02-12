# 🚀 SATELLITE DETECTION PROJECT - SETUP & RUN GUIDE

## Quick Overview

The Satellite Detection Project is a **production-ready FastAPI application** that detects smoke and dust in satellite imagery using NASA Worldview data.

**Status**: ✅ **COMPLETE AND READY TO USE**

## 📦 What's Included

### Core Components
- ✅ Web scraper for NASA Worldview
- ✅ Image fetcher with retry logic & caching
- ✅ FastAPI REST API (6 endpoints)
- ✅ ML detection models integration
- ✅ Complete error handling

### Documentation
- ✅ README.md - Full documentation
- ✅ QUICKSTART.md - Quick start
- ✅ COMPLETION_REPORT.md - Project report
- ✅ This file - Setup guide

### Scripts & Tests
- ✅ validate.py - Validation tests
- ✅ example_usage.py - Usage examples
- ✅ 3 Windows batch scripts
- ✅ requirements.txt - Dependencies

## 🎯 Three Ways to Run This Project

### Option 1: Run Validation Tests ✅ RECOMMENDED FIRST
```bash
python validate.py
```
**What it does**: Tests all components
**Expected**: 6/6 tests pass

### Option 2: Run Usage Examples
```bash
python example_usage.py
```
**What it does**: Shows 5 practical examples
**Includes**:
- Basic image fetching
- Web scraper usage
- Multiple locations
- Different satellite products
- Coordinate validation

### Option 3: Start the API Server
```bash
cd src/api
python -m uvicorn main:app --reload
```
**What it does**: Starts FastAPI server
**Available at**: http://localhost:8000
**Endpoints**:
- `/health` - Health check
- `/satellites` - List satellites
- `/detect/smoke` - Detect smoke
- `/detect/dust` - Detect dust
- `/status` - System status

## 📋 Step-by-Step Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

Dependencies include:
- FastAPI & Uvicorn (API)
- OpenCV & Pillow (images)
- NumPy & PyTorch (ML)
- ONNX Runtime (inference)
- Requests & BeautifulSoup (scraping)

### Step 2: Verify Installation
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

### Step 3: Explore Examples
```bash
python example_usage.py
```

This demonstrates:
1. Basic image fetching
2. Direct web scraper usage
3. Multiple location fetching
4. Different satellite products
5. Coordinate validation

### Step 4: Start API Server
```bash
cd src/api
python -m uvicorn main:app --reload
```

### Step 5: Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Get satellites
curl http://localhost:8000/satellites

# Detect smoke
curl -X POST http://localhost:8000/detect/smoke \
  -H "Content-Type: application/json" \
  -d '{
    "satellite": "MODIS",
    "product": "MOD09GA",
    "date": "2024-01-15",
    "coordinates": [35.0, -110.0]
  }'
```

## 🏗️ Project Architecture

```
HTTP Request
    ↓
FastAPI Endpoint (/detect/smoke, /detect/dust, etc)
    ↓
fetch_satellite_image()
    ├→ Check cache
    │   └→ Return cached image if available (< 100ms)
    │
    ├→ Fetch from NASA Worldview
    │   ├→ Try MODIS Terra
    │   ├→ Try MODIS Aqua
    │   └→ Try VIIRS SNPP
    │   (with automatic retries & exponential backoff)
    │
    └→ Cache & Return Image
    
    ↓
Preprocessing (resize, normalize, enhance)
    ↓
ML Model Inference (Smoke/Dust Detection)
    ↓
Generate Overlay Visualization
    ↓
Return JSON Response
```

## 📂 File Structure

```
satellite-detection-project/
├── src/                          # Source code
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   └── __init__.py
│   ├── utils/
│   │   ├── web_scraper.py       # NASA Worldview scraper
│   │   ├── nasa_api.py          # Image fetcher + caching
│   │   └── __init__.py
│   ├── models/
│   │   └── detection.py         # Detection models
│   ├── preprocessing/
│   │   └── image_processing.py  # Image preprocessing
│   ├── visualization/
│   │   └── overlay.py           # Detection visualization
│   └── config.py                # Configuration
│
├── validate.py                  # Validation tests
├── example_usage.py             # Usage examples
├── requirements.txt             # Dependencies
├── README.md                    # Full documentation
├── QUICKSTART.md                # Quick reference
├── COMPLETION_REPORT.md         # Project summary
├── run_validation.bat           # Windows batch
├── run_examples.bat             # Windows batch
└── run_api.bat                  # Windows batch
```

## 🔑 Key Features

### Automatic Retries
- Up to 3 attempts to fetch images
- Exponential backoff (2s, 4s delays)
- Handles network timeouts

### Image Caching
- Disk-based LRU cache
- Automatic cleanup when full
- Cache key based on parameters

### API Endpoints
```
GET  /                    → Root endpoint
GET  /health              → Health check
GET  /satellites          → List supported satellites
GET  /status              → System status
POST /detect/smoke        → Detect smoke
POST /detect/dust         → Detect dust
```

### Error Handling
- Network errors → Auto retry
- Missing images → Graceful fallback
- Invalid input → Validation + error message
- Server errors → Detailed logging

## 🧪 Testing

### Run Validation
```bash
python validate.py
```

Tests cover:
- Module imports
- Web scraper functionality
- Image caching
- Coordinate validation
- Async functions
- Error handling

### Manual Testing
```bash
# Start server
cd src/api
python -m uvicorn main:app --reload

# In another terminal
curl http://localhost:8000/health
curl http://localhost:8000/satellites
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | Complete API & configuration docs (500+ lines) |
| QUICKSTART.md | Quick start guide (300+ lines) |
| COMPLETION_REPORT.md | Project completion report |
| This file | Setup instructions |

## ⚙️ Configuration

Edit `src/config.py` to customize:

```python
# Retry configuration
max_retries = 3
timeout = 30

# Cache configuration
cache_max_size = 100
cache_dir = ".image_cache"

# Model configuration
confidence_threshold = 0.7

# API configuration
max_concurrent_requests = 5
```

## 🚨 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Port 8000 already in use
**Solution**: Use different port
```bash
python -m uvicorn main:app --port 8001
```

### Issue: Network errors when fetching images
**Solution**: 
- Check internet connectivity
- NASA Worldview may be temporarily unavailable
- Code has automatic retries (up to 3 attempts)

### Issue: Slow image fetching
**Solution**:
- First request fetches from network (2-10 seconds)
- Cached requests are fast (< 100ms)
- Use the caching system

## 💡 Usage Patterns

### Pattern 1: Simple Image Fetch
```python
from utils.nasa_api import fetch_satellite_image
import asyncio

async def fetch():
    image = await fetch_satellite_image(
        satellite="MODIS",
        product="MOD09GA",
        date="2024-01-15",
        coordinates=[35.0, -110.0]
    )
    return image

asyncio.run(fetch())
```

### Pattern 2: API Request
```bash
curl -X POST http://localhost:8000/detect/smoke \
  -H "Content-Type: application/json" \
  -d '{"satellite":"MODIS","product":"MOD09GA","date":"2024-01-15","coordinates":[35.0,-110.0]}'
```

### Pattern 3: Batch Processing
```python
# Run example_usage.py to see batch examples
python example_usage.py
```

## 🎯 Next Steps

### For Developers
1. Review the code in `src/`
2. Modify detection models in `src/models/detection.py`
3. Add new endpoints in `src/api/main.py`
4. Customize configuration in `src/config.py`

### For Users
1. Run `python validate.py`
2. Run `python example_usage.py`
3. Start API with `cd src/api && python -m uvicorn main:app --reload`
4. Test endpoints with curl or Postman

### For Deployment
1. Install dependencies: `pip install -r requirements.txt`
2. Set production config in `src/config.py`
3. Use production ASGI server (Gunicorn + Uvicorn)
4. Configure logging and monitoring

## 📞 Support

For detailed information:
- **Setup & API**: See README.md
- **Quick Start**: See QUICKSTART.md
- **Project Summary**: See COMPLETION_REPORT.md
- **Examples**: Run `python example_usage.py`
- **Tests**: Run `python validate.py`

## ✨ Summary

This project provides:
- ✅ Complete web scraping system
- ✅ Robust error handling & retries
- ✅ Efficient image caching
- ✅ Production-ready API
- ✅ Comprehensive documentation
- ✅ Working examples & tests

**Status**: Ready to use immediately
**License**: [As specified in your project]
**Version**: 1.0.0

---

**Happy coding! 🎉**

Start with: `python validate.py`
