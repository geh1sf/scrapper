#!/usr/bin/env python3
"""
Quick email test script
"""

import smtplib
import os
from dotenv import load_dotenv

def test_basic_email():
    """Test basic email functionality"""
    load_dotenv()

    email_addr = os.getenv('GMAIL_EMAIL')
    password = os.getenv('GMAIL_APP_PASSWORD')

    if not email_addr or not password:
        print("❌ Gmail credentials not found")
        return False

    try:
        # Test 1: Basic SMTP connection
        print("🔗 Testing SMTP connection...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_addr, password)
        print("✅ SMTP connection successful")

        # Test 2: Import email modules
        print("📧 Testing email imports...")
        from email.mime.text import MimeText
        from email.mime.multipart import MimeMultipart
        print("✅ Email imports successful")

        # Test 3: Send actual email
        print("📤 Sending test email...")
        msg = MimeMultipart()
        msg['Subject'] = '[Property Scraper Test] Email Working!'
        msg['From'] = email_addr
        msg['To'] = email_addr

        body = """
        <h2>🎉 Property Scraper Email Test</h2>
        <p>If you receive this email, your property scraper email notifications are working!</p>
        <p><strong>Next step:</strong> Run your property scraper to get real estate alerts.</p>
        """

        msg.attach(MimeText(body, 'html'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_addr, password)
            server.send_message(msg)

        print("✅ Test email sent successfully!")
        print(f"📬 Check your inbox: {email_addr}")
        return True

    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

if __name__ == "__main__":
    test_basic_email()