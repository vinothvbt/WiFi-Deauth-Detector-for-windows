#!/usr/bin/env python3
"""
Test script for WiFi Deauth Detector
Tests the MAC address tracking and attacker identification functionality
"""

import sys
import time
from datetime import datetime

# Import our detector
from wifi_deauth_detector import WiFiDeauthDetector

# Mock Scapy components for testing
class MockDot11:
    def __init__(self, addr1, addr2, addr3):
        self.addr1 = addr1
        self.addr2 = addr2 
        self.addr3 = addr3

class MockDeauthPacket:
    def __init__(self, addr1, addr2, addr3):
        self.dot11 = MockDot11(addr1, addr2, addr3)
    
    def haslayer(self, layer_type):
        return True  # Mock that it has Dot11 and Dot11Deauth layers
    
    def __getitem__(self, layer_type):
        return self.dot11

def test_mac_tracking():
    """Test MAC address frequency tracking"""
    print("Testing MAC address tracking and attacker identification...")
    
    # Create detector instance
    detector = WiFiDeauthDetector(interface="test", display_interval=5)
    
    # Create mock deauth packets
    test_packets = [
        MockDeauthPacket("AA:BB:CC:DD:EE:01", "FF:FF:FF:FF:FF:01", "11:22:33:44:55:01"),  # Attacker 1
        MockDeauthPacket("AA:BB:CC:DD:EE:02", "FF:FF:FF:FF:FF:01", "11:22:33:44:55:02"),  # Attacker 1 again
        MockDeauthPacket("AA:BB:CC:DD:EE:03", "FF:FF:FF:FF:FF:01", "11:22:33:44:55:03"),  # Attacker 1 again
        MockDeauthPacket("AA:BB:CC:DD:EE:04", "FF:FF:FF:FF:FF:02", "11:22:33:44:55:04"),  # Attacker 2
        MockDeauthPacket("AA:BB:CC:DD:EE:05", "FF:FF:FF:FF:FF:01", "11:22:33:44:55:05"),  # Attacker 1 again
    ]
    
    print(f"Processing {len(test_packets)} mock deauth packets...")
    
    # Process each packet
    for i, packet in enumerate(test_packets):
        print(f"\nProcessing packet {i+1}:")
        detector.log_frame_addresses(packet)
        time.sleep(0.1)  # Small delay to make timestamps different
    
    # Test attacker identification
    print("\n" + "="*60)
    print("TESTING ATTACKER IDENTIFICATION")
    print("="*60)
    
    attacker_info = detector.identify_attacker()
    if attacker_info:
        attacker_mac, count = attacker_info
        print(f"✅ Successfully identified attacker: {attacker_mac}")
        print(f"✅ Attack count: {count}")
        
        # Verify it's the expected attacker (FF:FF:FF:FF:FF:01 should have 4 attacks)
        if attacker_mac == "FF:FF:FF:FF:FF:01" and count == 4:
            print("✅ Correct attacker identified!")
        else:
            print(f"❌ Expected FF:FF:FF:FF:FF:01 with count 4, got {attacker_mac} with count {count}")
    else:
        print("❌ No attacker identified")
    
    # Test display functionality
    print("\n" + "="*60)
    print("TESTING DISPLAY FUNCTIONALITY")
    print("="*60)
    detector.display_attacker_info()
    
    # Test summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total frames processed: {len(detector.deauth_frames)}")
    print(f"Unique MACs detected: {len(detector.mac_frequency)}")
    print("MAC frequency distribution:")
    for mac, count in detector.mac_frequency.most_common():
        print(f"  {mac}: {count} frames")
    
    # Verify the expected results
    if (len(detector.deauth_frames) == 5 and 
        len(detector.mac_frequency) == 2 and
        detector.mac_frequency["FF:FF:FF:FF:FF:01"] == 4 and
        detector.mac_frequency["FF:FF:FF:FF:FF:02"] == 1):
        print("\n✅ ALL TESTS PASSED!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        return False

def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*60)
    print("TESTING EDGE CASES")
    print("="*60)
    
    detector = WiFiDeauthDetector(interface="test")
    
    # Test with no packets
    print("Testing with no packets...")
    attacker_info = detector.identify_attacker()
    if attacker_info is None:
        print("✅ Correctly handled empty packet list")
    else:
        print("❌ Should return None for empty packet list")
    
    # Test with single packet (should not identify as attacker)
    print("\nTesting with single packet...")
    single_packet = MockDeauthPacket("AA:BB:CC:DD:EE:01", "FF:FF:FF:FF:FF:01", "11:22:33:44:55:01")
    detector.log_frame_addresses(single_packet)
    
    attacker_info = detector.identify_attacker()
    if attacker_info is None:
        print("✅ Correctly ignored single packet")
    else:
        print("❌ Should not identify attacker from single packet")
    
    print("✅ Edge case tests completed")

if __name__ == "__main__":
    print("WiFi Deauth Detector - Test Suite")
    print("="*60)
    
    try:
        # Run main tests
        success = test_mac_tracking()
        
        # Run edge case tests
        test_edge_cases()
        
        if success:
            print(f"\n🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)