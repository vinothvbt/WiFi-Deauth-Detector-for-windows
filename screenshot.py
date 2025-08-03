#!/usr/bin/env python3
"""
Screenshot script for WiFi Deauth Detector
Creates screenshots of the application for documentation
"""

import sys
import os
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from main import WiFiDeauthDetectorGUI

def create_screenshots():
    """Create screenshots of the application"""
    print("📸 Creating screenshots for documentation...")
    
    app = QApplication(sys.argv)
    
    # Create window
    window = WiFiDeauthDetectorGUI()
    window.show()
    
    # Wait for window to render
    app.processEvents()
    time.sleep(1)
    
    # Configure demo settings
    window.discord_webhook_edit.setText("https://discord.com/api/webhooks/demo/url")
    window.backup_network_combo.setEditText("BackupWiFi_5G")
    window.auto_switch_cb.setChecked(True)
    window.discord_enabled_cb.setChecked(True)
    window.confirm_switch_cb.setChecked(True)
    window.notifications_cb.setChecked(True)
    window.logging_cb.setChecked(True)
    
    # Add some demo log entries
    window.log_message("Application started")
    window.log_message("Monitoring configuration loaded")
    window.log_message("Network profiles detected: 5")
    
    # Add demo alerts
    window.alerts_display.append("[2024-08-03 17:30:15] ATTACK! Attacker: 00:11:22:33:44:55 → Target: aa:bb:cc:dd:ee:ff")
    window.alerts_display.append("[2024-08-03 17:32:22] ATTACK! Attacker: 66:77:88:99:aa:bb → Target: cc:dd:ee:ff:00:11")
    
    # Update statistics
    window.total_attacks_label.setText("2")
    window.last_attack_label.setText("2024-08-03 17:32:22")
    
    app.processEvents()
    time.sleep(1)
    
    # Take screenshot of Monitor tab
    pixmap = window.grab()
    pixmap.save("screenshot_monitor.png")
    print("✅ Monitor tab screenshot saved")
    
    # Switch to Settings tab
    tab_widget = window.findChild(window.centralWidget().__class__)
    for child in window.centralWidget().children():
        if hasattr(child, 'setCurrentIndex'):
            child.setCurrentIndex(1)
            break
    
    app.processEvents()
    time.sleep(1)
    
    # Take screenshot of Settings tab
    pixmap = window.grab()
    pixmap.save("screenshot_settings.png")
    print("✅ Settings tab screenshot saved")
    
    # Switch to Logs tab
    for child in window.centralWidget().children():
        if hasattr(child, 'setCurrentIndex'):
            child.setCurrentIndex(2)
            break
    
    app.processEvents()
    time.sleep(1)
    
    # Take screenshot of Logs tab
    pixmap = window.grab()
    pixmap.save("screenshot_logs.png")
    print("✅ Logs tab screenshot saved")
    
    app.quit()
    print("📸 All screenshots created successfully!")

if __name__ == "__main__":
    create_screenshots()