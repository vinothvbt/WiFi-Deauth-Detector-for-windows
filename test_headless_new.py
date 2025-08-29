#!/usr/bin/env python3
"""
Headless test for WiFi Deauth Detector
Tests the core functionality without GUI
"""

import sys
import os
import time
import threading
from datetime import datetime

# Add the main directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from windows_wifi_monitor import WindowsWiFiMonitor, LegacyDeauthDetector
from main import SettingsManager, NetworkManager, DiscordWebhook

def test_windows_monitor():
    """Test the Windows WiFi monitor"""
    print("🔍 Testing Windows WiFi Monitor...")
    
    monitor = WindowsWiFiMonitor()
    
    # Test status checking
    status = monitor._get_wifi_status()
    print(f"📡 Current WiFi Status: {status}")
    
    # Test interface detection
    interfaces = monitor.get_network_interfaces()
    print(f"🔌 Network Interfaces: {len(interfaces)} found")
    for interface in interfaces:
        print(f"   - {interface['name']}: {'UP' if interface['is_up'] else 'DOWN'}")
    
    return True

def test_legacy_detector():
    """Test the legacy detector for demo purposes"""
    print("🎭 Testing Legacy Detector (Demo Mode)...")
    
    detector = LegacyDeauthDetector()
    events_received = []
    
    def handle_attack(attacker, target, timestamp):
        events_received.append((attacker, target, timestamp))
        print(f"📨 Demo Attack: {attacker} -> {target} at {timestamp}")
    
    detector.attack_detected.connect(handle_attack)
    
    # Start monitoring briefly
    detector.start_monitoring()
    print("⏳ Monitoring for 15 seconds...")
    time.sleep(15)
    detector.stop_monitoring()
    
    print(f"✅ Detected {len(events_received)} demo events")
    return len(events_received) > 0

def test_network_manager():
    """Test network management functionality"""
    print("🌐 Testing Network Manager...")
    
    manager = NetworkManager()
    profiles = manager.get_available_profiles()
    
    print(f"📋 Available WiFi Profiles: {len(profiles)}")
    for profile in profiles[:5]:  # Show first 5
        print(f"   - {profile}")
    
    return True

def test_settings_manager():
    """Test settings management"""
    print("⚙️ Testing Settings Manager...")
    
    settings = SettingsManager("test_settings.json")
    
    # Test default settings
    print(f"🔧 Demo mode: {settings.get('demo_mode')}")
    print(f"🔔 Notifications: {settings.get('notifications_enabled')}")
    print(f"📝 Logging: {settings.get('log_attacks')}")
    
    # Test saving settings
    settings.set("demo_mode", True)
    success = settings.save_settings()
    print(f"💾 Settings save: {'✅' if success else '❌'}")
    
    # Clean up
    if os.path.exists("test_settings.json"):
        os.remove("test_settings.json")
    
    return success

def main():
    """Run all headless tests"""
    print("🚀 WiFi Deauth Detector - Headless Test Suite")
    print("=" * 50)
    
    tests = [
        ("Settings Manager", test_settings_manager),
        ("Network Manager", test_network_manager),
        ("Windows WiFi Monitor", test_windows_monitor),
        ("Legacy Detector", test_legacy_detector),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{'✅' if result else '❌'} {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print(f"\n📊 Test Results Summary:")
    print("=" * 30)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        print(f"{'✅' if result else '❌'} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready.")
    else:
        print("⚠️ Some tests failed. Check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)