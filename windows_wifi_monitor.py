#!/usr/bin/env python3
"""
Windows WiFi Connection Monitor
Monitors WiFi connection events using native Windows APIs instead of monitor mode
"""

import time
import threading
import subprocess
import json
import re
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal
import psutil


class WindowsWiFiMonitor(QObject):
    """Monitor WiFi connection events using Windows native APIs"""
    
    # Signal emitted when suspicious disconnect pattern detected
    suspicious_disconnect = pyqtSignal(str, str, str)  # reason, timestamp, details
    
    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        self.monitor_thread = None
        self.disconnect_history = []
        self.last_check_time = datetime.now()
        
        # Suspicious disconnect reason codes (common in deauth attacks)
        self.suspicious_reasons = {
            1: "Unspecified reason",
            2: "Previous authentication no longer valid", 
            3: "Deauthenticated because sending STA is leaving",
            6: "Class 2 frame received from nonauthenticated STA",
            7: "Class 3 frame received from nonassociated STA",
            8: "Disassociated because sending STA is leaving"
        }
        
        # Pattern detection settings
        self.max_disconnects_per_minute = 3
        self.suspicious_window_minutes = 5
        
    def start_monitoring(self):
        """Start monitoring WiFi connection events"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        last_connection_status = self._get_wifi_status()
        
        while self.is_monitoring:
            try:
                time.sleep(2)  # Check every 2 seconds
                
                current_status = self._get_wifi_status()
                
                # Detect disconnect events
                if last_connection_status.get('connected') and not current_status.get('connected'):
                    self._handle_disconnect_event(current_status)
                
                # Check for suspicious patterns periodically
                if (datetime.now() - self.last_check_time).seconds >= 30:
                    self._analyze_disconnect_patterns()
                    self.last_check_time = datetime.now()
                
                last_connection_status = current_status
                
            except Exception as e:
                print(f"Error in WiFi monitoring loop: {e}")
                time.sleep(5)  # Wait longer on error
                
    def _get_wifi_status(self):
        """Get current WiFi connection status using netsh"""
        try:
            # Get WiFi interface status
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True, text=True, shell=True, timeout=10
            )
            
            if result.returncode != 0:
                return {'connected': False, 'ssid': None, 'signal': 0}
            
            # Parse output
            lines = result.stdout.split('\n')
            status = {
                'connected': False,
                'ssid': None,
                'signal': 0,
                'state': 'disconnected'
            }
            
            for line in lines:
                line = line.strip()
                if 'State' in line and ':' in line:
                    state = line.split(':')[1].strip().lower()
                    status['state'] = state
                    status['connected'] = state == 'connected'
                elif 'SSID' in line and ':' in line:
                    ssid = line.split(':')[1].strip()
                    if ssid and ssid != 'N/A':
                        status['ssid'] = ssid
                elif 'Signal' in line and ':' in line:
                    signal_text = line.split(':')[1].strip()
                    # Extract percentage from signal strength
                    match = re.search(r'(\d+)%', signal_text)
                    if match:
                        status['signal'] = int(match.group(1))
            
            return status
            
        except Exception as e:
            print(f"Error getting WiFi status: {e}")
            return {'connected': False, 'ssid': None, 'signal': 0}
    
    def _handle_disconnect_event(self, status):
        """Handle a WiFi disconnect event"""
        timestamp = datetime.now()
        
        # Record the disconnect
        disconnect_info = {
            'timestamp': timestamp,
            'ssid': status.get('ssid', 'Unknown'),
            'state': status.get('state', 'disconnected')
        }
        
        self.disconnect_history.append(disconnect_info)
        
        # Keep only recent history (last hour)
        cutoff_time = timestamp - timedelta(hours=1)
        self.disconnect_history = [
            d for d in self.disconnect_history 
            if d['timestamp'] > cutoff_time
        ]
        
        print(f"WiFi disconnect detected: {disconnect_info}")
        
        # Check if this looks like a potential attack
        self._check_immediate_suspicion(disconnect_info)
    
    def _check_immediate_suspicion(self, disconnect_info):
        """Check if this single disconnect looks suspicious"""
        # For now, treat unexpected disconnects from known networks as suspicious
        # In a real implementation, we could check additional factors like:
        # - Signal strength before disconnect
        # - Recent connection stability
        # - Time of day patterns
        
        if disconnect_info['ssid'] and disconnect_info['ssid'] != 'Unknown':
            # This was a disconnect from an active connection
            reason = "Unexpected WiFi disconnect"
            timestamp = disconnect_info['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            details = f"Disconnected from {disconnect_info['ssid']}"
            
            # Emit signal for immediate notification
            self.suspicious_disconnect.emit(reason, timestamp, details)
    
    def _analyze_disconnect_patterns(self):
        """Analyze disconnect patterns for signs of attack"""
        if len(self.disconnect_history) < 2:
            return
        
        now = datetime.now()
        
        # Check for frequent disconnects in short time window
        recent_disconnects = [
            d for d in self.disconnect_history
            if (now - d['timestamp']).total_seconds() <= self.suspicious_window_minutes * 60
        ]
        
        if len(recent_disconnects) >= self.max_disconnects_per_minute:
            # Suspicious pattern detected
            reason = "Frequent disconnect pattern detected"
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            details = f"{len(recent_disconnects)} disconnects in {self.suspicious_window_minutes} minutes"
            
            self.suspicious_disconnect.emit(reason, timestamp, details)
            
            # Clear history to avoid duplicate alerts
            self.disconnect_history.clear()
    
    def get_recent_events(self):
        """Get list of recent disconnect events"""
        cutoff_time = datetime.now() - timedelta(hours=1)
        return [
            {
                'timestamp': d['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                'ssid': d['ssid'],
                'state': d['state']
            }
            for d in self.disconnect_history
            if d['timestamp'] > cutoff_time
        ]
    
    def get_network_interfaces(self):
        """Get list of network interfaces and their status"""
        try:
            interfaces = []
            for interface in psutil.net_if_stats():
                stats = psutil.net_if_stats()[interface]
                addresses = psutil.net_if_addrs().get(interface, [])
                
                # Check if this looks like a WiFi interface
                is_wifi = any(keyword in interface.lower() for keyword in ['wifi', 'wireless', 'wlan'])
                
                if is_wifi or stats.isup:
                    interfaces.append({
                        'name': interface,
                        'is_up': stats.isup,
                        'speed': stats.speed,
                        'is_wifi': is_wifi,
                        'addresses': [addr.address for addr in addresses if addr.family.name == 'AF_INET']
                    })
            
            return interfaces
        except Exception as e:
            print(f"Error getting network interfaces: {e}")
            return []


class LegacyDeauthDetector(QObject):
    """Legacy detector that simulates deauth attacks for demo/testing purposes"""
    attack_detected = pyqtSignal(str, str, str)  # attacker_mac, target_mac, timestamp
    
    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start simulated monitoring for demo purposes"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._demo_loop, daemon=True)
            self.monitor_thread.start()
            
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        
    def _demo_loop(self):
        """Demo loop that simulates attacks occasionally"""
        while self.is_monitoring:
            time.sleep(10)  # Check every 10 seconds for demo
            
            # Simulate random attack detection for demo
            import random
            if random.random() < 0.1:  # 10% chance every 10 seconds
                attacker_mac = f"00:11:22:{random.randint(10,99):02d}:{random.randint(10,99):02d}:{random.randint(10,99):02d}"
                target_mac = f"aa:bb:cc:{random.randint(10,99):02d}:{random.randint(10,99):02d}:{random.randint(10,99):02d}"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.attack_detected.emit(attacker_mac, target_mac, timestamp)