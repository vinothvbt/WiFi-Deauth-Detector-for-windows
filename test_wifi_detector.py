#!/usr/bin/env python3
"""
Test script for WiFi Detector functionality
Tests the three main requirements from Issue #3
"""

import sys
import os

# Add the current directory to path to import wifi_detector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wifi_detector import WiFiDetector


def test_interface_detection():
    """Test WiFi interface detection via scapy.all.get_if_list()"""
    print("Testing WiFi interface detection...")
    detector = WiFiDetector()
    
    interfaces = detector.detect_wifi_interfaces()
    
    if interfaces:
        print(f"✓ Successfully detected {len(interfaces)} interfaces")
        for i, iface in enumerate(interfaces, 1):
            print(f"  {i}. {iface}")
        return True
    else:
        print("✗ No interfaces detected")
        return False


def test_interface_selection():
    """Test interface selection functionality"""
    print("\nTesting interface selection...")
    detector = WiFiDetector()
    
    # Get interfaces
    interfaces = detector.detect_wifi_interfaces()
    
    if not interfaces:
        print("✗ Cannot test selection - no interfaces available")
        return False
    
    # Test display functionality
    try:
        detector.display_interfaces(interfaces)
        print("✓ Interface display works correctly")
        return True
    except Exception as e:
        print(f"✗ Interface display failed: {e}")
        return False


def test_monitor_mode_setup():
    """Test monitor mode setup functionality"""
    print("\nTesting monitor mode setup...")
    detector = WiFiDetector()
    
    # Get a real interface for testing
    interfaces = detector.detect_wifi_interfaces()
    if not interfaces:
        print("✗ No interfaces available for monitor mode test")
        return False
        
    test_interface = interfaces[0]  # Use first available interface
    
    try:
        # This should work but show instructions
        result = detector.setup_monitor_mode(test_interface)
        if result:
            print("✓ Monitor mode setup completed successfully")
            return True
        else:
            print("✗ Monitor mode setup failed")
            return False
    except Exception as e:
        print(f"✗ Monitor mode setup error: {e}")
        return False


def main():
    """Run all tests"""
    print("WiFi Detector Test Suite")
    print("=" * 40)
    
    tests = [
        ("Interface Detection (scapy.all.get_if_list())", test_interface_detection),
        ("User Interface Selection", test_interface_selection), 
        ("Monitor Mode Setup", test_monitor_mode_setup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[TEST] {test_name}")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All core requirements implemented successfully!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())