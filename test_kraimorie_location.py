#!/usr/bin/env python3
"""
Test script to verify Kraimorie location ID
"""

import os
import sys
import requests
from bs4 import BeautifulSoup

def test_location_id(location_id):
    """Test if a location ID actually shows Kraimorie properties"""

    # Test both apartment and house URLs
    test_urls = [
        f"https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/?region_id=2&location_ids={location_id}",
        f"https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/?region_id=2&location_ids={location_id}"
    ]

    for url in test_urls:
        print(f"\n🔍 Testing: {url}")

        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check page title
            title = soup.find('title')
            print(f"📄 Page title: {title.get_text() if title else 'No title'}")

            # Look for properties
            properties = soup.find_all('div', class_='listtop-item')
            print(f"🏠 Found {len(properties)} properties")

            # Check first few property locations
            for i, prop in enumerate(properties[:5], 1):
                try:
                    # Get location from property
                    address_elem = prop.find('div', class_='listtop-item-address')
                    if address_elem:
                        location = address_elem.get_text(strip=True)
                        print(f"  Property {i}: {location}")

                    # Get title
                    title_elem = prop.find('h3', class_='listtop-item-title')
                    if title_elem:
                        title = title_elem.get_text(strip=True)[:50]
                        print(f"    Title: {title}...")

                except Exception as e:
                    print(f"  Property {i}: Error extracting info - {e}")

        except Exception as e:
            print(f"❌ Error testing {url}: {e}")

def main():
    """Test different location IDs"""
    print("🧪 Testing Kraimorie location IDs...")

    # Test the provided location ID
    print("\n" + "="*60)
    print("Testing location_ids=300 (provided)")
    test_location_id(300)

    # Test some other possible IDs around that number
    test_ids = [299, 301, 302, 4300]
    for test_id in test_ids:
        print("\n" + "="*60)
        print(f"Testing location_ids={test_id} (alternative)")
        test_location_id(test_id)

if __name__ == "__main__":
    main()