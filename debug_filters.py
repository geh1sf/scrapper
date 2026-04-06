#!/usr/bin/env python3
"""
Debug script to test filtering logic
"""

import os
import sys
sys.path.append('src')

from property_scraper import AloPropertyScraper
import yaml

def debug_single_property():
    """Test filtering on a single property manually"""

    # Load config
    with open('config/filters.yaml', 'r', encoding='utf-8') as f:
        filters = yaml.safe_load(f)

    print("🔍 Current filters:")
    for key, value in filters.items():
        print(f"  {key}: {value}")

    # Create test property that should FAIL criteria
    test_property_bad = {
        'title': 'Тристаен апартамент в София centrum',  # Wrong location
        'price': '200 000 €',
        'location': 'Център, София',  # Not Burgas/Kraimorie
        'area': '85 кв.м',
        'floor': '5 ет',  # Too high (>2)
        'url': 'https://test.com',
        'lister': 'Test Agency',
        'search_city': 'София - apartments'
    }

    # Create test property that should PASS criteria
    test_property_good = {
        'title': 'Двустаен апартамент в Крайморие',
        'price': '150 000 €',
        'location': 'Крайморие, Бургас',  # Correct location
        'area': '65 кв.м',
        'floor': '1 ет',  # Good floor
        'url': 'https://test.com',
        'lister': 'Test Agency',
        'search_city': 'Бургас - apartments'
    }

    scraper = AloPropertyScraper('config/filters.yaml')

    print("\n" + "="*60)
    print("Testing BAD property (should be REJECTED):")
    print_property_debug(test_property_bad, scraper)

    print("\n" + "="*60)
    print("Testing GOOD property (should be ACCEPTED):")
    print_property_debug(test_property_good, scraper)

def print_property_debug(property_data, scraper):
    """Print detailed debug info for a property"""

    print("\n📋 Property Details:")
    for key, value in property_data.items():
        print(f"  {key}: '{value}'")

    print(f"\n✅/❌ Filter Results:")

    # Test each filter manually
    title = property_data.get('title', '').lower()
    location = property_data.get('location', '').lower()
    full_text = f"{title} {location}".lower()

    # Check Kraimorie keywords
    kraimorie_keywords = scraper.filters.get('kraimorie_keywords', [])
    search_city = property_data.get('search_city', '')

    print(f"  Search city: '{search_city}'")
    print(f"  Is Burgas search: {'бургас' in search_city.lower()}")
    print(f"  Kraimorie keywords: {kraimorie_keywords}")

    if 'бургас' in search_city.lower() and kraimorie_keywords:
        has_kraimorie = any(keyword.lower() in full_text for keyword in kraimorie_keywords)
        print(f"  Has Kraimorie keyword: {has_kraimorie}")
        print(f"  Full text to search: '{full_text}'")
        for keyword in kraimorie_keywords:
            in_text = keyword.lower() in full_text
            print(f"    '{keyword}' in text: {in_text}")

    # Check floor
    max_floor = scraper.filters.get('features', {}).get('max_floor')
    floor_text = property_data.get('floor', '')
    print(f"  Max floor allowed: {max_floor}")
    print(f"  Property floor text: '{floor_text}'")

    import re
    floor_match = re.search(r'(\d+)', floor_text)
    if floor_match:
        floor_num = int(floor_match.group(1))
        print(f"  Extracted floor number: {floor_num}")
        print(f"  Floor within limit: {floor_num <= max_floor if max_floor else 'No limit'}")

    # Check property type
    property_types = scraper.filters.get('property_type', [])
    print(f"  Allowed property types: {property_types}")
    if property_types:
        has_matching_type = any(prop_type.lower() in title for prop_type in property_types)
        print(f"  Has matching type: {has_matching_type}")
        for prop_type in property_types:
            in_title = prop_type.lower() in title
            print(f"    '{prop_type}' in title: {in_title}")

    # Final result
    result = scraper.meets_criteria(property_data)
    print(f"\n🎯 FINAL RESULT: {'✅ PASS' if result else '❌ FAIL'}")

if __name__ == "__main__":
    debug_single_property()