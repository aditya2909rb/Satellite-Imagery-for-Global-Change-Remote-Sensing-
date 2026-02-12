"""
Fire history tracking and data export
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import csv

class FireHistoryTracker:
    """Track historical fire data"""
    
    def __init__(self, history_dir: str = ".fire_history"):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
        self.history_file = self.history_dir / "fires.json"
        self.csv_file = self.history_dir / "fires.csv"
    
    def add_fire(self, fire_data: Dict):
        """Add fire to history"""
        try:
            fires = self._load_history()
            fires.append({
                **fire_data,
                'recorded_at': datetime.now().isoformat()
            })
            
            # Keep only last 1000 fires
            fires = fires[-1000:]
            
            with open(self.history_file, 'w') as f:
                json.dump(fires, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding fire: {e}")
            return False
    
    def _load_history(self) -> List[Dict]:
        """Load fire history"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def get_history(self, days: int = 7) -> List[Dict]:
        """Get fires from last N days"""
        fires = self._load_history()
        cutoff = datetime.now() - timedelta(days=days)
        
        return [
            f for f in fires
            if datetime.fromisoformat(f.get('recorded_at', datetime.now().isoformat())) > cutoff
        ]
    
    def get_by_region(self, latitude: float, longitude: float, radius_km: float = 50) -> List[Dict]:
        """Get fires in region from history"""
        from math import radians, cos, sin, asin, sqrt
        
        fires = self._load_history()
        result = []
        
        for fire in fires:
            lat1, lon1 = radians(latitude), radians(longitude)
            lat2, lon2 = radians(fire['latitude']), radians(fire['longitude'])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            distance = 6371 * c
            
            if distance <= radius_km:
                result.append(fire)
        
        return result
    
    def export_csv(self) -> str:
        """Export fires as CSV"""
        fires = self._load_history()
        
        if not fires:
            return "latitude,longitude,confidence,power_mw,distance_km,source,timestamp,recorded_at\n"
        
        try:
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fires[0].keys())
                writer.writeheader()
                writer.writerows(fires)
            
            with open(self.csv_file, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return ""
    
    def export_json(self) -> Dict:
        """Export fires as JSON"""
        return {
            'fires': self._load_history(),
            'exported_at': datetime.now().isoformat(),
            'total_count': len(self._load_history())
        }
    
    def get_stats(self, days: int = 7) -> Dict:
        """Get fire statistics"""
        fires = self.get_history(days)
        
        if not fires:
            return {
                'total_fires': 0,
                'high_confidence': 0,
                'total_power_mw': 0,
                'avg_confidence': 0
            }
        
        high_conf = len([f for f in fires if f['confidence'] >= 0.8])
        total_power = sum([f.get('power_mw', 0) for f in fires])
        avg_conf = sum([f['confidence'] for f in fires]) / len(fires)
        
        return {
            'total_fires': len(fires),
            'high_confidence': high_conf,
            'total_power_mw': int(total_power),
            'avg_confidence': round(avg_conf, 2),
            'period_days': days
        }

# Global tracker
tracker = FireHistoryTracker()
