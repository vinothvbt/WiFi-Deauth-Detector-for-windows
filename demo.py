#!/usr/bin/env python3
"""
Demo script for WiFi Deauth Detector v2.0
Shows the application running with new normal mode functionality
"""

import sys
import os
import time
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from main import WiFiDeauthDetectorGUI

class DemoController:
    """Controls the demo flow for v2.0"""
    
    def __init__(self, app_window):
        self.window = app_window
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.run_demo_sequence)
        self.demo_step = 0
        
    def start_demo(self):
        """Start the demo sequence"""
        print("🎬 Starting WiFi Deauth Detector v2.0 Demo...")
        
        # Configure demo settings
        self.window.discord_webhook_edit.setText("https://discord.com/api/webhooks/demo/url")
        self.window.backup_network_combo.setEditText("DemoBackupNetwork")
        self.window.auto_switch_cb.setChecked(True)
        self.window.discord_enabled_cb.setChecked(True)
        self.window.demo_mode_cb.setChecked(True)  # Enable demo mode
        
        # Save settings
        self.window.save_settings()
        
        # Start demo timer
        self.demo_timer.start(5000)  # Every 5 seconds
        
    def run_demo_sequence(self):
        """Run the demo sequence steps"""
        if self.demo_step == 0:
            print("📡 Starting WiFi connection monitoring...")
            self.window.start_monitoring()
            
        elif self.demo_step == 1:
            print("🔍 Demonstrating normal mode detection...")
            # In demo mode, the detector will generate events
            
        elif self.demo_step == 3:
            print("📊 Checking logs tab...")
            # Switch to logs tab
            for child in self.window.centralWidget().findChildren(self.window.centralWidget().__class__):
                if hasattr(child, 'setCurrentIndex'):
                    child.setCurrentIndex(2)  # Logs tab
                    break
                        
        elif self.demo_step == 5:
            print("⚙️ Showing new settings...")
            # Switch to settings tab
            for child in self.window.centralWidget().findChildren(self.window.centralWidget().__class__):
                if hasattr(child, 'setCurrentIndex'):
                    child.setCurrentIndex(1)  # Settings tab
                    break
                        
        elif self.demo_step == 7:
            print("📱 Switching back to monitor view...")
            # Switch back to monitor tab
            for child in self.window.centralWidget().findChildren(self.window.centralWidget().__class__):
                if hasattr(child, 'setCurrentIndex'):
                    child.setCurrentIndex(0)  # Monitor tab
                    break
                        
        elif self.demo_step == 10:
            print("✅ Demo completed!")
            print("📸 Screenshots should be taken now")
            self.demo_timer.stop()
            
        self.demo_step += 1

def run_demo():
    """Run the demo application"""
    print("🎯 WiFi Deauth Detector v2.0 Demo")
    print("=" * 50)
    print("🆕 New in v2.0:")
    print("✅ Normal mode operation (no monitor mode)")
    print("✅ Works on ALL Windows laptops")
    print("✅ Windows WLAN API integration") 
    print("✅ Enhanced pattern detection")
    print("✅ Universal hardware compatibility")
    print("✅ No special drivers required")
    print("✅ Demo mode for safe testing")
    print()
    
    app = QApplication(sys.argv)
    
    # Create main window
    window = WiFiDeauthDetectorGUI()
    window.show()
    
    # Start demo controller
    demo = DemoController(window)
    demo.start_demo()
    
    print("🖥️  Application window opened")
    print("⏰ Demo sequence will run automatically")
    print("📸 Take screenshots of the different tabs")
    print("🔽 Close the window to end demo")
    print()
    
    # Run application
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\n👋 Demo ended by user")

if __name__ == "__main__":
    run_demo()