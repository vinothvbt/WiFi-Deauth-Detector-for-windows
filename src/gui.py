#!/usr/bin/env python3
"""
GUI Module for WiFi Deauth Detector

This module provides the graphical user interface for the WiFi deauth detector
using PyQt5. It displays real-time alerts and allows users to configure
monitoring settings.

Author: WiFi Security Team
License: MIT
"""

import sys
import logging
from datetime import datetime
from typing import Dict, Any
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QTextEdit, QGroupBox, QSystemTrayIcon, QMenu, QMessageBox
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QFont

from sniffer import WiFiSniffer
from utils import send_notification


class SnifferThread(QThread):
    """Thread for running the WiFi sniffer in background."""
    
    attack_detected = pyqtSignal(dict)
    
    def __init__(self, interface=None):
        super().__init__()
        self.sniffer = WiFiSniffer(interface)
        self.sniffer.set_packet_callback(self.on_attack_detected)
        
    def on_attack_detected(self, attack_info: Dict[str, Any]):
        """Emit signal when attack is detected."""
        self.attack_detected.emit(attack_info)
        
    def run(self):
        """Start the sniffer thread."""
        self.sniffer.start_sniffing()
        
    def stop(self):
        """Stop the sniffer thread."""
        self.sniffer.stop_sniffing()
        self.wait()


class DeauthDetectorGUI(QMainWindow):
    """Main GUI window for the WiFi Deauth Detector."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.sniffer_thread = None
        self.is_monitoring = False
        self.attack_count = 0
        
        self.init_ui()
        self.init_system_tray()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("WiFi Deauth Detector")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("🛡️ WiFi Deauth Detector")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Control panel
        control_group = QGroupBox("Monitor Controls")
        control_layout = QHBoxLayout(control_group)
        
        # Interface selection
        control_layout.addWidget(QLabel("Interface:"))
        self.interface_combo = QComboBox()
        self.populate_interfaces()
        control_layout.addWidget(self.interface_combo)
        
        # Start/Stop button
        self.monitor_button = QPushButton("Start Monitoring")
        self.monitor_button.clicked.connect(self.toggle_monitoring)
        control_layout.addWidget(self.monitor_button)
        
        # Status label
        self.status_label = QLabel("Status: Stopped")
        control_layout.addWidget(self.status_label)
        
        layout.addWidget(control_group)
        
        # Statistics panel
        stats_group = QGroupBox("Statistics")
        stats_layout = QHBoxLayout(stats_group)
        
        self.attack_count_label = QLabel("Attacks Detected: 0")
        stats_layout.addWidget(self.attack_count_label)
        
        self.uptime_label = QLabel("Uptime: 00:00:00")
        stats_layout.addWidget(self.uptime_label)
        
        layout.addWidget(stats_group)
        
        # Attack log table
        log_group = QGroupBox("Attack Log")
        log_layout = QVBoxLayout(log_group)
        
        self.attack_table = QTableWidget()
        self.attack_table.setColumnCount(6)
        self.attack_table.setHorizontalHeaderLabels([
            "Time", "Type", "Attacker MAC", "Target MAC", "BSSID", "Reason"
        ])
        log_layout.addWidget(self.attack_table)
        
        layout.addWidget(log_group)
        
        # Console output
        console_group = QGroupBox("Console Output")
        console_layout = QVBoxLayout(console_group)
        
        self.console_output = QTextEdit()
        self.console_output.setMaximumHeight(150)
        self.console_output.setReadOnly(True)
        console_layout.addWidget(self.console_output)
        
        layout.addWidget(console_group)
        
        # Timer for uptime
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        self.start_time = None
        
    def init_system_tray(self):
        """Initialize system tray functionality."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.warning("System tray not available")
            return
            
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Set tray icon (placeholder)
        self.tray_icon.setToolTip("WiFi Deauth Detector")
        self.tray_icon.show()
        
    def populate_interfaces(self):
        """Populate the interface dropdown with available interfaces."""
        try:
            sniffer = WiFiSniffer()
            interfaces = sniffer.get_available_interfaces()
            self.interface_combo.addItems(interfaces)
            
            if interfaces:
                self.log_message(f"Found {len(interfaces)} network interfaces")
            else:
                self.log_message("No network interfaces found")
                
        except Exception as e:
            self.log_message(f"Error loading interfaces: {e}")
            
    def toggle_monitoring(self):
        """Toggle monitoring on/off."""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        """Start WiFi monitoring."""
        try:
            interface = self.interface_combo.currentText()
            if not interface:
                QMessageBox.warning(self, "Warning", "Please select a network interface")
                return
                
            self.log_message(f"Starting monitoring on interface: {interface}")
            
            # Create and start sniffer thread
            self.sniffer_thread = SnifferThread(interface)
            self.sniffer_thread.attack_detected.connect(self.on_attack_detected)
            self.sniffer_thread.start()
            
            # Update UI
            self.is_monitoring = True
            self.monitor_button.setText("Stop Monitoring")
            self.status_label.setText("Status: Monitoring")
            self.interface_combo.setEnabled(False)
            
            # Start uptime timer
            self.start_time = datetime.now()
            self.uptime_timer.start(1000)  # Update every second
            
            self.log_message("Monitoring started successfully")
            
        except Exception as e:
            self.log_message(f"Error starting monitoring: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start monitoring: {e}")
            
    def stop_monitoring(self):
        """Stop WiFi monitoring."""
        try:
            self.log_message("Stopping monitoring...")
            
            if self.sniffer_thread:
                self.sniffer_thread.stop()
                self.sniffer_thread = None
                
            # Update UI
            self.is_monitoring = False
            self.monitor_button.setText("Start Monitoring")
            self.status_label.setText("Status: Stopped")
            self.interface_combo.setEnabled(True)
            
            # Stop uptime timer
            self.uptime_timer.stop()
            
            self.log_message("Monitoring stopped")
            
        except Exception as e:
            self.log_message(f"Error stopping monitoring: {e}")
            
    def on_attack_detected(self, attack_info: Dict[str, Any]):
        """Handle detected attacks."""
        self.attack_count += 1
        self.attack_count_label.setText(f"Attacks Detected: {self.attack_count}")
        
        # Add to attack table
        row = self.attack_table.rowCount()
        self.attack_table.insertRow(row)
        
        timestamp = datetime.fromtimestamp(attack_info['timestamp']).strftime('%H:%M:%S')
        
        self.attack_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.attack_table.setItem(row, 1, QTableWidgetItem(attack_info['type'].upper()))
        self.attack_table.setItem(row, 2, QTableWidgetItem(attack_info['attacker_mac']))
        self.attack_table.setItem(row, 3, QTableWidgetItem(attack_info['target_mac']))
        self.attack_table.setItem(row, 4, QTableWidgetItem(attack_info['bssid']))
        self.attack_table.setItem(row, 5, QTableWidgetItem(str(attack_info['reason_code'])))
        
        # Scroll to bottom
        self.attack_table.scrollToBottom()
        
        # Log attack
        attack_msg = f"🚨 {attack_info['type'].upper()} ATTACK: {attack_info['attacker_mac']} → {attack_info['target_mac']}"
        self.log_message(attack_msg)
        
        # Send system notification
        try:
            send_notification(
                "WiFi Attack Detected!",
                f"{attack_info['type'].upper()} attack from {attack_info['attacker_mac']}"
            )
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            
        # Show tray notification
        if hasattr(self, 'tray_icon'):
            self.tray_icon.showMessage(
                "WiFi Attack Detected!",
                attack_msg,
                QSystemTrayIcon.Warning,
                5000
            )
            
    def update_uptime(self):
        """Update the uptime display."""
        if self.start_time:
            uptime = datetime.now() - self.start_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            self.uptime_label.setText(f"Uptime: {uptime_str}")
            
    def log_message(self, message: str):
        """Add a message to the console output."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        self.console_output.append(formatted_message)
        self.logger.info(message)
        
    def tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()
            
    def closeEvent(self, event):
        """Handle window close event."""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.quit_application()
            
    def quit_application(self):
        """Quit the application."""
        if self.is_monitoring:
            self.stop_monitoring()
            
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
            
        QApplication.quit()
        
    def run(self):
        """Run the GUI application."""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            
        self.show()
        return app.exec_()