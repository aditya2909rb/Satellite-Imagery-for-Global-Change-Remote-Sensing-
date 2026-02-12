"""
NASA FIRMS API Client

Fetches real-time active fire data from NASA satellites using the FIRMS API.

Uses VIIRS (Visible Infrared Imaging Radiometer Suite) and MODIS thermal anomaly data
to detect active fires with high accuracy.

Data sources:
- VIIRS NOAA-20: 375m resolution, twice-daily coverage
- VIIRS Suomi NPP: 375m resolution, twice-daily coverage  
- MODIS Combined (Aqua + Terra): 1km resolution, four times daily

Returns fire detections with:
- Geographic coordinates (lat/lon)
- Brightness temperature (Kelvin)
- Fire Radiative Power (MW)
- Confidence level
- Acquisition date/time
- Satellite identifier
"""

import requests
from datetime import datetime, timedelta
import math
import csv
from io import StringIO
import logging

logger = logging.getLogger(__name__)

class NASAFIRMSAPIClient:
    """Client for fetching real-time fire data from NASA FIRMS API"""
    
    # FIRMS API endpoint
    BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
    
    # MAP KEY for authentication
    MAP_KEY = "c0e5c18bf19930f3dedbeb10e2a8b9e0"
    
    # Available data sources
    SOURCES = {
        'viirs_noaa20': 'VIIRS_NOAA20_NRT',
        'viirs_snpp': 'VIIRS_SNPP_NRT',
        'modis': 'MODIS_NRT',
        'viirs': 'VIIRS_SNPP_NRT'  # Default VIIRS
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NASA-FIRMS-Fire-Detection/1.0'
        })
    
    def fetch_fires_in_region(self, lat, lon, radius_km=200, date=None, source='viirs_noaa20', day_range=1):
        """
        Fetch active fires within a specified region using FIRMS API.
        
        Args:
            lat: Latitude of center point
            lon: Longitude of center point
            radius_km: Search radius in kilometers (default 200, max 1000)
            date: Date to query (YYYY-MM-DD format), defaults to yesterday
            source: Data source (viirs_noaa20, viirs_snpp, modis, viirs)
            day_range: Number of days to look back (1-10, default 1)
            
        Returns:
            List of fire detections with properties:
            - latitude, longitude: Fire location
            - brightness: Brightness temperature (Kelvin)
            - brightness_t31: Channel T31 brightness (Kelvin) for VIIRS
            - frp: Fire Radiative Power (MW)
            - confidence: Detection confidence (0.0-1.0)
            - daynight: 'D' for day, 'N' for night
            - acq_date: Acquisition date (YYYY-MM-DD)
            - acq_time: Acquisition time (HHMM)
            - satellite: Satellite identifier
            - scan: Scan pixel size (km)
            - track: Track pixel size (km)
        """
        # Limit radius to API maximum
        radius_km = min(radius_km, 1000)
        
        # Get data source name
        source_name = self.SOURCES.get(source, self.SOURCES['viirs_noaa20'])
        
        # Build API URL: /api/area/csv/{MAP_KEY}/{source}/{lon},{lat},{radius_km}/{day_range}
        url = f"{self.BASE_URL}/{self.MAP_KEY}/{source_name}/{lon},{lat},{radius_km}/{day_range}"
        
        logger.info(f"Fetching FIRMS data from: {url}")
        
        try:
            # Short timeout (3s) to fail fast when network is blocked
            response = self.session.get(url, timeout=3)
            response.raise_for_status()
            
            # Parse CSV response
            fires = self._parse_csv_response(response.text)
            
            logger.info(f"Found {len(fires)} fires in region")
            
            # Calculate distances
            for fire in fires:
                distance = self._haversine_distance(
                    lat, lon,
                    fire['latitude'], fire['longitude']
                )
                fire['distance_km'] = distance
            
            return fires
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch FIRMS data: {e}")
            return []
    
    def _parse_csv_response(self, csv_text):
        """
        Parse CSV response from FIRMS API.
        
        Args:
            csv_text: CSV text response from API
            
        Returns:
            List of fire detections
        """
        fires = []
        
        try:
            reader = csv.DictReader(StringIO(csv_text))
            
            for row in reader:
                fire = {
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'brightness': float(row.get('brightness', 0)),
                    'brightness_t31': float(row.get('bright_t31', 0)) if 'bright_t31' in row else 0,
                    'frp': float(row.get('frp', 0)),
                    'confidence': self._normalize_confidence(row.get('confidence', 0)),
                    'daynight': row.get('daynight', 'D'),
                    'acq_date': row.get('acq_date', ''),
                    'acq_time': row.get('acq_time', ''),
                    'satellite': row.get('satellite', 'Unknown'),
                    'scan': float(row.get('scan', 0)) if 'scan' in row else 0,
                    'track': float(row.get('track', 0)) if 'track' in row else 0,
                    'instrument': row.get('instrument', 'Unknown'),
                    'version': row.get('version', '1.0')
                }
                fires.append(fire)
            
        except Exception as e:
            logger.error(f"Error parsing CSV response: {e}")
        
        return fires
    
    def _normalize_confidence(self, confidence):
        """
        Normalize confidence value to 0.0-1.0 range.
        
        VIIRS uses categorical confidence: 'l' (low), 'n' (nominal), 'h' (high)
        MODIS uses percentage: 0-100
        
        Args:
            confidence: Raw confidence value (string or numeric)
            
        Returns:
            Float between 0.0 and 1.0
        """
        if isinstance(confidence, str):
            # VIIRS categorical
            conf_lower = confidence.lower()
            if conf_lower in ['l', 'low']:
                return 0.3
            elif conf_lower in ['n', 'nominal']:
                return 0.6
            elif conf_lower in ['h', 'high']:
                return 0.9
            else:
                return 0.5
        else:
            # MODIS percentage or numeric
            try:
                val = float(confidence)
                # If already 0-1 range, return as is
                if 0 <= val <= 1:
                    return val
                # If 0-100 range, normalize
                elif 0 <= val <= 100:
                    return val / 100.0
                else:
                    return 0.5
            except:
                return 0.5
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def get_global_fires(self, date=None, source='viirs_noaa20', day_range=1):
        """
        Get fires from major global hotspots.
        
        Args:
            date: Date to query (YYYY-MM-DD format), defaults to yesterday
            source: Data source to use
            day_range: Number of days to look back (1-10)
            
        Returns:
            List of all fire detections from global hotspots
        """
        # Major fire-prone regions worldwide
        hotspots = [
            {'name': 'Western US', 'lat': 40.0, 'lon': -120.0, 'radius': 500},
            {'name': 'Amazon Basin', 'lat': -5.0, 'lon': -60.0, 'radius': 800},
            {'name': 'Australia', 'lat': -25.0, 'lon': 135.0, 'radius': 800},
            {'name': 'Indonesia', 'lat': -2.0, 'lon': 118.0, 'radius': 600},
            {'name': 'Central Africa', 'lat': 0.0, 'lon': 20.0, 'radius': 800},
            {'name': 'Siberia', 'lat': 60.0, 'lon': 100.0, 'radius': 1000},
            {'name': 'Mediterranean', 'lat': 40.0, 'lon': 10.0, 'radius': 500},
            {'name': 'India', 'lat': 22.0, 'lon': 80.0, 'radius': 600}
        ]
        
        all_fires = []
        for hotspot in hotspots:
            fires = self.fetch_fires_in_region(
                hotspot['lat'], hotspot['lon'],
                radius_km=hotspot['radius'],
                date=date,
                source=source,
                day_range=day_range
            )
            for fire in fires:
                fire['region'] = hotspot['name']
            all_fires.extend(fires)
        
        return all_fires
