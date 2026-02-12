"""Utils module for satellite detection project"""

try:
    from .web_scraper import NASAWorldviewScraper
except ImportError:
    NASAWorldviewScraper = None

try:
    from .nasa_api import (
        SatelliteImageFetcher,
        ImageCache,
        fetch_satellite_image,
        validate_coordinates,
        enhance_satellite_image,
        create_image_thumbnail
    )
except ImportError:
    SatelliteImageFetcher = None
    ImageCache = None
    fetch_satellite_image = None
    validate_coordinates = None
    enhance_satellite_image = None
    create_image_thumbnail = None

__all__ = [
    'NASAWorldviewScraper',
    'SatelliteImageFetcher',
    'ImageCache',
    'fetch_satellite_image',
    'validate_coordinates',
    'enhance_satellite_image',
    'create_image_thumbnail'
]