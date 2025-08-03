#!/usr/bin/env python3
"""
WiFi Deauth Detector for Windows
Detects WiFi interfaces and starts monitor mode sniffing using Npcap
"""

import sys
import platform
from scapy.all import get_if_list, conf
from scapy.layers.dot11 import Dot11, Dot11Deauth


class WiFiDetector:
    def __init__(self):
        self.interfaces = []
        self.selected_interface = None
        
    def detect_wifi_interfaces(self):
        """
        Detect WiFi interfaces using scapy.all.get_if_list()
        Returns list of available network interfaces
        """
        try:
            print("Detecting WiFi interfaces...")
            self.interfaces = get_if_list()
            
            # Filter for likely WiFi interfaces (this is a heuristic)
            wifi_interfaces = []
            for iface in self.interfaces:
                # On Windows, WiFi interfaces often contain "Wi-Fi", "Wireless", or "WiFi"
                if any(keyword.lower() in iface.lower() for keyword in ['wi-fi', 'wireless', 'wifi', 'wlan']):
                    wifi_interfaces.append(iface)
            
            if not wifi_interfaces:
                print("No WiFi interfaces detected. Showing all interfaces:")
                wifi_interfaces = self.interfaces
                
            return wifi_interfaces
            
        except Exception as e:
            print(f"Error detecting interfaces: {e}")
            return []
    
    def display_interfaces(self, interfaces):
        """
        Display available interfaces for user selection
        """
        print("\nAvailable Network Interfaces:")
        print("-" * 50)
        for i, iface in enumerate(interfaces, 1):
            print(f"{i}. {iface}")
        print("-" * 50)
        
    def select_interface(self, interfaces):
        """
        Let user select interface from available options
        """
        if not interfaces:
            print("No interfaces available for selection.")
            return None
            
        self.display_interfaces(interfaces)
        
        while True:
            try:
                choice = input(f"\nSelect interface (1-{len(interfaces)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    return None
                    
                choice_num = int(choice)
                if 1 <= choice_num <= len(interfaces):
                    selected = interfaces[choice_num - 1]
                    self.selected_interface = selected
                    print(f"\nSelected interface: {selected}")
                    return selected
                else:
                    print(f"Please enter a number between 1 and {len(interfaces)}")
                    
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                return None
    
    def setup_monitor_mode(self, interface):
        """
        Setup monitor mode for the selected interface
        Note: This requires Npcap to be installed with monitor mode support
        """
        print(f"\nSetting up monitor mode for interface: {interface}")
        print("\n" + "="*60)
        print("MONITOR MODE SETUP INSTRUCTIONS")
        print("="*60)
        print("1. Ensure Npcap is installed with the following options:")
        print("   - ✓ WinPcap Compatible Mode")
        print("   - ✓ Support raw 802.11 traffic (monitor mode)")
        print("\n2. Your wireless adapter must support monitor mode")
        print("   (Not all Windows WiFi adapters support this)")
        print("\n3. You may need to manually enable monitor mode using:")
        print("   - Device Manager → Network Adapters → Your WiFi Adapter")
        print("   - Properties → Advanced → Monitor Mode = Enabled")
        print("\n4. Some adapters require third-party drivers or tools")
        print("="*60)
        
        # Set the interface for scapy
        try:
            conf.iface = interface
            print(f"✓ Scapy configured to use interface: {interface}")
            return True
        except Exception as e:
            print(f"✗ Error configuring interface: {e}")
            return False
    
    def start_monitoring(self):
        """
        Start monitoring for deauthentication frames
        This is a basic implementation that would be expanded for full functionality
        """
        if not self.selected_interface:
            print("No interface selected. Cannot start monitoring.")
            return
            
        print(f"\nStarting monitor mode on interface: {self.selected_interface}")
        print("Note: This is a demonstration. Full packet capture requires proper setup.")
        print("Press Ctrl+C to stop monitoring...\n")
        
        try:
            # This is a placeholder for actual packet sniffing
            # In a real implementation, this would use scapy.sniff() with appropriate filters
            print("Monitor mode setup complete.")
            print("Ready to detect WiFi deauthentication attacks.")
            print("(Full implementation would capture and analyze 802.11 frames here)")
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"Error during monitoring: {e}")


def check_requirements():
    """
    Check if running on Windows and scapy is available
    """
    if platform.system() != "Windows":
        print("Warning: This tool is designed for Windows with Npcap")
        print(f"Current OS: {platform.system()}")
        
    try:
        import scapy
        print(f"✓ Scapy version: {scapy.__version__}")
    except ImportError:
        print("✗ Scapy not found. Please install: pip install scapy")
        return False
        
    return True


def main():
    """
    Main application entry point
    """
    print("WiFi Deauth Detector for Windows")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Initialize detector
    detector = WiFiDetector()
    
    # Detect WiFi interfaces
    interfaces = detector.detect_wifi_interfaces()
    
    if not interfaces:
        print("No network interfaces found. Exiting.")
        sys.exit(1)
    
    # Let user select interface
    selected = detector.select_interface(interfaces)
    
    if not selected:
        print("No interface selected. Exiting.")
        sys.exit(0)
    
    # Setup monitor mode
    if detector.setup_monitor_mode(selected):
        # Start monitoring
        detector.start_monitoring()
    else:
        print("Failed to setup monitor mode. Please check your configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()