#!/usr/bin/env python3
"""
Email notifications for new properties using SendGrid
"""

import os
import json
import logging
import requests
from datetime import datetime

class PropertyEmailNotifier:
    def __init__(self):
        """Initialize email notifier with environment variables"""
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@propertytracker.com')
        self.to_email = os.getenv('TO_EMAIL')

        # Check if email is properly configured
        if not self.api_key or not self.to_email:
            self.enabled = False
            logging.info("📧 Email not configured (missing SENDGRID_API_KEY or TO_EMAIL)")
        else:
            self.enabled = True
            logging.info("📧 Email notifications enabled")

    def should_send_email(self, new_apartments, new_houses, argosdom_apartments, argosdom_houses):
        """Determine if we should send an email notification"""
        if not self.enabled:
            return False

        # Send email if there are ANY new properties OR any Argosdom properties
        total_new = len(new_apartments) + len(new_houses)
        total_argosdom = len(argosdom_apartments) + len(argosdom_houses)

        return total_new > 0 or total_argosdom > 0

    def generate_email_html(self, new_apartments, new_houses, argosdom_apartments, argosdom_houses, timestamp):
        """Generate HTML email content"""

        total_new = len(new_apartments) + len(new_houses)
        total_argosdom = len(argosdom_apartments) + len(argosdom_houses)

        # Parse timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M UTC')
        except:
            formatted_time = timestamp

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; }}
        .header {{ background: #2c3e50; color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .summary {{ background: #ecf0f1; padding: 20px; text-align: center; }}
        .section {{ padding: 20px; }}
        .section h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .property {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 8px; background: #f9f9f9; }}
        .property h3 {{ color: #2980b9; margin-top: 0; }}
        .property-image {{ text-align: center; margin: 10px 0; }}
        .property-image img {{ max-width: 300px; max-height: 200px; border-radius: 6px; }}
        .property-details {{ margin: 10px 0; }}
        .detail-row {{ margin: 5px 0; color: #555; }}
        .view-btn {{ display: inline-block; background: #27ae60; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 15px; }}
        .argosdom-tag {{ background: #e74c3c; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .vip-tag {{ background: #f39c12; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .footer {{ background: #34495e; color: white; padding: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Kraimorie Property Alert</h1>
            <p>New properties found in Kraimorie, Burgas</p>
        </div>

        <div class="summary">
            <h3>📊 Summary for {formatted_time}</h3>
            <p><strong>{total_new} new properties</strong> • <strong>{total_argosdom} Argosdom properties</strong></p>
        </div>
"""

        # Add new apartments section
        if new_apartments:
            html += self.generate_property_section("🏠 NEW APARTMENTS", new_apartments)

        # Add new houses section
        if new_houses:
            html += self.generate_property_section("🏡 NEW HOUSES", new_houses)

        # Add Argosdom sections
        if argosdom_apartments:
            html += self.generate_property_section("⭐ ARGOSDOM APARTMENTS", argosdom_apartments)

        if argosdom_houses:
            html += self.generate_property_section("⭐ ARGOSDOM HOUSES", argosdom_houses)

        html += """
        <div class="footer">
            <p>🤖 Automated by Kraimorie Property Tracker</p>
            <p>🔄 Daily scans at 23:57 UTC</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def generate_property_section(self, title, properties):
        """Generate HTML for a property section"""
        html = f"""
        <div class="section">
            <h2>{title} ({len(properties)})</h2>
"""

        for i, prop in enumerate(properties, 1):
            badges = ""
            if prop.get('is_argosdom'):
                badges += '<span class="argosdom-tag">ARGOSDOM</span> '
            if prop.get('listing_type') == 'vip':
                badges += '<span class="vip-tag">VIP</span>'

            image_html = ""
            if prop.get('image_url'):
                image_html = f"""
                <div class="property-image">
                    <img src="{prop.get('image_url')}" alt="Property image">
                </div>
"""

            html += f"""
            <div class="property">
                <h3>Property #{i} {badges}</h3>
                <h4>{prop.get('title', 'No title')}</h4>
                {image_html}
                <div class="property-details">
                    <div class="detail-row"><strong>💰 Price:</strong> {prop.get('price', 'Not specified')}</div>
                    <div class="detail-row"><strong>📍 Location:</strong> {prop.get('location', 'Not specified')}</div>
                </div>
                <a href="{prop.get('url', '#')}" class="view-btn" target="_blank">View on alo.bg</a>
            </div>
"""

        html += "</div>"
        return html

    def send_notification(self, new_apartments, new_houses, argosdom_apartments, argosdom_houses, timestamp):
        """Send email notification"""
        if not self.should_send_email(new_apartments, new_houses, argosdom_apartments, argosdom_houses):
            logging.info("📧 No email sent - no new properties or Argosdom properties")
            return True

        try:
            total_new = len(new_apartments) + len(new_houses)
            total_argosdom = len(argosdom_apartments) + len(argosdom_houses)

            subject = f"🏠 Kraimorie Alert: {total_new} New Properties"
            if total_argosdom > 0:
                subject += f" + {total_argosdom} Argosdom"

            html_content = self.generate_email_html(new_apartments, new_houses, argosdom_apartments, argosdom_houses, timestamp)

            # SendGrid API payload
            payload = {
                "personalizations": [{
                    "to": [{"email": self.to_email}]
                }],
                "from": {"email": self.from_email, "name": "Kraimorie Property Tracker"},
                "subject": subject,
                "content": [{
                    "type": "text/html",
                    "value": html_content
                }]
            }

            # Send via SendGrid
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 202:
                logging.info(f"✅ Email sent successfully to {self.to_email}")
                logging.info(f"📊 Subject: {subject}")
                return True
            else:
                logging.error(f"❌ SendGrid error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logging.error(f"❌ Email sending failed: {e}")
            return False