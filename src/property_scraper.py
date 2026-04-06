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

    def build_search_urls(self) -> List[str]:
        """Build search URLs for all configured locations and property types"""
        urls = []

        # Property type URLs
        property_types = {
            'apartments': "https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/",
            'houses': "https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/"
        }

        # Check which property types to search
        search_types = self.filters.get('search_property_types', ['apartments'])  # Default to apartments only

        # Get locations from new multi-location config
        locations = self.filters.get('locations', [])

        if not locations:
            # Fallback to old single location config
            old_location = self.filters.get('location', {})
            if old_location:
                locations = [{
                    'city': old_location.get('city', 'София'),
                    'region_id': 22,
                    'location_ids': 4342
                }]

        # Build URLs for each property type and location combination
        for prop_type in search_types:
            if prop_type not in property_types:
                continue

            base_url = property_types[prop_type]

            for location in locations:
                params = {
                    'region_id': location['region_id']
                }

                if location.get('location_ids'):
                    params['location_ids'] = location['location_ids']

                query_string = urlencode(params)
                url = f"{base_url}?{query_string}"
                search_label = f"{location['city']} - {prop_type}"
                urls.append((url, search_label))

        return urls if urls else [("https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/?region_id=22&location_ids=4342", "София - apartments")]

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
            'url': '',
            'lister': ''
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

            # Extract lister/agent from publisher section
            publisher_elem = property_element.find('div', class_='listtop-publisher')
            if publisher_elem:
                publisher_text = publisher_elem.get_text(strip=True)
                # Clean up the publisher name
                import re
                publisher_lines = publisher_text.split('\n')
                for line in publisher_lines:
                    line = line.strip()
                    if line and not re.match(r'^\d+\s*(ден|час|минут)', line):  # Skip time info
                        property_data['lister'] = line
                        break

            # Extract area and other details from the full text
            full_text = property_element.get_text()

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
            location = property_data.get('location', '').lower()
            full_text = f"{title} {location}".lower()
            lister = property_data.get('lister', '').lower()

            # Check exclude keywords
            exclude_keywords = self.filters.get('exclude_keywords', [])
            for keyword in exclude_keywords:
                if keyword.lower() in full_text:
                    logging.debug(f"Property excluded due to keyword: {keyword}")
                    return False

            # Check include keywords (if specified, at least one must be present)
            include_keywords = self.filters.get('include_keywords', [])
            if include_keywords:
                has_required_keyword = any(
                    keyword.lower() in full_text for keyword in include_keywords
                )
                if not has_required_keyword:
                    logging.debug(f"Property excluded: missing required keywords {include_keywords}")
                    return False

            # Check Kraimorie-specific keywords for Burgas properties
            kraimorie_keywords = self.filters.get('kraimorie_keywords', [])
            search_city = property_data.get('search_city', '')
            if 'бургас' in search_city.lower() and kraimorie_keywords:
                has_kraimorie = any(
                    keyword.lower() in full_text for keyword in kraimorie_keywords
                )
                if not has_kraimorie:
                    logging.debug("Burgas property excluded: not in Kraimorie")
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

            # Check preferred listers
            preferred_listers = self.filters.get('preferred_listers', [])
            if preferred_listers:
                has_preferred_lister = any(
                    preferred.lower() in lister for preferred in preferred_listers
                )
                if not has_preferred_lister:
                    logging.debug(f"Property excluded: lister not in preferred list")
                    return False

            # Check excluded listers
            excluded_listers = self.filters.get('excluded_listers', [])
            for excluded in excluded_listers:
                if excluded.lower() in lister:
                    logging.debug(f"Property excluded due to lister: {excluded}")
                    return False

            logging.debug("Property meets all criteria")
            return True

        except Exception as e:
            logging.error(f"Error checking criteria: {e}")
            return True

    def scrape_properties(self, max_pages: int = 3) -> List[Dict[str, str]]:
        """Main scraping method with multi-location and pagination support"""
        logging.info("Starting multi-location property scraping...")
        all_properties = []

        # Get all search URLs for different locations
        search_urls = self.build_search_urls()

        for url_info in search_urls:
            search_url, city_name = url_info
            logging.info(f"🏙️ Searching in {city_name}...")

            city_properties = []

            for page_num in range(1, max_pages + 1):
                # Add page parameter for pagination
                current_url = search_url
                if page_num > 1:
                    separator = '&' if '?' in search_url else '?'
                    current_url += f"{separator}p={page_num}"

                logging.info(f"Searching {city_name} page {page_num}: {current_url}")

                soup = self.fetch_page(current_url)
                if not soup:
                    logging.error(f"Failed to fetch {city_name} page {page_num}")
                    break

                # Save first page for analysis
                if page_num == 1 and city_name == search_urls[0][1]:  # First city, first page
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
                    logging.info(f"No properties found on {city_name} page {page_num}, stopping pagination for this city")
                    break

                logging.info(f"Found {len(property_elements)} property elements on {city_name} page {page_num}")

                page_properties = 0
                limit_per_page = 10 if page_num == 1 else 20

                for i, element in enumerate(property_elements[:limit_per_page]):
                    property_data = self.extract_property_info(element)

                    # Add city information to property data
                    property_data['search_city'] = city_name

                    # Debug for first page of first city only
                    if page_num == 1 and city_name == search_urls[0][1] and i < 3:
                        logging.info(f"{city_name} page {page_num}, Property {i+1} extracted data:")
                        for key, value in property_data.items():
                            logging.info(f"  {key}: '{value}'")
                        logging.info(f"  meets_criteria: {self.meets_criteria(property_data)}")
                        logging.info(f"  has_url: {bool(property_data['url'])}")
                        logging.info("---")

                    if property_data['url'] and self.meets_criteria(property_data):
                        city_properties.append(property_data)
                        page_properties += 1

                logging.info(f"Found {page_properties} matching properties on {city_name} page {page_num}")

                # Add small delay between pages
                if page_num < max_pages:
                    time.sleep(2)

            logging.info(f"🏙️ {city_name} total: {len(city_properties)} matching properties")
            all_properties.extend(city_properties)

            # Delay between cities
            if city_name != search_urls[-1][1]:  # Not the last city
                logging.info("⏸️ Pausing between cities...")
                time.sleep(3)

        logging.info(f"🎯 Grand total: Found {len(all_properties)} matching properties across all locations")
        return all_properties