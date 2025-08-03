"""
Notification Manager for WiFi Deauth Detector

Handles system notifications for security alerts using plyer.
"""

import logging
from datetime import datetime
from typing import Set, Optional
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Warning: plyer not available. Using mock notifications.")
    try:
        from .mock_notification import create_mock_notification
        notification = create_mock_notification()
        PLYER_AVAILABLE = True  # Enable mock notifications
    except ImportError:
        # If we can't import the mock either, try relative import
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(__file__))
            from mock_notification import create_mock_notification
            notification = create_mock_notification()
            PLYER_AVAILABLE = True
        except ImportError:
            notification = None


class NotificationManager:
    """Manages system notifications for WiFi deauth detection events."""
    
    def __init__(self, enabled: bool = True):
        """
        Initialize the notification manager.
        
        Args:
            enabled: Whether notifications are enabled by default
        """
        self.enabled = enabled and PLYER_AVAILABLE
        self.known_attackers: Set[str] = set()
        self.logger = logging.getLogger(__name__)
        
        if not PLYER_AVAILABLE:
            self.logger.warning("Plyer not available - notifications disabled")
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable notifications."""
        self.enabled = enabled and PLYER_AVAILABLE
        self.logger.info(f"Notifications {'enabled' if self.enabled else 'disabled'}")
    
    def is_enabled(self) -> bool:
        """Check if notifications are enabled."""
        return self.enabled
    
    def notify_new_attacker(self, attacker_mac: str, target_mac: Optional[str] = None) -> None:
        """
        Send notification for a new attacker MAC address.
        
        Args:
            attacker_mac: MAC address of the detected attacker
            target_mac: MAC address of the target (optional)
        """
        if not self.enabled:
            return
            
        # Check if this is a new attacker
        if attacker_mac in self.known_attackers:
            return
            
        # Add to known attackers
        self.known_attackers.add(attacker_mac)
        
        # Create notification message
        title = "🚨 WiFi Deauth Attack Detected!"
        message = f"New attacker detected: {attacker_mac}"
        if target_mac:
            message += f"\nTarget: {target_mac}"
        message += f"\nTime: {datetime.now().strftime('%H:%M:%S')}"
        
        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=None,  # Could add icon path here
                timeout=10  # Show for 10 seconds
            )
            self.logger.info(f"Notification sent for new attacker: {attacker_mac}")
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            # Fallback to console notification for testing
            print(f"\n┌─ NOTIFICATION ({'─' * 40})")
            print(f"│ 📢 {title}")
            print(f"│ {message}")
            print(f"└{'─' * 50}")
    
    def notify_attack_summary(self, attack_count: int, unique_attackers: int) -> None:
        """
        Send a summary notification of detected attacks.
        
        Args:
            attack_count: Total number of attacks detected
            unique_attackers: Number of unique attacker MACs
        """
        if not self.enabled:
            return
            
        title = "📊 Attack Summary"
        message = f"Detected {attack_count} attacks from {unique_attackers} unique sources"
        
        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=None,
                timeout=8
            )
            self.logger.info("Attack summary notification sent")
        except Exception as e:
            self.logger.error(f"Failed to send summary notification: {e}")
            # Fallback to console notification for testing
            print(f"\n┌─ NOTIFICATION ({'─' * 40})")
            print(f"│ 📢 {title}")
            print(f"│ {message}")
            print(f"└{'─' * 50}")
    
    def clear_known_attackers(self) -> None:
        """Clear the list of known attackers."""
        self.known_attackers.clear()
        self.logger.info("Cleared known attackers list")
    
    def get_known_attackers(self) -> Set[str]:
        """Get the set of known attacker MAC addresses."""
        return self.known_attackers.copy()