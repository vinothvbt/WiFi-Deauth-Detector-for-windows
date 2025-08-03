# WiFi Deauth Detector - Notification System

This implementation provides notification alerts for WiFi deauthentication attack detection as specified in Issue 7.

## Features Implemented

✅ **Plyer.notification integration** - System notifications for security alerts  
✅ **New attacker MAC detection** - Alerts only for previously unseen attackers  
✅ **GUI toggle for notifications** - Enable/disable notifications via interface  
✅ **Duplicate filtering** - Prevents spam from repeated attacks by same MAC  
✅ **Fallback notifications** - Console output when system notifications unavailable  
✅ **Integration hooks** - Easy integration with packet detection logic  

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Basic Usage

```python
from src.deauth_integration import trigger_deauth_detection, configure_notifications

# Enable notifications
configure_notifications(True)

# Trigger notification when deauth attack detected
trigger_deauth_detection("AA:BB:CC:DD:EE:FF", "Target:Device:MAC")
```

### 3. GUI Interface

```python
from src.gui import main
main()  # Starts GUI with notification toggle
```

## API Reference

### NotificationManager

Core notification handling:

```python
from src.notification_manager import NotificationManager

notif = NotificationManager(enabled=True)
notif.notify_new_attacker("attacker_mac", "target_mac")
notif.set_enabled(False)  # Disable notifications
```

### DeauthDetectionIntegration

High-level integration layer:

```python
from src.deauth_integration import detection_integration

# Register custom callback
def my_callback(attacker_mac, target_mac, timestamp):
    print(f"Attack detected: {attacker_mac}")

detection_integration.register_detection_callback("logger", my_callback)

# Trigger detection
detection_integration.on_deauth_detected("AA:BB:CC:DD:EE:FF")
```

## Testing

Run the notification system tests:

```bash
python test_notifications.py
python demo.py
```

## Integration with Packet Detection

The notification system is designed to integrate with packet capture logic:

```python
# In your packet capture callback:
def packet_handler(packet):
    if is_deauth_packet(packet):
        attacker_mac = extract_attacker_mac(packet)
        target_mac = extract_target_mac(packet)
        
        # Trigger notification for new attackers
        trigger_deauth_detection(attacker_mac, target_mac)
```

## File Structure

```
src/
├── notification_manager.py    # Core notification logic
├── deauth_integration.py     # Integration layer
├── gui.py                   # GUI with notification toggle
└── mock_notification.py     # Testing utilities

demo.py                      # Demo script
test_notifications.py       # Comprehensive tests
requirements.txt            # Dependencies
```

## Configuration

### Enable/Disable Notifications

```python
# Via integration layer
configure_notifications(True)   # Enable
configure_notifications(False)  # Disable

# Via notification manager directly
notif_manager.set_enabled(True)
```

### Custom Notification Messages

Customize notification content in `NotificationManager.notify_new_attacker()`:

```python
title = "🚨 WiFi Deauth Attack Detected!"
message = f"New attacker detected: {attacker_mac}"
```

## Requirements

- Python 3.6+
- plyer >= 2.1.0 (for system notifications)
- PyQt5 >= 5.15.0 (for GUI toggle)
- scapy >= 2.5.0 (for packet detection integration)

## Notes

- Notifications gracefully degrade to console output if system notifications unavailable
- Duplicate attacker filtering prevents notification spam
- GUI requires display environment (X11/Wayland on Linux, Windows desktop on Windows)
- All components can work independently for modular integration