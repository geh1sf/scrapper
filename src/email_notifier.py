import smtplib
import yaml
import os
from datetime import datetime
from typing import List, Dict
import logging
from dotenv import load_dotenv

# More robust email import handling
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_IMPORTS_OK = True
except ImportError:
    try:
        # Alternative approach
        import email.mime.text
        import email.mime.multipart
        MimeText = email.mime.text.MimeText
        MimeMultipart = email.mime.multipart.MimeMultipart
        EMAIL_IMPORTS_OK = True
    except (ImportError, AttributeError):
        # Final fallback - create dummy classes
        logging.warning("Email imports failed, email notifications disabled")
        EMAIL_IMPORTS_OK = False

        class MimeText:
            def __init__(self, *args, **kwargs):
                pass

        class MimeMultipart:
            def __init__(self, *args, **kwargs):
                pass

class EmailNotifier:
    def __init__(self, email_config_path: str):
        """Initialize email notifier with configuration"""
        load_dotenv()
        self.config = self.load_email_config(email_config_path)

        # Get credentials from environment variables
        self.sender_email = os.getenv('GMAIL_EMAIL')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD')

        if not self.sender_email or not self.sender_password:
            logging.error("Gmail credentials not found in environment variables")
            raise ValueError("Gmail credentials required")

    def load_email_config(self, config_path: str) -> Dict:
        """Load email configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Error loading email config: {e}")
            return {}

    def format_property_email(self, properties: List[Dict[str, str]]) -> str:
        """Format properties list into HTML email content"""
        if not properties:
            return "<p>No new properties found matching your criteria.</p>"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .property {{
                    border: 1px solid #ddd;
                    margin: 15px 0;
                    padding: 15px;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }}
                .property h3 {{
                    color: #2c5aa0;
                    margin-top: 0;
                }}
                .property-details {{
                    margin: 10px 0;
                }}
                .price {{
                    font-weight: bold;
                    color: #d32f2f;
                    font-size: 1.2em;
                }}
                .link {{
                    display: inline-block;
                    margin-top: 10px;
                    padding: 8px 15px;
                    background-color: #2c5aa0;
                    color: white;
                    text-decoration: none;
                    border-radius: 3px;
                }}
                .summary {{
                    background-color: #e3f2fd;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="summary">
                <h2>Property Alert Summary</h2>
                <p><strong>Found {len(properties)} properties</strong> matching your criteria</p>
                <p><strong>Search Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
        """

        for i, prop in enumerate(properties, 1):
            html_content += f"""
            <div class="property">
                <h3>Property #{i}: {prop.get('title', 'No title')}</h3>
                <div class="property-details">
                    <div class="price">{prop.get('price', 'Price not specified')}</div>
                    <p><strong>Location:</strong> {prop.get('location', 'Not specified')}</p>
                    <p><strong>Area:</strong> {prop.get('area', 'Not specified')}</p>
                    <p><strong>Floor:</strong> {prop.get('floor', 'Not specified')}</p>
                </div>
                <a href="{prop.get('url', '#')}" class="link" target="_blank">View Property</a>
            </div>
            """

        html_content += """
        </body>
        </html>
        """

        return html_content

    def send_notification(self, properties: List[Dict[str, str]]) -> bool:
        """Send email notification with property listings"""
        if not EMAIL_IMPORTS_OK:
            logging.error("Email functionality not available due to import issues")
            # Instead, save to file
            self.save_to_file(properties)
            return False

        try:
            # Get recipient email from config or use sender as default
            recipient_email = (
                self.config.get('email', {}).get('recipient_email') or
                self.sender_email
            )

            # Create message
            msg = MimeMultipart('alternative')
            msg['Subject'] = f"{self.config.get('notification', {}).get('subject_prefix', '[Property Alert]')} {len(properties)} New Properties Found"
            msg['From'] = self.sender_email
            msg['To'] = recipient_email

            # Create HTML content
            html_content = self.format_property_email(properties)
            html_part = MimeText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # Create plain text version
            if properties:
                text_content = f"Found {len(properties)} properties:\n\n"
                for i, prop in enumerate(properties, 1):
                    text_content += f"{i}. {prop.get('title', 'No title')}\n"
                    text_content += f"   Price: {prop.get('price', 'Not specified')}\n"
                    text_content += f"   Location: {prop.get('location', 'Not specified')}\n"
                    text_content += f"   URL: {prop.get('url', 'No URL')}\n\n"
            else:
                text_content = "No new properties found matching your criteria."

            text_part = MimeText(text_content, 'plain', 'utf-8')
            msg.attach(text_part)

            # Send email
            with smtplib.SMTP(
                self.config['email']['smtp_server'],
                self.config['email']['smtp_port']
            ) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logging.info(f"Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            # Fallback: save to file
            self.save_to_file(properties)
            return False

    def save_to_file(self, properties: List[Dict[str, str]]):
        """Fallback: Save properties to HTML file if email fails"""
        try:
            html_content = self.format_property_email(properties)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"logs/properties_{timestamp}.html"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logging.info(f"Properties saved to {filename}")
            print(f"📧 Email failed, but properties saved to: {filename}")

        except Exception as e:
            logging.error(f"Failed to save to file: {e}")