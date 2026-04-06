import os
import requests
from bs4 import BeautifulSoup
import yaml
import json
import time
import logging
from datetime import datetime
from urllib.parse import urljoin, urlencode
from typing import List, Dict, Any

class AloPropertyScraper:
    def __init__(self, filters_config_path: str):
        """Initialize the scraper with configuration"""
        self.base_url = "https://www.alo.bg"
        self.search_url = "https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/"
        self.session = requests.Session()

        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'bg-BG,bg;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })

        self.filters = self.load_filters(filters_config_path)
        self.setup_logging()

    def load_filters(self, config_path: str) -> Dict[str, Any]:
        """Load filter configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Error loading filters: {e}")
            return {}

    def setup_logging(self):
        """Setup logging configuration"""
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/scraper.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    def build_search_url(self) -> str:
        """Build search URL with filters"""
        base_url = "https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/"

        params = {}

        # Location mapping - major Bulgarian cities with region_id and location_ids
        location_map = {
            "софия": {"region_id": 22, "location_ids": 4342},  # Sofia city
            "пловдив": {"region_id": 15, "location_ids": None},  # Plovdiv (need to find location_ids)
            "варна": {"region_id": 3, "location_ids": None},   # Varna (need to find location_ids)
            "бургас": {"region_id": 2, "location_ids": None},   # Burgas (need to find location_ids)
        }

        # Get location from filters
        location = self.filters.get('location', {}).get('city', "").lower()
        if location in location_map:
            params['region_id'] = location_map[location]['region_id']
            if location_map[location]['location_ids']:
                params['location_ids'] = location_map[location]['location_ids']
        else:
            # Default to Sofia if no location specified
            params['region_id'] = 22
            params['location_ids'] = 4342

        # Build URL with parameters
        if params:
            query_string = urlencode(params)
            return f"{base_url}?{query_string}"
        else:
            return base_url

    def fetch_page(self, url: str, max_retries: int = 3) -> BeautifulSoup:
        """Fetch a page and return parsed HTML with retry logic"""
        for attempt in range(max_retries):
            try:
                logging.info(f"Fetching {url} (attempt {attempt + 1}/{max_retries})")

                # Add delay between requests to be respectful
                if attempt > 0:
                    time.sleep(2 * attempt)  # Increasing delay: 2, 4 seconds

                response = self.session.get(url, timeout=30)  # Increased timeout
                response.raise_for_status()

                # Check if we got a valid response
                if len(response.content) < 1000:
                    logging.warning(f"Response too small ({len(response.content)} bytes), might be blocked")
                    if attempt < max_retries - 1:
                        continue

                logging.info(f"Successfully fetched page ({len(response.content)} bytes)")
                return BeautifulSoup(response.content, 'html.parser')

            except requests.exceptions.Timeout:
                logging.warning(f"Timeout on attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    logging.error(f"Final timeout fetching {url}")

            except requests.exceptions.RequestException as e:
                logging.warning(f"Request error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    logging.error(f"Final error fetching {url}: {e}")

            except Exception as e:
                logging.error(f"Unexpected error fetching {url}: {e}")
                break

        return None

    def extract_property_info(self, property_element) -> Dict[str, str]:
        """Extract property information from a listing element"""
        property_data = {
            'title': '',
            'price': '',
            'location': '',
            'area': '',
            'floor': '',
            'url': ''
        }

        try:
            # Extract title from h3.listtop-item-title
            title_elem = property_element.find('h3', class_='listtop-item-title')
            if title_elem:
                property_data['title'] = title_elem.get_text(strip=True)

            # Extract URL from the title link
            title_link = property_element.find('a', href=True)
            if title_link:
                property_data['url'] = urljoin(self.base_url, title_link['href'])

            # Extract location from listtop-item-address
            address_elem = property_element.find('div', class_='listtop-item-address')
            if address_elem:
                property_data['location'] = address_elem.get_text(strip=True)

            # Extract price from the price section
            price_spans = property_element.find_all('span', style=lambda value: value and 'white-space: nowrap' in value)
            for span in price_spans:
                text = span.get_text(strip=True)
                if '€' in text and any(c.isdigit() for c in text):
                    property_data['price'] = text
                    break

            # Extract area and other details from the full text
            full_text = property_element.get_text()
            import re

            # Extract area
            area_pattern = r'(\d+(?:\.\d+)?)\s*кв\.?м'
            area_match = re.search(area_pattern, full_text, re.IGNORECASE)
            if area_match:
                property_data['area'] = f"{area_match.group(1)} кв.м"

            # Extract floor
            floor_pattern = r'(\d+)\s*ет(?:аж)?'
            floor_match = re.search(floor_pattern, full_text, re.IGNORECASE)
            if floor_match:
                property_data['floor'] = f"{floor_match.group(1)} ет"

        except Exception as e:
            logging.error(f"Error extracting property info: {e}")

        return property_data

    def meets_criteria(self, property_data: Dict[str, str]) -> bool:
        """Check if property meets the specified criteria"""
        try:
            title = property_data.get('title', '').lower()

            # Check exclude keywords
            exclude_keywords = self.filters.get('exclude_keywords', [])
            for keyword in exclude_keywords:
                if keyword.lower() in title:
                    logging.debug(f"Property excluded due to keyword: {keyword}")
                    return False

            # Check include keywords (if specified, at least one must be present)
            include_keywords = self.filters.get('include_keywords', [])
            if include_keywords:
                has_required_keyword = any(
                    keyword.lower() in title for keyword in include_keywords
                )
                if not has_required_keyword:
                    logging.debug(f"Property excluded: missing required keywords {include_keywords}")
                    return False

            # Check property type
            property_types = self.filters.get('property_type', [])
            if property_types:
                has_matching_type = any(
                    prop_type.lower() in title for prop_type in property_types
                )
                if not has_matching_type:
                    logging.debug(f"Property excluded: type not in {property_types}")
                    return False

            logging.debug("Property meets all criteria")
            return True

        except Exception as e:
            logging.error(f"Error checking criteria: {e}")
            return True

    def scrape_properties(self, max_pages: int = 3) -> List[Dict[str, str]]:
        """Main scraping method with pagination support"""
        logging.info("Starting property scraping...")
        properties = []

        for page_num in range(1, max_pages + 1):
            # Build URL for current page
            search_url = self.build_search_url()
            if page_num > 1:
                # Add page parameter
                separator = '&' if '?' in search_url else '?'
                search_url += f"{separator}p={page_num}"

            logging.info(f"Searching page {page_num}: {search_url}")

            soup = self.fetch_page(search_url)
            if not soup:
                logging.error(f"Failed to fetch page {page_num}")
                break

            # Save first page for analysis
            if page_num == 1:
                with open('logs/sample_page.html', 'w', encoding='utf-8') as f:
                    f.write(str(soup.prettify()))
                logging.info("Saved sample page for analysis")

                # Debug: Print page title
                title = soup.find('title')
                logging.info(f"Page title: {title.get_text() if title else 'No title'}")

            # Look for property listings
            property_elements = soup.find_all('div', class_='listtop-item')

            if not property_elements:
                property_elements = soup.find_all('div', {'class': lambda x: x and 'listtop-item' in x})

            if not property_elements:
                logging.info(f"No properties found on page {page_num}, stopping pagination")
                break

            logging.info(f"Found {len(property_elements)} property elements on page {page_num}")

            page_properties = 0
            limit_per_page = 10 if page_num == 1 else 20  # First page: 10 for debugging, others: 20

            for i, element in enumerate(property_elements[:limit_per_page]):
                property_data = self.extract_property_info(element)

                # Debug for first page only
                if page_num == 1 and i < 3:
                    logging.info(f"Page {page_num}, Property {i+1} extracted data:")
                    for key, value in property_data.items():
                        logging.info(f"  {key}: '{value}'")
                    logging.info(f"  meets_criteria: {self.meets_criteria(property_data)}")
                    logging.info(f"  has_url: {bool(property_data['url'])}")
                    logging.info("---")

                if property_data['url'] and self.meets_criteria(property_data):
                    properties.append(property_data)
                    page_properties += 1

            logging.info(f"Found {page_properties} matching properties on page {page_num}")

            # Add small delay between pages to be respectful
            if page_num < max_pages:
                time.sleep(2)

        logging.info(f"Total: Found {len(properties)} matching properties across {min(page_num, max_pages)} pages")
        return properties