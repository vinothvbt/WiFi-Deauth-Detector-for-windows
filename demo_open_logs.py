#!/usr/bin/env python3
"""
Demo script to showcase the Open Logs functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wifi_deauth_detector import LogManager

def demo_open_logs_feature():
    print("🛡️  WiFi Deauth Detector - Open Logs Feature Demo")
    print("=" * 50)
    
    # Create a demo log manager
    log_manager = LogManager("demo_logs.json")
    
    # Simulate some realistic WiFi deauth detection logs
    print("\n📝 Adding sample deauth detection logs...")
    
    sample_events = [
        ("INFO", "WiFi Deauth Detector started"),
        ("INFO", "Monitoring interface wlan0 in monitor mode"),
        ("WARNING", "Deauth frame detected", "24:A4:3C:FF:12:34", "E8:DE:27:AB:CD:EF"),
        ("WARNING", "Multiple deauth frames from same source", "24:A4:3C:FF:12:34", "E8:DE:27:AB:CD:EF"),
        ("CRITICAL", "Potential deauth attack in progress!", "24:A4:3C:FF:12:34", "E8:DE:27:AB:CD:EF"),
        ("INFO", "Attack pattern stopped, resuming normal monitoring"),
        ("INFO", "Network traffic returned to normal"),
        ("WARNING", "Suspicious deauth activity detected", "AA:BB:CC:12:34:56", "11:22:33:44:55:66"),
        ("INFO", "False positive - legitimate disconnect"),
        ("INFO", "Monitoring continues..."),
    ]
    
    for level, message, *macs in sample_events:
        source_mac = macs[0] if len(macs) > 0 else None
        target_mac = macs[1] if len(macs) > 1 else None
        log_manager.add_log(level, message, source_mac, target_mac)
        print(f"   Added: {level} - {message}")
    
    # Add some additional logs to test the "last 20" functionality
    print(f"\n📊 Adding more logs to test 'last 20' limit...")
    for i in range(15):
        log_manager.add_log("INFO", f"Routine monitoring check #{i+1}")
    
    print(f"\n📈 Log Statistics:")
    print(f"   Total logs in system: {len(log_manager.logs)}")
    
    # Demonstrate the "Open Logs" functionality
    print(f"\n🪟 Simulating 'Open Logs' button click...")
    recent_logs = log_manager.get_recent_logs(20)
    print(f"   Retrieved last {len(recent_logs)} logs for popup display")
    
    print(f"\n📋 Log Popup Window Content (Last 20 entries):")
    print("=" * 70)
    print("Last 20 Deauth Detection Logs")
    print("-" * 70)
    
    # Display logs in reverse chronological order (most recent first)
    for i, log in enumerate(reversed(recent_logs)):
        timestamp_str = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        mac_info = ""
        if log.source_mac and log.target_mac:
            mac_info = f" | Source: {log.source_mac} | Target: {log.target_mac}"
        elif log.source_mac:
            mac_info = f" | MAC: {log.source_mac}"
        
        log_line = f"[{timestamp_str}] {log.level}: {log.message}{mac_info}"
        print(f"{i+1:2d}. {log_line}")
    
    print("-" * 70)
    print("(Close button would be here)")
    print("=" * 70)
    
    # Cleanup
    if os.path.exists("demo_logs.json"):
        os.unlink("demo_logs.json")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"\n💡 Key Features Demonstrated:")
    print(f"   ✅ Open Logs button functionality")
    print(f"   ✅ Last 20 logs limitation")
    print(f"   ✅ Proper chronological ordering")
    print(f"   ✅ Formatted display with timestamps and MAC addresses")
    print(f"   ✅ Different log levels (INFO, WARNING, CRITICAL)")
    print(f"   ✅ Persistent storage and retrieval")
    
    print(f"\n🚀 To run the actual GUI:")
    print(f"   python wifi_deauth_detector.py")
    print(f"   (Then click 'Open Logs' button)")

if __name__ == "__main__":
    demo_open_logs_feature()