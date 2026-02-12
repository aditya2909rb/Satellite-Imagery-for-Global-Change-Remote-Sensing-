"""
Historical fire data tracking and storage system
"""

import sqlite3
import json
import csv
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import asdict

from ..config import AppConfig

logger = logging.getLogger(__name__)

class FireHistoryTracker:
    """Tracks and stores historical fire detection data"""
    
    def __init__(self):
        self.db_path = AppConfig.database.db_path
        self.max_history_days = AppConfig.database.max_history_days
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for fire history"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create fires table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS fires (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        detection_time TEXT NOT NULL,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        confidence REAL NOT NULL,
                        power_mw REAL,
                        distance_km REAL,
                        source TEXT,
                        search_radius_km REAL,
                        center_lat REAL,
                        center_lon REAL,
                        alert_sent BOOLEAN DEFAULT 0,
                        alert_time TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_fires_time ON fires(detection_time)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_fires_coords ON fires(latitude, longitude)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_fires_confidence ON fires(confidence)')
                
                conn.commit()
                logger.info(f"Fire history database initialized at {self.db_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize fire history database: {e}")
            raise
    
    def add_detection(
        self, 
        detection: Dict,
        search_radius_km: float,
        center_coordinates: List[float]
    ) -> int:
        """
        Add a fire detection to history
        
        Args:
            detection: Fire detection data
            search_radius_km: Search radius used
            center_coordinates: [lat, lon] of search center
            
        Returns:
            int: ID of inserted record
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO fires (
                        detection_time, latitude, longitude, confidence, power_mw,
                        distance_km, source, search_radius_km, center_lat, center_lon
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    detection.get('timestamp', datetime.now().isoformat()),
                    detection.get('latitude', 0),
                    detection.get('longitude', 0),
                    detection.get('confidence', 0),
                    detection.get('power_mw', 0),
                    detection.get('distance_km', 0),
                    detection.get('source', 'Unknown'),
                    search_radius_km,
                    center_coordinates[0],
                    center_coordinates[1]
                ))
                
                record_id = cursor.lastrowid
                conn.commit()
                
                logger.debug(f"Added fire detection record {record_id}")
                return record_id
                
        except Exception as e:
            logger.error(f"Failed to add fire detection to history: {e}")
            raise
    
    def add_detections_batch(
        self, 
        detections: List[Dict],
        search_radius_km: float,
        center_coordinates: List[float]
    ) -> List[int]:
        """
        Add multiple fire detections to history
        
        Args:
            detections: List of fire detection data
            search_radius_km: Search radius used
            center_coordinates: [lat, lon] of search center
            
        Returns:
            List[int]: IDs of inserted records
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Prepare batch insert
                records = []
                for detection in detections:
                    records.append((
                        detection.get('timestamp', datetime.now().isoformat()),
                        detection.get('latitude', 0),
                        detection.get('longitude', 0),
                        detection.get('confidence', 0),
                        detection.get('power_mw', 0),
                        detection.get('distance_km', 0),
                        detection.get('source', 'Unknown'),
                        search_radius_km,
                        center_coordinates[0],
                        center_coordinates[1]
                    ))
                
                cursor.executemany('''
                    INSERT INTO fires (
                        detection_time, latitude, longitude, confidence, power_mw,
                        distance_km, source, search_radius_km, center_lat, center_lon
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', records)
                
                conn.commit()
                
                # Get inserted IDs
                cursor.execute('SELECT last_insert_rowid()')
                last_id = cursor.fetchone()[0]
                record_ids = list(range(last_id - len(records) + 1, last_id + 1))
                
                logger.info(f"Added {len(records)} fire detections to history")
                return record_ids
                
        except Exception as e:
            logger.error(f"Failed to add batch fire detections to history: {e}")
            raise
    
    def get_recent_detections(
        self, 
        hours: int = 24,
        min_confidence: float = 0.5,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Get recent fire detections
        
        Args:
            hours: Number of hours to look back
            min_confidence: Minimum confidence threshold
            limit: Maximum number of records to return
            
        Returns:
            List[Dict]: List of fire detection records
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, detection_time, latitude, longitude, confidence, 
                           power_mw, distance_km, source, search_radius_km, 
                           center_lat, center_lon, alert_sent, alert_time, created_at
                    FROM fires 
                    WHERE detection_time >= ? AND confidence >= ?
                    ORDER BY detection_time DESC
                    LIMIT ?
                ''', (cutoff_time.isoformat(), min_confidence, limit))
                
                columns = [desc[0] for desc in cursor.description]
                records = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                return records
                
        except Exception as e:
            logger.error(f"Failed to get recent detections: {e}")
            return []
    
    def get_detections_by_location(
        self, 
        latitude: float,
        longitude: float,
        radius_km: float = 50.0,
        days: int = 30
    ) -> List[Dict]:
        """
        Get fire detections by location and time period
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in km
            days: Number of days to look back
            
        Returns:
            List[Dict]: List of fire detection records
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            # Simple distance calculation for filtering
            # In a real implementation, you might want to use spatial indexing
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, detection_time, latitude, longitude, confidence, 
                           power_mw, distance_km, source, search_radius_km, 
                           center_lat, center_lon, alert_sent, alert_time, created_at
                    FROM fires 
                    WHERE detection_time >= ? 
                    AND center_lat BETWEEN ? AND ?
                    AND center_lon BETWEEN ? AND ?
                    ORDER BY detection_time DESC
                ''', (
                    cutoff_time.isoformat(),
                    latitude - (radius_km / 111.0),
                    latitude + (radius_km / 111.0),
                    longitude - (radius_km / 111.0),
                    longitude + (radius_km / 111.0)
                ))
                
                columns = [desc[0] for desc in cursor.description]
                records = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                # Filter by actual distance
                filtered_records = []
                for record in records:
                    dist = self._haversine_distance(
                        latitude, longitude, 
                        record['latitude'], record['longitude']
                    )
                    if dist <= radius_km:
                        filtered_records.append(record)
                
                return filtered_records
                
        except Exception as e:
            logger.error(f"Failed to get detections by location: {e}")
            return []
    
    def mark_alert_sent(self, detection_id: int) -> bool:
        """Mark a detection as having an alert sent"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE fires 
                    SET alert_sent = 1, alert_time = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), detection_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to mark alert as sent: {e}")
            return False
    
    def cleanup_old_records(self) -> int:
        """Remove old records beyond retention period"""
        try:
            cutoff_time = datetime.now() - timedelta(days=self.max_history_days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM fires WHERE detection_time < ?
                ''', (cutoff_time.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old fire records")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
            return 0
    
    def get_statistics(self, days: int = 30) -> Dict:
        """Get fire detection statistics"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total detections
                cursor.execute('''
                    SELECT COUNT(*) FROM fires WHERE detection_time >= ?
                ''', (cutoff_time.isoformat(),))
                total_detections = cursor.fetchone()[0]
                
                # High confidence detections
                cursor.execute('''
                    SELECT COUNT(*) FROM fires 
                    WHERE detection_time >= ? AND confidence >= 0.8
                ''', (cutoff_time.isoformat(),))
                high_conf_detections = cursor.fetchone()[0]
                
                # Average confidence
                cursor.execute('''
                    SELECT AVG(confidence) FROM fires WHERE detection_time >= ?
                ''', (cutoff_time.isoformat(),))
                avg_confidence = cursor.fetchone()[0] or 0
                
                # Total thermal power
                cursor.execute('''
                    SELECT SUM(power_mw) FROM fires WHERE detection_time >= ?
                ''', (cutoff_time.isoformat(),))
                total_power = cursor.fetchone()[0] or 0
                
                # Alerts sent
                cursor.execute('''
                    SELECT COUNT(*) FROM fires 
                    WHERE detection_time >= ? AND alert_sent = 1
                ''', (cutoff_time.isoformat(),))
                alerts_sent = cursor.fetchone()[0]
                
                return {
                    'total_detections': total_detections,
                    'high_confidence_detections': high_conf_detections,
                    'average_confidence': round(avg_confidence, 2),
                    'total_thermal_power_mw': round(total_power, 2),
                    'alerts_sent': alerts_sent,
                    'period_days': days,
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export all fire history to CSV"""
        try:
            if filename is None:
                filename = f"fire_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            filepath = os.path.join(AppConfig.export.export_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT detection_time, latitude, longitude, confidence, 
                           power_mw, distance_km, source, search_radius_km, 
                           center_lat, center_lon, alert_sent, alert_time, created_at
                    FROM fires ORDER BY detection_time DESC
                ''')
                
                columns = [desc[0] for desc in cursor.description]
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(columns)
                    writer.writerows(cursor.fetchall())
                
                logger.info(f"Exported fire history to {filepath}")
                return filepath
                
        except Exception as e:
            logger.error(f"Failed to export fire history to CSV: {e}")
            return ""
    
    def export_to_json(self, filename: str = None) -> str:
        """Export all fire history to JSON"""
        try:
            if filename is None:
                filename = f"fire_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            filepath = os.path.join(AppConfig.export.export_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            detections = self.get_recent_detections(hours=24*365)  # All data
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(detections, jsonfile, indent=AppConfig.export.json_indent)
            
            logger.info(f"Exported fire history to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export fire history to JSON: {e}")
            return ""

# Global fire history tracker instance
fire_history = FireHistoryTracker()