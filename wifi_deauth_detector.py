#!/usr/bin/env python3
"""
WiFi Deauthentication Attack Detector
Monitors WiFi traffic for deauth frames and identifies potential attackers
"""

import sys
import time
import threading
from collections import defaultdict, Counter
from datetime import datetime
import argparse

try:
    from scapy.all import *
    from scapy.layers.dot11 import Dot11, Dot11Deauth, Dot11Disas
except ImportError:
    print("Error: Scapy not installed. Run: pip install scapy")
    sys.exit(1)

try:
    from colorama import init, Fore, Back, Style
    init()  # Initialize colorama for Windows
except ImportError:
    print("Warning: colorama not installed. Colors may not work properly.")
    # Define empty color constants if colorama is not available
    class Fore:
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        CYAN = ""
        WHITE = ""
        RESET = ""
    
    class Style:
        BRIGHT = ""
        RESET_ALL = ""


class WiFiDeauthDetector:
    def __init__(self, interface=None, display_interval=30):
        self.interface = interface
        self.display_interval = display_interval
        
        # Track deauth frames and MAC addresses
        self.deauth_frames = []
        self.mac_frequency = Counter()
        self.attack_log = []
        
        # Threading control
        self.running = False
        self.display_thread = None
        
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} WiFi Deauth Detector initialized")
        print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Display interval: {display_interval} seconds")
    
    def log_frame_addresses(self, packet):
        """Extract and log addr1, addr2, addr3 from 802.11 frame"""
        if packet.haslayer(Dot11):
            dot11 = packet[Dot11]
            
            # Extract the three address fields
            addr1 = dot11.addr1 if dot11.addr1 else "N/A"  # Destination
            addr2 = dot11.addr2 if dot11.addr2 else "N/A"  # Source  
            addr3 = dot11.addr3 if dot11.addr3 else "N/A"  # BSSID/Additional
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            frame_info = {
                'timestamp': timestamp,
                'addr1': addr1,  # Destination MAC
                'addr2': addr2,  # Source MAC (potential attacker)
                'addr3': addr3,  # BSSID or other
                'type': 'deauth' if packet.haslayer(Dot11Deauth) else 'disassoc'
            }
            
            self.deauth_frames.append(frame_info)
            
            # Track source MAC frequency (addr2 is typically the sender)
            if addr2 != "N/A":
                self.mac_frequency[addr2] += 1
            
            # Log the frame
            print(f"{Fore.CYAN}[FRAME]{Style.RESET_ALL} {timestamp}")
            print(f"  addr1 (dest): {addr1}")
            print(f"  addr2 (src):  {Fore.RED}{addr2}{Style.RESET_ALL}")
            print(f"  addr3 (bssid): {addr3}")
            print(f"  type: {frame_info['type']}")
            print("-" * 50)
    
    def identify_attacker(self):
        """Identify the most frequent source MAC as potential attacker"""
        if not self.mac_frequency:
            return None
        
        # Get the most common source MAC
        most_common = self.mac_frequency.most_common(1)
        if most_common:
            attacker_mac, count = most_common[0]
            
            # Only consider it an attacker if there are multiple frames
            if count >= 2:
                return attacker_mac, count
        
        return None
    
    def display_attacker_info(self):
        """Display information about potential attacker"""
        attacker_info = self.identify_attacker()
        
        if attacker_info:
            attacker_mac, count = attacker_info
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n{Fore.RED}{Style.BRIGHT}[ALERT]{Style.RESET_ALL} {timestamp}")
            print(f"{Fore.RED}Possible attacker: {attacker_mac}{Style.RESET_ALL}")
            print(f"Deauth frames sent: {count}")
            
            # Log the attack
            attack_entry = {
                'timestamp': timestamp,
                'attacker_mac': attacker_mac,
                'frame_count': count
            }
            self.attack_log.append(attack_entry)
            
            # Display recent targets (addr1 from frames with this source)
            targets = [frame['addr1'] for frame in self.deauth_frames 
                      if frame['addr2'] == attacker_mac and frame['addr1'] != "N/A"]
            
            if targets:
                unique_targets = list(set(targets))
                print(f"Targets: {', '.join(unique_targets[:5])}")  # Show first 5 targets
                
        else:
            print(f"\n{Fore.GREEN}[INFO]{Style.RESET_ALL} No suspicious activity detected")
        
        print("=" * 60)
    
    def display_loop(self):
        """Periodic display of attacker information"""
        while self.running:
            time.sleep(self.display_interval)
            if self.running:  # Check again in case we were stopped
                self.display_attacker_info()
    
    def packet_handler(self, packet):
        """Handle captured packets"""
        try:
            # Check for deauth or disassociation frames
            if packet.haslayer(Dot11Deauth) or packet.haslayer(Dot11Disas):
                self.log_frame_addresses(packet)
                
        except Exception as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Error processing packet: {e}")
    
    def start_monitoring(self):
        """Start monitoring for deauth frames"""
        if not self.interface:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} No interface specified")
            return
        
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Starting deauth detection on interface: {self.interface}")
        print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Press Ctrl+C to stop")
        print("=" * 60)
        
        self.running = True
        
        # Start the display thread
        self.display_thread = threading.Thread(target=self.display_loop, daemon=True)
        self.display_thread.start()
        
        try:
            # Start packet capture
            sniff(iface=self.interface, prn=self.packet_handler, store=0, monitor=True)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[INFO]{Style.RESET_ALL} Stopping deauth detector...")
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to start monitoring: {e}")
            print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Make sure:")
            print("  1. You're running as administrator")
            print("  2. The interface supports monitor mode")
            print("  3. Npcap is installed with raw 802.11 support")
            
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.running = False
        
        # Final summary
        print(f"\n{Fore.BLUE}[SUMMARY]{Style.RESET_ALL}")
        print(f"Total deauth frames captured: {len(self.deauth_frames)}")
        print(f"Unique source MACs detected: {len(self.mac_frequency)}")
        
        if self.attack_log:
            print(f"Potential attacks logged: {len(self.attack_log)}")
            for attack in self.attack_log:
                print(f"  {attack['timestamp']}: {attack['attacker_mac']} ({attack['frame_count']} frames)")
        
    def list_interfaces(self):
        """List available network interfaces"""
        try:
            interfaces = get_if_list()
            print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} Available network interfaces:")
            for i, iface in enumerate(interfaces):
                print(f"  {i}: {iface}")
            return interfaces
        except Exception as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Could not list interfaces: {e}")
            return []


def main():
    parser = argparse.ArgumentParser(description='WiFi Deauth Attack Detector')
    parser.add_argument('-i', '--interface', type=str, help='Network interface to monitor')
    parser.add_argument('-l', '--list', action='store_true', help='List available interfaces')
    parser.add_argument('-t', '--interval', type=int, default=30, 
                       help='Display interval in seconds (default: 30)')
    
    args = parser.parse_args()
    
    detector = WiFiDeauthDetector(interface=args.interface, display_interval=args.interval)
    
    if args.list:
        detector.list_interfaces()
        return
    
    if not args.interface:
        print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} No interface specified. Available interfaces:")
        interfaces = detector.list_interfaces()
        if interfaces:
            print(f"\nUsage: python {sys.argv[0]} -i <interface_name>")
        return
    
    detector.start_monitoring()


if __name__ == "__main__":
    main()