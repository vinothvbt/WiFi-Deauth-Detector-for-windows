"""
Create a visual representation of the GUI interface for documentation.
"""

def show_gui_layout():
    """Show what the GUI interface looks like."""
    gui_layout = """
╔══════════════════════════════════════════════════════════════╗
║                    🛡️ WiFi Deauth Detector                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Notification Settings                                       ║
║  ─────────────────────                                       ║
║                                                              ║
║  ☑️ Enable notifications                                      ║
║                                                              ║
║  ✅ Notifications enabled | Known attackers: 3               ║
║                                                              ║
║  [Test Notification]    [Clear Known Attackers]             ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Detection Log:                                              ║
║  ──────────────                                              ║
║                                                              ║
║  ┌────────────────────────────────────────────────────────┐ ║
║  │ Waiting for deauth attacks...                          │ ║
║  │ Simulated attack from AA:BB:CC:DD:EE:01               │ ║
║  │ Simulated attack from AA:BB:CC:DD:EE:02               │ ║
║  └────────────────────────────────────────────────────────┘ ║
║                                                              ║
║  [Simulate Attack #1]    [Simulate Attack #2]              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Key Features Shown:
━━━━━━━━━━━━━━━━━━

✅ Notification Toggle Checkbox
   - Easy on/off control for notifications
   - Immediately applies when clicked

✅ Status Display  
   - Shows if notifications are enabled/disabled
   - Displays count of known attackers

✅ Control Buttons
   - Test Notification: Send sample notification
   - Clear Known Attackers: Reset the detection list

✅ Detection Log Area
   - Shows recent attack detections
   - Updates in real-time when attacks detected

✅ Demo Buttons
   - Simulate different attack scenarios
   - Useful for testing and demonstration
"""
    
    print(gui_layout)
    
    print("\nNotification Popup Example:")
    print("─" * 50)
    notification_example = """
    ┌─ System Notification ────────────────────────┐
    │ 🚨 WiFi Deauth Attack Detected!              │
    │                                              │
    │ New attacker detected: AA:BB:CC:DD:EE:FF     │
    │ Target: 11:22:33:44:55:66                    │
    │ Time: 17:31:25                               │
    │                                              │
    │                                   [X] Close  │
    └──────────────────────────────────────────────┘
    """
    print(notification_example)


if __name__ == "__main__":
    show_gui_layout()