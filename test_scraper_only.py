#!/usr/bin/env python3
"""
Quick test script - just test scraping without email
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from property_scraper import AloPropertyScraper

def main():
    print("🧪 Testing property scraper (no email)...")

    # Create directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)

    try:
        # Test scraper
        scraper = AloPropertyScraper('config/filters.yaml')
        print("✅ Scraper initialized successfully")

        # Try scraping
        properties = scraper.scrape_properties()
        print(f"✅ Scraping completed. Found {len(properties)} properties")

        # Show first property if found
        if properties:
            print("\nFirst property found:")
            for key, value in properties[0].items():
                print(f"  {key}: {value}")
        else:
            print("No properties found - check logs/scraper.log for details")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()