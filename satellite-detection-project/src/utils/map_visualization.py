"""
Map visualization system for fire and smoke detection
"""

import folium
import json
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

from ..config import AppConfig

logger = logging.getLogger(__name__)

class MapVisualizer:
    """Creates interactive maps for fire and smoke detection visualization"""
    
    def __init__(self):
        self.config = AppConfig.map
        self.map_dir = "static/maps"
        os.makedirs(self.map_dir, exist_ok=True)
    
    def create_fire_map(
        self, 
        detections: List[Dict],
        center_coordinates: List[float],
        search_radius_km: float,
        title: str = "Fire Detection Map"
    ) -> str:
        """
        Create an interactive map showing fire detections
        
        Args:
            detections: List of fire detection data
            center_coordinates: [lat, lon] of map center
            search_radius_km: Search radius used
            title: Map title
            
        Returns:
            str: Path to saved HTML map file
        """
        try:
            # Create base map
            center_lat, center_lon = center_coordinates
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=self.config.default_zoom,
                tiles=self.config.map_tile_provider
            )
            
            # Add search radius circle
            folium.Circle(
                location=[center_lat, center_lon],
                radius=search_radius_km * 1000,  # Convert to meters
                color='blue',
                fill=True,
                fill_opacity=0.1,
                popup=f"Search Radius: {search_radius_km} km"
            ).add_to(m)
            
            # Add fire markers
            for detection in detections:
                lat = detection.get('latitude', 0)
                lon = detection.get('longitude', 0)
                conf = detection.get('confidence', 0)
                power = detection.get('power_mw', 0)
                dist = detection.get('distance_km', 0)
                source = detection.get('source', 'Unknown')
                
                # Determine marker color based on confidence
                if conf >= 0.9:
                    color = 'red'
                    icon = 'fire'
                elif conf >= 0.7:
                    color = 'orange'
                    icon = 'fire'
                else:
                    color = 'yellow'
                    icon = 'map-marker'
                
                # Create popup content
                popup_content = f"""
                <div style="width: 200px;">
                    <h4>🔥 Fire Detection</h4>
                    <p><strong>Location:</strong> {lat:.4f}, {lon:.4f}</p>
                    <p><strong>Confidence:</strong> {conf:.1%}</p>
                    <p><strong>Thermal Power:</strong> {power:,.0f} MW</p>
                    <p><strong>Distance:</strong> {dist:.1f} km</p>
                    <p><strong>Source:</strong> {source}</p>
                    <p><strong>Time:</strong> {detection.get('timestamp', 'Unknown')}</p>
                </div>
                """
                
                # Add marker
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=color, icon=icon, prefix='fa'),
                    tooltip=f"Confidence: {conf:.1%}"
                ).add_to(m)
            
            # Add legend
            legend_html = '''
            <div id="legend" style="position: fixed; 
                bottom: 50px; left: 50px; width: 150px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
            <p><i class="fa fa-fire" style="color:red"></i> High Confidence (>90%)</p>
            <p><i class="fa fa-fire" style="color:orange"></i> Medium Confidence (70-90%)</p>
            <p><i class="fa fa-map-marker" style="color:yellow"></i> Low Confidence (<70%)</p>
            <p><i class="fa fa-circle" style="color:blue"></i> Search Area</p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Add title
            title_html = f'''
            <h3 style="font-size:20px; color:black; background-color:white; padding:10px; border:1px solid grey; text-align:center;">
            {title}
            </h3>
            '''
            m.get_root().html.add_child(folium.Element(title_html))
            
            # Save map
            filename = f"fire_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(self.map_dir, filename)
            m.save(filepath)
            
            logger.info(f"Created fire map: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to create fire map: {e}")
            return ""
    
    def create_smoke_map(
        self, 
        detections: List[Dict],
        center_coordinates: List[float],
        title: str = "Smoke Detection Map"
    ) -> str:
        """
        Create an interactive map showing smoke detections
        
        Args:
            detections: List of smoke detection data
            center_coordinates: [lat, lon] of map center
            title: Map title
            
        Returns:
            str: Path to saved HTML map file
        """
        try:
            center_lat, center_lon = center_coordinates
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=self.config.default_zoom,
                tiles=self.config.map_tile_provider
            )
            
            # Add smoke markers
            for detection in detections:
                lat = detection.get('latitude', 0)
                lon = detection.get('longitude', 0)
                conf = detection.get('confidence', 0)
                area = detection.get('area_km2', 0)
                
                # Create popup content
                popup_content = f"""
                <div style="width: 200px;">
                    <h4>💨 Smoke Detection</h4>
                    <p><strong>Location:</strong> {lat:.4f}, {lon:.4f}</p>
                    <p><strong>Confidence:</strong> {conf:.1%}</p>
                    <p><strong>Area:</strong> {area:.2f} km²</p>
                    <p><strong>Method:</strong> {detection.get('method', 'Unknown')}</p>
                </div>
                """
                
                # Add marker
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=self.config.smoke_marker_color, icon='cloud', prefix='fa'),
                    tooltip=f"Smoke Confidence: {conf:.1%}"
                ).add_to(m)
            
            # Save map
            filename = f"smoke_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(self.map_dir, filename)
            m.save(filepath)
            
            logger.info(f"Created smoke map: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to create smoke map: {e}")
            return ""
    
    def create_dust_map(
        self, 
        detections: List[Dict],
        center_coordinates: List[float],
        title: str = "Dust Detection Map"
    ) -> str:
        """
        Create an interactive map showing dust detections
        
        Args:
            detections: List of dust detection data
            center_coordinates: [lat, lon] of map center
            title: Map title
            
        Returns:
            str: Path to saved HTML map file
        """
        try:
            center_lat, center_lon = center_coordinates
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=self.config.default_zoom,
                tiles=self.config.map_tile_provider
            )
            
            # Add dust markers
            for detection in detections:
                lat = detection.get('latitude', 0)
                lon = detection.get('longitude', 0)
                conf = detection.get('confidence', 0)
                optical_depth = detection.get('optical_depth', 0)
                
                # Create popup content
                popup_content = f"""
                <div style="width: 200px;">
                    <h4>🌪️ Dust Detection</h4>
                    <p><strong>Location:</strong> {lat:.4f}, {lon:.4f}</p>
                    <p><strong>Confidence:</strong> {conf:.1%}</p>
                    <p><strong>Optical Depth:</strong> {optical_depth:.2f}</p>
                    <p><strong>Source:</strong> {detection.get('source', 'Unknown')}</p>
                </div>
                """
                
                # Add marker
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=self.config.dust_marker_color, icon='wind', prefix='fa'),
                    tooltip=f"Dust Confidence: {conf:.1%}"
                ).add_to(m)
            
            # Save map
            filename = f"dust_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(self.map_dir, filename)
            m.save(filepath)
            
            logger.info(f"Created dust map: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to create dust map: {e}")
            return ""
    
    def create_historical_map(
        self, 
        detections: List[Dict],
        center_coordinates: Optional[List[float]] = None,
        title: str = "Historical Fire Activity"
    ) -> str:
        """
        Create a map showing historical fire activity
        
        Args:
            detections: List of historical fire data
            center_coordinates: [lat, lon] of map center (optional)
            title: Map title
            
        Returns:
            str: Path to saved HTML map file
        """
        try:
            # Calculate center if not provided
            if center_coordinates is None:
                if detections:
                    avg_lat = sum(d.get('latitude', 0) for d in detections) / len(detections)
                    avg_lon = sum(d.get('longitude', 0) for d in detections) / len(detections)
                    center_coordinates = [avg_lat, avg_lon]
                else:
                    center_coordinates = [0, 0]
            
            center_lat, center_lon = center_coordinates
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=self.config.default_zoom,
                tiles=self.config.map_tile_provider
            )
            
            # Group detections by confidence for clustering
            high_conf = [d for d in detections if d.get('confidence', 0) >= 0.8]
            medium_conf = [d for d in detections if 0.5 <= d.get('confidence', 0) < 0.8]
            low_conf = [d for d in detections if d.get('confidence', 0) < 0.5]
            
            # Add markers for each confidence level
            for conf_group, color, label in [
                (high_conf, 'red', 'High Confidence'),
                (medium_conf, 'orange', 'Medium Confidence'), 
                (low_conf, 'yellow', 'Low Confidence')
            ]:
                for detection in conf_group:
                    lat = detection.get('latitude', 0)
                    lon = detection.get('longitude', 0)
                    conf = detection.get('confidence', 0)
                    power = detection.get('power_mw', 0)
                    time = detection.get('detection_time', 'Unknown')
                    
                    popup_content = f"""
                    <div style="width: 250px;">
                        <h4>🔥 Historical Fire</h4>
                        <p><strong>Location:</strong> {lat:.4f}, {lon:.4f}</p>
                        <p><strong>Confidence:</strong> {conf:.1%}</p>
                        <p><strong>Thermal Power:</strong> {power:,.0f} MW</p>
                        <p><strong>Time:</strong> {time}</p>
                        <p><strong>Alert Sent:</strong> {'Yes' if detection.get('alert_sent', False) else 'No'}</p>
                    </div>
                    """
                    
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=6 if conf >= 0.8 else 4 if conf >= 0.5 else 2,
                        color=color,
                        fill=True,
                        fill_opacity=0.7,
                        popup=folium.Popup(popup_content, max_width=300),
                        tooltip=f"{label}: {conf:.1%}"
                    ).add_to(m)
            
            # Add timeline slider if we have many detections
            if len(detections) > 10:
                # Add a simple timeline visualization
                times = [d.get('detection_time', '') for d in detections if d.get('detection_time')]
                if times:
                    min_time = min(times)
                    max_time = max(times)
                    
                    timeline_html = f'''
                    <div style="position: fixed; top: 10px; right: 10px; background: white; 
                        padding: 10px; border: 1px solid grey; z-index: 9999; font-size: 12px;">
                        <h4>Time Range</h4>
                        <p><strong>From:</strong> {min_time}</p>
                        <p><strong>To:</strong> {max_time}</p>
                        <p><strong>Total Fires:</strong> {len(detections)}</p>
                    </div>
                    '''
                    m.get_root().html.add_child(folium.Element(timeline_html))
            
            # Save map
            filename = f"historical_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(self.map_dir, filename)
            m.save(filepath)
            
            logger.info(f"Created historical map: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to create historical map: {e}")
            return ""
    
    def create_summary_dashboard(
        self, 
        fire_detections: List[Dict],
        smoke_detections: List[Dict],
        dust_detections: List[Dict],
        center_coordinates: List[float],
        title: str = "Detection Summary Dashboard"
    ) -> str:
        """
        Create a comprehensive dashboard map showing all detection types
        
        Args:
            fire_detections: List of fire detection data
            smoke_detections: List of smoke detection data  
            dust_detections: List of dust detection data
            center_coordinates: [lat, lon] of map center
            title: Map title
            
        Returns:
            str: Path to saved HTML map file
        """
        try:
            center_lat, center_lon = center_coordinates
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=self.config.default_zoom,
                tiles=self.config.map_tile_provider
            )
            
            # Add all detection types with different icons
            detection_types = [
                (fire_detections, 'red', 'fire', '🔥 Fire'),
                (smoke_detections, 'orange', 'cloud', '💨 Smoke'),
                (dust_detections, 'brown', 'wind', '🌪️ Dust')
            ]
            
            for detections, color, icon, label in detection_types:
                for detection in detections:
                    lat = detection.get('latitude', 0)
                    lon = detection.get('longitude', 0)
                    conf = detection.get('confidence', 0)
                    
                    popup_content = f"""
                    <div style="width: 200px;">
                        <h4>{label}</h4>
                        <p><strong>Location:</strong> {lat:.4f}, {lon:.4f}</p>
                        <p><strong>Confidence:</strong> {conf:.1%}</p>
                        <p><strong>Time:</strong> {detection.get('timestamp', 'Unknown')}</p>
                    </div>
                    """
                    
                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_content, max_width=300),
                        icon=folium.Icon(color=color, icon=icon, prefix='fa'),
                        tooltip=f"{label}: {conf:.1%}"
                    ).add_to(m)
            
            # Add summary statistics
            stats_html = f'''
            <div style="position: fixed; bottom: 50px; right: 50px; width: 200px; height: 150px; 
                background-color: white; border:2px solid grey; z-index:9999; font-size:14px; padding: 10px">
                <h4>Summary</h4>
                <p><i class="fa fa-fire" style="color:red"></i> Fires: {len(fire_detections)}</p>
                <p><i class="fa fa-cloud" style="color:orange"></i> Smoke: {len(smoke_detections)}</p>
                <p><i class="fa fa-wind" style="color:brown"></i> Dust: {len(dust_detections)}</p>
                <p><strong>Total:</strong> {len(fire_detections) + len(smoke_detections) + len(dust_detections)}</p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(stats_html))
            
            # Save map
            filename = f"dashboard_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(self.map_dir, filename)
            m.save(filepath)
            
            logger.info(f"Created dashboard map: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to create dashboard map: {e}")
            return ""

# Global map visualizer instance
map_visualizer = MapVisualizer()