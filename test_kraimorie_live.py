#!/usr/bin/env python3
"""
Test the actual Kraimorie URLs to see if there are properties
"""

import requests
from bs4 import BeautifulSoup

def test_kraimorie_urls():
    """Test both Kraimorie URLs for properties"""

    test_urls = [
        ("Apartments", "https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/?region_id=2&location_ids=300&section_ids=25"),
        ("Houses", "https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/?region_id=2&location_ids=300&section_ids=25")
    ]

    for property_type, url in test_urls:
        print(f"\n{'='*60}")
        print(f"🧪 Testing {property_type}: {url}")

        try:
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            print(f"📡 Response: {response.status_code}")

            soup = BeautifulSoup(response.content, 'html.parser')

            # Check page title
            title = soup.find('title')
            print(f"📄 Title: {title.get_text() if title else 'No title'}")

            # Look for properties
            properties = soup.find_all('div', class_='listtop-item')
            print(f"🏠 Properties found: {len(properties)}")

            # Check if it's an empty/error page
            if len(response.content) < 5000:
                print(f"⚠️ Very small page ({len(response.content)} bytes) - might be empty")

            # Look for specific Kraimorie or error messages
            page_text = soup.get_text().lower()
            if 'крайморие' in page_text:
                print(f"✅ 'крайморие' found in page text")
            else:
                print(f"❌ 'крайморие' NOT found in page text")

            if 'няма обяви' in page_text or 'no results' in page_text:
                print(f"📭 'No results' message found")

            # Show first few property titles if any
            if properties:
                print(f"\n📝 First {min(3, len(properties))} properties:")
                for i, prop in enumerate(properties[:3], 1):
                    try:
                        title_elem = prop.find('h3', class_='listtop-item-title')
                        if title_elem:
                            title = title_elem.get_text(strip=True)[:60]
                            print(f"  {i}. {title}...")

                        # Check for lister info
                        publisher = prop.find('div', class_='listtop-publisher')
                        if publisher:
                            lister = publisher.get_text(strip=True)[:30]
                            print(f"     Lister: {lister}...")
                            if 'argos' in lister.lower():
                                print(f"     ✅ ARGOSDOM FOUND!")

                    except Exception as e:
                        print(f"  {i}. Error parsing: {e}")
            else:
                print(f"📭 No properties found")

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_kraimorie_urls()