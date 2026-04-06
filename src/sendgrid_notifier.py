import os
import json
import logging
from typing import List, Dict
from datetime import datetime
import requests

class SendGridNotifier:
    def __init__(self):
        """Initialize SendGrid notifier"""
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@yourdomain.com')
        self.to_email = os.getenv('TO_EMAIL')

        if not self.api_key:
            logging.error("SENDGRID_API_KEY not found in environment variables")
            self.enabled = False
        elif not self.to_email:
            logging.error("TO_EMAIL not found in environment variables")
            self.enabled = False
        else:
            self.enabled = True
            logging.info("SendGrid notifier initialized successfully")

    def group_properties_by_type(self, properties: List[Dict]) -> Dict[str, List[Dict]]:
        """Group properties by broker and type for email"""
        grouped = {
            'argosdom_houses': [],
            'argosdom_apartments': [],
            'other_houses': [],
            'other_apartments': []
        }

        for prop in properties:
            lister = prop.get('lister', '').lower()
            title = prop.get('title', '').lower()
            search_city = prop.get('search_city', '').lower()

            # Check if it's from Argosdom
            is_argosdom = any(keyword in lister for keyword in ['argosdom', 'argos'])

            # Check if it's a house or apartment
            is_house = any(keyword in title or keyword in search_city for keyword in [
                'къща', 'вила', 'house', 'villa', 'houses'
            ])

            # Categorize
            if is_argosdom and is_house:
                grouped['argosdom_houses'].append(prop)
            elif is_argosdom:
                grouped['argosdom_apartments'].append(prop)
            elif is_house:
                grouped['other_houses'].append(prop)
            else:
                grouped['other_apartments'].append(prop)

        return grouped

    def format_property_email(self, properties: List[Dict[str, str]]) -> str:
        """Format properties into organized HTML email"""
        if not properties:
            return """
            <h2>🏠 Property Alert - No New Properties</h2>
            <p>No new properties found in your latest search.</p>
            <p>The scraper is working correctly and will continue checking daily.</p>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #2c5aa0; margin-bottom: 30px; }}
                .summary {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center; }}
                .section {{ margin: 30px 0; }}
                .section h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 8px; margin-bottom: 20px; }}
                .section-count {{ color: #7f8c8d; font-weight: normal; }}
                .property {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; background-color: #f9f9f9; }}
                .property h3 {{ color: #2c5aa0; margin-top: 0; }}
                .price {{ font-weight: bold; color: #d32f2f; font-size: 1.2em; }}
                .details {{ margin: 10px 0; }}
                .info-item {{ display: block; margin: 5px 0; color: #555; }}
                .view-btn {{ display: inline-block; background-color: #2c5aa0; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏠 New Properties Found!</h1>
                </div>

                <div class="summary">
                    <h3>📊 Summary</h3>
                    <p><strong>{len(properties)} new properties</strong> found matching your criteria</p>
                    <p><strong>Search Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC</p>
                </div>
        """

        # Group properties by type
        grouped = self.group_properties_by_type(properties)

        # Generate sections
        sections = [
            ("🏡 Argosdom Houses", grouped['argosdom_houses']),
            ("🏢 Argosdom Apartments", grouped['argosdom_apartments']),
            ("🏠 Other Agency Houses", grouped['other_houses']),
            ("🏘️ Other Agency Apartments", grouped['other_apartments'])
        ]

        for section_title, section_properties in sections:
            if section_properties:
                html += f"""
                <div class="section">
                    <h2>{section_title} <span class="section-count">({len(section_properties)})</span></h2>
                """

                for i, prop in enumerate(section_properties, 1):
                    lister_info = f"<div class='info-item'><strong>👤 Listed by:</strong> {prop.get('lister', 'Not specified')}</div>" if prop.get('lister') else ""

                    html += f"""
                    <div class="property">
                        <h3>🏠 Property #{i}</h3>
                        <h4>{prop.get('title', 'No title')}</h4>
                        <div class="price">{prop.get('price', 'Price not specified')}</div>
                        <div class="details">
                            <div class="info-item"><strong>📍 Location:</strong> {prop.get('location', 'Not specified')}</div>
                            <div class="info-item"><strong>📐 Area:</strong> {prop.get('area', 'Not specified')}</div>
                            <div class="info-item"><strong>🏢 Floor:</strong> {prop.get('floor', 'Not specified')}</div>
                            <div class="info-item"><strong>🏙️ Type:</strong> {prop.get('search_city', 'Not specified')}</div>
                            {lister_info}
                        </div>
                        <a href="{prop.get('url', '#')}" class="view-btn" target="_blank">View Property on alo.bg</a>
                    </div>
                    """

                html += "</div>"

        html += """
                <div class="footer">
                    <p>🤖 Automated by GitHub Actions Property Scraper</p>
                    <p>🔄 Daily updates at 8:00 AM UTC</p>
                    <p>⚙️ Update your filters in the GitHub repository</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def send_notification(self, properties: List[Dict[str, str]]) -> bool:
        """Send email notification via SendGrid"""
        if not self.enabled:
            logging.warning("SendGrid not properly configured")
            return False

        try:
            subject = f"🏠 Property Alert: {len(properties)} New Properties Found" if properties else "🏠 Property Alert: No New Properties"

            html_content = self.format_property_email(properties)

            # SendGrid API payload
            payload = {
                "personalizations": [{
                    "to": [{"email": self.to_email}]
                }],
                "from": {"email": self.from_email, "name": "Property Scraper"},
                "subject": subject,
                "content": [{
                    "type": "text/html",
                    "value": html_content
                }]
            }

            # Send via SendGrid API
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
                logging.info(f"✅ Email sent successfully via SendGrid to {self.to_email}")
                return True
            else:
                logging.error(f"❌ SendGrid API error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logging.error(f"❌ Failed to send email via SendGrid: {e}")
            return False