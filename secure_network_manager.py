#!/usr/bin/env python3
"""
Secure Network Manager v2.1
Enhanced security with input validation and safe command execution
"""

import subprocess
import re
import logging
import shlex
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# Set up logging
logger = logging.getLogger(__name__)


class SecureNetworkManager:
    """Enhanced network manager with security improvements"""
    
    def __init__(self):
        self.command_timeout = 10
        self.max_profile_name_length = 32
        self.allowed_profile_chars = re.compile(r'^[a-zA-Z0-9\s\-_\.]+$')
        self.command_history = []  # For audit trail
        
    def _sanitize_profile_name(self, profile_name: str) -> Optional[str]:
        """Sanitize and validate WiFi profile names to prevent command injection"""
        if not profile_name or not isinstance(profile_name, str):
            logger.warning("Invalid profile name: empty or not string")
            return None
            
        # Remove leading/trailing whitespace
        profile_name = profile_name.strip()
        
        # Check length
        if len(profile_name) > self.max_profile_name_length:
            logger.warning(f"Profile name too long: {len(profile_name)} chars (max: {self.max_profile_name_length})")
            return None
            
        # Check for allowed characters only
        if not self.allowed_profile_chars.match(profile_name):
            logger.warning(f"Profile name contains invalid characters: {profile_name}")
            return None
            
        # Additional security: remove any potential command injection patterns
        dangerous_patterns = [';', '&', '|', '`', '$', '(', ')', '{', '}', '<', '>', '"', "'"]
        for pattern in dangerous_patterns:
            if pattern in profile_name:
                logger.warning(f"Profile name contains dangerous character '{pattern}': {profile_name}")
                return None
                
        return profile_name
    
    def _execute_safe_command(self, command: List[str], timeout: int = None) -> Tuple[bool, str, str]:
        """Execute command safely with timeout and logging"""
        if timeout is None:
            timeout = self.command_timeout
            
        # Log command for audit trail
        command_str = ' '.join(command)
        self.command_history.append({
            'timestamp': datetime.now(),
            'command': command_str,
            'sanitized': True
        })
        
        # Keep only recent history
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-50:]
        
        try:
            logger.debug(f"Executing command: {command_str}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,  # Important: never use shell=True for security
                check=False   # We'll check return code manually
            )
            
            success = result.returncode == 0
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""
            
            if not success:
                logger.warning(f"Command failed with code {result.returncode}: {command_str}")
                logger.warning(f"Error output: {stderr}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {command_str}")
            return False, "", f"Command timed out after {timeout} seconds"
            
        except FileNotFoundError:
            logger.error(f"Command not found: {command[0]}")
            return False, "", f"Command '{command[0]}' not found"
            
        except Exception as e:
            logger.error(f"Error executing command '{command_str}': {e}")
            return False, "", str(e)
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available WiFi profiles with enhanced security"""
        try:
            success, stdout, stderr = self._execute_safe_command([
                'netsh', 'wlan', 'show', 'profiles'
            ])
            
            if not success:
                logger.error(f"Failed to get WiFi profiles: {stderr}")
                return []
            
            profiles = []
            lines = stdout.split('\n')
            
            for line in lines:
                line = line.strip()
                if 'All User Profile' in line and ':' in line:
                    try:
                        # Extract profile name safely
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            profile_name = parts[1].strip()
                            
                            # Sanitize the extracted profile name
                            sanitized_name = self._sanitize_profile_name(profile_name)
                            if sanitized_name:
                                profiles.append(sanitized_name)
                            else:
                                logger.warning(f"Skipping invalid profile: {profile_name}")
                                
                    except Exception as e:
                        logger.warning(f"Error parsing profile line '{line}': {e}")
                        continue
            
            logger.info(f"Found {len(profiles)} valid WiFi profiles")
            return profiles
            
        except Exception as e:
            logger.error(f"Error getting WiFi profiles: {e}")
            return []
    
    def connect_to_network(self, profile_name: str) -> Tuple[bool, str]:
        """Connect to a specific WiFi network with enhanced security and feedback"""
        # Sanitize input
        safe_profile_name = self._sanitize_profile_name(profile_name)
        if not safe_profile_name:
            error_msg = f"Invalid profile name: {profile_name}"
            logger.error(error_msg)
            return False, error_msg
        
        try:
            logger.info(f"Attempting to connect to network: {safe_profile_name}")
            
            # Use safe command execution
            success, stdout, stderr = self._execute_safe_command([
                'netsh', 'wlan', 'connect', f'name={safe_profile_name}'
            ], timeout=15)  # Longer timeout for connection attempts
            
            if success:
                # Verify connection was actually established
                connection_verified = self._verify_connection(safe_profile_name)
                if connection_verified:
                    logger.info(f"Successfully connected to {safe_profile_name}")
                    return True, f"Connected to {safe_profile_name}"
                else:
                    logger.warning(f"Connection command succeeded but verification failed for {safe_profile_name}")
                    return False, f"Connection to {safe_profile_name} could not be verified"
            else:
                error_msg = f"Failed to connect to {safe_profile_name}: {stderr}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error connecting to network {safe_profile_name}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def _verify_connection(self, expected_profile: str, max_wait_time: int = 10) -> bool:
        """Verify that we're actually connected to the expected network"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                success, stdout, _ = self._execute_safe_command([
                    'netsh', 'wlan', 'show', 'interfaces'
                ], timeout=5)
                
                if success:
                    current_ssid = self._extract_current_ssid(stdout)
                    if current_ssid and current_ssid == expected_profile:
                        return True
                
                time.sleep(1)  # Wait a bit before retrying
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying connection to {expected_profile}: {e}")
            return False
    
    def _extract_current_ssid(self, interface_output: str) -> Optional[str]:
        """Safely extract current SSID from interface output"""
        try:
            lines = interface_output.split('\n')
            for line in lines:
                line = line.strip()
                if 'SSID' in line and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        ssid = parts[1].strip()
                        if ssid and ssid != 'N/A':
                            return self._sanitize_profile_name(ssid)
            return None
        except Exception as e:
            logger.error(f"Error extracting SSID from output: {e}")
            return None
    
    def get_current_connection_info(self) -> Dict[str, any]:
        """Get detailed information about current connection"""
        try:
            success, stdout, stderr = self._execute_safe_command([
                'netsh', 'wlan', 'show', 'interfaces'
            ])
            
            if not success:
                logger.error(f"Failed to get interface info: {stderr}")
                return {}
            
            info = self._parse_interface_info(stdout)
            
            # Add connection quality assessment
            if info.get('connected'):
                info['connection_quality'] = self._assess_connection_quality(info)
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting connection info: {e}")
            return {}
    
    def _parse_interface_info(self, output: str) -> Dict[str, any]:
        """Parse interface information safely"""
        info = {
            'connected': False,
            'ssid': None,
            'signal_strength': 0,
            'channel': None,
            'auth_type': None,
            'cipher': None,
            'state': 'disconnected'
        }
        
        try:
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                
                if 'State' in line and ':' in line:
                    state = line.split(':', 1)[1].strip().lower()
                    info['state'] = state
                    info['connected'] = (state == 'connected')
                    
                elif 'SSID' in line and ':' in line:
                    ssid = line.split(':', 1)[1].strip()
                    if ssid and ssid != 'N/A':
                        info['ssid'] = self._sanitize_profile_name(ssid)
                        
                elif 'Signal' in line and ':' in line:
                    signal_text = line.split(':', 1)[1].strip()
                    match = re.search(r'(\d+)%', signal_text)
                    if match:
                        info['signal_strength'] = int(match.group(1))
                        
                elif 'Channel' in line and ':' in line:
                    channel_text = line.split(':', 1)[1].strip()
                    match = re.search(r'(\d+)', channel_text)
                    if match:
                        info['channel'] = int(match.group(1))
                        
                elif 'Authentication' in line and ':' in line:
                    auth = line.split(':', 1)[1].strip()
                    info['auth_type'] = auth
                    
                elif 'Cipher' in line and ':' in line:
                    cipher = line.split(':', 1)[1].strip()
                    info['cipher'] = cipher
                    
        except Exception as e:
            logger.error(f"Error parsing interface info: {e}")
        
        return info
    
    def _assess_connection_quality(self, connection_info: Dict[str, any]) -> str:
        """Assess connection quality based on signal strength and other factors"""
        signal = connection_info.get('signal_strength', 0)
        
        if signal >= 80:
            return "Excellent"
        elif signal >= 60:
            return "Good"
        elif signal >= 40:
            return "Fair"
        elif signal >= 20:
            return "Poor"
        else:
            return "Very Poor"
    
    def disconnect_from_current_network(self) -> Tuple[bool, str]:
        """Safely disconnect from current network"""
        try:
            logger.info("Attempting to disconnect from current network")
            
            success, stdout, stderr = self._execute_safe_command([
                'netsh', 'wlan', 'disconnect'
            ])
            
            if success:
                logger.info("Successfully disconnected from network")
                return True, "Disconnected from network"
            else:
                error_msg = f"Failed to disconnect: {stderr}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error disconnecting from network: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_available_networks(self) -> List[Dict[str, any]]:
        """Get list of available networks with signal strength and security info"""
        try:
            success, stdout, stderr = self._execute_safe_command([
                'netsh', 'wlan', 'show', 'profiles'
            ])
            
            if not success:
                logger.error(f"Failed to get available networks: {stderr}")
                return []
            
            networks = []
            current_network = None
            
            lines = stdout.split('\n')
            for line in lines:
                line = line.strip()
                
                # Parse network entries
                if 'SSID' in line and ':' in line:
                    if current_network:
                        networks.append(current_network)
                    
                    ssid = line.split(':', 1)[1].strip()
                    safe_ssid = self._sanitize_profile_name(ssid)
                    if safe_ssid:
                        current_network = {
                            'ssid': safe_ssid,
                            'signal_strength': 0,
                            'security': 'Unknown',
                            'available': True
                        }
                
                elif current_network and 'Signal' in line:
                    match = re.search(r'(\d+)%', line)
                    if match:
                        current_network['signal_strength'] = int(match.group(1))
                
                elif current_network and 'Authentication' in line:
                    auth = line.split(':', 1)[1].strip()
                    current_network['security'] = auth
            
            # Add the last network
            if current_network:
                networks.append(current_network)
            
            # Sort by signal strength (descending)
            networks.sort(key=lambda x: x['signal_strength'], reverse=True)
            
            logger.info(f"Found {len(networks)} available networks")
            return networks
            
        except Exception as e:
            logger.error(f"Error getting available networks: {e}")
            return []
    
    def get_command_history(self) -> List[Dict[str, any]]:
        """Get recent command history for audit purposes"""
        # Return only sanitized history (no sensitive data)
        return [
            {
                'timestamp': entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                'command_type': entry['command'].split()[0] if entry['command'] else 'Unknown',
                'sanitized': entry['sanitized']
            }
            for entry in self.command_history[-20:]  # Last 20 commands
        ]
    
    def validate_network_security(self, profile_name: str) -> Dict[str, any]:
        """Validate security settings of a network profile"""
        safe_profile_name = self._sanitize_profile_name(profile_name)
        if not safe_profile_name:
            return {'valid': False, 'error': 'Invalid profile name'}
        
        try:
            success, stdout, stderr = self._execute_safe_command([
                'netsh', 'wlan', 'show', 'profile', f'name={safe_profile_name}'
            ])
            
            if not success:
                return {'valid': False, 'error': f'Could not retrieve profile: {stderr}'}
            
            security_info = {
                'valid': True,
                'profile_name': safe_profile_name,
                'has_password': False,
                'auth_type': 'Unknown',
                'cipher': 'Unknown',
                'auto_connect': False,
                'security_level': 'Unknown'
            }
            
            lines = stdout.split('\n')
            for line in lines:
                line = line.strip()
                
                if 'Authentication' in line and ':' in line:
                    auth = line.split(':', 1)[1].strip()
                    security_info['auth_type'] = auth
                    
                elif 'Cipher' in line and ':' in line:
                    cipher = line.split(':', 1)[1].strip()
                    security_info['cipher'] = cipher
                    
                elif 'Security key' in line and ':' in line:
                    security_info['has_password'] = 'Present' in line
                    
                elif 'Connect automatically' in line and ':' in line:
                    security_info['auto_connect'] = 'Yes' in line
            
            # Assess security level
            security_info['security_level'] = self._assess_security_level(security_info)
            
            return security_info
            
        except Exception as e:
            logger.error(f"Error validating network security for {safe_profile_name}: {e}")
            return {'valid': False, 'error': str(e)}
    
    def _assess_security_level(self, security_info: Dict[str, any]) -> str:
        """Assess security level based on authentication and cipher"""
        auth_type = security_info.get('auth_type', '').upper()
        cipher = security_info.get('cipher', '').upper()
        has_password = security_info.get('has_password', False)
        
        if not has_password:
            return "Open (No Security)"
        elif 'WPA3' in auth_type:
            return "WPA3 (Excellent)"
        elif 'WPA2' in auth_type and 'AES' in cipher:
            return "WPA2-AES (Good)"
        elif 'WPA2' in auth_type:
            return "WPA2 (Fair)"
        elif 'WPA' in auth_type:
            return "WPA (Poor)"
        elif 'WEP' in auth_type:
            return "WEP (Very Poor)"
        else:
            return "Unknown"


# Legacy NetworkManager class for backward compatibility
class NetworkManager:
    """Legacy network manager - redirects to SecureNetworkManager"""
    
    def __init__(self):
        self.secure_manager = SecureNetworkManager()
        logger.warning("Using legacy NetworkManager. Consider upgrading to SecureNetworkManager.")
    
    def get_available_profiles(self) -> List[str]:
        """Legacy method - get available profiles"""
        return self.secure_manager.get_available_profiles()
    
    def connect_to_network(self, profile_name: str) -> bool:
        """Legacy method - connect to network (returns bool only)"""
        success, _ = self.secure_manager.connect_to_network(profile_name)
        return success
