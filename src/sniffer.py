#!/usr/bin/env python3
"""
WiFi Packet Sniffer Module

This module handles the packet sniffing functionality for detecting
WiFi deauthentication attacks using Scapy and Npcap.

Author: WiFi Security Team
License: MIT
"""

import logging
import threading
from typing import Callable, Optional
from scapy.all import sniff, Dot11, Dot11Deauth, Dot11Disas
from scapy.error import Scapy_Exception


class WiFiSniffer:
    """WiFi packet sniffer for detecting deauth attacks."""
    
    def __init__(self, interface: Optional[str] = None):
        """
        Initialize the WiFi sniffer.
        
        Args:
            interface: Network interface to sniff on. If None, uses default.
        """
        self.interface = interface
        self.is_running = False
        self.sniffer_thread = None
        self.packet_callback = None
        self.logger = logging.getLogger(__name__)
        
    def set_packet_callback(self, callback: Callable):
        """
        Set the callback function for processing packets.
        
        Args:
            callback: Function to call when a deauth packet is detected.
        """
        self.packet_callback = callback
        
    def _packet_handler(self, packet):
        """
        Handle incoming packets and filter for deauth/disassoc frames.
        
        Args:
            packet: The captured packet from Scapy.
        """
        try:
            # Check if packet contains 802.11 frame
            if not packet.haslayer(Dot11):
                return
                
            # Check for deauthentication frames
            if packet.haslayer(Dot11Deauth):
                self._handle_deauth_packet(packet)
                
            # Check for disassociation frames  
            elif packet.haslayer(Dot11Disas):
                self._handle_disassoc_packet(packet)
                
        except Exception as e:
            self.logger.error(f"Error processing packet: {e}")
            
    def _handle_deauth_packet(self, packet):
        """
        Process deauthentication packets.
        
        Args:
            packet: The deauth packet to process.
        """
        try:
            dot11 = packet.getlayer(Dot11)
            deauth = packet.getlayer(Dot11Deauth)
            
            attack_info = {
                'type': 'deauth',
                'attacker_mac': dot11.addr2,
                'target_mac': dot11.addr1,
                'bssid': dot11.addr3,
                'reason_code': deauth.reason,
                'timestamp': packet.time
            }
            
            self.logger.warning(f"Deauth attack detected: {attack_info}")
            
            if self.packet_callback:
                self.packet_callback(attack_info)
                
        except Exception as e:
            self.logger.error(f"Error handling deauth packet: {e}")
            
    def _handle_disassoc_packet(self, packet):
        """
        Process disassociation packets.
        
        Args:
            packet: The disassoc packet to process.
        """
        try:
            dot11 = packet.getlayer(Dot11)
            disassoc = packet.getlayer(Dot11Disas)
            
            attack_info = {
                'type': 'disassoc',
                'attacker_mac': dot11.addr2,
                'target_mac': dot11.addr1,
                'bssid': dot11.addr3,
                'reason_code': disassoc.reason,
                'timestamp': packet.time
            }
            
            self.logger.warning(f"Disassoc attack detected: {attack_info}")
            
            if self.packet_callback:
                self.packet_callback(attack_info)
                
        except Exception as e:
            self.logger.error(f"Error handling disassoc packet: {e}")
            
    def start_sniffing(self):
        """Start the packet sniffing process."""
        if self.is_running:
            self.logger.warning("Sniffer is already running")
            return
            
        self.is_running = True
        self.logger.info(f"Starting WiFi sniffing on interface: {self.interface}")
        
        def sniff_worker():
            try:
                sniff(
                    iface=self.interface,
                    prn=self._packet_handler,
                    filter="type mgt subtype 12",  # Deauth frames
                    store=0,
                    stop_filter=lambda x: not self.is_running
                )
            except Scapy_Exception as e:
                self.logger.error(f"Scapy sniffing error: {e}")
                self.is_running = False
            except Exception as e:
                self.logger.error(f"Unexpected sniffing error: {e}")
                self.is_running = False
                
        self.sniffer_thread = threading.Thread(target=sniff_worker, daemon=True)
        self.sniffer_thread.start()
        
    def stop_sniffing(self):
        """Stop the packet sniffing process."""
        if not self.is_running:
            return
            
        self.logger.info("Stopping WiFi sniffing...")
        self.is_running = False
        
        if self.sniffer_thread and self.sniffer_thread.is_alive():
            self.sniffer_thread.join(timeout=5)
            
    def get_available_interfaces(self):
        """
        Get list of available network interfaces.
        
        Returns:
            List of available interface names.
        """
        try:
            from scapy.arch import get_if_list
            return get_if_list()
        except Exception as e:
            self.logger.error(f"Error getting interfaces: {e}")
            return []