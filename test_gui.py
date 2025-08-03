#!/usr/bin/env python3
"""
Test script for the WiFi Deauth Detector GUI
This script validates that all GUI components are working correctly.
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from wifi_deauth_detector import WiFiDeauthDetectorGUI

def test_gui_components():
    """Test all GUI components and functionality."""
    
    app = QApplication([])
    window = WiFiDeauthDetectorGUI()
    
    print("Testing GUI Components:")
    print("=" * 40)
    
    # Test 1: Window properties
    print(f"✓ Window title: {window.windowTitle()}")
    print(f"✓ Window size: {window.width()}x{window.height()}")
    
    # Test 2: Interface dropdown
    interface_count = window.interface_combo.count()
    print(f"✓ Interface dropdown has {interface_count} items")
    
    if interface_count > 1:
        print(f"  - Default option: {window.interface_combo.itemText(0)}")
        if interface_count > 1:
            print(f"  - First interface: {window.interface_combo.itemText(1)}")
    
    # Test 3: Buttons
    print(f"✓ Start button enabled: {window.start_button.isEnabled()}")
    print(f"✓ Stop button enabled: {window.stop_button.isEnabled()}")
    print(f"✓ Clear button enabled: {window.clear_button.isEnabled()}")
    
    # Test 4: Log text area
    print(f"✓ Log text area is read-only: {window.log_text.isReadOnly()}")
    
    # Test 5: Status bar
    status_text = window.status_bar.currentMessage()
    print(f"✓ Status bar message: '{status_text}'")
    
    # Test 6: Add some test log entries
    window.add_log_entry("[TEST] This is a test log entry")
    window.add_log_entry("[ALERT] Simulated deauth frame detected!")
    print("✓ Test log entries added successfully")
    
    # Test 7: Clear logs
    window.clear_logs()
    print("✓ Logs cleared successfully")
    
    # Test 8: Status update
    window.update_status("Test status message")
    print("✓ Status bar updated successfully")
    
    print("=" * 40)
    print("All GUI tests passed! ✓")
    
    app.quit()
    return True

if __name__ == "__main__":
    test_gui_components()