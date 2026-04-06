#!/usr/bin/env python3
"""
Main entry point for daily Kraimorie tracking
Combines tracking and website generation
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging():
    """Setup logging for GitHub Actions"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def main():
    """Main tracking and website generation"""
    setup_logging()
    logging.info("🏠 Starting daily Kraimorie property tracking...")

    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    try:
        # Import and run tracker
        from kraimorie_tracker import KraimorieTracker

        tracker = KraimorieTracker()
        results = tracker.track_all_listings()

        if results:
            logging.info("✅ Property tracking completed successfully!")
            logging.info(f"📊 Found {results['new_properties_today']} new properties")
            logging.info(f"📊 Total {results['total_current_properties']} properties available")
            logging.info(f"📊 {results['argosdom_properties']} Argosdom properties")

            # Generate website
            logging.info("🌐 Generating website...")
            import subprocess
            subprocess.run(['python', 'generate_daily_website.py'], check=True)

            logging.info("✅ Daily tracking completed successfully!")

        else:
            logging.error("❌ Property tracking failed")
            # Create error results file
            error_results = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': 'Tracking failed - possibly missing dependencies',
                'total_current_properties': 0,
                'new_properties_today': 0,
                'argosdom_properties': 0,
                'new_properties': [],
                'all_argosdom_properties': [],
                'summary': {}
            }

            with open('data/daily_kraimorie_results.json', 'w', encoding='utf-8') as f:
                json.dump(error_results, f, ensure_ascii=False, indent=2)

            # Generate website anyway
            import subprocess
            subprocess.run(['python', 'generate_daily_website.py'], check=False)

            sys.exit(1)

    except Exception as e:
        logging.error(f"❌ Tracker failed: {e}")
        # Create error results file
        error_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e),
            'total_current_properties': 0,
            'new_properties_today': 0,
            'argosdom_properties': 0,
            'new_properties': [],
            'all_argosdom_properties': [],
            'summary': {}
        }

        with open('data/daily_kraimorie_results.json', 'w', encoding='utf-8') as f:
            json.dump(error_results, f, ensure_ascii=False, indent=2)

        # Generate website anyway
        import subprocess
        subprocess.run(['python', 'generate_daily_website.py'], check=False)

        sys.exit(1)

if __name__ == "__main__":
    main()