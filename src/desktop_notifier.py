import os
import subprocess
from typing import List, Dict
import logging

class DesktopNotifier:
    def send_notification(self, properties: List[Dict[str, str]]) -> bool:
        """Send Windows desktop notification"""
        try:
            if not properties:
                return True

            count = len(properties)
            title = f"🏠 Found {count} New Properties!"

            # Get first property as preview
            first_prop = properties[0]
            message = f"{first_prop['title']}\n💰 {first_prop['price']}\n📍 {first_prop['location']}"

            if count > 1:
                message += f"\n\n...and {count-1} more properties"

            # Use Windows toast notification
            powershell_cmd = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
            $template = [Windows.UI.Notifications.ToastTemplateType]::ToastText02
            $toastXml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($template)
            $toastXml.SelectSingleNode("//text[@id='1']").InnerText = "{title}"
            $toastXml.SelectSingleNode("//text[@id='2']").InnerText = "{message.replace('"', "'")}"
            $toast = [Windows.UI.Notifications.ToastNotification]::new($toastXml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Property Scraper").Show($toast)
            '''

            subprocess.run(["powershell", "-Command", powershell_cmd],
                         capture_output=True, text=True)

            logging.info(f"Desktop notification sent for {count} properties")
            print(f"🔔 Desktop notification sent: {count} properties found!")
            return True

        except Exception as e:
            logging.error(f"Desktop notification failed: {e}")
            return False