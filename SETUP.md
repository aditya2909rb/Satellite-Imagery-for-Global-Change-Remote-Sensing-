# Setup Guide

This guide will walk you through setting up the Satellite Fire Detection System on your local machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Internet connection (for NASA FIRMS data access)

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/satellite-fire-detection.git
cd satellite-fire-detection
```

### 2. Create a Virtual Environment

Creating a virtual environment is highly recommended to avoid dependency conflicts.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
# Install main project dependencies
pip install -r requirements.txt

# Install satellite-detection-project specific dependencies
cd satellite-detection-project
pip install -r requirements.txt
cd ..
```

### 4. Verify Installation

Run the validation script to ensure everything is set up correctly:

```bash
cd satellite-detection-project
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
...
Total: 6/6 tests passed
```

### 5. Create Data Directories

The application will create these automatically, but you can create them manually:

```bash
mkdir -p data/images
mkdir -p data/models
mkdir -p static/exports
mkdir -p static/maps
mkdir -p logs
```

### 6. Configure Environment Variables (Optional)

Create a `.env` file in the project root for custom configuration:

```bash
# NASA FIRMS API (optional)
NASA_FIRMS_API_KEY=your_api_key_here

# Email alerts (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_RECIPIENTS=recipient1@email.com,recipient2@email.com

# Server configuration
HOST=0.0.0.0
PORT=8000
```

### 7. Run the Application

**Option 1: Using the quick launcher (Windows)**
```bash
# From project root
python app.py
```

**Option 2: Using start_server.py**
```bash
cd satellite-detection-project
python start_server.py
```

**Option 3: Using uvicorn directly**
```bash
cd satellite-detection-project/src
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 8. Access the Application

Open your browser and navigate to:

- **Dashboard:** http://localhost:8000/
- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## Troubleshooting

### Import Errors

If you get import errors:
1. Make sure you're in the correct directory
2. Verify virtual environment is activated
3. Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use

If port 8000 is unavailable:
```bash
# Use a different port
uvicorn api.main:app --host 0.0.0.0 --port 8080
```

### Missing Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Permission Issues (Linux/Mac)

```bash
# Make scripts executable
chmod +x satellite-detection-project/run_server.py
chmod +x satellite-detection-project/start_server.py
```

## Development Setup

For development with auto-reload:

```bash
cd satellite-detection-project/src
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Install development dependencies:

```bash
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
```

## Testing

Run tests:

```bash
cd satellite-detection-project
pytest

# With coverage
pytest --cov=src --cov-report=html
```

## Docker Setup (Alternative)

Coming soon! Docker support for containerized deployment.

## Need Help?

- Check the [README.md](README.md) for general information
- See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- Open an issue on GitHub for bugs or questions

## Next Steps

Once the application is running, check out:
- [API Documentation](http://localhost:8000/docs) - Interactive API explorer
- [Example Usage](satellite-detection-project/example_usage.py) - Code examples
- [QUICKSTART.md](satellite-detection-project/QUICKSTART.md) - Quick reference guide

Happy coding! 🚀
