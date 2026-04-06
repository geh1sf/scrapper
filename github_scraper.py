#!/usr/bin/env python3
"""
GitHub Actions optimized property scraper
Saves results as JSON for GitHub Pages
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
import logging

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from property_scraper import AloPropertyScraper
from persistence import PropertyTracker

def setup_logging():
    """Setup logging for GitHub Actions"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main GitHub scraper function"""
    setup_logging()
    logging.info("🏠 Starting GitHub property scraper...")

    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    os.makedirs('logs', exist_ok=True)  # Create logs directory

    # Initialize scraper components
    scraper = AloPropertyScraper('config/filters.yaml')
    tracker = PropertyTracker('data/seen_properties.json')

    try:
        # Clean up old entries
        tracker.cleanup_old_entries(days_to_keep=30)

        # Scrape properties (more pages for GitHub since it's free)
        all_properties = scraper.scrape_properties(max_pages=5)

        if not all_properties:
            logging.info("No properties found")
            save_results([], tracker.get_stats())
            return

        # Filter new properties
        new_properties = tracker.filter_new_properties(all_properties)

        # Save results
        save_results(new_properties, tracker.get_stats(), all_properties)

        logging.info(f"✅ GitHub scraper completed successfully!")
        logging.info(f"📊 Found {len(new_properties)} new properties")
        logging.info(f"📊 Total {len(all_properties)} properties scanned")

    except Exception as e:
        logging.error(f"❌ Scraper failed: {e}")
        # Save error info
        save_error(str(e))
        sys.exit(1)

def save_results(new_properties, stats, all_properties=None):
    """Save results as JSON for GitHub Pages"""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Current run results
    current_results = {
        'timestamp': timestamp,
        'new_properties': new_properties,
        'stats': stats,
        'total_properties_scanned': len(all_properties) if all_properties else 0
    }

    # Save current results
    with open('data/latest_results.json', 'w', encoding='utf-8') as f:
        json.dump(current_results, f, ensure_ascii=False, indent=2)

    # Update history (keep last 30 days)
    history_file = 'data/scraping_history.json'
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
    except:
        history = []

    # Add current results to history
    history.append({
        'date': timestamp[:10],  # YYYY-MM-DD
        'timestamp': timestamp,
        'new_count': len(new_properties),
        'total_scanned': len(all_properties) if all_properties else 0,
        'has_new': len(new_properties) > 0
    })

    # Keep only last 30 days
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
    cutoff_date = cutoff_date.isoformat()[:10]

    history = [h for h in history if h['date'] >= cutoff_date]

    # Save history
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    logging.info(f"💾 Results saved: {len(new_properties)} new properties")

def save_error(error_msg):
    """Save error information"""
    timestamp = datetime.now(timezone.utc).isoformat()
    error_data = {
        'timestamp': timestamp,
        'error': error_msg,
        'new_properties': [],
        'stats': {'total_properties_seen': 0, 'properties_today': 0}
    }

    with open('data/latest_results.json', 'w', encoding='utf-8') as f:
        json.dump(error_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()