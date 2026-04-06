#!/usr/bin/env python3
"""
Property Scraper - Main Application
Scrapes alo.bg for property listings and sends email notifications
"""

import os
import sys
import schedule
import time
import logging
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from property_scraper import AloPropertyScraper
from email_notifier import EmailNotifier
from persistence import PropertyTracker
from desktop_notifier import DesktopNotifier
from browser_notifier import BrowserNotifier

class PropertyScrapingService:
    def __init__(self):
        """Initialize the property scraping service"""
        self.setup_directories()
        self.setup_logging()

        # Initialize components
        self.scraper = AloPropertyScraper('config/filters.yaml')
        self.emailer = EmailNotifier('config/email_config.yaml')
        self.tracker = PropertyTracker('data/seen_properties.json')

        logging.info("Property Scraping Service initialized")

    def setup_directories(self):
        """Ensure required directories exist"""
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data', exist_ok=True)

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/service.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def run_scraping_job(self):
        """Run a single scraping job"""
        try:
            logging.info("=" * 50)
            logging.info("Starting scheduled property scraping job")

            # Clean up old entries periodically
            self.tracker.cleanup_old_entries(days_to_keep=30)

            # Scrape properties
            all_properties = self.scraper.scrape_properties()

            if not all_properties:
                logging.info("No properties found")
                return

            # Filter out properties we've seen before
            new_properties = self.tracker.filter_new_properties(all_properties)

            # Send email notification
            if new_properties:
                success = self.emailer.send_notification(new_properties)
                if success:
                    logging.info(f"Email notification sent for {len(new_properties)} new properties")
                else:
                    logging.error("Failed to send email notification")
            else:
                logging.info("No new properties to notify about")

            # Log statistics
            stats = self.tracker.get_stats()
            logging.info(f"Session stats: {stats}")

        except Exception as e:
            logging.error(f"Error during scraping job: {e}", exc_info=True)
        finally:
            logging.info("Scraping job completed")
            logging.info("=" * 50)

    def run_once(self):
        """Run scraping once and exit"""
        logging.info("Running property scraper once...")
        self.run_scraping_job()

    def start_scheduled_service(self):
        """Start the scheduled service"""
        logging.info("Starting scheduled property scraping service")
        logging.info("Service will run daily at 09:00")

        # Schedule daily run at 9 AM
        schedule.every().day.at("09:00").do(self.run_scraping_job)

        # Also run immediately on startup
        logging.info("Running initial scraping job...")
        self.run_scraping_job()

        # Keep the service running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logging.info("Service stopped by user")

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Property Scraping Service for alo.bg')
    parser.add_argument(
        '--mode',
        choices=['once', 'schedule', 'test'],
        default='schedule',
        help='Run mode: once (single run), schedule (continuous), or test (analyze website)'
    )

    args = parser.parse_args()

    service = PropertyScrapingService()

    if args.mode == 'once':
        service.run_once()
    elif args.mode == 'test':
        # Test mode - just scrape and analyze without sending emails
        logging.info("Test mode - analyzing alo.bg structure...")
        properties = service.scraper.scrape_properties()
        logging.info(f"Test completed. Found {len(properties)} properties")
        print("\nFirst property (for structure analysis):")
        if properties:
            for key, value in properties[0].items():
                print(f"  {key}: {value}")
    else:
        service.start_scheduled_service()

if __name__ == "__main__":
    main()