# 🚀 HOW TO RUN THE SATELLITE DETECTION APP

## Quick Start (3 Steps)

### Step 1: Install Dependencies (First Time Only)
```bash
cd "g:\data science p2\satellite-detection-project"
pip install -r requirements.txt
```

### Step 2: Start the API Server
```bash
cd "g:\data science p2\satellite-detection-project\src\api"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO:     Uvicorn running with 1 worker
```

### Step 3: Test the Server (in another terminal)
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{"status": "healthy", "timestamp": "2024-01-15T10:30:00.000Z"}
```

---

## 🎯 What Happens When Server Starts

When you run the server, it will:

1. ✅ Load all models
2. ✅ Initialize the web scraper
3. ✅ Start listening on `http://localhost:8000`
4. ✅ Display API documentation at `/docs` (Swagger UI)

---

## 📍 Available Endpoints

Once server is running, you can access:

### Web Interface
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

**1. Health Check**
```bash
curl http://localhost:8000/health
```

**2. Get Supported Satellites**
```bash
curl http://localhost:8000/satellites
```

**3. System Status**
```bash
curl http://localhost:8000/status
```

**4. Detect Smoke**
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

**5. Detect Dust**
```bash
curl -X POST http://localhost:8000/detect/dust \
  -H "Content-Type: application/json" \
  -d '{
    "satellite": "MODIS",
    "product": "MOD09GA",
    "date": "2024-01-15",
    "coordinates": [35.0, -110.0],
    "radius_km": 50.0
  }'
```

---

## 🔧 Troubleshooting

### Issue: "Module not found" error
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Port 8000 already in use
**Solution**: Use a different port
```bash
python -m uvicorn main:app --port 8001
```

### Issue: "Cannot find module main"
**Solution**: Make sure you're in the src/api directory
```bash
cd "g:\data science p2\satellite-detection-project\src\api"
python -m uvicorn main:app
```

### Issue: Models not loading
**Solution**: Check that model files exist in data/models directory

---

## 📚 Quick Reference

### File Locations
```
g:\data science p2\
├── satellite-detection-project\
│   ├── src\
│   │   └── api\
│   │       └── main.py          ← API server
│   ├── requirements.txt          ← Dependencies
│   ├── README.md                 ← Full documentation
│   └── SETUP_GUIDE.md           ← Setup instructions
```

### Commands
| Action | Command |
|--------|---------|
| Install deps | `pip install -r requirements.txt` |
| Start server | `python -m uvicorn main:app --reload` |
| Test health | `curl http://localhost:8000/health` |
| View docs | Open http://localhost:8000/docs |
| Stop server | Press `CTRL+C` |

---

## 🎓 Using Postman or Other API Clients

If you prefer a GUI, you can use:
- **Postman** (https://www.postman.com)
- **Insomnia** (https://insomnia.rest)
- **Thunder Client** (VSCode extension)

Or use the built-in Swagger UI at: **http://localhost:8000/docs**

---

## ✅ Next Steps

1. **Start the server** (follow Step 2 above)
2. **Open browser** to http://localhost:8000/docs
3. **Try an endpoint** by clicking on it in Swagger UI
4. **Send a request** with sample data
5. **See the response** in the UI

---

## 💡 Tips

- **Live reload**: The server will auto-reload when you change code (due to `--reload` flag)
- **Documentation**: Visit `/docs` for interactive API documentation
- **Caching**: Images are cached, so repeated requests are faster
- **Retries**: Failed image fetches automatically retry up to 3 times
- **Logging**: Check console output for detailed logs

---

**Happy testing! 🎉**

For full documentation, see `README.md` or `SETUP_GUIDE.md`
