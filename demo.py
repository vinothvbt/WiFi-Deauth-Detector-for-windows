#!/usr/bin/env python3
"""
Demo script for WiFi Deauth Detector
Demonstrates the functionality without requiring actual WiFi monitoring
"""

import time
from wifi_deauth_detector import WiFiDeauthDetector

def run_demo():
    """Run a demonstration of the detector functionality"""
    print("🛡️ WiFi Deauth Detector - Live Demo")
    print("="*60)
    print("This demo simulates detecting deauth attacks without requiring")
    print("actual WiFi monitoring or administrator privileges.")
    print("="*60)
    
    # Create detector instance
    detector = WiFiDeauthDetector(interface="demo", display_interval=10)
    
    # Simulate some legitimate traffic first
    print("\n📡 Simulating normal WiFi traffic...")
    time.sleep(1)
    
    # Now simulate an attack scenario
    print("\n🚨 Simulating deauth attack scenario...")
    print("An attacker (MAC: DE:AD:BE:EF:CA:FE) is sending deauth frames")
    print("to multiple targets...\n")
    
    # Mock some attack data directly into the detector
    attack_frames = [
        {
            'timestamp': '2025-08-03 17:30:01',
            'addr1': 'AA:BB:CC:DD:EE:11',  # Target 1
            'addr2': 'DE:AD:BE:EF:CA:FE',  # Attacker
            'addr3': '00:11:22:33:44:55',  # AP BSSID
            'type': 'deauth'
        },
        {
            'timestamp': '2025-08-03 17:30:02', 
            'addr1': 'AA:BB:CC:DD:EE:22',  # Target 2
            'addr2': 'DE:AD:BE:EF:CA:FE',  # Same attacker
            'addr3': '00:11:22:33:44:55',  # Same AP
            'type': 'deauth'
        },
        {
            'timestamp': '2025-08-03 17:30:03',
            'addr1': 'AA:BB:CC:DD:EE:33',  # Target 3  
            'addr2': 'DE:AD:BE:EF:CA:FE',  # Same attacker
            'addr3': '00:11:22:33:44:55',  # Same AP
            'type': 'deauth'
        },
        {
            'timestamp': '2025-08-03 17:30:04',
            'addr1': 'AA:BB:CC:DD:EE:11',  # Target 1 again
            'addr2': 'DE:AD:BE:EF:CA:FE',  # Same attacker  
            'addr3': '00:11:22:33:44:55',  # Same AP
            'type': 'deauth'
        },
        {
            'timestamp': '2025-08-03 17:30:05',
            'addr1': 'AA:BB:CC:DD:EE:44',  # Target 4
            'addr2': 'DE:AD:BE:EF:CA:FE',  # Same attacker
            'addr3': '00:11:22:33:44:55',  # Same AP  
            'type': 'deauth'
        }
    ]
    
    # Add frames to detector and track MAC frequencies
    for frame in attack_frames:
        detector.deauth_frames.append(frame)
        detector.mac_frequency[frame['addr2']] += 1
        
        # Display frame as it would appear during live capture
        print(f"[FRAME] {frame['timestamp']}")
        print(f"  addr1 (dest): {frame['addr1']}")
        print(f"  addr2 (src):  {frame['addr2']}")  
        print(f"  addr3 (bssid): {frame['addr3']}")
        print(f"  type: {frame['type']}")
        print("-" * 50)
        time.sleep(0.5)
    
    print("\n🔍 Analyzing attack patterns...")
    time.sleep(2)
    
    # Display attacker identification
    print("\n" + "="*60)
    detector.display_attacker_info()
    
    # Show final summary
    print(f"\n📊 ATTACK SUMMARY:")
    print(f"Total deauth frames detected: {len(detector.deauth_frames)}")
    print(f"Unique source MACs: {len(detector.mac_frequency)}")
    print(f"Most active source: {detector.mac_frequency.most_common(1)[0]}")
    
    targets = list(set([frame['addr1'] for frame in detector.deauth_frames]))
    print(f"Targets affected: {len(targets)}")
    for target in targets:
        print(f"  • {target}")
    
    print("\n✅ Demo completed! The detector successfully:")
    print("  ✓ Logged addr1, addr2, addr3 from deauth frames")
    print("  ✓ Identified the most frequent source MAC")
    print("  ✓ Displayed 'Possible attacker: XX:XX:XX:XX:XX:XX'")
    print("  ✓ Tracked multiple targets and attack patterns")

if __name__ == "__main__":
    run_demo()