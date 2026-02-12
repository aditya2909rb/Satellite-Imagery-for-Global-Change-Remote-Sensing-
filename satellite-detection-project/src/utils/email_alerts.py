"""
Email alert system for high-confidence fire detections
"""

import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Dict, Optional
import json
import csv
import os
from datetime import datetime
import logging

from ..config import AppConfig

logger = logging.getLogger(__name__)

class EmailAlertSystem:
    """Handles email alerts for fire detections"""
    
    def __init__(self):
        self.config = AppConfig.email
        self.is_configured = self._check_configuration()
    
    def _check_configuration(self) -> bool:
        """Check if email is properly configured"""
        if not self.config.enabled:
            logger.info("Email alerts disabled in configuration")
            return False
        
        if not self.config.sender_email or not self.config.sender_password:
            logger.warning("Email credentials not configured")
            return False
        
        if not self.config.recipients:
            logger.warning("No email recipients configured")
            return False
        
        return True
    
    async def send_fire_alert(
        self, 
        detections: List[Dict], 
        coordinates: List[float],
        radius_km: float,
        confidence_threshold: float = 0.8
    ) -> bool:
        """
        Send email alert for high-confidence fire detections
        
        Args:
            detections: List of fire detection results
            coordinates: [latitude, longitude] of detection center
            radius_km: Search radius
            confidence_threshold: Minimum confidence for alert
            
        Returns:
            bool: True if email sent successfully
        """
        if not self.is_configured:
            logger.warning("Email not configured, skipping alert")
            return False
        
        # Filter high-confidence detections
        high_conf_detections = [
            d for d in detections 
            if d.get('confidence', 0) >= confidence_threshold
        ]
        
        if not high_conf_detections:
            logger.info(f"No high-confidence fires (>{confidence_threshold}) found for alert")
            return False
        
        try:
            # Create email content
            subject = f"🔥 High-Confidence Fire Alert - {len(high_conf_detections)} Fires Detected"
            body = self._create_alert_body(high_conf_detections, coordinates, radius_km)
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.config.sender_email
            msg['To'] = ', '.join(self.config.recipients)
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            # Attach CSV data
            csv_attachment = self._create_csv_attachment(high_conf_detections)
            if csv_attachment:
                msg.attach(csv_attachment)
            
            # Send email
            await self._send_email(msg)
            logger.info(f"Fire alert email sent to {len(self.config.recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send fire alert email: {e}")
            return False
    
    def _create_alert_body(
        self, 
        detections: List[Dict], 
        coordinates: List[float],
        radius_km: float
    ) -> str:
        """Create HTML email body for fire alert"""
        
        lat, lon = coordinates
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate summary statistics
        total_power = sum(d.get('power_mw', 0) for d in detections)
        avg_confidence = sum(d.get('confidence', 0) for d in detections) / len(detections) if detections else 0
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #ff4444; color: white; padding: 15px; border-radius: 5px; }}
                .summary {{ background-color: #f0f0f0; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .detection {{ border: 1px solid #ddd; margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .stats {{ display: flex; gap: 20px; margin: 10px 0; }}
                .stat-box {{ background: white; padding: 10px; border-radius: 5px; flex: 1; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🔥 URGENT: High-Confidence Fire Detection Alert</h2>
                <p><strong>Time:</strong> {timestamp}</p>
                <p><strong>Location:</strong> Latitude {lat:.4f}, Longitude {lon:.4f}</p>
                <p><strong>Search Radius:</strong> {radius_km} km</p>
            </div>
            
            <div class="summary">
                <h3>Alert Summary</h3>
                <div class="stats">
                    <div class="stat-box">
                        <strong>{len(detections)}</strong><br>
                        <span style="color: #666;">Total Fires Detected</span>
                    </div>
                    <div class="stat-box">
                        <strong>{avg_confidence:.1%}</strong><br>
                        <span style="color: #666;">Average Confidence</span>
                    </div>
                    <div class="stat-box">
                        <strong>{total_power:,.0f} MW</strong><br>
                        <span style="color: #666;">Total Thermal Power</span>
                    </div>
                </div>
            </div>
            
            <h3>Fire Detections Details</h3>
            <table>
                <tr>
                    <th>Latitude</th>
                    <th>Longitude</th>
                    <th>Confidence</th>
                    <th>Thermal Power (MW)</th>
                    <th>Distance (km)</th>
                    <th>Source</th>
                </tr>
        """
        
        for detection in detections:
            lat_d = detection.get('latitude', 0)
            lon_d = detection.get('longitude', 0)
            conf = detection.get('confidence', 0)
            power = detection.get('power_mw', 0)
            dist = detection.get('distance_km', 0)
            source = detection.get('source', 'Unknown')
            
            html += f"""
                <tr>
                    <td>{lat_d:.4f}</td>
                    <td>{lon_d:.4f}</td>
                    <td>{conf:.1%}</td>
                    <td>{power:,.0f}</td>
                    <td>{dist:.1f}</td>
                    <td>{source}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <div style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px;">
                <h4>⚠️ Recommended Actions:</h4>
                <ul>
                    <li>Verify fire locations with local authorities</li>
                    <li>Monitor fire progression and spread</li>
                    <li>Prepare emergency response if needed</li>
                    <li>Check air quality in affected areas</li>
                </ul>
            </div>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                This alert was generated automatically by the Satellite Fire Detection System.
                For more information, contact your system administrator.
            </p>
        </body>
        </html>
        """
        
        return html
    
    def _create_csv_attachment(self, detections: List[Dict]) -> Optional[MIMEApplication]:
        """Create CSV attachment with detection data"""
        try:
            if not detections:
                return None
            
            # Create CSV content
            csv_content = "Latitude,Longitude,Confidence,Thermal_Power_MW,Distance_km,Source,Timestamp\n"
            for detection in detections:
                csv_content += f"{detection.get('latitude', '')},{detection.get('longitude', '')},{detection.get('confidence', '')},{detection.get('power_mw', '')},{detection.get('distance_km', '')},{detection.get('source', '')},{detection.get('timestamp', '')}\n"
            
            # Create MIME attachment
            attachment = MIMEApplication(csv_content.encode('utf-8'), Name="fire_detections.csv")
            attachment['Content-Disposition'] = f'attachment; filename="fire_detections_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            return attachment
            
        except Exception as e:
            logger.error(f"Failed to create CSV attachment: {e}")
            return None
    
    async def _send_email(self, msg: MIMEMultipart) -> None:
        """Send email using SMTP"""
        try:
            # Create SMTP connection
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.sender_email, self.config.sender_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.config.sender_email, self.config.recipients, text)
            server.quit()
            
            logger.info("Email sent successfully")
            
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            raise
    
    def enable_alerts(self, email: str, password: str, recipients: List[str]):
        """Enable email alerts with credentials"""
        self.config.sender_email = email
        self.config.sender_password = password
        self.config.recipients = recipients
        self.config.enabled = True
        self.is_configured = self._check_configuration()
    
    def disable_alerts(self):
        """Disable email alerts"""
        self.config.enabled = False
        self.is_configured = False

# Global email alert instance
email_alerts = EmailAlertSystem()