#!/usr/bin/env python3
"""
Demo script for WiFi Deauth Detector
Shows the application running and demonstrates features
"""

import sys
import os
import time
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from main import WiFiDeauthDetectorGUI

class DemoController:
    """Controls the demo flow"""
    
    def __init__(self, app_window):
        self.window = app_window
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.run_demo_sequence)
        self.demo_step = 0
        
    def start_demo(self):
        """Start the demo sequence"""
        print("🎬 Starting WiFi Deauth Detector Demo...")
        
        # Configure some demo settings
        self.window.discord_webhook_edit.setText("https://discord.com/api/webhooks/demo/url")
        self.window.backup_network_combo.setEditText("DemoBackupNetwork")
        self.window.auto_switch_cb.setChecked(True)
        self.window.discord_enabled_cb.setChecked(True)
        
        # Save settings
        self.window.save_settings()
        
        # Start demo timer
        self.demo_timer.start(3000)  # Every 3 seconds
        
    def run_demo_sequence(self):
        """Run the demo sequence steps"""
        if self.demo_step == 0:
            print("📡 Starting monitoring...")
            self.window.start_monitoring()
            
        elif self.demo_step == 1:
            print("🚨 Simulating deauth attack detection...")
            # The detector will automatically generate simulated attacks
            
        elif self.demo_step == 5:
            print("📊 Checking logs tab...")
            # Switch to logs tab
            tab_widget = self.window.centralWidget().findChild(self.window.QTabWidget)
            if hasattr(self.window, 'centralWidget'):
                for child in self.window.centralWidget().findChildren(self.window.centralWidget().__class__):
                    if hasattr(child, 'setCurrentIndex'):
                        child.setCurrentIndex(2)  # Logs tab
                        break
                        
        elif self.demo_step == 8:
            print("⚙️ Checking settings...")
            # Switch to settings tab
            tab_widget = self.window.centralWidget().findChild(self.window.QTabWidget)
            if hasattr(self.window, 'centralWidget'):
                for child in self.window.centralWidget().findChildren(self.window.centralWidget().__class__):
                    if hasattr(child, 'setCurrentIndex'):
                        child.setCurrentIndex(1)  # Settings tab
                        break
                        
        elif self.demo_step == 10:
            print("✅ Demo completed!")
            print("📸 Screenshots should be taken now")
            self.demo_timer.stop()
            
        self.demo_step += 1

def run_demo():
    """Run the demo application"""
    print("🎯 WiFi Deauth Detector Demo")
    print("=" * 40)
    print("This demo shows all the implemented features:")
    print("✅ Real-time deauth detection simulation")
    print("✅ Auto network switching configuration") 
    print("✅ Discord webhook alerts")
    print("✅ System notifications")
    print("✅ Event logging")
    print("✅ Complete GUI with settings")
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