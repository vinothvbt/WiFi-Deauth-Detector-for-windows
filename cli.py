#!/usr/bin/env python3
"""
CLI mode for WiFi Deauth Detector v2.0
Demonstrates functionality without GUI
"""

import sys
import os
import time
import signal
import threading
from datetime import datetime

# Add the main directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from windows_wifi_monitor import WindowsWiFiMonitor, LegacyDeauthDetector
from main import SettingsManager, NetworkManager, DiscordWebhook

class CLIDeauthDetector:
    """Command-line interface for the detector"""
    
    def __init__(self):
        self.running = False
        self.settings = SettingsManager()
        self.network_manager = NetworkManager()
        
        # Determine monitoring mode
        use_real_monitoring = os.name == 'nt' and not self.settings.get("demo_mode", False)
        
        if use_real_monitoring:
            print("🔍 Using Windows WLAN API monitoring (Normal Mode)")
            self.monitor = WindowsWiFiMonitor()
            self.monitor.suspicious_disconnect.connect(self._handle_suspicious_event)
        else:
            print("🎭 Using legacy detector (Demo Mode)")
            self.monitor = LegacyDeauthDetector()
            self.monitor.attack_detected.connect(self._handle_demo_event)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n📡 Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def _handle_suspicious_event(self, reason, timestamp, details):
        """Handle suspicious WiFi events"""
        print(f"\n🚨 SECURITY ALERT!")
        print(f"   Time: {timestamp}")
        print(f"   Event: {reason}")
        print(f"   Details: {details}")
        
        # Send Discord notification if configured
        if self.settings.get("discord_enabled"):
            webhook_url = self.settings.get("discord_webhook")
            if webhook_url:
                webhook = DiscordWebhook(webhook_url)
                success = webhook.send_alert(reason, details, timestamp)
                print(f"   Discord: {'✅ Sent' if success else '❌ Failed'}")
        
        # Auto-switch network if enabled
        if self.settings.get("auto_switch_enabled"):
            backup_network = self.settings.get("backup_network")
            if backup_network:
                print(f"   Switching to backup network: {backup_network}")
                success = self.network_manager.connect_to_network(backup_network)
                print(f"   Network switch: {'✅ Success' if success else '❌ Failed'}")
    
    def _handle_demo_event(self, attacker, target, timestamp):
        """Handle demo events"""
        print(f"\n🎭 DEMO EVENT!")
        print(f"   Time: {timestamp}")
        print(f"   Simulated Attack: {attacker} → {target}")
    
    def show_status(self):
        """Display current status"""
        print("\n📊 Current Status:")
        print(f"   Mode: {'Windows API' if os.name == 'nt' else 'Demo'}")
        print(f"   Monitoring: {'🟢 Active' if self.running else '🔴 Stopped'}")
        print(f"   Discord Alerts: {'🟢 Enabled' if self.settings.get('discord_enabled') else '🔴 Disabled'}")
        print(f"   Auto-Switch: {'🟢 Enabled' if self.settings.get('auto_switch_enabled') else '🔴 Disabled'}")
        
        if self.settings.get("auto_switch_enabled"):
            backup = self.settings.get("backup_network", "Not configured")
            print(f"   Backup Network: {backup}")
    
    def show_networks(self):
        """Display available networks"""
        print("\n📡 Available WiFi Networks:")
        profiles = self.network_manager.get_available_profiles()
        if profiles:
            for i, profile in enumerate(profiles, 1):
                print(f"   {i}. {profile}")
        else:
            print("   No saved WiFi profiles found")
    
    def start(self):
        """Start monitoring"""
        if not self.running:
            print("🚀 Starting WiFi Deauth Detector v2.0 (CLI Mode)")
            self.running = True
            self.monitor.start_monitoring()
            print("📡 Monitoring started - Press Ctrl+C to stop")
            self.show_status()
    
    def stop(self):
        """Stop monitoring"""
        if self.running:
            print("🛑 Stopping monitoring...")
            self.running = False
            self.monitor.stop_monitoring()
            print("✅ Monitoring stopped")
    
    def run_interactive(self):
        """Run interactive CLI mode"""
        print("🛡️ WiFi Deauth Detector v2.0 - Interactive CLI")
        print("=" * 50)
        
        while True:
            print("\nCommands:")
            print("  1. Start monitoring")
            print("  2. Stop monitoring") 
            print("  3. Show status")
            print("  4. Show networks")
            print("  5. Configure settings")
            print("  6. Exit")
            
            try:
                choice = input("\nEnter choice (1-6): ").strip()
                
                if choice == '1':
                    self.start()
                elif choice == '2':
                    self.stop()
                elif choice == '3':
                    self.show_status()
                elif choice == '4':
                    self.show_networks()
                elif choice == '5':
                    self.configure_settings()
                elif choice == '6':
                    self.stop()
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-6.")
                    
            except (KeyboardInterrupt, EOFError):
                self.stop()
                print("\n👋 Goodbye!")
                break
    
    def configure_settings(self):
        """Configure basic settings"""
        print("\n⚙️ Settings Configuration:")
        print("(Press Enter to keep current value)")
        
        # Discord webhook
        current_webhook = self.settings.get("discord_webhook", "")
        webhook = input(f"Discord webhook URL [{current_webhook}]: ").strip()
        if webhook:
            self.settings.set("discord_webhook", webhook)
            self.settings.set("discord_enabled", True)
        
        # Backup network
        current_backup = self.settings.get("backup_network", "")
        backup = input(f"Backup network name [{current_backup}]: ").strip()
        if backup:
            self.settings.set("backup_network", backup)
            self.settings.set("auto_switch_enabled", True)
        
        # Save settings
        if self.settings.save_settings():
            print("✅ Settings saved successfully!")
        else:
            print("❌ Failed to save settings")

def main():
    """Main CLI entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        detector = CLIDeauthDetector()
        
        if command == 'start':
            detector.start()
            try:
                while detector.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                detector.stop()
                
        elif command == 'status':
            detector.show_status()
            
        elif command == 'networks':
            detector.show_networks()
            
        elif command == 'interactive':
            detector.run_interactive()
            
        else:
            print("Usage: python cli.py [start|status|networks|interactive]")
            print("  start       - Start monitoring in background")
            print("  status      - Show current status")
            print("  networks    - List available WiFi networks")
            print("  interactive - Run interactive mode")
    else:
        # Default to interactive mode
        detector = CLIDeauthDetector()
        detector.run_interactive()

if __name__ == "__main__":
    main()