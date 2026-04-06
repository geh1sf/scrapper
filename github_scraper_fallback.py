#!/usr/bin/env python3
"""
Fallback GitHub scraper - uses local test data if alo.bg is blocked
"""

import os
import sys
import json
from datetime import datetime, timezone
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_sample_data():
    """Create sample property data for testing/fallback"""
    return [
        {
            'title': 'Двустаен апартамент в кв. Овча купел',
            'price': '144 000 €',
            'location': 'Овча Купел, София',
            'area': '84 кв.м',
            'floor': '4 ет',
            'url': 'https://www.alo.bg/sample-property-1'
        },
        {
            'title': 'Тристаен апартамент в центъра',
            'price': '280 000 €',
            'location': 'Център, София',
            'area': '95 кв.м',
            'floor': '6 ет',
            'url': 'https://www.alo.bg/sample-property-2'
        }
    ]

def main():
    setup_logging()
    logging.info("🏠 Starting fallback GitHub scraper...")

    os.makedirs('data', exist_ok=True)
    os.makedirs('docs', exist_ok=True)

    try:
        # Try the real scraper first
        sys.path.append('src')
        from property_scraper import AloPropertyScraper

        logging.info("📡 Attempting real scraper...")
        scraper = AloPropertyScraper('config/filters.yaml')
        properties = scraper.scrape_properties(max_pages=2)  # Fewer pages for GitHub

        if not properties:
            logging.warning("🔄 No properties from real scraper, using sample data")
            properties = create_sample_data()

    except Exception as e:
        logging.warning(f"🔄 Real scraper failed ({e}), using sample data for demo")
        properties = create_sample_data()

    # Save results
    timestamp = datetime.now(timezone.utc).isoformat()
    results = {
        'timestamp': timestamp,
        'new_properties': properties,
        'stats': {'total_properties_seen': len(properties), 'properties_today': len(properties)},
        'total_properties_scanned': len(properties),
        'note': 'Demo data - replace with real scraper when network allows'
    }

    with open('data/latest_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logging.info(f"✅ Fallback scraper completed with {len(properties)} properties")

if __name__ == "__main__":
    main()