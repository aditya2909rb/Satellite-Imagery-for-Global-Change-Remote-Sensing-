"""
Data export functionality for fire detection data
"""

import json
import csv
import os
from typing import List, Dict, Optional, Union
from datetime import datetime
import logging

from ..config import AppConfig

logger = logging.getLogger(__name__)

class DataExporter:
    """Handles exporting detection data to various formats"""
    
    def __init__(self):
        self.export_dir = AppConfig.export.export_dir
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_to_csv(
        self, 
        data: List[Dict], 
        filename: str = None,
        include_headers: bool = True
    ) -> str:
        """
        Export data to CSV format
        
        Args:
            data: List of detection data dictionaries
            filename: Output filename (optional)
            include_headers: Whether to include column headers
            
        Returns:
            str: Path to exported file
        """
        try:
            if not data:
                logger.warning("No data to export to CSV")
                return ""
            
            if filename is None:
                filename = f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            filepath = os.path.join(self.export_dir, filename)
            
            # Get all possible field names
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(
                    csvfile, 
                    fieldnames=fieldnames,
                    delimiter=AppConfig.export.csv_delimiter
                )
                
                if include_headers:
                    writer.writeheader()
                
                for row in data:
                    # Ensure all fields are present
                    row_data = {field: row.get(field, '') for field in fieldnames}
                    writer.writerow(row_data)
            
            logger.info(f"Exported {len(data)} records to CSV: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export data to CSV: {e}")
            return ""
    
    def export_to_json(
        self, 
        data: List[Dict], 
        filename: str = None,
        pretty_print: bool = True
    ) -> str:
        """
        Export data to JSON format
        
        Args:
            data: List of detection data dictionaries
            filename: Output filename (optional)
            pretty_print: Whether to format JSON with indentation
            
        Returns:
            str: Path to exported file
        """
        try:
            if not data:
                logger.warning("No data to export to JSON")
                return ""
            
            if filename is None:
                filename = f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            filepath = os.path.join(self.export_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                if pretty_print:
                    json.dump(
                        data, 
                        jsonfile, 
                        indent=AppConfig.export.json_indent,
                        ensure_ascii=False
                    )
                else:
                    json.dump(data, jsonfile, ensure_ascii=False)
            
            logger.info(f"Exported {len(data)} records to JSON: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export data to JSON: {e}")
            return ""
    
    def export_to_excel(
        self, 
        data: List[Dict], 
        filename: str = None
    ) -> str:
        """
        Export data to Excel format (requires pandas)
        
        Args:
            data: List of detection data dictionaries
            filename: Output filename (optional)
            
        Returns:
            str: Path to exported file
        """
        try:
            import pandas as pd
            
            if not data:
                logger.warning("No data to export to Excel")
                return ""
            
            if filename is None:
                filename = f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            filepath = os.path.join(self.export_dir, filename)
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Export to Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            logger.info(f"Exported {len(data)} records to Excel: {filepath}")
            return filepath
            
        except ImportError:
            logger.warning("Pandas not available, cannot export to Excel")
            return ""
        except Exception as e:
            logger.error(f"Failed to export data to Excel: {e}")
            return ""
    
    def export_fire_summary(
        self, 
        detections: List[Dict],
        filename: str = None
    ) -> str:
        """
        Export a summary report of fire detections
        
        Args:
            detections: List of fire detection data
            filename: Output filename (optional)
            
        Returns:
            str: Path to exported file
        """
        try:
            if not detections:
                logger.warning("No fire detections to export summary")
                return ""
            
            if filename is None:
                filename = f"fire_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            filepath = os.path.join(self.export_dir, filename)
            
            # Calculate summary statistics
            total_detections = len(detections)
            high_confidence = len([d for d in detections if d.get('confidence', 0) >= 0.8])
            medium_confidence = len([d for d in detections if 0.5 <= d.get('confidence', 0) < 0.8])
            low_confidence = len([d for d in detections if d.get('confidence', 0) < 0.5])
            
            avg_confidence = sum(d.get('confidence', 0) for d in detections) / total_detections
            total_power = sum(d.get('power_mw', 0) for d in detections)
            
            # Group by source
            sources = {}
            for detection in detections:
                source = detection.get('source', 'Unknown')
                if source not in sources:
                    sources[source] = 0
                sources[source] += 1
            
            summary = {
                "report_metadata": {
                    "export_time": datetime.now().isoformat(),
                    "total_detections": total_detections,
                    "report_type": "Fire Detection Summary"
                },
                "confidence_analysis": {
                    "high_confidence": {
                        "count": high_confidence,
                        "percentage": round((high_confidence / total_detections) * 100, 2)
                    },
                    "medium_confidence": {
                        "count": medium_confidence,
                        "percentage": round((medium_confidence / total_detections) * 100, 2)
                    },
                    "low_confidence": {
                        "count": low_confidence,
                        "percentage": round((low_confidence / total_detections) * 100, 2)
                    }
                },
                "statistical_summary": {
                    "average_confidence": round(avg_confidence, 2),
                    "total_thermal_power_mw": round(total_power, 2),
                    "max_confidence": round(max(d.get('confidence', 0) for d in detections), 2),
                    "min_confidence": round(min(d.get('confidence', 0) for d in detections), 2)
                },
                "source_breakdown": sources,
                "detection_details": detections
            }
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(summary, jsonfile, indent=AppConfig.export.json_indent, ensure_ascii=False)
            
            logger.info(f"Exported fire summary to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export fire summary: {e}")
            return ""
    
    def export_alert_report(
        self, 
        detections: List[Dict],
        alert_recipients: List[str],
        filename: str = None
    ) -> str:
        """
        Export an alert report showing what would be sent via email
        
        Args:
            detections: List of high-confidence detections
            alert_recipients: List of email recipients
            filename: Output filename (optional)
            
        Returns:
            str: Path to exported file
        """
        try:
            if not detections:
                logger.warning("No detections for alert report")
                return ""
            
            if filename is None:
                filename = f"alert_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            filepath = os.path.join(self.export_dir, filename)
            
            # Calculate alert statistics
            total_power = sum(d.get('power_mw', 0) for d in detections)
            avg_confidence = sum(d.get('confidence', 0) for d in detections) / len(detections)
            
            alert_report = {
                "alert_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "recipients": alert_recipients,
                    "total_detections": len(detections),
                    "alert_type": "High-Confidence Fire Alert"
                },
                "alert_summary": {
                    "total_thermal_power_mw": round(total_power, 2),
                    "average_confidence": round(avg_confidence, 2),
                    "high_confidence_count": len(detections)
                },
                "detection_details": [
                    {
                        "latitude": d.get('latitude'),
                        "longitude": d.get('longitude'),
                        "confidence": d.get('confidence'),
                        "power_mw": d.get('power_mw'),
                        "distance_km": d.get('distance_km'),
                        "source": d.get('source'),
                        "timestamp": d.get('timestamp')
                    }
                    for d in detections
                ],
                "email_content_preview": {
                    "subject": f"🔥 High-Confidence Fire Alert - {len(detections)} Fires Detected",
                    "body_preview": "HTML email content would be generated here"
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(alert_report, jsonfile, indent=AppConfig.export.json_indent, ensure_ascii=False)
            
            logger.info(f"Exported alert report to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export alert report: {e}")
            return ""
    
    def export_historical_trends(
        self, 
        detections: List[Dict],
        filename: str = None
    ) -> str:
        """
        Export historical trends analysis
        
        Args:
            detections: List of historical detection data
            filename: Output filename (optional)
            
        Returns:
            str: Path to exported file
        """
        try:
            if not detections:
                logger.warning("No historical data for trends analysis")
                return ""
            
            if filename is None:
                filename = f"historical_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            filepath = os.path.join(self.export_dir, filename)
            
            # Analyze trends by time
            time_groups = {}
            for detection in detections:
                time_str = detection.get('detection_time', '')
                if time_str:
                    date = time_str.split('T')[0]  # Get date part
                    if date not in time_groups:
                        time_groups[date] = []
                    time_groups[date].append(detection)
            
            # Calculate daily statistics
            daily_stats = {}
            for date, daily_detections in time_groups.items():
                daily_stats[date] = {
                    "total_detections": len(daily_detections),
                    "average_confidence": sum(d.get('confidence', 0) for d in daily_detections) / len(daily_detections),
                    "total_power": sum(d.get('power_mw', 0) for d in daily_detections),
                    "high_confidence_count": len([d for d in daily_detections if d.get('confidence', 0) >= 0.8])
                }
            
            trends_report = {
                "trends_metadata": {
                    "analysis_period": "Historical",
                    "total_records": len(detections),
                    "analysis_type": "Temporal Trends"
                },
                "daily_statistics": daily_stats,
                "overall_statistics": {
                    "total_days_with_detections": len(time_groups),
                    "average_detections_per_day": round(len(detections) / len(time_groups), 2) if time_groups else 0,
                    "peak_detection_day": max(daily_stats.items(), key=lambda x: x[1]['total_detections']) if daily_stats else None,
                    "highest_confidence_day": max(daily_stats.items(), key=lambda x: x[1]['average_confidence']) if daily_stats else None
                },
                "detection_data": detections
            }
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(trends_report, jsonfile, indent=AppConfig.export.json_indent, ensure_ascii=False)
            
            logger.info(f"Exported historical trends to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export historical trends: {e}")
            return ""
    
    def batch_export(
        self, 
        data: List[Dict],
        formats: List[str] = ['csv', 'json'],
        filename_base: str = None
    ) -> Dict[str, str]:
        """
        Export data to multiple formats at once
        
        Args:
            data: List of detection data
            formats: List of formats to export to
            filename_base: Base filename (optional)
            
        Returns:
            Dict[str, str]: Dictionary of format -> file path
        """
        try:
            if filename_base is None:
                filename_base = f"batch_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            results = {}
            
            for format_type in formats:
                if format_type.lower() == 'csv':
                    filename = f"{filename_base}.csv"
                    results['csv'] = self.export_to_csv(data, filename)
                
                elif format_type.lower() == 'json':
                    filename = f"{filename_base}.json"
                    results['json'] = self.export_to_json(data, filename)
                
                elif format_type.lower() == 'excel':
                    filename = f"{filename_base}.xlsx"
                    results['excel'] = self.export_to_excel(data, filename)
                
                else:
                    logger.warning(f"Unknown export format: {format_type}")
            
            logger.info(f"Batch export completed: {list(results.keys())}")
            return results
            
        except Exception as e:
            logger.error(f"Failed batch export: {e}")
            return {}

# Global data exporter instance
data_exporter = DataExporter()