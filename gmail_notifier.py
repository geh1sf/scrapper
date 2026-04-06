#!/usr/bin/env python3
"""
Email notifications using Gmail SMTP (simplest option)
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class GmailNotifier:
    def __init__(self):
        """Initialize Gmail SMTP notifier"""
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = os.getenv('GMAIL_USER')
        self.password = os.getenv('GMAIL_APP_PASSWORD')  # App password, not regular password
        self.from_email = os.getenv('FROM_EMAIL', self.username)
        self.to_email = os.getenv('TO_EMAIL', self.username)

        # Check if Gmail is properly configured
        if not self.username or not self.password:
            self.enabled = False
            logging.info("📧 Gmail not configured (missing GMAIL_USER or GMAIL_APP_PASSWORD)")
        else:
            self.enabled = True
            logging.info(f"📧 Gmail notifications enabled for {self.to_email}")

    def should_send_email(self, new_apartments, new_houses, argosdom_apartments, argosdom_houses):
        """Determine if we should send an email notification"""
        if not self.enabled:
            return False

        # Send email on every run to provide daily status updates
        return True

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
        .container {{ max-width: 800px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: #2c3e50; color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .summary {{ background: #ecf0f1; padding: 20px; text-align: center; font-size: 18px; }}
        .section {{ padding: 20px; }}
        .section h2 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .property {{ border: 1px solid #ddd; margin: 15px 0; padding: 20px; border-radius: 8px; background: #f9f9f9; }}
        .property h3 {{ color: #2980b9; margin-top: 0; font-size: 18px; }}
        .property-image {{ text-align: center; margin: 15px 0; }}
        .property-image img {{ max-width: 300px; max-height: 200px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .property-details {{ margin: 15px 0; }}
        .detail-row {{ margin: 8px 0; color: #555; font-size: 14px; }}
        .view-btn {{ display: inline-block; background: #27ae60; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 15px; font-weight: bold; }}
        .view-btn:hover {{ background: #229954; }}
        .argosdom-tag {{ background: #e74c3c; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-left: 10px; }}
        .vip-tag {{ background: #f39c12; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-left: 10px; }}
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
            <strong>📊 {formatted_time}</strong><br>"""

        # Create status message based on findings
        if total_new > 0 or total_argosdom > 0:
            html += f"            🏠 <strong>{total_new} new properties</strong> • ⭐ <strong>{total_argosdom} Argosdom properties</strong>"
        else:
            html += "            🔍 <strong>No new properties today</strong> • ✅ <strong>System monitoring active</strong>"

        html += """
        </div>
"""

        # Add property sections or status message
        if new_apartments:
            html += self.generate_property_section("🏠 NEW APARTMENTS TODAY", new_apartments)

        if new_houses:
            html += self.generate_property_section("🏡 NEW HOUSES TODAY", new_houses)

        if argosdom_apartments:
            html += self.generate_property_section("⭐ ARGOSDOM APARTMENTS", argosdom_apartments)

        if argosdom_houses:
            html += self.generate_property_section("⭐ ARGOSDOM HOUSES", argosdom_houses)

        # Add status section when no properties found
        if total_new == 0 and total_argosdom == 0:
            html += """
        <div class="section">
            <h2>📊 Daily Monitoring Status</h2>
            <div class="property">
                <h3>✅ System Running Successfully</h3>
                <div class="property-details">
                    <div class="detail-row"><strong>🔍 Search Areas:</strong> Kraimorie, Burgas - Apartments & Houses</div>
                    <div class="detail-row"><strong>⭐ Special Focus:</strong> Monitoring for Argosdom properties</div>
                    <div class="detail-row"><strong>⏰ Next Check:</strong> Daily at 23:57 UTC</div>
                    <div class="detail-row"><strong>📊 Today's Result:</strong> No new properties found</div>
                </div>
            </div>
        </div>
"""

        html += """
        <div class="footer">
            <p>🤖 Automated by Kraimorie Property Tracker</p>
            <p>🔄 Daily scans at 23:57 UTC</p>
            <p>📧 Powered by Gmail SMTP</p>
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
                badges += '<span class="argosdom-tag">ARGOSDOM</span>'
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
                <h3>🏠 Property #{i}{badges}</h3>
                <h4 style="color: #2c3e50; margin: 10px 0;">{prop.get('title', 'No title')}</h4>
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
        """Send email notification via Gmail SMTP"""
        if not self.should_send_email(new_apartments, new_houses, argosdom_apartments, argosdom_houses):
            logging.info("📧 No email sent - Gmail not configured")
            return True

        try:
            total_new = len(new_apartments) + len(new_houses)
            total_argosdom = len(argosdom_apartments) + len(argosdom_houses)

            # Create subject based on findings
            if total_new > 0 or total_argosdom > 0:
                subject = f"🏠 Kraimorie Alert: {total_new} New Properties"
                if total_argosdom > 0:
                    subject += f" + {total_argosdom} Argosdom"
            else:
                subject = "🔍 Kraimorie Daily Report: No New Properties"

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = self.to_email

            # Generate HTML content
            html_content = self.generate_email_html(new_apartments, new_houses, argosdom_apartments, argosdom_houses, timestamp)

            # Create HTML part
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # Connect to Gmail SMTP and send
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()  # Enable encryption
            server.login(self.username, self.password)

            # Send email
            text = msg.as_string()
            server.sendmail(self.from_email, self.to_email, text)
            server.quit()

            logging.info(f"✅ Gmail email sent successfully to {self.to_email}")
            logging.info(f"📊 Subject: {subject}")
            return True

        except smtplib.SMTPAuthenticationError:
            logging.error("❌ Gmail authentication failed - check GMAIL_USER and GMAIL_APP_PASSWORD")
            logging.error("💡 Make sure you're using an App Password, not your regular Gmail password!")
            return False
        except Exception as e:
            logging.error(f"❌ Gmail sending failed: {e}")
            return False