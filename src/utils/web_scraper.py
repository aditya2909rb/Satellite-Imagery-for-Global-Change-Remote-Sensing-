import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
from datetime import datetime
import time
import logging
import numpy as np
import cv2
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

class NASAWorldviewScraper:
    """Web scraper for NASA Worldview website to fetch satellite imagery"""

    def __init__(self, base_url: str = "https://worldview.earthdata.nasa.gov", request_timeout: int = 30):
        self.base_url = base_url
        self.request_timeout = request_timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _construct_image_url(self, coordinates: List[float], date: str, layers: List[str]) -> str:
        """Construct direct image download URL based on coordinates, date, and layers"""
        try:
            lat, lon = coordinates[0], coordinates[1]
            
            # Construct Worldview API URL for downloading snapshots
            # This uses the snapshot API endpoint
            url = f"{self.base_url}/api/v1/snapshot"
            
            # Prepare parameters for the snapshot request
            params = {
                'REQUEST': 'GetSnapshot',
                'VERSION': '1.3.0',
                'BBOX': f"{lon-0.5},{lat-0.5},{lon+0.5},{lat+0.5}",
                'CRS': 'EPSG:4326',
                'SRS': 'EPSG:4326',
                'LAYERS': ','.join(layers),
                'TIME': date,
                'WIDTH': '512',
                'HEIGHT': '512',
                'FORMAT': 'image/jpeg',
                'TRANSPARENT': 'false'
            }
            
            # Return complete URL with parameters
            query_string = '&'.join(f"{k}={v}" for k, v in params.items())
            return f"{url}?{query_string}"
            
        except Exception as e:
            logger.error(f"Error constructing image URL: {e}")
            return None

    def fetch_satellite_image(self, coordinates: List[float], date: str, 
                            layers: List[str] = None) -> Optional[np.ndarray]:
        """Fetch satellite image from NASA Worldview"""
        try:
            if layers is None:
                layers = [
                    'VIIRS_SNPP_CorrectedReflectance_TrueColor',
                    'MODIS_Aqua_CorrectedReflectance_TrueColor',
                    'MODIS_Terra_CorrectedReflectance_TrueColor'
                ]

            logger.info(f"Fetching satellite image for coordinates {coordinates} on {date}")

            # Try to get image from different services
            for layer in layers:
                try:
                    image = self._fetch_from_layer(coordinates, date, layer)
                    if image is not None:
                        logger.info(f"Successfully fetched image from layer {layer}")
                        return image
                except Exception as e:
                    logger.warning(f"Failed to fetch from layer {layer}: {e}")
                    continue

            logger.warning("Could not fetch image from any layer")
            return None

        except Exception as e:
            logger.error(f"Error fetching satellite image: {e}")
            return None

    def _fetch_from_layer(self, coordinates: List[float], date: str, layer: str) -> Optional[np.ndarray]:
        """Fetch image from specific layer"""
        try:
            # Construct WMS request
            lat, lon = coordinates[0], coordinates[1]
            
            # Use GIBS (Global Imagery Browse Services) or WorldView endpoints
            url = f"{self.base_url}/geoserver/wms"
            
            params = {
                'service': 'WMS',
                'version': '1.3.0',
                'request': 'GetMap',
                'layers': layer,
                'bbox': f"{lon-0.5},{lat-0.5},{lon+0.5},{lat+0.5}",
                'width': '512',
                'height': '512',
                'crs': 'EPSG:4326',
                'format': 'image/jpeg',
                'time': date
            }

            response = self.session.get(url, params=params, timeout=self.request_timeout)
            response.raise_for_status()

            # Convert bytes to numpy array
            image = Image.open(BytesIO(response.content))
            image_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            return image_array

        except Exception as e:
            logger.debug(f"Error fetching from layer {layer}: {e}")
            return None

    def get_available_layers(self) -> List[str]:
        """Get list of available layers"""
        return [
            'VIIRS_SNPP_CorrectedReflectance_TrueColor',
            'MODIS_Aqua_CorrectedReflectance_TrueColor',
            'MODIS_Terra_CorrectedReflectance_TrueColor',
            'GOES16_ABI_DisplayTrueColor'
        ]

    def get_image_metadata(self, coordinates: List[float], date: str) -> Dict:
        """Get metadata for the image"""
        return {
            'source': 'NASA Worldview',
            'coordinates': coordinates,
            'date': date,
            'timestamp': datetime.now().isoformat(),
            'layers': 'True Color Imagery'
        }