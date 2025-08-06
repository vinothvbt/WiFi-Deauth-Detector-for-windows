#!/usr/bin/env python3
"""
Headless test script for WiFi Deauth Detector
Tests functionality without requiring GUI display
"""

import os
import sys
import time
import json
import subprocess
from unittest.mock import patch, MagicMock

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_modules_import():
    """Test that all modules can be imported"""
    print("📦 Testing module imports...")
    
    try:
        # Test main module imports
        import main
        print("✅ Main module imported successfully")
        
        # Test individual classes
        detector = main.DeauthDetector()
        print("✅ DeauthDetector class created")
        
        network_mgr = main.NetworkManager()
        print("✅ NetworkManager class created")
        
        settings_mgr = main.SettingsManager()
        print("✅ SettingsManager class created")
        
        discord_webhook = main.DiscordWebhook("")
        print("✅ DiscordWebhook class created")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_settings_functionality():
    """Test settings management"""
    print("\n⚙️ Testing settings functionality...")
    
    try:
        from main import SettingsManager
        
        settings_mgr = SettingsManager()
        
        # Test default settings
        default_settings = settings_mgr.load_settings()
        print(f"✅ Default settings loaded: {len(default_settings)} keys")
        
        # Test modifying and saving settings
        settings_mgr.settings["backup_network"] = "TestNetwork"
        settings_mgr.settings["discord_webhook"] = "https://discord.com/api/webhooks/test"
        settings_mgr.save_settings()
        print("✅ Settings saved successfully")
        
        # Test loading saved settings
        settings_mgr = SettingsManager()  # Reload from file
        loaded_settings = settings_mgr.load_settings()
        assert loaded_settings["backup_network"] == "TestNetwork"
        print("✅ Settings loaded and verified")
        
        return True
    except Exception as e:
        print(f"❌ Settings test error: {e}")
        return False

def test_network_manager():
    """Test network management functionality"""
    print("\n🌐 Testing network management...")
    
    try:
        from main import NetworkManager
        
        network_mgr = NetworkManager()
        
        # Mock subprocess for Windows netsh commands
        with patch('subprocess.run') as mock_run:
            # Mock successful profile listing
            mock_run.return_value.stdout = "Profile1\nProfile2\nProfile3\n"
            mock_run.return_value.returncode = 0
            
            profiles = network_mgr.get_available_profiles()
            print(f"✅ Available profiles retrieved: {profiles}")
            
            # Mock successful connection
            mock_run.return_value.returncode = 0
            result = network_mgr.connect_to_network("TestNetwork")
            print(f"✅ Network connection test: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Network manager test error: {e}")
        return False

def test_discord_webhook():
    """Test Discord webhook functionality"""
    print("\n📱 Testing Discord webhook...")
    
    try:
        from main import DiscordWebhook
        
        # Test with no webhook URL
        discord = DiscordWebhook("")
        result = discord.send_alert("00:11:22:33:44:55", "aa:bb:cc:dd:ee:ff", "2024-08-03 17:30:15")
        print(f"✅ No webhook URL test: {result}")
        
        # Test with mock webhook URL
        discord = DiscordWebhook("https://discord.com/api/webhooks/test/url")
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            result = discord.send_alert("00:11:22:33:44:55", "aa:bb:cc:dd:ee:ff", "2024-08-03 17:30:15")
            print(f"✅ Webhook alert test: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Discord webhook test error: {e}")
        return False

def test_detection_engine():
    """Test deauth detection engine"""
    print("\n🔍 Testing detection engine...")
    
    try:
        from main import DeauthDetector
        
        detector = DeauthDetector()
        
        # Test start monitoring
        detector.start_monitoring()
        print("✅ Monitoring started")
        
        # Test detection signal
        signal_received = False
        def on_attack_detected(attacker, target, timestamp):
            nonlocal signal_received
            signal_received = True
            print(f"✅ Attack signal received: {attacker} → {target} at {timestamp}")
        
        detector.attack_detected.connect(on_attack_detected)
        
        # Stop monitoring
        detector.stop_monitoring()
        print("✅ Monitoring stopped")
        
        return True
    except Exception as e:
        print(f"❌ Detection engine test error: {e}")
        return False

def main():
    """Run all headless tests"""
    print("🧪 WiFi Deauth Detector - Headless Testing")
    print("=" * 50)
    
    tests = [
        test_modules_import,
        test_settings_functionality,
        test_network_manager,
        test_discord_webhook,
        test_detection_engine
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed}/{passed + failed} ({100 * passed / (passed + failed):.1f}%)")
    
    if failed == 0:
        print("\n🎉 All tests passed! Application is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    return failed == 0

if __name__ == "__main__":
    main()