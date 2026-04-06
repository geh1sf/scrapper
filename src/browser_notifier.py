import webbrowser
import os
from typing import List, Dict
import logging

class BrowserNotifier:
    def send_notification(self, properties: List[Dict[str, str]], html_file: str) -> bool:
        """Open browser with property results"""
        try:
            if not properties:
                return True

            # Make path absolute
            abs_path = os.path.abspath(html_file)
            file_url = f"file:///{abs_path.replace(os.sep, '/')}"

            # Open in default browser
            webbrowser.open(file_url)

            logging.info(f"Opened browser with {len(properties)} properties")
            print(f"🌐 Browser opened with {len(properties)} properties!")
            return True

        except Exception as e:
            logging.error(f"Browser notification failed: {e}")
            return False