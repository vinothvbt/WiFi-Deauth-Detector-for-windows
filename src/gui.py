"""
Simple GUI for WiFi Deauth Detector with notification toggle.

This provides a minimal interface for toggling notifications on/off.
"""

import sys
import logging
from typing import Optional

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                                QHBoxLayout, QWidget, QPushButton, QCheckBox, 
                                QLabel, QTextEdit, QFrame)
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    print("Warning: PyQt5 not available. GUI features will be disabled.")

from notification_manager import NotificationManager


class NotificationControlWidget(QWidget):
    """Widget for controlling notification settings."""
    
    def __init__(self, notification_manager: NotificationManager):
        super().__init__()
        self.notification_manager = notification_manager
        self.init_ui()
    
    def init_ui(self):
        """Initialize the notification control UI."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Notification Settings")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Notification toggle
        self.notification_checkbox = QCheckBox("Enable notifications")
        self.notification_checkbox.setChecked(self.notification_manager.is_enabled())
        self.notification_checkbox.stateChanged.connect(self.toggle_notifications)
        layout.addWidget(self.notification_checkbox)
        
        # Status label
        self.status_label = QLabel()
        self.update_status_label()
        layout.addWidget(self.status_label)
        
        # Test notification button
        test_button = QPushButton("Test Notification")
        test_button.clicked.connect(self.test_notification)
        layout.addWidget(test_button)
        
        # Clear attackers button
        clear_button = QPushButton("Clear Known Attackers")
        clear_button.clicked.connect(self.clear_attackers)
        layout.addWidget(clear_button)
        
        self.setLayout(layout)
    
    def toggle_notifications(self, state):
        """Toggle notification enable/disable."""
        enabled = state == Qt.Checked
        self.notification_manager.set_enabled(enabled)
        self.update_status_label()
    
    def update_status_label(self):
        """Update the status label."""
        if self.notification_manager.is_enabled():
            status = "✅ Notifications enabled"
        else:
            status = "❌ Notifications disabled"
        
        known_count = len(self.notification_manager.get_known_attackers())
        status += f" | Known attackers: {known_count}"
        
        self.status_label.setText(status)
    
    def test_notification(self):
        """Send a test notification."""
        self.notification_manager.notify_new_attacker(
            "AA:BB:CC:DD:EE:FF", 
            "11:22:33:44:55:66"
        )
    
    def clear_attackers(self):
        """Clear the known attackers list."""
        self.notification_manager.clear_known_attackers()
        self.update_status_label()


class DeauthDetectorMainWindow(QMainWindow):
    """Main window for WiFi Deauth Detector."""
    
    def __init__(self):
        super().__init__()
        self.notification_manager = NotificationManager()
        self.init_ui()
        
        # Timer to update UI periodically
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(1000)  # Update every second
    
    def init_ui(self):
        """Initialize the main UI."""
        self.setWindowTitle("WiFi Deauth Detector")
        self.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🛡️ WiFi Deauth Detector")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Notification control widget
        self.notification_widget = NotificationControlWidget(self.notification_manager)
        layout.addWidget(self.notification_widget)
        
        # Another separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator2)
        
        # Log area (placeholder for now)
        log_label = QLabel("Detection Log:")
        log_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.append("Waiting for deauth attacks...")
        layout.addWidget(self.log_text)
        
        # Demo buttons
        demo_layout = QHBoxLayout()
        demo_button1 = QPushButton("Simulate Attack #1")
        demo_button1.clicked.connect(lambda: self.simulate_attack("AA:BB:CC:DD:EE:01"))
        demo_layout.addWidget(demo_button1)
        
        demo_button2 = QPushButton("Simulate Attack #2")
        demo_button2.clicked.connect(lambda: self.simulate_attack("AA:BB:CC:DD:EE:02"))
        demo_layout.addWidget(demo_button2)
        
        layout.addLayout(demo_layout)
        
        central_widget.setLayout(layout)
    
    def simulate_attack(self, attacker_mac: str):
        """Simulate a deauth attack for demonstration."""
        self.notification_manager.notify_new_attacker(attacker_mac, "Target:Device:MAC")
        self.log_text.append(f"Simulated attack from {attacker_mac}")
        self.notification_widget.update_status_label()
    
    def update_ui(self):
        """Update UI elements periodically."""
        self.notification_widget.update_status_label()


def main():
    """Main entry point for the GUI application."""
    if not PYQT5_AVAILABLE:
        print("PyQt5 is not available. Please install it to use the GUI.")
        return
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    window = DeauthDetectorMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()