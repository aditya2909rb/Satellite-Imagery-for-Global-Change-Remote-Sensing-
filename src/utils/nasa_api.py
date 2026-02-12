import asyncio
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
import cv2
from datetime import datetime, timedelta
import logging
import hashlib
from functools import lru_cache
import pickle
from .web_scraper import NASAWorldviewScraper

logger = logging.getLogger(__name__)

class ImageCache:
    """Simple cache for satellite images"""
    def __init__(self, cache_dir: str = ".image_cache", max_size: int = 100):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size = max_size
        self.access_times = {}

    def _get_cache_key(self, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_str = str(sorted(kwargs.items()))
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, **kwargs) -> Optional[np.ndarray]:
        """Get image from cache"""
        try:
            cache_key = self._get_cache_key(**kwargs)
            cache_path = self.cache_dir / f"{cache_key}.pkl"

            if cache_path.exists():
                self.access_times[cache_key] = datetime.now()
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        return None

    def set(self, image: np.ndarray, **kwargs):
        """Store image in cache"""
        try:
            cache_key = self._get_cache_key(**kwargs)
            cache_path = self.cache_dir / f"{cache_key}.pkl"

            with open(cache_path, 'wb') as f:
                pickle.dump(image, f)
            self.access_times[cache_key] = datetime.now()
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    def clear_old(self):
        """Remove least recently used cache entries"""
        if len(self.access_times) > self.max_size:
            oldest = min(self.access_times.items(), key=lambda x: x[1])
            cache_path = self.cache_dir / f"{oldest[0]}.pkl"
            try:
                cache_path.unlink()
                del self.access_times[oldest[0]]
            except Exception as e:
                logger.warning(f"Cache cleanup error: {e}")

class SatelliteImageFetcher:
    """Fetch satellite imagery from NASA Worldview with retry and caching"""
    def __init__(self, max_retries: int = 3, timeout: int = 30, enable_cache: bool = True):
        self.scraper = NASAWorldviewScraper()
        self.max_retries = max_retries
        self.timeout = timeout
        self.cache = ImageCache() if enable_cache else None

    async def fetch_satellite_image(
        self,
        satellite: str,
        product: str,
        date: str,
        coordinates: List[float],
        radius_km: float = 50.0
    ) -> Optional[np.ndarray]:
        """Fetch satellite image with retry logic and caching"""
        try:
            cache_key = {
                'satellite': satellite,
                'product': product,
                'date': date,
                'coordinates': tuple(coordinates),
                'radius_km': radius_km
            }

            if self.cache:
                cached_image = self.cache.get(**cache_key)
                if cached_image is not None:
                    logger.info("Returning image from cache")
                    return cached_image

            image = None
            last_error = None

            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Fetching image (attempt {attempt + 1}/{self.max_retries})")
                    
                    image = await self._fetch_with_timeout(
                        satellite, product, date, coordinates, radius_km
                    )

                    if image is not None:
                        if self.cache:
                            self.cache.set(image, **cache_key)
                            self.cache.clear_old()
                        return image

                except asyncio.TimeoutError as e:
                    last_error = e
                    logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                except Exception as e:
                    last_error = e
                    logger.warning(f"Error on attempt {attempt + 1}: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)

            logger.error(f"Failed to fetch image after {self.max_retries} attempts: {last_error}")
            return None

        except Exception as e:
            logger.error(f"Error fetching satellite image: {e}")
            return None

    async def _fetch_with_timeout(
        self,
        satellite: str,
        product: str,
        date: str,
        coordinates: List[float],
        radius_km: float
    ) -> Optional[np.ndarray]:
        """Fetch image with timeout"""
        try:
            loop = asyncio.get_event_loop()
            image = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    self.scraper.fetch_satellite_image,
                    coordinates,
                    date,
                    self._get_layers_for_product(product)
                ),
                timeout=self.timeout
            )
            return image
        except asyncio.TimeoutError:
            raise
        except Exception as e:
            logger.error(f"Error in _fetch_with_timeout: {e}")
            return None

    def _get_layers_for_product(self, product: str) -> List[str]:
        """Get appropriate layers for product type"""
        layers_map = {
            'MOD09GA': ['MODIS_Terra_CorrectedReflectance_TrueColor'],
            'MYD09GA': ['MODIS_Aqua_CorrectedReflectance_TrueColor'],
            'VNP09': ['VIIRS_SNPP_CorrectedReflectance_TrueColor'],
            'ABI': ['GOES16_ABI_DisplayTrueColor']
        }
        return layers_map.get(product, [
            'VIIRS_SNPP_CorrectedReflectance_TrueColor',
            'MODIS_Aqua_CorrectedReflectance_TrueColor',
            'MODIS_Terra_CorrectedReflectance_TrueColor'
        ])

# Helper functions for coordinate handling
def validate_coordinates(coordinates: List[float]) -> bool:
    """Validate latitude and longitude coordinates"""
    if len(coordinates) != 2:
        return False
    lat, lon = coordinates
    return -90 <= lat <= 90 and -180 <= lon <= 180

def calculate_radius_pixels(image_size: Tuple[int, int], radius_km: float, resolution_km: float) -> int:
    """Calculate radius in pixels based on image size and resolution"""
    image_width, image_height = image_size
    # Approximate conversion (assuming square pixels)
    return int((radius_km / resolution_km) * 0.5)

# Image processing utilities
def enhance_satellite_image(image: np.ndarray) -> np.ndarray:
    """Enhance satellite image for better visualization"""
    # Convert to LAB color space for illumination correction
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)

    # Merge channels and convert back
    lab_enhanced = cv2.merge([l_enhanced, a, b])
    image_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    return image_enhanced

def create_image_thumbnail(image: np.ndarray, max_size: int = 256) -> np.ndarray:
    """Create thumbnail of image"""
    height, width = image.shape[:2]
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))

    thumbnail = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return thumbnail

# Global fetcher instance
_fetcher = SatelliteImageFetcher(max_retries=3, timeout=30, enable_cache=True)

# Export main function
async def fetch_satellite_image(
    satellite: str,
    product: str,
    date: str,
    coordinates: List[float],
    radius_km: float = 50.0
) -> Optional[np.ndarray]:
    """
    Fetch satellite image from NASA Worldview.
    
    Args:
        satellite: Satellite name (e.g., 'MODIS', 'VIIRS')
        product: Product name (e.g., 'MOD09GA', 'VNP09')
        date: Date in YYYY-MM-DD format
        coordinates: [lat, lon] coordinates
        radius_km: Search radius in kilometers
        
    Returns:
        Image as numpy array or None if fetch fails
    """
    return await _fetcher.fetch_satellite_image(
        satellite=satellite,
        product=product,
        date=date,
        coordinates=coordinates,
        radius_km=radius_km
    )