#!/usr/bin/env python3
"""
Utility Functions for WiFi Deauth Detector

This module contains utility functions for logging, notifications,
system checks, and other helper functions.

Author: WiFi Security Team
License: MIT
"""

import os
import sys
import logging
import platform
import subprocess
from pathlib import Path
from typing import Optional


def setup_logging(log_file: Optional[Path] = None, level: int = logging.INFO):
    """
    Setup logging configuration for the application.
    
    Args:
        log_file: Path to log file. If None, logs only to console.
        level: Logging level (default: INFO).
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
    logging.info(f"Logging initialized. Level: {logging.getLevelName(level)}")


def check_requirements() -> bool:
    """
    Check if system requirements are met.
    
    Returns:
        True if all requirements are met, False otherwise.
    """
    logger = logging.getLogger(__name__)
    
    # Check if running on Windows
    if platform.system() != "Windows":
        logger.error("This application requires Windows")
        return False
        
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
        
    # Check for required packages
    required_packages = ['scapy', 'PyQt5', 'plyer']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
            
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Install with: pip install " + " ".join(missing_packages))
        return False
        
    # Check for Npcap (Windows specific)
    if not check_npcap():
        logger.error("Npcap is required for packet capture on Windows")
        logger.info("Download Npcap from: https://npcap.com/#download")
        logger.info("Install with 'WinPcap Compatible Mode' and 'Support raw 802.11 traffic' options")
        return False
        
    logger.info("All system requirements are met")
    return True


def check_npcap() -> bool:
    """
    Check if Npcap is installed and properly configured.
    
    Returns:
        True if Npcap is available, False otherwise.
    """
    try:
        # Check for Npcap installation
        npcap_paths = [
            r"C:\Windows\System32\Npcap",
            r"C:\Windows\SysWOW64\Npcap",
            r"C:\Program Files\Npcap"
        ]
        
        for path in npcap_paths:
            if os.path.exists(path):
                return True
                
        # Alternative check: try to import scapy and check for WinPcap
        from scapy.arch.windows import get_windows_if_list
        interfaces = get_windows_if_list()
        return len(interfaces) > 0
        
    except Exception:
        return False


def send_notification(title: str, message: str, timeout: int = 5):
    """
    Send a system notification.
    
    Args:
        title: Notification title.
        message: Notification message.
        timeout: Notification timeout in seconds.
    """
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            timeout=timeout,
            app_name="WiFi Deauth Detector"
        )
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to send notification: {e}")


def get_network_interfaces():
    """
    Get list of available network interfaces on Windows.
    
    Returns:
        List of interface names.
    """
    try:
        from scapy.arch.windows import get_windows_if_list
        interfaces = get_windows_if_list()
        return [iface['name'] for iface in interfaces]
    except Exception as e:
        logging.getLogger(__name__).error(f"Error getting interfaces: {e}")
        return []


def is_admin() -> bool:
    """
    Check if the current process is running with administrator privileges.
    
    Returns:
        True if running as admin, False otherwise.
    """
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """
    Restart the current script with administrator privileges.
    """
    try:
        import ctypes
        if is_admin():
            return
            
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            " ".join(sys.argv), 
            None, 
            1
        )
        sys.exit(0)
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to restart as admin: {e}")


def format_mac_address(mac: str) -> str:
    """
    Format MAC address to a standard format.
    
    Args:
        mac: MAC address string.
        
    Returns:
        Formatted MAC address (XX:XX:XX:XX:XX:XX).
    """
    # Remove any existing separators
    mac = mac.replace(':', '').replace('-', '').replace('.', '')
    
    # Add colons every 2 characters
    if len(mac) == 12:
        return ':'.join(mac[i:i+2] for i in range(0, 12, 2)).upper()
    
    return mac.upper()


def save_attack_log(attack_info: dict, log_file: Path):
    """
    Save attack information to a log file.
    
    Args:
        attack_info: Dictionary containing attack details.
        log_file: Path to the log file.
    """
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = attack_info.get('timestamp', 'unknown')
            attack_type = attack_info.get('type', 'unknown')
            attacker = attack_info.get('attacker_mac', 'unknown')
            target = attack_info.get('target_mac', 'unknown')
            bssid = attack_info.get('bssid', 'unknown')
            reason = attack_info.get('reason_code', 'unknown')
            
            log_line = f"{timestamp},{attack_type},{attacker},{target},{bssid},{reason}\n"
            f.write(log_line)
            
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to save attack log: {e}")


def check_monitor_mode_support(interface: str) -> bool:
    """
    Check if the given interface supports monitor mode.
    
    Args:
        interface: Network interface name.
        
    Returns:
        True if monitor mode is supported, False otherwise.
    """
    try:
        # This is a placeholder - actual implementation would need
        # to check the specific wireless driver capabilities
        logger = logging.getLogger(__name__)
        logger.info(f"Checking monitor mode support for {interface}")
        
        # For now, assume all interfaces support monitor mode if Npcap is installed
        return check_npcap()
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error checking monitor mode: {e}")
        return False


def get_system_info() -> dict:
    """
    Get system information for debugging purposes.
    
    Returns:
        Dictionary containing system information.
    """
    info = {
        'platform': platform.platform(),
        'system': platform.system(),
        'version': platform.version(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
        'is_admin': is_admin(),
        'npcap_installed': check_npcap()
    }
    
    return info


def validate_mac_address(mac: str) -> bool:
    """
    Validate if a string is a valid MAC address.
    
    Args:
        mac: MAC address string to validate.
        
    Returns:
        True if valid, False otherwise.
    """
    import re
    
    # Remove any separators
    clean_mac = mac.replace(':', '').replace('-', '').replace('.', '')
    
    # Check if it's 12 hex characters
    return bool(re.match(r'^[0-9a-fA-F]{12}$', clean_mac))