# Satellite Smoke & Dust Detection System

A comprehensive system for detecting smoke from wildfires and atmospheric dust using satellite imagery. This system fetches satellite imagery from NASA Worldview (using web scraping with retry logic and caching) and uses machine learning models to detect smoke and dust particles.

## Features

- **Smoke Detection**: Detect smoke from wildfires using deep learning models
- **Dust Detection**: Identify atmospheric dust particles
- **NASA Worldview Integration**: Fetch real-time satellite imagery via web scraping
- **Web Scraping with Retry Logic**: Automatic retries with exponential backoff
- **Image Caching**: Disk-based caching for frequently requested images
- **Real-time Processing**: Fast inference using ONNX and hardware optimization
- **Error Handling**: Comprehensive error handling and logging
- **Visualization**: Create overlays and heatmaps for detected areas
- **API Interface**: RESTful API for easy integration

## System Architecture

```
satellite-detection-project/
├── src/
│   ├── config.py                  # Configuration settings
│   ├── api/
│   │   ├── main.py                # FastAPI application and endpoints
│   │   └── __init__.py
│   ├── models/
│   │   ├── detection.py           # ML detection models
│   │   └── __init__.py
│   ├── preprocessing/
│   │   ├── image_processing.py    # Image preprocessing pipeline
│   │   └── __init__.py
│   ├── visualization/
│   │   ├── overlay.py             # Visualization and overlays
│   │   └── __init__.py
│   └── utils/
│       ├── web_scraper.py         # NASA Worldview web scraper
│       ├── nasa_api.py            # Image fetching with caching and retries
│       └── __init__.py
├── data/
│   ├── models/                    # ML model files
│   └── images/                    # Processed images
├── validate.py                    # Validation and testing script
├── README.md                      # This file
└── requirements.txt
```

## Key Components

### Web Scraper (`utils/web_scraper.py`)
- Fetches satellite images from NASA Worldview
- Supports multiple satellite layers (MODIS, VIIRS, GOES)
- Handles WMS requests for coordinate-based image retrieval

### Image Fetcher (`utils/nasa_api.py`)
- **Retry Logic**: Automatic retries with exponential backoff (up to 3 attempts)
- **Caching**: LRU cache with disk persistence
- **Error Handling**: Comprehensive exception handling and logging
- **Async Support**: Fully asynchronous operations

### Detection Models (`models/detection.py`)
- ONNX runtime-based inference
- GPU acceleration support
- Configurable confidence thresholds
- Bounding box and confidence score outputs

## Installation

### Prerequisites

- Python 3.8+
- pip or conda
- CUDA 11.0+ (optional, for GPU support)

### Setup

1. Clone the repository:
```bash
cd g:\data science p2\satellite-detection-project
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install fastapi uvicorn aiohttp pillow opencv-python numpy torch onnxruntime beautifulsoup4 requests psutil
```

4. Verify installation:
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

## Configuration

Edit `src/config.py` to customize settings:

```python
# Model Configuration
class ModelConfig:
    smoke_model_path: str = "data/models/smoke_detection.onnx"
    dust_model_path: str = "data/models/dust_detection.onnx"
    confidence_threshold: float = 0.7
    max_image_size: int = 2048

# Web Scraping
SatelliteImageFetcher(
    max_retries=3,        # Number of retry attempts
    timeout=30,           # Request timeout in seconds
    enable_cache=True     # Enable image caching
)

# Image Caching
ImageCache(
    cache_dir=".image_cache",  # Cache directory
    max_size=100               # Maximum cached images
)
```

## Usage

### Running the API Server

```bash
cd src/api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Get Supported Satellites
```bash
GET /satellites
```

Response:
```json
{
  "satellites": ["MODIS", "VIIRS", "GOES"],
  "products": ["MOD09GA", "VNP09", "ABI-L2-CMIPF"]
}
```

#### Detect Smoke
```bash
POST /detect/smoke
Content-Type: application/json

{
  "satellite": "MODIS",
  "product": "MOD09GA",
  "date": "2024-01-15",
  "coordinates": [35.0, -110.0],
  "radius_km": 50.0,
  "confidence": 0.7
}
```

#### Detect Dust
```bash
POST /detect/dust
Content-Type: application/json

{
  "satellite": "MODIS",
  "product": "MOD09GA",
  "date": "2024-01-15",
  "coordinates": [35.0, -110.0],
  "radius_km": 50.0,
  "confidence": 0.7
}
```

#### System Status
```bash
GET /status
```

Returns GPU availability, memory usage, and model status.

### Example Requests

```bash
# Health check
curl http://localhost:8000/health

# Detect smoke
curl -X POST http://localhost:8000/detect/smoke \
  -H "Content-Type: application/json" \
  -d '{
    "satellite": "MODIS",
    "product": "MOD09GA",
    "date": "2024-01-15",
    "coordinates": [35.0, -110.0],
    "radius_km": 50.0
  }'

# Get system status
curl http://localhost:8000/status
```

## Error Handling

### Retry Logic

The web scraper automatically retries failed requests:
- 1st attempt: Immediate
- 2nd attempt: After 2 seconds
- 3rd attempt: After 4 seconds

### Caching

Images are cached to avoid redundant downloads:
- Automatic cache cleanup when size exceeds max
- Cache key based on satellite, product, date, coordinates, and radius

### Error Messages

```json
{
  "detail": "Image not found for coordinates [35.0, -110.0] on 2024-01-15"
}
```

Common error codes:
- `404`: Image not found
- `500`: Server error (see detail for cause)
- `422`: Invalid request parameters

## Performance Optimization

### Image Caching
Images are cached locally to avoid redundant fetches from NASA Worldview. Cache is stored in `.image_cache/` directory.

### Rate Limiting
Configure max concurrent requests to avoid overwhelming the server:
```python
AppConfig.max_concurrent_requests = 5
```

### Model Optimization
- GPU acceleration when CUDA is available
- ONNX runtime for efficient inference
- Model quantization for faster processing

## Testing & Validation

Run the validation script to verify all components:

```bash
python validate.py
```

This script tests:
- Module imports
- Web scraper functionality
- Image caching
- Satellite image fetcher
- Coordinate validation
- Async fetch function

## Preprocessing Pipeline

1. **Image Normalization**: Normalize pixel values to [0, 1]
2. **Resizing**: Resize to model input dimensions (512x512)
3. **Enhancement**: Apply CLAHE for contrast enhancement
4. **Atmospheric Correction**: Remove haze and atmospheric effects

## Models

The system uses pre-trained ONNX models:

- **Smoke Detection**: `data/models/smoke_detection.onnx`
- **Dust Detection**: `data/models/dust_detection.onnx`

Both models support:
- GPU inference with CUDA
- Batch processing for efficiency
- Configurable confidence thresholds

## Development

### Running Tests

```bash
python validate.py
```

### Code Structure

- **Web Scraper** (`utils/web_scraper.py`): NASA Worldview integration
- **Image Fetcher** (`utils/nasa_api.py`): Retry logic, caching, error handling
- **Detection Models** (`models/detection.py`): ML inference
- **Preprocessing** (`preprocessing/image_processing.py`): Image normalization
- **Visualization** (`visualization/overlay.py`): Detection visualization
- **API** (`api/main.py`): FastAPI endpoints

### Contributing

1. Test changes with `python validate.py`
2. Ensure error handling is comprehensive
3. Add logging for debugging
4. Follow PEP 8 code style

## Troubleshooting

### Import Errors
Ensure the Python path is correct and all packages are installed.

### Network Issues
The web scraper includes automatic retry logic. If issues persist:
1. Check internet connectivity
2. Verify NASA Worldview is accessible
3. Check firewall rules

### Memory Issues
Reduce cache size or limit concurrent requests to use less memory.

## Performance Metrics

### Typical Response Times
- Image fetch: 2-10 seconds (network dependent)
- Detection inference: 0.5-2 seconds (CPU)
- Detection inference: 0.1-0.5 seconds (GPU)
- Total request: 3-15 seconds

### Resource Usage
- Memory: 500MB - 2GB
- Disk: 100MB base + cache
- CPU: 1-4 cores recommended

## License

This project is licensed under the MIT License.

## Contact

For questions and support, please open an issue in the repository.