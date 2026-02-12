# 🚀 Quick Reference Guide

## Starting the Application

### Method 1: Quick Launch (Recommended)
```bash
python app.py
```

### Method 2: From Project Directory
```bash
cd satellite-detection-project
python start_server.py
```

### Method 3: Using Uvicorn Directly
```bash
cd satellite-detection-project/src
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Access Points

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| System Status | http://localhost:8000/status |

## Common Commands

### Verification
```bash
# Check if ready for GitHub
python check_github_ready.py

# Validate installation
cd satellite-detection-project
python validate.py

# Run tests
pytest
```

### Git Commands
```bash
# Initialize repository
git init

# First commit
git add .
git commit -m "Initial commit"

# Connect to GitHub
git remote add origin https://github.com/username/repo.git
git branch -M main
git push -u origin main

# Subsequent pushes
git add .
git commit -m "Your message"
git push
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
cd satellite-detection-project
pip install -r requirements.txt
```

## API Quick Reference

### Fire Detection
```bash
# Detect fires in region
POST /detect/smoke
{
  "latitude": 36.7783,
  "longitude": -119.4179,
  "radius_km": 100
}

# Get real-time fires
POST /fires/realtime
{
  "source": "VIIRS",
  "hours": 24
}
```

### History & Data
```bash
# Recent detections
GET /history/recent?days=7&limit=50

# Fire statistics
GET /history/stats?start_date=2026-01-01

# Export data
GET /export/csv
GET /export/json
```

### Visualization
```bash
# Generate fire map
POST /maps/fire
{
  "latitude": 36.7783,
  "longitude": -119.4179,
  "radius_km": 100
}

# Summary dashboard
GET /maps/dashboard
```

### Alerts
```bash
# Configure alerts
POST /alerts/configure
{
  "recipients": ["email@example.com"],
  "smtp_server": "smtp.gmail.com"
}

# Enable/disable
POST /alerts/enable
POST /alerts/disable
```

## Troubleshooting

### Import Errors
```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Test import
python -c "import sys; sys.path.insert(0, 'satellite-detection-project/src'); from api.main import app; print('OK')"
```

### Port Issues
```bash
# Use different port
uvicorn api.main:app --host 0.0.0.0 --port 8080
```

### Dependency Issues
```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## File Structure

```
satellite-fire-detection/
├── app.py                          # Quick launcher
├── README.md                       # Main documentation
├── requirements.txt                # Dependencies
├── LICENSE                         # MIT License
├── .gitignore                      # Git ignore rules
├── CONTRIBUTING.md                 # Contribution guide
├── SETUP.md                        # Setup instructions
├── .env.example                    # Config template
├── check_github_ready.py           # Readiness checker
├── GITHUB_READY.md                 # Deployment guide
├── DEPLOYMENT_CHECKLIST.md         # Pre-push checklist
├── .github/workflows/              # CI/CD
└── satellite-detection-project/    # Main application
    ├── src/                        # Source code
    │   ├── api/                    # API endpoints
    │   ├── models/                 # ML models
    │   ├── preprocessing/          # Image processing
    │   ├── visualization/          # Maps & charts
    │   └── utils/                  # Utilities
    ├── data/                       # Data storage
    ├── static/                     # Static files
    ├── logs/                       # Log files
    └── requirements.txt            # Project dependencies
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
NASA_FIRMS_API_KEY=your_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_password
ALERT_RECIPIENTS=email1@test.com,email2@test.com
```

## Resources

- **NASA FIRMS:** https://firms.modaps.eosdis.nasa.gov/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **API Testing:** http://localhost:8000/docs
- **Project Repo:** [Update with your GitHub URL]

## Support

- Open an issue on GitHub
- Check SETUP.md for detailed instructions
- Review DEPLOYMENT_CHECKLIST.md before deploying
- Run `python check_github_ready.py` to verify setup

---

Need help? Run `python app.py` to start and visit http://localhost:8000/docs
