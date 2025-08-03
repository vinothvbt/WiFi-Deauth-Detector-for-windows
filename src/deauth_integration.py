"""
Deauth Attack Detection Integration

This module provides integration points for other components to trigger notifications
when deauth attacks are detected.
"""

import logging
from typing import Dict, Optional, Callable
from datetime import datetime
from src.notification_manager import NotificationManager


class DeauthDetectionIntegration:
    """Integration layer for deauth attack detection and notifications."""
    
    def __init__(self, enable_notifications: bool = True):
        """
        Initialize the detection integration.
        
        Args:
            enable_notifications: Whether to enable notifications by default
        """
        self.notification_manager = NotificationManager(enabled=enable_notifications)
        self.attack_count = 0
        self.detection_callbacks: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
        
    def register_detection_callback(self, name: str, callback: Callable) -> None:
        """
        Register a callback to be called when an attack is detected.
        
        Args:
            name: Name of the callback for identification
            callback: Function to call with (attacker_mac, target_mac, timestamp)
        """
        self.detection_callbacks[name] = callback
        self.logger.info(f"Registered detection callback: {name}")
    
    def unregister_detection_callback(self, name: str) -> None:
        """Unregister a detection callback."""
        if name in self.detection_callbacks:
            del self.detection_callbacks[name]
            self.logger.info(f"Unregistered detection callback: {name}")
    
    def on_deauth_detected(self, attacker_mac: str, target_mac: Optional[str] = None, 
                          timestamp: Optional[datetime] = None) -> None:
        """
        Handle a detected deauth attack.
        
        This is the main integration point that should be called by
        the packet detection logic when a deauth attack is found.
        
        Args:
            attacker_mac: MAC address of the attacking device
            target_mac: MAC address of the target device (optional)
            timestamp: When the attack was detected (optional, defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        self.attack_count += 1
        
        # Send notification for new attackers
        self.notification_manager.notify_new_attacker(attacker_mac, target_mac)
        
        # Log the attack
        self.logger.info(f"Deauth attack detected: {attacker_mac} -> {target_mac} at {timestamp}")
        
        # Call registered callbacks
        for name, callback in self.detection_callbacks.items():
            try:
                callback(attacker_mac, target_mac, timestamp)
            except Exception as e:
                self.logger.error(f"Error in detection callback '{name}': {e}")
    
    def set_notifications_enabled(self, enabled: bool) -> None:
        """Enable or disable notifications."""
        self.notification_manager.set_enabled(enabled)
        
    def are_notifications_enabled(self) -> bool:
        """Check if notifications are enabled."""
        return self.notification_manager.is_enabled()
    
    def get_attack_stats(self) -> Dict[str, int]:
        """Get attack statistics."""
        return {
            'total_attacks': self.attack_count,
            'unique_attackers': len(self.notification_manager.get_known_attackers())
        }
    
    def send_attack_summary(self) -> None:
        """Send a summary notification of detected attacks."""
        stats = self.get_attack_stats()
        self.notification_manager.notify_attack_summary(
            stats['total_attacks'], 
            stats['unique_attackers']
        )
    
    def reset_stats(self) -> None:
        """Reset attack statistics and known attackers."""
        self.attack_count = 0
        self.notification_manager.clear_known_attackers()
        self.logger.info("Reset attack statistics")


# Global instance for easy access
detection_integration = DeauthDetectionIntegration()


def trigger_deauth_detection(attacker_mac: str, target_mac: Optional[str] = None) -> None:
    """
    Convenience function to trigger deauth detection.
    
    This can be called from packet capture logic when deauth frames are detected.
    
    Args:
        attacker_mac: MAC address of the attacking device  
        target_mac: MAC address of the target device (optional)
    """
    detection_integration.on_deauth_detected(attacker_mac, target_mac)


def configure_notifications(enabled: bool) -> None:
    """
    Convenience function to configure notifications.
    
    Args:
        enabled: Whether to enable notifications
    """
    detection_integration.set_notifications_enabled(enabled)