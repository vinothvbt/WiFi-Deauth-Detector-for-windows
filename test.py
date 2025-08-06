#!/usr/bin/env python3
"""
Test script for WiFi Deauth Detector
Tests core functionality without requiring actual WiFi monitoring
"""

import unittest
import sys
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add the main directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import SettingsManager, NetworkManager, DiscordWebhook

class TestSettingsManager(unittest.TestCase):
    """Test settings management functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_file = tempfile.mktemp(suffix='.json')
        self.settings = SettingsManager(self.temp_file)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
    
    def test_default_settings(self):
        """Test default settings are loaded correctly"""
        self.assertFalse(self.settings.get("discord_enabled"))
        self.assertFalse(self.settings.get("auto_switch_enabled"))
        self.assertTrue(self.settings.get("notifications_enabled"))
        self.assertTrue(self.settings.get("log_attacks"))
    
    def test_save_and_load_settings(self):
        """Test saving and loading settings"""
        # Modify settings
        self.settings.set("discord_enabled", True)
        self.settings.set("backup_network", "TestNetwork")
        
        # Save settings
        self.assertTrue(self.settings.save_settings())
        
        # Create new settings manager and verify settings persist
        new_settings = SettingsManager(self.temp_file)
        self.assertTrue(new_settings.get("discord_enabled"))
        self.assertEqual(new_settings.get("backup_network"), "TestNetwork")

class TestNetworkManager(unittest.TestCase):
    """Test network management functionality"""
    
    @patch('subprocess.run')
    def test_get_available_profiles(self, mock_run):
        """Test getting available WiFi profiles"""
        # Mock netsh output
        mock_result = MagicMock()
        mock_result.stdout = """
            All User Profile     : Home Network
            All User Profile     : Office WiFi
            All User Profile     : Guest Network
        """
        mock_run.return_value = mock_result
        
        profiles = NetworkManager.get_available_profiles()
        self.assertIn("Home Network", profiles)
        self.assertIn("Office WiFi", profiles)
        self.assertIn("Guest Network", profiles)
    
    @patch('subprocess.run')
    def test_connect_to_network_success(self, mock_run):
        """Test successful network connection"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        success = NetworkManager.connect_to_network("TestNetwork")
        self.assertTrue(success)
        
        # Verify correct command was called
        mock_run.assert_called_with(
            ['netsh', 'wlan', 'connect', 'name="TestNetwork"'],
            capture_output=True, text=True, shell=True
        )
    
    @patch('subprocess.run')
    def test_connect_to_network_failure(self, mock_run):
        """Test failed network connection"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        success = NetworkManager.connect_to_network("TestNetwork")
        self.assertFalse(success)

class TestDiscordWebhook(unittest.TestCase):
    """Test Discord webhook functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.webhook_url = "https://discord.com/api/webhooks/test/webhook"
        self.discord = DiscordWebhook(self.webhook_url)
    
    @patch('requests.post')
    def test_send_alert_success(self, mock_post):
        """Test successful Discord alert"""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        success = self.discord.send_alert(
            "aa:bb:cc:dd:ee:ff",
            "11:22:33:44:55:66",
            "2024-01-01 12:00:00"
        )
        
        self.assertTrue(success)
        mock_post.assert_called_once()
        
        # Verify correct payload structure
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['embeds'][0]['title'], "🚨 WiFi Deauth Attack Detected!")
    
    @patch('requests.post')
    def test_send_alert_failure(self, mock_post):
        """Test failed Discord alert"""
        mock_post.side_effect = Exception("Network error")
        
        success = self.discord.send_alert(
            "aa:bb:cc:dd:ee:ff",
            "11:22:33:44:55:66", 
            "2024-01-01 12:00:00"
        )
        
        self.assertFalse(success)
    
    def test_send_alert_no_webhook(self):
        """Test Discord alert with no webhook URL"""
        discord = DiscordWebhook("")
        success = discord.send_alert("test", "test", "test")
        self.assertFalse(success)

def run_tests():
    """Run all tests"""
    print("🧪 Running WiFi Deauth Detector Tests")
    print("=" * 40)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestSettingsManager))
    test_suite.addTest(unittest.makeSuite(TestNetworkManager))
    test_suite.addTest(unittest.makeSuite(TestDiscordWebhook))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print results
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return True
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)