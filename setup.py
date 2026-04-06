#!/usr/bin/env python3
"""
Setup script for Property Scraper
Helps configure Gmail credentials and test the setup
"""

import os
import sys
import getpass
from pathlib import Path

def create_env_file():
    """Create .env file with Gmail credentials"""
    print("🔧 Setting up Gmail credentials...")
    print()
    print("You'll need to create a Gmail App Password for this service.")
    print("Follow these steps:")
    print("1. Go to https://myaccount.google.com/security")
    print("2. Enable 2-Step Verification if not already enabled")
    print("3. Click on 'App passwords'")
    print("4. Generate a new app password for 'Mail'")
    print("5. Copy the 16-character password")
    print()

    email = input("Enter your Gmail address: ").strip()
    print("Enter your Gmail App Password (16 characters, no spaces):")
    password = getpass.getpass("App Password: ").replace(' ', '')

    env_content = f"""# Gmail Configuration
GMAIL_EMAIL={email}
GMAIL_APP_PASSWORD={password}
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("✅ Credentials saved to .env file")
    return email

def update_email_config(email):
    """Update email configuration file with user's email"""
    config_file = 'config/email_config.yaml'

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace placeholder emails with actual email
        content = content.replace('your_email@gmail.com', email)

        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Updated {config_file} with your email address")
    except Exception as e:
        print(f"⚠️  Could not update {config_file}: {e}")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    print("✅ Dependencies installed")

def test_setup():
    """Test the setup by running a quick check"""
    print("🧪 Testing setup...")

    try:
        # Test imports
        sys.path.append('src')
        from email_notifier import EmailNotifier
        from property_scraper import AloPropertyScraper

        # Test email configuration
        notifier = EmailNotifier('config/email_config.yaml')
        print("✅ Email configuration loaded successfully")

        # Test property scraper configuration
        scraper = AloPropertyScraper('config/filters.yaml')
        print("✅ Property scraper configuration loaded successfully")

        print("🎉 Setup test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🏠 Property Scraper Setup")
    print("=" * 40)

    # Check if .env already exists
    if os.path.exists('.env'):
        overwrite = input(".env file already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Skipping credential setup...")
            email = None
        else:
            email = create_env_file()
    else:
        email = create_env_file()

    print()

    # Update email config if we have an email
    if email:
        update_email_config(email)
        print()

    # Install dependencies
    install_dependencies()
    print()

    # Test setup
    test_passed = test_setup()
    print()

    if test_passed:
        print("🚀 Setup completed successfully!")
        print()
        print("Next steps:")
        print("1. Edit 'config/filters.yaml' to set your property search criteria")
        print("2. Run 'python main.py --mode test' to test scraping")
        print("3. Run 'python main.py --mode once' to run once")
        print("4. Run 'python main.py' to start the scheduled service")
    else:
        print("❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()