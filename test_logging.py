#!/usr/bin/env python3
"""
Test script for WiFi Deauth Detector logging functionality
"""

import sys
import os
import tempfile
import json
from datetime import datetime

# Add current directory to path to import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wifi_deauth_detector import LogManager, LogEntry

def test_log_manager():
    print("Testing LogManager functionality...")
    
    # Create temporary log file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
        tmp_log_file = tmp_file.name
    
    try:
        # Initialize log manager with temp file
        log_manager = LogManager(tmp_log_file)
        
        # Test adding logs
        log_manager.add_log("INFO", "Test info message")
        log_manager.add_log("WARNING", "Test warning with MAC", "AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66")
        log_manager.add_log("CRITICAL", "Test critical alert")
        
        # Add more logs to test the "last 20" functionality
        for i in range(25):
            log_manager.add_log("INFO", f"Test log entry {i+1}")
        
        # Test recent logs retrieval
        recent_logs = log_manager.get_recent_logs(20)
        
        print(f"✓ Total logs: {len(log_manager.logs)}")
        print(f"✓ Recent logs (last 20): {len(recent_logs)}")
        
        # Verify we get exactly 20 or fewer logs
        assert len(recent_logs) <= 20, "Should return at most 20 logs"
        
        # Verify logs are in correct order (most recent last)
        if len(recent_logs) > 1:
            assert recent_logs[-1].timestamp >= recent_logs[0].timestamp, "Logs should be in chronological order"
        
        # Test log persistence
        log_manager2 = LogManager(tmp_log_file)
        assert len(log_manager2.logs) == len(log_manager.logs), "Logs should persist between instances"
        
        print("✓ All LogManager tests passed!")
        
    finally:
        # Clean up temp file
        if os.path.exists(tmp_log_file):
            os.unlink(tmp_log_file)

def test_log_entry():
    print("\nTesting LogEntry functionality...")
    
    # Create log entry
    timestamp = datetime.now()
    entry = LogEntry(timestamp, "WARNING", "Test message", "AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66")
    
    # Test serialization
    entry_dict = entry.to_dict()
    print(f"✓ Serialization: {entry_dict}")
    
    # Test deserialization
    entry2 = LogEntry.from_dict(entry_dict)
    
    assert entry2.level == entry.level, "Level should match"
    assert entry2.message == entry.message, "Message should match"
    assert entry2.source_mac == entry.source_mac, "Source MAC should match"
    assert entry2.target_mac == entry.target_mac, "Target MAC should match"
    
    print("✓ All LogEntry tests passed!")

if __name__ == "__main__":
    print("WiFi Deauth Detector - Testing Logging Functionality")
    print("=" * 50)
    
    test_log_entry()
    test_log_manager()
    
    print("\n🎉 All tests passed! The logging functionality is working correctly.")
    print("\nTo test the GUI:")
    print("1. Run: python3 wifi_deauth_detector.py")
    print("2. Click 'Open Logs' button to view the log popup")
    print("3. Start detection to see live logging in action")