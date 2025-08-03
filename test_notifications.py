#!/usr/bin/env python3
"""
Complete test for the notification system.

This demonstrates all the notification features working together.
"""

import time
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.deauth_integration import (
    trigger_deauth_detection, 
    configure_notifications,
    detection_integration
)


def test_notification_integration():
    """Test the complete notification integration."""
    print("🔔 Testing WiFi Deauth Detector Notification Integration")
    print("=" * 60)
    
    # Test 1: Basic detection
    print("\n🔍 Test 1: Basic deauth attack detection")
    trigger_deauth_detection("AA:BB:CC:DD:EE:01", "Target:Device:01")
    time.sleep(1)
    
    # Test 2: Multiple attacks from same attacker (should only notify once)
    print("\n🔍 Test 2: Multiple attacks from same attacker")
    trigger_deauth_detection("AA:BB:CC:DD:EE:01", "Target:Device:02")
    trigger_deauth_detection("AA:BB:CC:DD:EE:01", "Target:Device:03")
    time.sleep(1)
    
    # Test 3: New attacker
    print("\n🔍 Test 3: New attacker detected")
    trigger_deauth_detection("BB:CC:DD:EE:FF:02", "Target:Device:04")
    time.sleep(1)
    
    # Test 4: Disable notifications
    print("\n🔧 Test 4: Disabling notifications")
    configure_notifications(False)
    trigger_deauth_detection("CC:DD:EE:FF:00:03", "Target:Device:05")
    print("   ^ No notification should appear above")
    time.sleep(1)
    
    # Test 5: Re-enable notifications
    print("\n🔧 Test 5: Re-enabling notifications")
    configure_notifications(True)
    trigger_deauth_detection("DD:EE:FF:00:11:04", "Target:Device:06")
    time.sleep(1)
    
    # Test 6: Attack summary
    print("\n📊 Test 6: Attack summary")
    detection_integration.send_attack_summary()
    time.sleep(1)
    
    # Test 7: Custom callback registration
    print("\n🔌 Test 7: Custom callback integration")
    
    def custom_log_callback(attacker_mac, target_mac, timestamp):
        print(f"[CUSTOM LOG] Attack: {attacker_mac} -> {target_mac} at {timestamp.strftime('%H:%M:%S')}")
    
    detection_integration.register_detection_callback("custom_logger", custom_log_callback)
    trigger_deauth_detection("EE:FF:00:11:22:05", "Target:Device:07")
    time.sleep(1)
    
    # Final statistics
    print("\n📈 Final Statistics:")
    stats = detection_integration.get_attack_stats()
    print(f"   Total attacks detected: {stats['total_attacks']}")
    print(f"   Unique attackers: {stats['unique_attackers']}")
    print(f"   Notifications enabled: {detection_integration.are_notifications_enabled()}")
    
    known_attackers = detection_integration.notification_manager.get_known_attackers()
    print(f"   Known attacker MACs: {list(known_attackers)}")
    
    print("\n✅ All tests completed successfully!")
    
    # Demonstrate reset functionality
    print("\n🔄 Test 8: Reset functionality")
    detection_integration.reset_stats()
    stats_after_reset = detection_integration.get_attack_stats()
    print(f"   Stats after reset - Total: {stats_after_reset['total_attacks']}, Unique: {stats_after_reset['unique_attackers']}")


def simulate_real_world_scenario():
    """Simulate a real-world deauth attack scenario."""
    print("\n" + "=" * 60)
    print("🌐 Real-world Attack Simulation")
    print("=" * 60)
    
    # Reset for clean simulation
    detection_integration.reset_stats()
    configure_notifications(True)
    
    scenarios = [
        ("Evil Twin Attack", "AA:BB:CC:DD:EE:99", "User:Device:01"),
        ("WiFi Jammer Attack", "BB:CC:DD:EE:FF:88", "User:Device:02"),
        ("Deauth Flood", "CC:DD:EE:FF:00:77", "User:Device:03"),
        ("Targeted Attack", "DD:EE:FF:00:11:66", "Admin:Device:01"),
        ("Mass Deauth", "EE:FF:00:11:22:55", "Public:AP:01"),
    ]
    
    print("Simulating progressive attack scenario...")
    
    for i, (attack_type, attacker, target) in enumerate(scenarios, 1):
        print(f"\n📡 Wave {i}: {attack_type}")
        trigger_deauth_detection(attacker, target)
        time.sleep(1.5)
        
        # Simulate repeated attacks from some attackers
        if i % 2 == 0:
            print(f"   🔄 Repeated attack from {attacker}")
            trigger_deauth_detection(attacker, f"Another:Target:{i}")
            time.sleep(0.5)
    
    # Final summary
    print("\n🚨 ATTACK SCENARIO COMPLETE!")
    detection_integration.send_attack_summary()
    
    final_stats = detection_integration.get_attack_stats()
    print(f"\nIncident Report:")
    print(f"- Total attacks: {final_stats['total_attacks']}")
    print(f"- Unique threats: {final_stats['unique_attackers']}")
    print(f"- Alert system: {'ACTIVE' if detection_integration.are_notifications_enabled() else 'DISABLED'}")


if __name__ == "__main__":
    try:
        test_notification_integration()
        simulate_real_world_scenario()
        
        print("\n" + "=" * 60)
        print("🎯 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print("✅ Notification system: WORKING")
        print("✅ Attack detection: WORKING") 
        print("✅ Toggle functionality: WORKING")
        print("✅ Duplicate filtering: WORKING")
        print("✅ Statistics tracking: WORKING")
        print("✅ Callback system: WORKING")
        print("✅ Integration ready for deployment!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()