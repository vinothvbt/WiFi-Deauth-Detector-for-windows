"""
Mock notification system for testing when actual notifications aren't available.
"""

from typing import Dict, Any
from datetime import datetime


class MockNotification:
    """Mock notification class for testing."""
    
    @staticmethod
    def notify(title: str, message: str, app_icon: str = None, timeout: int = 10) -> None:
        """Mock notification function that prints to console."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n┌─ NOTIFICATION [{timestamp}] {'─' * 40}")
        print(f"│ 📢 {title}")
        print(f"│ {message}")
        print(f"│ (Timeout: {timeout}s)")
        print(f"└{'─' * 50}")


def create_mock_notification():
    """Create a mock notification object for testing."""
    return MockNotification()