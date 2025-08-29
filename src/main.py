#!/usr/bin/env python3
"""
WiFi Deauth Detector - Main Application Entry Point

A lightweight real-time WiFi deauthentication attack detector for Windows.
This application monitors the local wireless environment for signs of WiFi 
deauth/disassoc attacks and alerts the user via GUI or system notifications.

Author: WiFi Security Team
License: MIT
"""

import sys
import logging
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from gui import DeauthDetectorGUI
from sniffer import WiFiSniffer
from utils import setup_logging, check_requirements


def main():
    """Main application entry point."""
    
    # Setup logging
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    setup_logging(log_dir / "deauth_detector.log")
    
    logger = logging.getLogger(__name__)
    logger.info("Starting WiFi Deauth Detector...")
    
    try:
        # Check system requirements
        if not check_requirements():
            logger.error("System requirements not met. Exiting.")
            return 1
        
        # Initialize and start the GUI application
        app = DeauthDetectorGUI()
        return app.run()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())