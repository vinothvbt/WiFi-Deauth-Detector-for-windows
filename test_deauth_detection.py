#!/usr/bin/env python3
"""
Test script for deauth detection logic
Creates sample packets to test the filtering and parsing functionality
"""

import sys
from datetime import datetime
from scapy.all import *
from scapy.layers.dot11 import Dot11, Dot11Deauth


def test_deauth_detection():
    """
    Test the deauth detection logic with sample packets
    """
    print("Testing deauth detection logic...")
    print("=" * 40)
    
    # Import the packet handler from our main script
    sys.path.insert(0, '.')
    from deauth_detector import packet_handler, print_deauth_frame
    
    # Create a sample deauth frame
    # Dot11.type = 0 (management frame), subtype = 12 (deauth)
    deauth_packet = RadioTap() / Dot11(
        type=0,
        subtype=12,
        addr1="aa:bb:cc:dd:ee:ff",  # Destination (victim)
        addr2="11:22:33:44:55:66",  # Source (attacker)
        addr3="aa:bb:cc:dd:ee:ff"   # BSSID
    ) / Dot11Deauth(reason=7)
    
    print("Test 1: Valid deauth frame (should be detected)")
    packet_handler(deauth_packet)
    
    # Create a non-deauth frame (should be ignored)
    non_deauth_packet = RadioTap() / Dot11(
        type=0,
        subtype=8,  # Different subtype (beacon frame)
        addr1="aa:bb:cc:dd:ee:ff",
        addr2="11:22:33:44:55:66",
        addr3="aa:bb:cc:dd:ee:ff"
    )
    
    print("Test 2: Non-deauth frame (should be ignored)")
    packet_handler(non_deauth_packet)
    
    # Create a data frame (should be ignored)
    data_packet = RadioTap() / Dot11(
        type=2,  # Data frame
        subtype=0,
        addr1="aa:bb:cc:dd:ee:ff",
        addr2="11:22:33:44:55:66",
        addr3="aa:bb:cc:dd:ee:ff"
    )
    
    print("Test 3: Data frame (should be ignored)")
    packet_handler(data_packet)
    
    print("Testing complete!")


if __name__ == "__main__":
    test_deauth_detection()