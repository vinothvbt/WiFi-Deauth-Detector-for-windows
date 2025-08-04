#!/usr/bin/env python3
"""
WiFi Deauth Detector for Windows
Real-time deauthentication frame detection and analysis

Issue 4 Implementation:
- Capture all packets
- Filter: Dot11.type == 0 and Dot11.subtype == 12
- Parse: Source MAC, Destination MAC, Timestamp
- Print to console
"""

import sys
import time
from datetime import datetime
from scapy.all import *
from scapy.layers.dot11 import Dot11, Dot11Deauth


def print_deauth_frame(packet):
    """
    Parse and print deauth frame information to console
    """
    try:
        # Extract timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Extract MAC addresses
        if packet.haslayer(Dot11):
            src_mac = packet[Dot11].addr2  # Source MAC (transmitter)
            dst_mac = packet[Dot11].addr1  # Destination MAC (receiver)
            
            # Print to console
            print(f"[{timestamp}] DEAUTH DETECTED:")
            print(f"  Source MAC:      {src_mac}")
            print(f"  Destination MAC: {dst_mac}")
            print(f"  Frame Type:      {packet[Dot11].type}")
            print(f"  Frame Subtype:   {packet[Dot11].subtype}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error parsing packet: {e}")


def packet_handler(packet):
    """
    Handle captured packets and filter for deauth frames
    """
    # Check if packet has Dot11 layer
    if packet.haslayer(Dot11):
        # Filter: Dot11.type == 0 and Dot11.subtype == 12
        if packet[Dot11].type == 0 and packet[Dot11].subtype == 12:
            print_deauth_frame(packet)


def main():
    """
    Main function to start packet capture and deauth detection
    """
    print("WiFi Deauth Detector for Windows")
    print("=" * 40)
    print("Starting packet capture...")
    print("Monitoring for deauth frames (type=0, subtype=12)")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    try:
        # Start packet sniffing
        # Note: On Windows with Npcap, you may need to specify the interface
        # and ensure monitor mode is enabled
        sniff(prn=packet_handler, store=False, monitor=True)
        
    except KeyboardInterrupt:
        print("\nStopping deauth detection...")
        sys.exit(0)
    except PermissionError:
        print("Error: Administrator privileges required for packet capture")
        print("Please run as administrator")
        sys.exit(1)
    except Exception as e:
        print(f"Error during packet capture: {e}")
        print("Ensure Npcap is installed and wireless adapter supports monitor mode")
        sys.exit(1)


if __name__ == "__main__":
    main()