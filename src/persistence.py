import json
import os
from typing import Set, List, Dict
from datetime import datetime, timedelta
import logging

class PropertyTracker:
    def __init__(self, data_file: str = "data/seen_properties.json"):
        """Initialize property tracker with persistent storage"""
        self.data_file = data_file
        self.ensure_data_directory()
        self.seen_properties = self.load_seen_properties()

    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

    def load_seen_properties(self) -> Dict[str, Dict]:
        """Load previously seen properties from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Error loading seen properties: {e}")
            return {}

    def save_seen_properties(self):
        """Save seen properties to file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.seen_properties, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Error saving seen properties: {e}")

    def generate_property_id(self, property_data: Dict[str, str]) -> str:
        """Generate unique ID for property based on URL or other unique attributes"""
        # Use URL as primary identifier, fallback to title + price
        if property_data.get('url'):
            return property_data['url']
        else:
            # Fallback ID generation
            title = property_data.get('title', '')
            price = property_data.get('price', '')
            location = property_data.get('location', '')
            return f"{title}_{price}_{location}".replace(' ', '_')

    def is_property_new(self, property_data: Dict[str, str]) -> bool:
        """Check if property is new (not seen before)"""
        property_id = self.generate_property_id(property_data)
        return property_id not in self.seen_properties

    def mark_property_as_seen(self, property_data: Dict[str, str]):
        """Mark property as seen with timestamp"""
        property_id = self.generate_property_id(property_data)
        self.seen_properties[property_id] = {
            'first_seen': datetime.now().isoformat(),
            'title': property_data.get('title', ''),
            'price': property_data.get('price', ''),
            'url': property_data.get('url', '')
        }

    def filter_new_properties(self, properties: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Filter out properties that have been seen before"""
        new_properties = []

        for prop in properties:
            if self.is_property_new(prop):
                new_properties.append(prop)
                self.mark_property_as_seen(prop)

        if new_properties:
            self.save_seen_properties()

        logging.info(f"Found {len(new_properties)} new properties out of {len(properties)} total")
        return new_properties

    def cleanup_old_entries(self, days_to_keep: int = 30):
        """Remove entries older than specified days to prevent file from growing too large"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # Filter out old entries
            cleaned_properties = {}
            for prop_id, data in self.seen_properties.items():
                try:
                    first_seen = datetime.fromisoformat(data['first_seen'])
                    if first_seen >= cutoff_date:
                        cleaned_properties[prop_id] = data
                except (KeyError, ValueError):
                    # Keep entries with invalid dates for safety
                    cleaned_properties[prop_id] = data

            removed_count = len(self.seen_properties) - len(cleaned_properties)
            self.seen_properties = cleaned_properties

            if removed_count > 0:
                self.save_seen_properties()
                logging.info(f"Cleaned up {removed_count} old property entries")

        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about tracked properties"""
        return {
            'total_properties_seen': len(self.seen_properties),
            'properties_today': len([
                p for p in self.seen_properties.values()
                if datetime.fromisoformat(p['first_seen']).date() == datetime.now().date()
            ])
        }