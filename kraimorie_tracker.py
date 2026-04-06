#!/usr/bin/env python3
"""
Daily Kraimorie Property Tracker
Monitors ALL new property listings in Kraimorie, with special attention to Argosdom
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timezone

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging():
    """Setup logging"""
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/tracker.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

class KraimorieTracker:
    def __init__(self):
        """Initialize the tracker"""
        self.base_url = "https://www.alo.bg"

        # ALL property types for Kraimorie
        self.search_urls = [
            {
                "name": "Kraimorie - All Apartments",
                "url": "https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/?region_id=2&location_ids=300&section_ids=25"
            },
            {
                "name": "Kraimorie - All Houses",
                "url": "https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/?region_id=2&location_ids=300&section_ids=25"
            },
            {
                "name": "Kraimorie - Commercial",
                "url": "https://www.alo.bg/obiavi/imoti-prodajbi/magazini-ofisi/?region_id=2&location_ids=300&section_ids=25"
            },
            {
                "name": "Kraimorie - Land",
                "url": "https://www.alo.bg/obiavi/imoti-prodajbi/parceli-za-zastroiavane-investicionni-proekti/?region_id=2&location_ids=300&section_ids=25"
            }
        ]

        # Special Argosdom URL
        self.argosdom_url = "https://www.alo.bg/users/argosdom"

        self.seen_properties_file = 'data/seen_kraimorie_properties.json'
        self.results_file = 'data/daily_kraimorie_results.json'

        # Load seen properties
        self.seen_properties = self.load_seen_properties()

    def load_seen_properties(self):
        """Load previously seen properties"""
        try:
            if os.path.exists(self.seen_properties_file):
                with open(self.seen_properties_file, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
        except:
            pass
        return set()

    def save_seen_properties(self):
        """Save seen properties"""
        os.makedirs('data', exist_ok=True)
        with open(self.seen_properties_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.seen_properties), f, ensure_ascii=False, indent=2)

    def extract_simple_property(self, element):
        """Extract basic property info from listing element"""
        prop = {
            'title': '',
            'price': '',
            'location': '',
            'url': '',
            'lister': '',
            'is_argosdom': False,
            'listing_type': 'regular'
        }

        try:
            # Check if this is VIP or regular listing
            if 'listvip-item' in str(element.get('class', [])):
                prop['listing_type'] = 'vip'

            # Title - handle both types
            title_elem = element.find('h3', class_='listtop-item-title') or element.find('h3', class_='listvip-item-title')
            if title_elem:
                prop['title'] = title_elem.get_text(strip=True)

            # URL
            link_elem = element.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if not href.startswith('http'):
                    href = f"https://www.alo.bg{href}"
                prop['url'] = href

            # Location
            addr_elem = element.find('div', class_='listtop-item-address') or element.find('div', class_='listvip-item-address')
            if addr_elem:
                prop['location'] = addr_elem.get_text(strip=True)

            # Price - simple extraction
            full_text = element.get_text()
            import re
            price_match = re.search(r'([\d\s,]+)\s*€', full_text)
            if price_match:
                prop['price'] = f"{price_match.group(1).strip()} €"

            # Check for Argosdom
            all_links = element.find_all('a', href=True)
            element_text = element.get_text().lower()

            for link in all_links:
                href = link.get('href', '').lower()
                if 'argosdom' in href or '/users/argosdom' in href:
                    prop['is_argosdom'] = True
                    break

            if 'argosdom' in element_text:
                prop['is_argosdom'] = True

            # Generate unique ID for this property
            if prop['url']:
                prop['property_id'] = prop['url'].split('/')[-1]
            else:
                prop['property_id'] = hash(prop['title'] + prop['location'])

        except Exception as e:
            logging.error(f"Error extracting property: {e}")

        return prop

    def track_all_listings(self):
        """Track all listings in Kraimorie"""

        try:
            import requests
            from bs4 import BeautifulSoup

            logging.info("Starting Kraimorie daily tracking...")

            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            all_current_properties = []
            new_properties = []
            argosdom_properties = []

            # Check each property type
            for search in self.search_urls:
                logging.info(f"Checking {search['name']}...")

                try:
                    response = session.get(search['url'], timeout=30)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Find all listings - both types
                    listings = soup.find_all('div', class_='listtop-item') + soup.find_all('div', class_='listvip-item')

                    logging.info(f"Found {len(listings)} listings in {search['name']}")

                    for listing in listings:
                        prop = self.extract_simple_property(listing)

                        if prop['property_id']:
                            all_current_properties.append(prop)

                            # Check if this is new
                            if prop['property_id'] not in self.seen_properties:
                                new_properties.append(prop)
                                self.seen_properties.add(prop['property_id'])
                                logging.info(f"NEW: {prop['title'][:50]}...")

                            # Track Argosdom separately
                            if prop['is_argosdom']:
                                argosdom_properties.append(prop)

                    time.sleep(2)  # Be respectful

                except Exception as e:
                    logging.error(f"Error checking {search['name']}: {e}")

            # Also check Argosdom user page directly
            try:
                logging.info("Checking Argosdom user page...")
                response = session.get(self.argosdom_url, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')
                listings = soup.find_all('div', class_='listtop-item') + soup.find_all('div', class_='listvip-item')

                logging.info(f"Found {len(listings)} listings on Argosdom page")

                for listing in listings:
                    prop = self.extract_simple_property(listing)
                    prop['is_argosdom'] = True  # Force this since it's from their page
                    prop['source'] = 'argosdom_page'

                    # Check if it's Kraimorie-related
                    if 'крайморие' in prop['title'].lower() or 'крайморие' in prop['location'].lower():
                        if prop['property_id'] not in [p['property_id'] for p in all_current_properties]:
                            all_current_properties.append(prop)
                            argosdom_properties.append(prop)

                            if prop['property_id'] not in self.seen_properties:
                                new_properties.append(prop)
                                self.seen_properties.add(prop['property_id'])
                                logging.info(f"NEW ARGOSDOM: {prop['title'][:50]}...")

            except Exception as e:
                logging.error(f"Error checking Argosdom page: {e}")

            # Save results
            self.save_seen_properties()

            results = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_current_properties': len(all_current_properties),
                'new_properties_today': len(new_properties),
                'argosdom_properties': len(argosdom_properties),
                'new_properties': new_properties,
                'all_argosdom_properties': argosdom_properties,
                'summary': {
                    'apartments': len([p for p in all_current_properties if 'apartament' in p['title'].lower()]),
                    'houses': len([p for p in all_current_properties if any(word in p['title'].lower() for word in ['къща', 'вила'])]),
                    'commercial': len([p for p in all_current_properties if any(word in p['title'].lower() for word in ['магазин', 'офис'])]),
                    'land': len([p for p in all_current_properties if 'парцел' in p['title'].lower()])
                }
            }

            os.makedirs('data', exist_ok=True)
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            # Print summary
            logging.info("=" * 60)
            logging.info("KRAIMORIE DAILY SUMMARY")
            logging.info("=" * 60)
            logging.info(f"Total current properties: {results['total_current_properties']}")
            logging.info(f"NEW properties today: {results['new_properties_today']}")
            logging.info(f"Argosdom properties: {results['argosdom_properties']}")
            logging.info(f"Breakdown: {results['apartments']} apartments, {results['houses']} houses, {results['commercial']} commercial, {results['land']} land")

            if new_properties:
                logging.info("\nNEW PROPERTIES TODAY:")
                logging.info("-" * 40)
                for i, prop in enumerate(new_properties, 1):
                    argosdom_flag = " [ARGOSDOM!]" if prop['is_argosdom'] else ""
                    logging.info(f"{i}. {prop['title'][:60]}...{argosdom_flag}")
                    logging.info(f"   Price: {prop['price']} | Location: {prop['location']}")
                    logging.info(f"   URL: {prop['url']}")
                    logging.info("")

            if argosdom_properties:
                logging.info("ARGOSDOM PROPERTIES (ALL):")
                logging.info("-" * 40)
                for i, prop in enumerate(argosdom_properties, 1):
                    logging.info(f"{i}. {prop['title'][:60]}...")
                    logging.info(f"   Price: {prop['price']} | Location: {prop['location']}")
                    logging.info(f"   URL: {prop['url']}")
                    logging.info("")

            return results

        except ImportError:
            logging.error("Required packages not available. Install beautifulsoup4 and requests.")
            return None

def main():
    setup_logging()

    tracker = KraimorieTracker()
    results = tracker.track_all_listings()

    if results:
        logging.info(f"Results saved to {tracker.results_file}")
    else:
        logging.error("Tracking failed")

if __name__ == "__main__":
    main()