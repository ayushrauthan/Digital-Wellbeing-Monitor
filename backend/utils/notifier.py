# backend/utils/notifier.py
from plyer import notification

class NotificationManager:
    """Handles sending desktop notifications."""

    def send_notification(self, title, message):
        """
        Sends a desktop notification.

        Args:
            title (str): The title of the notification.
            message (str): The body/message of the notification.
        """
        try:
            notification.notify(
                title=title,
                message=message,
                app_name='WellnessWatch',
                timeout=10  # Notification will disappear after 10 seconds
            )
            print(f"Sent notification: '{title}'")
        except Exception as e:
            print(f"Error sending notification: {e}")