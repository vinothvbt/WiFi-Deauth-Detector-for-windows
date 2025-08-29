#!/usr/bin/env python3
"""
WiFi Deauth Detector - Main Application
A lightweight real-time WiFi deauthentication attack detector for Windows
"""

import sys
import os
import json
import time
import threading
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QTextEdit, QGroupBox,
                             QLineEdit, QCheckBox, QComboBox, QMessageBox, QSystemTrayIcon,
                             QMenu, QAction, QTabWidget, QFormLayout, QSpinBox)
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QIcon, QFont, QPixmap
import subprocess
import requests
from plyer import notification
# Import enhanced components - fallback to original if not available
try:
    from enhanced_wifi_monitor import EnhancedWiFiMonitor as WindowsWiFiMonitor, LegacyDeauthDetector
    from secure_network_manager import SecureNetworkManager as NetworkManager
    from secure_settings_manager import SecureSettingsManager as SettingsManager
    ENHANCED_MODE = True
except ImportError as e:
    print(f"Enhanced components not available ({e}), using standard components")
    from windows_wifi_monitor import WindowsWiFiMonitor, LegacyDeauthDetector
    ENHANCED_MODE = False

class DeauthDetector(QObject):
    """Enhanced deauth detection engine using Windows WiFi monitoring"""
    attack_detected = pyqtSignal(str, str, str)  # reason, timestamp, details
    
    def __init__(self, use_real_monitoring=True):
        super().__init__()
        self.is_monitoring = False
        self.use_real_monitoring = use_real_monitoring
        
        if self.use_real_monitoring:
            # Use real Windows WiFi monitoring
            self.wifi_monitor = WindowsWiFiMonitor()
            self.wifi_monitor.suspicious_disconnect.connect(self._handle_suspicious_disconnect)
        else:
            # Use legacy demo detector for testing
            self.legacy_detector = LegacyDeauthDetector()
            self.legacy_detector.attack_detected.connect(self._handle_legacy_attack)
        
    def start_monitoring(self):
        """Start monitoring for deauth attacks"""
        if not self.is_monitoring:
            self.is_monitoring = True
            if self.use_real_monitoring:
                self.wifi_monitor.start_monitoring()
            else:
                self.legacy_detector.start_monitoring()
            
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        if self.use_real_monitoring:
            self.wifi_monitor.stop_monitoring()
        else:
            self.legacy_detector.stop_monitoring()
    
    def _handle_suspicious_disconnect(self, reason, timestamp, details):
        """Handle suspicious disconnect detected by Windows WiFi monitor"""
        # Emit in the format expected by the GUI (reason as "attacker", details as "target")
        self.attack_detected.emit(reason, details, timestamp)
    
    def _handle_legacy_attack(self, attacker_mac, target_mac, timestamp):
        """Handle legacy simulated attack for demo purposes"""
        self.attack_detected.emit(attacker_mac, target_mac, timestamp)
    
    def get_recent_events(self):
        """Get recent WiFi events for display"""
        if self.use_real_monitoring:
            return self.wifi_monitor.get_recent_events()
        else:
            return []
    
    def get_network_status(self):
        """Get current network status"""
        if self.use_real_monitoring:
            return self.wifi_monitor.get_network_interfaces()
        else:
            return []

# NetworkManager is now imported from secure_network_manager if available
if not ENHANCED_MODE:
    class NetworkManager:
        """Legacy network switching functionality with basic security"""
        
        @staticmethod
        def get_available_profiles():
            """Get list of available WiFi profiles"""
            try:
                result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                      capture_output=True, text=True, timeout=10)
                profiles = []
                for line in result.stdout.split('\n'):
                    if 'All User Profile' in line and ':' in line:
                        profile_name = line.split(':')[1].strip()
                        # Basic sanitization
                        if profile_name and len(profile_name) <= 32:
                            profiles.append(profile_name)
                return profiles
            except Exception as e:
                print(f"Error getting WiFi profiles: {e}")
                return []
        
        @staticmethod
        def connect_to_network(profile_name):
            """Connect to a specific WiFi network with basic validation"""
            try:
                # Basic input validation
                if not profile_name or len(profile_name) > 32:
                    print(f"Invalid profile name: {profile_name}")
                    return False
                
                result = subprocess.run(['netsh', 'wlan', 'connect', f'name="{profile_name}"'], 
                                      capture_output=True, text=True, timeout=15)
                return result.returncode == 0
            except Exception as e:
                print(f"Error connecting to network {profile_name}: {e}")
                return False

class DiscordWebhook:
    """Handles Discord webhook notifications"""
    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        
    def send_alert(self, attacker_mac, target_mac, timestamp):
        """Send deauth alert to Discord"""
        if not self.webhook_url:
            return False
            
        try:
            embed = {
                "title": "🚨 WiFi Deauth Attack Detected!",
                "color": 0xff0000,
                "fields": [
                    {"name": "Attacker MAC", "value": attacker_mac, "inline": True},
                    {"name": "Target MAC", "value": target_mac, "inline": True},
                    {"name": "Timestamp", "value": timestamp, "inline": False}
                ],
                "footer": {"text": "WiFi Deauth Detector"}
            }
            
            data = {"embeds": [embed]}
            response = requests.post(self.webhook_url, json=data, timeout=10)
            return response.status_code == 204
        except Exception as e:
            print(f"Error sending Discord webhook: {e}")
            return False

# SettingsManager is now imported from secure_settings_manager if available
if not ENHANCED_MODE:
    class SettingsManager:
        """Legacy settings management with basic security"""
        
        def __init__(self, settings_file="settings.json"):
            self.settings_file = settings_file
            self.default_settings = {
                "backup_network": "",
                "discord_webhook": "",
                "discord_enabled": False,
                "auto_switch_enabled": False,
                "auto_switch_confirm": True,
                "notifications_enabled": True,
                "log_attacks": True,
                "demo_mode": False
            }
            self.settings = self.load_settings()
        
        def load_settings(self):
            """Load settings from file with validation"""
            try:
                if os.path.exists(self.settings_file):
                    with open(self.settings_file, 'r') as f:
                        loaded = json.load(f)
                        # Merge with defaults and validate
                        settings = self.default_settings.copy()
                        for key, value in loaded.items():
                            if key in self.default_settings:
                                # Basic validation
                                if key == "backup_network" and isinstance(value, str) and len(value) <= 32:
                                    settings[key] = value
                                elif key == "discord_webhook" and isinstance(value, str):
                                    if not value or value.startswith('https://discord.com/api/webhooks/'):
                                        settings[key] = value
                                elif isinstance(value, type(self.default_settings[key])):
                                    settings[key] = value
                        return settings
                return self.default_settings.copy()
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.default_settings.copy()
        
        def save_settings(self):
            """Save settings to file with basic security"""
            try:
                # Set restrictive permissions
                with open(self.settings_file, 'w') as f:
                    json.dump(self.settings, f, indent=2)
                try:
                    os.chmod(self.settings_file, 0o600)  # Owner read/write only
                except:
                    pass  # May fail on Windows
                return True
            except Exception as e:
                print(f"Error saving settings: {e}")
                return False
        
        def get(self, key, default=None):
            """Get setting value"""
            return self.settings.get(key, default)
        
        def set(self, key, value):
            """Set setting value with basic validation"""
            if key == "backup_network" and isinstance(value, str) and len(value) > 32:
                print(f"Network name too long: {value}")
                return
            elif key == "discord_webhook" and value and not value.startswith('https://discord.com/api/webhooks/'):
                print(f"Invalid Discord webhook URL: {value}")
                return
            self.settings[key] = value

class WiFiDeauthDetectorGUI(QMainWindow):
    """Main GUI window"""
    
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        
        # Determine monitoring mode based on platform and settings
        use_real_monitoring = os.name == 'nt'  # Windows
        if self.settings.get("demo_mode", False):
            use_real_monitoring = False
            
        self.detector = DeauthDetector(use_real_monitoring=use_real_monitoring)
        self.discord_webhook = DiscordWebhook(self.settings.get("discord_webhook"))
        self.network_manager = NetworkManager()
        
        # Setup UI
        self.init_ui()
        self.setup_system_tray()
        
        # Connect signals
        self.detector.attack_detected.connect(self.handle_attack_detected)
        
        # Load settings into UI
        self.load_settings_to_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        title = "WiFi Deauth Detector v2.1" + (" [Enhanced]" if ENHANCED_MODE else " [Standard]")
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Monitor tab
        monitor_tab = self.create_monitor_tab()
        tab_widget.addTab(monitor_tab, "Monitor")
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        tab_widget.addTab(settings_tab, "Settings")
        
        # Logs tab
        logs_tab = self.create_logs_tab()
        tab_widget.addTab(logs_tab, "Logs")
        
    def create_monitor_tab(self):
        """Create the monitoring tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Detection method info
        info_group = QGroupBox("Detection Method")
        info_layout = QVBoxLayout(info_group)
        
        use_real_monitoring = os.name == 'nt' and not self.settings.get("demo_mode", False)
        if use_real_monitoring:
            mode_desc = "Enhanced" if ENHANCED_MODE else "Normal"
            method_text = f"🔍 {mode_desc} Mode: Advanced WiFi connection monitoring\n" \
                         "• Sophisticated pattern recognition\n" \
                         "• Multi-factor threat assessment\n" \
                         "• Signal strength analysis\n" \
                         "• Temporal attack detection"
        else:
            method_text = "🎭 Demo Mode: Simulated deauth attack detection\n" \
                         "• For demonstration purposes\n" \
                         "• Real monitoring requires Windows"
        
        method_label = QLabel(method_text)
        method_label.setStyleSheet("color: #666; font-size: 10px;")
        info_layout.addWidget(method_label)
        layout.addWidget(info_group)
        
        # Status section
        status_group = QGroupBox("Detection Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("⚪ Monitoring Stopped")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        status_layout.addWidget(self.status_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Monitoring")
        self.stop_btn = QPushButton("Stop Monitoring")
        self.stop_btn.setEnabled(False)
        
        self.start_btn.clicked.connect(self.start_monitoring)
        self.stop_btn.clicked.connect(self.stop_monitoring)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        status_layout.addLayout(button_layout)
        
        layout.addWidget(status_group)
        
        # Recent alerts section
        alerts_group = QGroupBox("Recent Alerts")
        alerts_layout = QVBoxLayout(alerts_group)
        
        self.alerts_display = QTextEdit()
        self.alerts_display.setReadOnly(True)
        self.alerts_display.setMaximumHeight(200)
        alerts_layout.addWidget(self.alerts_display)
        
        layout.addWidget(alerts_group)
        
        # Statistics section
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout(stats_group)
        
        self.total_attacks_label = QLabel("0")
        self.last_attack_label = QLabel("Never")
        
        stats_layout.addRow("Suspicious Events Detected:", self.total_attacks_label)
        stats_layout.addRow("Last Event:", self.last_attack_label)
        
        layout.addWidget(stats_group)
        
        return widget
    
    def create_settings_tab(self):
        """Create the settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Network switching settings
        network_group = QGroupBox("Auto Network Switching")
        network_layout = QFormLayout(network_group)
        
        self.auto_switch_cb = QCheckBox("Enable auto-switch on attack")
        self.confirm_switch_cb = QCheckBox("Confirm before switching")
        
        self.backup_network_combo = QComboBox()
        self.backup_network_combo.setEditable(True)
        self.refresh_networks_btn = QPushButton("Refresh Networks")
        self.refresh_networks_btn.clicked.connect(self.refresh_network_list)
        
        network_layout.addRow(self.auto_switch_cb)
        network_layout.addRow(self.confirm_switch_cb)
        network_layout.addRow("Backup Network:", self.backup_network_combo)
        network_layout.addRow("", self.refresh_networks_btn)
        
        layout.addWidget(network_group)
        
        # Discord settings
        discord_group = QGroupBox("Discord Webhook Alerts")
        discord_layout = QFormLayout(discord_group)
        
        self.discord_enabled_cb = QCheckBox("Enable Discord alerts")
        self.discord_webhook_edit = QLineEdit()
        self.discord_webhook_edit.setPlaceholderText("https://discord.com/api/webhooks/...")
        self.test_discord_btn = QPushButton("Test Webhook")
        self.test_discord_btn.clicked.connect(self.test_discord_webhook)
        
        discord_layout.addRow(self.discord_enabled_cb)
        discord_layout.addRow("Webhook URL:", self.discord_webhook_edit)
        discord_layout.addRow("", self.test_discord_btn)
        
        layout.addWidget(discord_group)
        
        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout(general_group)
        
        self.notifications_cb = QCheckBox("Enable system notifications")
        self.logging_cb = QCheckBox("Log attacks to file")
        self.demo_mode_cb = QCheckBox("Demo mode (simulated attacks for testing)")
        
        general_layout.addRow(self.notifications_cb)
        general_layout.addRow(self.logging_cb)
        general_layout.addRow(self.demo_mode_cb)
        
        layout.addWidget(general_group)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        # Load networks on startup
        self.refresh_network_list()
        
        return widget
    
    def create_logs_tab(self):
        """Create the logs tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        
        # Log controls
        button_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear Logs")
        export_btn = QPushButton("Export Logs")
        
        clear_btn.clicked.connect(self.clear_logs)
        export_btn.clicked.connect(self.export_logs)
        
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(export_btn)
        layout.addLayout(button_layout)
        
        return widget
    
    def setup_system_tray(self):
        """Setup system tray icon with enhanced normal mode information"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            # Create tray menu
            tray_menu = QMenu()
            
            # Status info
            use_real_monitoring = os.name == 'nt' and not self.settings.get("demo_mode", False)
            mode_text = "Normal Mode" if use_real_monitoring else "Demo Mode"
            mode_action = QAction(f"🔍 {mode_text} Active", self)
            mode_action.setEnabled(False)
            tray_menu.addAction(mode_action)
            
            tray_menu.addSeparator()
            
            # Main actions
            show_action = QAction("Show Window", self)
            start_action = QAction("Start Monitoring", self)
            stop_action = QAction("Stop Monitoring", self)
            
            show_action.triggered.connect(self.show)
            start_action.triggered.connect(self.start_monitoring)
            stop_action.triggered.connect(self.stop_monitoring)
            
            tray_menu.addAction(show_action)
            tray_menu.addAction(start_action)
            tray_menu.addAction(stop_action)
            tray_menu.addSeparator()
            
            # Quick settings
            settings_action = QAction("Settings", self)
            settings_action.triggered.connect(lambda: self.show() and None)
            tray_menu.addAction(settings_action)
            
            tray_menu.addSeparator()
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.setToolTip(f"WiFi Deauth Detector v2.0\n{mode_text} - Click to open")
            self.tray_icon.show()
            
            # Add double-click to show window
            self.tray_icon.activated.connect(self._tray_icon_activated)
    
    def _tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def start_monitoring(self):
        """Start deauth monitoring"""
        self.detector.start_monitoring()
        self.status_label.setText("🟢 Monitoring Active")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_message("Monitoring started")
    
    def stop_monitoring(self):
        """Stop deauth monitoring"""
        self.detector.stop_monitoring()
        self.status_label.setText("🔴 Monitoring Stopped")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log_message("Monitoring stopped")
    
    def handle_attack_detected(self, reason_or_attacker, details_or_target, timestamp):
        """Handle detected deauth attack or suspicious event"""
        # Determine if this is the new format (reason, details, timestamp) or legacy (attacker, target, timestamp)
        use_real_monitoring = os.name == 'nt' and not self.settings.get("demo_mode", False)
        
        if use_real_monitoring:
            # New format: reason, details, timestamp
            alert_text = f"[{timestamp}] SUSPICIOUS ACTIVITY! {reason_or_attacker}: {details_or_target}"
            notification_title = "WiFi Security Alert!"
            notification_message = f"{reason_or_attacker}"
            
            # For Discord webhook, adapt to expected format
            webhook_attacker = reason_or_attacker
            webhook_target = details_or_target
        else:
            # Legacy format: attacker_mac, target_mac, timestamp
            alert_text = f"[{timestamp}] SIMULATED ATTACK! Attacker: {reason_or_attacker} → Target: {details_or_target}"
            notification_title = "WiFi Deauth Attack Detected!"
            notification_message = f"Attacker: {reason_or_attacker}"
            
            webhook_attacker = reason_or_attacker
            webhook_target = details_or_target
        
        # Update UI
        self.alerts_display.append(alert_text)
        
        # Update statistics
        current_total = int(self.total_attacks_label.text())
        self.total_attacks_label.setText(str(current_total + 1))
        self.last_attack_label.setText(timestamp)
        
        # Log to file
        if self.settings.get("log_attacks"):
            self.log_message(f"SECURITY EVENT - {alert_text}")
        
        # System notification
        if self.settings.get("notifications_enabled"):
            notification.notify(
                title=notification_title,
                message=notification_message,
                timeout=10
            )
        
        # Discord webhook
        if self.settings.get("discord_enabled"):
            webhook = DiscordWebhook(self.settings.get("discord_webhook"))
            webhook.send_alert(webhook_attacker, webhook_target, timestamp)
        
        # Auto network switch (only for real suspicious events, not simulated)
        if use_real_monitoring and self.settings.get("auto_switch_enabled"):
            self.handle_auto_switch()
    
    def handle_auto_switch(self):
        """Handle automatic network switching"""
        backup_network = self.settings.get("backup_network")
        if not backup_network:
            return
        
        if self.settings.get("auto_switch_confirm"):
            reply = QMessageBox.question(
                self, 
                "Network Switch Confirmation",
                f"Suspicious WiFi activity detected! Switch to backup network '{backup_network}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Enhanced network manager returns tuple (success, message)
        if ENHANCED_MODE and hasattr(self.network_manager, 'connect_to_network'):
            try:
                success, message = self.network_manager.connect_to_network(backup_network)
            except (TypeError, ValueError):
                # Fallback for legacy manager
                success = self.network_manager.connect_to_network(backup_network)
                message = f"Connected to {backup_network}" if success else f"Failed to connect to {backup_network}"
        else:
            success = self.network_manager.connect_to_network(backup_network)
            message = f"Connected to {backup_network}" if success else f"Failed to connect to {backup_network}"
        
        self.log_message(f"Network switch attempt: {message}")
        if success:
            QMessageBox.information(self, "Network Switch", message)
        else:
            QMessageBox.warning(self, "Network Switch Failed", message)
    
    def refresh_network_list(self):
        """Refresh the list of available networks"""
        profiles = self.network_manager.get_available_profiles()
        self.backup_network_combo.clear()
        self.backup_network_combo.addItems(profiles)
    
    def test_discord_webhook(self):
        """Test Discord webhook"""
        webhook_url = self.discord_webhook_edit.text()
        if not webhook_url:
            QMessageBox.warning(self, "Error", "Please enter a webhook URL")
            return
        
        webhook = DiscordWebhook(webhook_url)
        success = webhook.send_alert("TEST:MAC", "TEST:TARGET", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if success:
            QMessageBox.information(self, "Success", "Test webhook sent successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to send test webhook")
    
    def load_settings_to_ui(self):
        """Load settings into UI controls"""
        self.auto_switch_cb.setChecked(self.settings.get("auto_switch_enabled"))
        self.confirm_switch_cb.setChecked(self.settings.get("auto_switch_confirm"))
        self.discord_enabled_cb.setChecked(self.settings.get("discord_enabled"))
        self.discord_webhook_edit.setText(self.settings.get("discord_webhook"))
        self.notifications_cb.setChecked(self.settings.get("notifications_enabled"))
        self.logging_cb.setChecked(self.settings.get("log_attacks"))
        self.demo_mode_cb.setChecked(self.settings.get("demo_mode"))
        
        # Set backup network if it exists
        backup_network = self.settings.get("backup_network")
        if backup_network:
            index = self.backup_network_combo.findText(backup_network)
            if index >= 0:
                self.backup_network_combo.setCurrentIndex(index)
            else:
                self.backup_network_combo.setEditText(backup_network)
    
    def save_settings(self):
        """Save settings from UI"""
        self.settings.set("auto_switch_enabled", self.auto_switch_cb.isChecked())
        self.settings.set("auto_switch_confirm", self.confirm_switch_cb.isChecked())
        self.settings.set("backup_network", self.backup_network_combo.currentText())
        self.settings.set("discord_enabled", self.discord_enabled_cb.isChecked())
        self.settings.set("discord_webhook", self.discord_webhook_edit.text())
        self.settings.set("notifications_enabled", self.notifications_cb.isChecked())
        self.settings.set("log_attacks", self.logging_cb.isChecked())
        self.settings.set("demo_mode", self.demo_mode_cb.isChecked())
        
        if self.settings.save_settings():
            QMessageBox.information(self, "Success", "Settings saved successfully!\nRestart the application for demo mode changes to take effect.")
        else:
            QMessageBox.warning(self, "Error", "Failed to save settings")
        
        # Update Discord webhook instance
        self.discord_webhook = DiscordWebhook(self.settings.get("discord_webhook"))
    
    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_display.append(log_entry)
        
        # Also save to file if logging enabled
        if self.settings.get("log_attacks"):
            try:
                with open("deauth_log.txt", "a") as f:
                    f.write(log_entry + "\n")
            except Exception as e:
                print(f"Error writing to log file: {e}")
    
    def clear_logs(self):
        """Clear log display"""
        self.log_display.clear()
    
    def export_logs(self):
        """Export logs to file"""
        from PyQt5.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", "deauth_logs_export.txt", "Text files (*.txt)"
        )
        if filename:
            try:
                with open(filename, "w") as f:
                    f.write(self.log_display.toPlainText())
                QMessageBox.information(self, "Success", f"Logs exported to {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export logs: {e}")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray
    
    # Create and show main window
    window = WiFiDeauthDetectorGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()