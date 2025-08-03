import sys
import logging
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QTextEdit, QDialog, 
                             QScrollArea, QMessageBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import json

class LogEntry:
    def __init__(self, timestamp, level, message, source_mac=None, target_mac=None):
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.source_mac = source_mac
        self.target_mac = target_mac
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message,
            'source_mac': self.source_mac,
            'target_mac': self.target_mac
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            level=data['level'],
            message=data['message'],
            source_mac=data.get('source_mac'),
            target_mac=data.get('target_mac')
        )

class LogManager:
    def __init__(self, log_file="deauth_logs.json"):
        self.log_file = log_file
        self.logs = []
        self.load_logs()
    
    def add_log(self, level, message, source_mac=None, target_mac=None):
        log_entry = LogEntry(datetime.now(), level, message, source_mac, target_mac)
        self.logs.append(log_entry)
        self.save_logs()
        return log_entry
    
    def get_recent_logs(self, count=20):
        return self.logs[-count:] if len(self.logs) >= count else self.logs
    
    def load_logs(self):
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.logs = [LogEntry.from_dict(entry) for entry in data]
        except Exception as e:
            print(f"Error loading logs: {e}")
            self.logs = []
    
    def save_logs(self):
        try:
            with open(self.log_file, 'w') as f:
                json.dump([log.to_dict() for log in self.logs], f, indent=2)
        except Exception as e:
            print(f"Error saving logs: {e}")

class LogViewerDialog(QDialog):
    def __init__(self, logs, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Last 20 Deauth Detection Logs")
        self.setGeometry(200, 200, 800, 600)
        self.setup_ui(logs)
    
    def setup_ui(self, logs):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Recent WiFi Deauth Detection Logs")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Log display area
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.setFont(QFont("Consolas", 9))
        
        if not logs:
            log_text.setText("No logs available.")
        else:
            log_content = []
            for log in reversed(logs):  # Show most recent first
                timestamp_str = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                mac_info = ""
                if log.source_mac and log.target_mac:
                    mac_info = f" | Source: {log.source_mac} | Target: {log.target_mac}"
                elif log.source_mac:
                    mac_info = f" | MAC: {log.source_mac}"
                
                log_line = f"[{timestamp_str}] {log.level}: {log.message}{mac_info}"
                log_content.append(log_line)
            
            log_text.setText("\n".join(log_content))
        
        layout.addWidget(log_text)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)

class WiFiDeauthDetector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.log_manager = LogManager()
        self.detection_active = False
        self.setup_ui()
        self.setup_demo_timer()
        
        # Add some initial logs for demonstration
        self.add_demo_logs()
    
    def setup_ui(self):
        self.setWindowTitle("WiFi Deauth Detector")
        self.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("WiFi Deauthentication Attack Detector")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Status display
        self.status_label = QLabel("Status: Idle")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Detection log area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(150)
        layout.addWidget(self.log_display)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Detection")
        self.start_button.clicked.connect(self.toggle_detection)
        button_layout.addWidget(self.start_button)
        
        self.open_logs_button = QPushButton("Open Logs")
        self.open_logs_button.clicked.connect(self.open_logs)
        button_layout.addWidget(self.open_logs_button)
        
        layout.addLayout(button_layout)
        
        # Info text
        info_text = QLabel("Note: This is a demonstration version. In production, this would monitor wireless traffic for deauth attacks.")
        info_text.setWordWrap(True)
        info_text.setFont(QFont("Arial", 9))
        info_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_text)
        
        central_widget.setLayout(layout)
    
    def setup_demo_timer(self):
        # Timer for demo deauth detection events
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.simulate_detection)
    
    def add_demo_logs(self):
        # Add some sample logs for demonstration
        sample_logs = [
            ("INFO", "Application started"),
            ("INFO", "Monitoring interface initialized"),
            ("WARNING", "Deauth packet detected", "AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"),
            ("CRITICAL", "Multiple deauth packets detected - possible attack!", "AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"),
            ("INFO", "Monitoring resumed"),
            ("WARNING", "Suspicious deauth activity", "FF:EE:DD:CC:BB:AA", "66:55:44:33:22:11"),
        ]
        
        for level, message, *macs in sample_logs:
            source_mac = macs[0] if len(macs) > 0 else None
            target_mac = macs[1] if len(macs) > 1 else None
            self.log_manager.add_log(level, message, source_mac, target_mac)
    
    def toggle_detection(self):
        if not self.detection_active:
            self.start_detection()
        else:
            self.stop_detection()
    
    def start_detection(self):
        self.detection_active = True
        self.start_button.setText("Stop Detection")
        self.status_label.setText("Status: Monitoring for deauth attacks...")
        self.log_display.append("Detection started...")
        
        # Start demo timer (simulates detection events)
        self.demo_timer.start(5000)  # Trigger every 5 seconds
        
        self.log_manager.add_log("INFO", "Deauth detection started")
    
    def stop_detection(self):
        self.detection_active = False
        self.start_button.setText("Start Detection")
        self.status_label.setText("Status: Idle")
        self.log_display.append("Detection stopped.")
        
        # Stop demo timer
        self.demo_timer.stop()
        
        self.log_manager.add_log("INFO", "Deauth detection stopped")
    
    def simulate_detection(self):
        # Simulate occasional deauth detection
        import random
        
        if random.random() < 0.3:  # 30% chance of detection
            source_mac = f"{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}"
            target_mac = f"{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}"
            
            message = "Deauth packet detected"
            self.log_display.append(f"🚨 {message} - Source: {source_mac}")
            self.log_manager.add_log("WARNING", message, source_mac, target_mac)
    
    def open_logs(self):
        # Get last 20 logs and display in popup
        recent_logs = self.log_manager.get_recent_logs(20)
        dialog = LogViewerDialog(recent_logs, self)
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    
    # Check if running on Windows with proper privileges (in a real implementation)
    detector = WiFiDeauthDetector()
    detector.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()