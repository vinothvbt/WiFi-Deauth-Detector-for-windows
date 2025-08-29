#!/usr/bin/env python3
"""
Enhanced Windows WiFi Connection Monitor v2.1
Improved detection algorithms and security enhancements
"""

import time
import threading
import subprocess
import json
import re
import hashlib
import hmac
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal
import psutil
import logging

# Set up secure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedWiFiMonitor(QObject):
    """Enhanced WiFi monitor with sophisticated pattern detection"""
    
    # Signal emitted when suspicious disconnect pattern detected
    suspicious_disconnect = pyqtSignal(str, str, str)  # reason, timestamp, details
    
    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        self.monitor_thread = None
        self.disconnect_history = []
        self.signal_history = []
        self.network_baselines = {}
        self.last_check_time = datetime.now()
        
        # Enhanced detection parameters
        self.rapid_disconnect_threshold = 3      # Max disconnects per minute
        self.suspicious_window_minutes = 5       # Analysis window
        self.signal_drop_threshold = 30          # Signal drop % that's suspicious
        self.minimum_connection_time = 30        # Min seconds for stable connection
        self.pattern_memory_hours = 24           # How long to remember patterns
        
        # Deauth attack reason codes (IEEE 802.11 standard)
        self.deauth_reason_codes = {
            1: "Unspecified reason",
            2: "Previous authentication no longer valid", 
            3: "Deauthenticated - sending STA leaving",
            4: "Disassociated - inactivity",
            5: "Disassociated - too many STAs",
            6: "Class 2 frame from non-authenticated STA",
            7: "Class 3 frame from non-associated STA",
            8: "Disassociated - sending STA leaving",
            9: "Association not authenticated"
        }
        
        # Threat assessment scoring
        self.threat_scores = {
            'rapid_disconnect': 8,      # Multiple fast disconnects
            'signal_drop_attack': 9,    # Sudden signal loss + disconnect
            'time_based_pattern': 7,    # Attacks at unusual times
            'repeated_target': 6,       # Same network attacked repeatedly
            'beacon_flood_indicator': 8, # Disconnect after signal anomaly
        }
        
    def start_monitoring(self):
        """Start enhanced monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._enhanced_monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Enhanced WiFi monitoring started")
            
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        logger.info("Enhanced WiFi monitoring stopped")
        
    def _enhanced_monitor_loop(self):
        """Enhanced monitoring loop with comprehensive analysis"""
        last_status = self._get_enhanced_wifi_status()
        connection_start_time = datetime.now() if last_status.get('connected') else None
        
        while self.is_monitoring:
            try:
                time.sleep(1)  # More frequent checking for better detection
                current_status = self._get_enhanced_wifi_status()
                
                # Track signal strength changes
                if current_status.get('connected'):
                    self._track_signal_changes(current_status)
                
                # Detect disconnect events with context
                if last_status.get('connected') and not current_status.get('connected'):
                    connection_duration = (datetime.now() - connection_start_time).total_seconds() if connection_start_time else 0
                    self._handle_enhanced_disconnect(current_status, last_status, connection_duration)
                    connection_start_time = None
                elif current_status.get('connected') and not last_status.get('connected'):
                    # New connection established
                    connection_start_time = datetime.now()
                
                # Periodic pattern analysis
                if (datetime.now() - self.last_check_time).seconds >= 15:  # More frequent analysis
                    self._enhanced_pattern_analysis()
                    self.last_check_time = datetime.now()
                
                last_status = current_status
                
            except Exception as e:
                logger.error(f"Error in enhanced monitoring loop: {e}")
                time.sleep(5)
                
    def _get_enhanced_wifi_status(self):
        """Enhanced WiFi status with additional security context"""
        try:
            # Get WiFi interface status with security info
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return self._get_default_status()
            
            status = self._parse_enhanced_interface_info(result.stdout)
            
            # Add additional network context
            if status['connected']:
                # Get detailed profile information
                profile_info = self._get_profile_security_info(status.get('ssid'))
                status.update(profile_info)
                
            return status
            
        except subprocess.TimeoutExpired:
            logger.warning("WiFi status check timed out")
            return self._get_default_status()
        except Exception as e:
            logger.error(f"Error getting enhanced WiFi status: {e}")
            return self._get_default_status()
    
    def _parse_enhanced_interface_info(self, output):
        """Parse netsh output with enhanced information extraction"""
        status = self._get_default_status()
        
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            try:
                if 'State' in line and ':' in line:
                    state = line.split(':', 1)[1].strip().lower()
                    status['state'] = state
                    status['connected'] = state == 'connected'
                elif 'SSID' in line and ':' in line:
                    ssid = line.split(':', 1)[1].strip()
                    if ssid and ssid not in ['N/A', '']:
                        status['ssid'] = ssid
                elif 'Signal' in line and ':' in line:
                    signal_text = line.split(':', 1)[1].strip()
                    match = re.search(r'(\d+)%', signal_text)
                    if match:
                        status['signal'] = int(match.group(1))
                elif 'Channel' in line and ':' in line:
                    channel_text = line.split(':', 1)[1].strip()
                    match = re.search(r'(\d+)', channel_text)
                    if match:
                        status['channel'] = int(match.group(1))
                elif 'Authentication' in line and ':' in line:
                    status['auth_type'] = line.split(':', 1)[1].strip()
                elif 'Cipher' in line and ':' in line:
                    status['cipher'] = line.split(':', 1)[1].strip()
            except (IndexError, ValueError) as e:
                logger.debug(f"Error parsing line '{line}': {e}")
                continue
        
        return status
    
    def _get_profile_security_info(self, ssid):
        """Get security information for a specific network profile"""
        try:
            if not ssid:
                return {}
                
            # Sanitize SSID to prevent command injection
            safe_ssid = re.sub(r'[^\w\s-]', '', ssid)[:32]  # Limit length and chars
            
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'profile', f'name="{safe_ssid}"', 'key=clear'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode != 0:
                return {}
            
            profile_info = {}
            lines = result.stdout.split('\n')
            for line in lines:
                line = line.strip()
                try:
                    if 'Security key' in line and ':' in line:
                        profile_info['has_password'] = 'Present' in line
                    elif 'Key Content' in line and ':' in line:
                        # Don't store actual password, just note if it exists
                        key_content = line.split(':', 1)[1].strip()
                        profile_info['key_configured'] = bool(key_content and key_content != 'N/A')
                    elif 'Connect automatically' in line and ':' in line:
                        profile_info['auto_connect'] = 'Yes' in line
                except (IndexError, ValueError):
                    continue
            
            return profile_info
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Profile info check timed out for {ssid}")
            return {}
        except Exception as e:
            logger.error(f"Error getting profile info for {ssid}: {e}")
            return {}
    
    def _get_default_status(self):
        """Return default status structure"""
        return {
            'connected': False,
            'ssid': None,
            'signal': 0,
            'state': 'disconnected',
            'channel': 0,
            'auth_type': 'Unknown',
            'cipher': 'Unknown',
            'timestamp': datetime.now()
        }
    
    def _track_signal_changes(self, current_status):
        """Track signal strength changes for anomaly detection"""
        if not current_status.get('connected') or current_status.get('signal', 0) == 0:
            return
        
        signal_entry = {
            'timestamp': datetime.now(),
            'ssid': current_status.get('ssid'),
            'signal': current_status.get('signal'),
            'channel': current_status.get('channel', 0)
        }
        
        self.signal_history.append(signal_entry)
        
        # Keep only recent signal history (last hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.signal_history = [s for s in self.signal_history if s['timestamp'] > cutoff_time]
        
        # Check for sudden signal drops
        self._detect_signal_anomalies(signal_entry)
    
    def _detect_signal_anomalies(self, current_signal):
        """Detect suspicious signal strength patterns"""
        if len(self.signal_history) < 10:  # Need enough history
            return
        
        ssid = current_signal['ssid']
        recent_signals = [s['signal'] for s in self.signal_history[-10:] if s['ssid'] == ssid]
        
        if len(recent_signals) < 5:
            return
        
        # Calculate signal baseline
        avg_signal = sum(recent_signals[:-1]) / len(recent_signals[:-1])
        current = current_signal['signal']
        
        # Detect sudden drops that might indicate jamming
        signal_drop = avg_signal - current
        if signal_drop > self.signal_drop_threshold and avg_signal > 50:
            logger.warning(f"Suspicious signal drop detected: {signal_drop}% on {ssid}")
            # This will be used in disconnect analysis if disconnect follows
    
    def _handle_enhanced_disconnect(self, current_status, last_status, connection_duration):
        """Enhanced disconnect handling with threat assessment"""
        timestamp = datetime.now()
        
        # Calculate threat score based on multiple factors
        threat_score = self._calculate_threat_score(current_status, last_status, connection_duration)
        
        disconnect_info = {
            'timestamp': timestamp,
            'ssid': last_status.get('ssid', 'Unknown'),
            'last_signal': last_status.get('signal', 0),
            'connection_duration': connection_duration,
            'channel': last_status.get('channel', 0),
            'auth_type': last_status.get('auth_type', 'Unknown'),
            'threat_score': threat_score,
            'disconnect_reason': self._infer_disconnect_reason(current_status, last_status)
        }
        
        self.disconnect_history.append(disconnect_info)
        
        # Maintain history within memory limit
        cutoff_time = timestamp - timedelta(hours=self.pattern_memory_hours)
        self.disconnect_history = [d for d in self.disconnect_history if d['timestamp'] > cutoff_time]
        
        logger.info(f"WiFi disconnect detected: {disconnect_info}")
        
        # Immediate threat assessment
        if threat_score >= 7:  # High threat threshold
            self._emit_security_alert(disconnect_info, "High-risk disconnect pattern")
        elif connection_duration < self.minimum_connection_time and threat_score >= 5:
            self._emit_security_alert(disconnect_info, "Rapid disconnect after brief connection")
    
    def _calculate_threat_score(self, current_status, last_status, connection_duration):
        """Calculate threat score based on multiple indicators"""
        score = 0
        
        # Factor 1: Connection duration (very short connections are suspicious)
        if connection_duration < 30:
            score += 6
        elif connection_duration < 120:
            score += 3
        
        # Factor 2: Signal strength at disconnect
        last_signal = last_status.get('signal', 0)
        if last_signal > 70:  # Strong signal disconnect is suspicious
            score += 4
        elif last_signal > 50:
            score += 2
        
        # Factor 3: Recent disconnect frequency
        recent_disconnects = self._get_recent_disconnects(minutes=5)
        if len(recent_disconnects) >= 3:
            score += 8  # Very suspicious
        elif len(recent_disconnects) >= 2:
            score += 5
        
        # Factor 4: Time-based patterns (attacks often at specific times)
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Late night attacks
            score += 2
        
        # Factor 5: Signal drop before disconnect
        if self._had_recent_signal_drop(last_status.get('ssid')):
            score += 6
        
        # Factor 6: Repeated targeting of same network
        ssid = last_status.get('ssid')
        if ssid:
            recent_same_network = [d for d in recent_disconnects if d.get('ssid') == ssid]
            if len(recent_same_network) >= 2:
                score += 5
        
        return min(score, 10)  # Cap at 10
    
    def _infer_disconnect_reason(self, current_status, last_status):
        """Infer likely reason for disconnect"""
        # This is a simplified inference - in a real implementation,
        # we might analyze system logs or other indicators
        
        if last_status.get('signal', 0) > 70:
            return "Strong signal disconnect (possible deauth)"
        elif last_status.get('signal', 0) < 30:
            return "Weak signal disconnect"
        else:
            return "Normal signal disconnect"
    
    def _get_recent_disconnects(self, minutes=5):
        """Get disconnects within specified time window"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [d for d in self.disconnect_history if d['timestamp'] > cutoff_time]
    
    def _had_recent_signal_drop(self, ssid, minutes=2):
        """Check if there was a recent significant signal drop for this SSID"""
        if not ssid:
            return False
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_signals = [s for s in self.signal_history if s['timestamp'] > cutoff_time and s['ssid'] == ssid]
        
        if len(recent_signals) < 5:
            return False
        
        # Check for significant drop in recent history
        signals = [s['signal'] for s in recent_signals]
        max_signal = max(signals)
        min_signal = min(signals)
        
        return (max_signal - min_signal) > self.signal_drop_threshold
    
    def _enhanced_pattern_analysis(self):
        """Enhanced pattern analysis with machine learning concepts"""
        if len(self.disconnect_history) < 2:
            return
        
        now = datetime.now()
        
        # Analysis 1: Rapid sequential disconnects
        self._analyze_rapid_disconnects(now)
        
        # Analysis 2: Temporal attack patterns
        self._analyze_temporal_patterns(now)
        
        # Analysis 3: Network targeting patterns
        self._analyze_network_targeting(now)
        
        # Analysis 4: Signal-based attack indicators
        self._analyze_signal_based_attacks(now)
    
    def _analyze_rapid_disconnects(self, now):
        """Analyze for rapid disconnect patterns"""
        recent_window = now - timedelta(minutes=self.suspicious_window_minutes)
        recent_disconnects = [d for d in self.disconnect_history if d['timestamp'] > recent_window]
        
        if len(recent_disconnects) >= self.rapid_disconnect_threshold:
            threat_score = min(len(recent_disconnects) * 2, 10)
            details = f"{len(recent_disconnects)} disconnects in {self.suspicious_window_minutes} minutes"
            
            self._emit_security_alert({
                'timestamp': now,
                'threat_score': threat_score,
                'pattern': 'rapid_disconnect',
                'details': details
            }, "Rapid disconnect pattern detected")
            
            # Clear to prevent duplicate alerts
            self.disconnect_history = [d for d in self.disconnect_history if d['timestamp'] <= recent_window]
    
    def _analyze_temporal_patterns(self, now):
        """Analyze temporal patterns that might indicate coordinated attacks"""
        # Look for disconnects at regular intervals (possible automated attacks)
        recent_hours = now - timedelta(hours=2)
        recent_disconnects = [d for d in self.disconnect_history if d['timestamp'] > recent_hours]
        
        if len(recent_disconnects) >= 4:
            # Calculate intervals between disconnects
            intervals = []
            for i in range(1, len(recent_disconnects)):
                interval = (recent_disconnects[i]['timestamp'] - recent_disconnects[i-1]['timestamp']).total_seconds()
                intervals.append(interval)
            
            # Check for regular patterns (automated attacks often have consistent timing)
            if len(intervals) >= 3:
                avg_interval = sum(intervals) / len(intervals)
                deviations = [abs(interval - avg_interval) for interval in intervals]
                avg_deviation = sum(deviations) / len(deviations)
                
                # If intervals are very regular, it might be automated
                if avg_deviation < 30 and avg_interval < 600:  # Less than 30s deviation, intervals under 10 min
                    self._emit_security_alert({
                        'timestamp': now,
                        'threat_score': 8,
                        'pattern': 'temporal_regularity',
                        'details': f"Regular disconnect pattern every {avg_interval:.0f}s"
                    }, "Automated attack pattern detected")
    
    def _analyze_network_targeting(self, now):
        """Analyze if specific networks are being repeatedly targeted"""
        recent_hours = now - timedelta(hours=1)
        recent_disconnects = [d for d in self.disconnect_history if d['timestamp'] > recent_hours]
        
        # Count disconnects per SSID
        ssid_counts = {}
        for disconnect in recent_disconnects:
            ssid = disconnect.get('ssid')
            if ssid and ssid != 'Unknown':
                ssid_counts[ssid] = ssid_counts.get(ssid, 0) + 1
        
        # Check for networks with excessive disconnects
        for ssid, count in ssid_counts.items():
            if count >= 3:  # 3+ disconnects from same network in 1 hour
                self._emit_security_alert({
                    'timestamp': now,
                    'threat_score': 7,
                    'pattern': 'network_targeting',
                    'details': f"Network '{ssid}' targeted {count} times in 1 hour"
                }, f"Network targeting detected: {ssid}")
    
    def _analyze_signal_based_attacks(self, now):
        """Analyze signal patterns that might indicate jamming or similar attacks"""
        recent_minutes = now - timedelta(minutes=10)
        recent_signals = [s for s in self.signal_history if s['timestamp'] > recent_minutes]
        
        if len(recent_signals) < 10:
            return
        
        # Look for unusual signal patterns
        signals_by_ssid = {}
        for signal_entry in recent_signals:
            ssid = signal_entry['ssid']
            if ssid:
                if ssid not in signals_by_ssid:
                    signals_by_ssid[ssid] = []
                signals_by_ssid[ssid].append(signal_entry['signal'])
        
        for ssid, signals in signals_by_ssid.items():
            if len(signals) >= 10:
                # Check for rapid signal fluctuations (possible jamming)
                signal_variance = self._calculate_variance(signals)
                avg_signal = sum(signals) / len(signals)
                
                # High variance with low average might indicate interference
                if signal_variance > 400 and avg_signal < 50:
                    self._emit_security_alert({
                        'timestamp': now,
                        'threat_score': 6,
                        'pattern': 'signal_interference',
                        'details': f"High signal variance ({signal_variance:.0f}) on {ssid}"
                    }, f"Signal interference detected on {ssid}")
    
    def _calculate_variance(self, values):
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        squared_diffs = [(x - mean) ** 2 for x in values]
        return sum(squared_diffs) / len(squared_diffs)
    
    def _emit_security_alert(self, event_info, alert_reason):
        """Emit security alert with detailed information"""
        timestamp = event_info.get('timestamp', datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        threat_score = event_info.get('threat_score', 5)
        
        # Format detailed alert information
        details = event_info.get('details', alert_reason)
        if 'ssid' in event_info:
            details = f"{details} (Network: {event_info['ssid']})"
        
        logger.warning(f"Security alert: {alert_reason} - {details} (Threat: {threat_score}/10)")
        
        # Emit signal for GUI
        self.suspicious_disconnect.emit(alert_reason, timestamp, details)
    
    def get_recent_events(self):
        """Get recent events with enhanced information"""
        cutoff_time = datetime.now() - timedelta(hours=1)
        events = []
        
        for disconnect in self.disconnect_history:
            if disconnect['timestamp'] > cutoff_time:
                events.append({
                    'timestamp': disconnect['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                    'ssid': disconnect['ssid'],
                    'threat_score': disconnect.get('threat_score', 0),
                    'reason': disconnect.get('disconnect_reason', 'Unknown'),
                    'duration': disconnect.get('connection_duration', 0)
                })
        
        return sorted(events, key=lambda x: x['timestamp'], reverse=True)
    
    def get_network_interfaces(self):
        """Get enhanced network interface information"""
        try:
            interfaces = []
            for interface in psutil.net_if_stats():
                stats = psutil.net_if_stats()[interface]
                addresses = psutil.net_if_addrs().get(interface, [])
                
                # Enhanced WiFi detection
                is_wifi = any(keyword in interface.lower() for keyword in 
                             ['wifi', 'wireless', 'wlan', '802.11'])
                
                if is_wifi or stats.isup:
                    interfaces.append({
                        'name': interface,
                        'is_up': stats.isup,
                        'speed': stats.speed,
                        'is_wifi': is_wifi,
                        'addresses': [addr.address for addr in addresses 
                                    if hasattr(addr, 'family') and addr.family.name == 'AF_INET'],
                        'mtu': stats.mtu if hasattr(stats, 'mtu') else 0
                    })
            
            return interfaces
        except Exception as e:
            logger.error(f"Error getting network interfaces: {e}")
            return []


# Keep the existing LegacyDeauthDetector for compatibility
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
