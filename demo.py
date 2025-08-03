#!/usr/bin/env python3
"""
Demo script for WiFi Deauth Detector notification system.

This script demonstrates the notification functionality.
"""

import time
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.notification_manager import NotificationManager


def demo_notifications():
    """Demonstrate the notification system."""
    print("🚀 WiFi Deauth Detector Notification Demo")
    print("=" * 50)
    
    # Create notification manager
    notif_manager = NotificationManager(enabled=True)
    
    if not notif_manager.is_enabled():
        print("❌ Notifications are disabled (plyer not available)")
        return
    
    print("✅ Notification system initialized")
    print(f"📊 Currently enabled: {notif_manager.is_enabled()}")
    
    # Demo 1: Test basic notification
    print("\n📢 Demo 1: Sending test notification...")
    notif_manager.notify_new_attacker("AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66")
    time.sleep(2)
    
    # Demo 2: Duplicate attacker (should not send notification)
    print("📢 Demo 2: Sending duplicate attacker notification (should be ignored)...")
    notif_manager.notify_new_attacker("AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66")
    time.sleep(2)
    
    # Demo 3: New attacker
    print("📢 Demo 3: Sending new attacker notification...")
    notif_manager.notify_new_attacker("BB:CC:DD:EE:FF:00", "22:33:44:55:66:77")
    time.sleep(2)
    
    # Demo 4: Summary notification
    print("📢 Demo 4: Sending attack summary...")
    notif_manager.notify_attack_summary(5, 2)
    time.sleep(2)
    
    # Demo 5: Toggle notifications off
    print("📢 Demo 5: Disabling notifications...")
    notif_manager.set_enabled(False)
    notif_manager.notify_new_attacker("CC:DD:EE:FF:00:11", "33:44:55:66:77:88")
    print("   (No notification should appear)")
    time.sleep(2)
    
    # Demo 6: Re-enable and test
    print("📢 Demo 6: Re-enabling notifications...")
    notif_manager.set_enabled(True)
    notif_manager.notify_new_attacker("DD:EE:FF:00:11:22", "44:55:66:77:88:99")
    time.sleep(2)
    
    print(f"\n📊 Final statistics:")
    print(f"   Known attackers: {len(notif_manager.get_known_attackers())}")
    print(f"   Attacker MACs: {list(notif_manager.get_known_attackers())}")
    
    print("\n✅ Demo completed!")


def demo_gui():
    """Demonstrate the GUI with notification toggle."""
    print("🖥️  Starting GUI demo...")
    
    try:
        from src.gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ GUI demo failed: {e}")
        print("Make sure PyQt5 is installed: pip install PyQt5")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        demo_gui()
    else:
        demo_notifications()
        
        print("\n" + "="*50)
        print("💡 To test the GUI interface, run:")
        print("   python demo.py --gui")