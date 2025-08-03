#!/usr/bin/env python3
"""
WiFi Deauth Detector - Windows GUI Application
A real-time WiFi deauthentication attack detector with PyQt5 interface.
"""

import sys
import threading
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QTextEdit, QComboBox, QLabel, 
                             QStatusBar, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

try:
    import scapy.all as scapy
    from scapy.layers.dot11 import Dot11, Dot11Deauth, Dot11Disas
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

try:
    import netifaces
    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class PacketSnifferThread(QThread):
    """Thread for packet sniffing to avoid blocking the GUI."""
    
    packet_received = pyqtSignal(str)  # Signal to emit packet information
    status_changed = pyqtSignal(str)   # Signal to emit status updates
    
    def __init__(self, interface=None):
        super().__init__()
        self.interface = interface
        self.running = False
        self.packet_count = 0
        
    def run(self):
        """Main packet sniffing loop."""
        if not SCAPY_AVAILABLE:
            self.status_changed.emit("Error: Scapy not available")
            return
            
        self.running = True
        self.status_changed.emit(f"Starting packet capture on {self.interface}")
        
        try:
            # Start packet sniffing
            scapy.sniff(
                iface=self.interface,
                prn=self.process_packet,
                stop_filter=lambda x: not self.running,
                store=False
            )
        except Exception as e:
            self.status_changed.emit(f"Error: {str(e)}")
            
    def process_packet(self, packet):
        """Process captured packets and detect deauth frames."""
        if not self.running:
            return
            
        self.packet_count += 1
        
        # Check if packet is a deauth or disassociation frame
        if packet.haslayer(Dot11Deauth) or packet.haslayer(Dot11Disas):
            frame_type = "Deauth" if packet.haslayer(Dot11Deauth) else "Disassoc"
            
            # Extract MAC addresses
            if packet.haslayer(Dot11):
                src_mac = packet[Dot11].addr2 if packet[Dot11].addr2 else "Unknown"
                dst_mac = packet[Dot11].addr1 if packet[Dot11].addr1 else "Unknown"
                
                log_entry = f"[ALERT] {frame_type} detected! Src: {src_mac} -> Dst: {dst_mac}"
                self.packet_received.emit(log_entry)
            else:
                log_entry = f"[ALERT] {frame_type} frame detected (no MAC info)"
                self.packet_received.emit(log_entry)
        else:
            # Log other packets with less detail
            if self.packet_count % 100 == 0:  # Log every 100th packet to avoid spam
                log_entry = f"[INFO] Processed {self.packet_count} packets..."
                self.packet_received.emit(log_entry)
                
    def stop_sniffing(self):
        """Stop the packet sniffing."""
        self.running = False
        self.status_changed.emit("Stopping packet capture...")


class WiFiDeauthDetectorGUI(QMainWindow):
    """Main GUI window for the WiFi Deauth Detector."""
    
    def __init__(self):
        super().__init__()
        self.sniffer_thread = None
        self.is_scanning = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("WiFi Deauth Detector")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create interface selection row
        interface_layout = QHBoxLayout()
        interface_label = QLabel("Network Interface:")
        interface_label.setMinimumWidth(120)
        
        self.interface_combo = QComboBox()
        self.interface_combo.setMinimumWidth(200)
        self.populate_interfaces()
        
        interface_layout.addWidget(interface_label)
        interface_layout.addWidget(self.interface_combo)
        interface_layout.addStretch()
        
        # Create control buttons row
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Scan")
        self.start_button.clicked.connect(self.start_scanning)
        self.start_button.setMinimumWidth(100)
        
        self.stop_button = QPushButton("Stop Scan")
        self.stop_button.clicked.connect(self.stop_scanning)
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumWidth(100)
        
        self.clear_button = QPushButton("Clear Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setMinimumWidth(100)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        
        # Create packet log display
        log_label = QLabel("Packet Logs:")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        
        # Add initial welcome message
        welcome_msg = "WiFi Deauth Detector initialized.\n"
        welcome_msg += "Select a network interface and click 'Start Scan' to begin monitoring.\n"
        welcome_msg += "Deauthentication and disassociation frames will be highlighted.\n"
        welcome_msg += "-" * 60 + "\n"
        self.log_text.append(welcome_msg)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Select interface and start scanning")
        
        # Add all components to main layout
        main_layout.addLayout(interface_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(log_label)
        main_layout.addWidget(self.log_text)
        
        # Check dependencies on startup
        self.check_dependencies()
        
    def populate_interfaces(self):
        """Populate the interface dropdown with available network interfaces."""
        self.interface_combo.clear()
        
        # Add a default option
        self.interface_combo.addItem("Select Interface...")
        
        interfaces = []
        
        if NETIFACES_AVAILABLE:
            try:
                # Use netifaces to get interfaces
                for iface in netifaces.interfaces():
                    interfaces.append(iface)
            except Exception as e:
                self.log_text.append(f"[ERROR] Failed to get interfaces via netifaces: {e}")
        
        if PSUTIL_AVAILABLE:
            try:
                # Use psutil as backup
                net_if_addrs = psutil.net_if_addrs()
                for iface in net_if_addrs.keys():
                    if iface not in interfaces:
                        interfaces.append(iface)
            except Exception as e:
                self.log_text.append(f"[ERROR] Failed to get interfaces via psutil: {e}")
        
        if not interfaces:
            # Fallback to common Windows interface names
            interfaces = ["Wi-Fi", "Wireless Network Connection", "wlan0", "wlan1"]
            self.log_text.append("[WARNING] Could not detect interfaces, using common names")
        
        # Add interfaces to combo box
        for iface in sorted(interfaces):
            self.interface_combo.addItem(iface)
            
    def check_dependencies(self):
        """Check if required dependencies are available."""
        issues = []
        
        if not SCAPY_AVAILABLE:
            issues.append("Scapy is not installed")
            
        if not NETIFACES_AVAILABLE:
            issues.append("netifaces is not installed (optional)")
            
        if not PSUTIL_AVAILABLE:
            issues.append("psutil is not installed (optional)")
            
        if issues:
            msg = "Dependency issues detected:\n" + "\n".join(f"- {issue}" for issue in issues)
            msg += "\n\nPlease run: pip install -r requirements.txt"
            self.log_text.append(f"[WARNING] {msg}")
            
    def start_scanning(self):
        """Start packet scanning."""
        if self.interface_combo.currentIndex() == 0:
            QMessageBox.warning(self, "Warning", "Please select a network interface first.")
            return
            
        if not SCAPY_AVAILABLE:
            QMessageBox.critical(self, "Error", "Scapy is not available. Please install it first.")
            return
            
        selected_interface = self.interface_combo.currentText()
        
        # Create and start sniffer thread
        self.sniffer_thread = PacketSnifferThread(selected_interface)
        self.sniffer_thread.packet_received.connect(self.add_log_entry)
        self.sniffer_thread.status_changed.connect(self.update_status)
        
        try:
            self.sniffer_thread.start()
            self.is_scanning = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.interface_combo.setEnabled(False)
            
            self.add_log_entry(f"[INFO] Started scanning on interface: {selected_interface}")
            self.update_status(f"Scanning on {selected_interface}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start scanning: {str(e)}")
            self.update_status("Failed to start scanning")
            
    def stop_scanning(self):
        """Stop packet scanning."""
        if self.sniffer_thread and self.sniffer_thread.isRunning():
            self.sniffer_thread.stop_sniffing()
            self.sniffer_thread.wait(5000)  # Wait up to 5 seconds for thread to finish
            
        self.is_scanning = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.interface_combo.setEnabled(True)
        
        self.add_log_entry("[INFO] Scanning stopped")
        self.update_status("Ready - Scanning stopped")
        
    def clear_logs(self):
        """Clear the log display."""
        self.log_text.clear()
        welcome_msg = "Logs cleared.\n"
        welcome_msg += "-" * 60 + "\n"
        self.log_text.append(welcome_msg)
        
    def add_log_entry(self, message):
        """Add a log entry to the text display."""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def update_status(self, message):
        """Update the status bar."""
        self.status_bar.showMessage(message)
        
    def closeEvent(self, event):
        """Handle application close event."""
        if self.is_scanning:
            self.stop_scanning()
        event.accept()


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("WiFi Deauth Detector")
    
    # Create and show main window
    window = WiFiDeauthDetectorGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()