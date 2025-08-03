# WiFi Deauth Detector Implementation

## Overview
This implementation addresses Issue 5 by providing functionality to:
- Log addr1, addr2, addr3 from WiFi deauth frames
- Identify the most frequent source MAC address
- Display "Possible attacker: XX:XX:XX:XX:XX:XX"

## Features Implemented

### 1. Address Logging
The detector captures and logs the three address fields from 802.11 deauth frames:
- **addr1**: Destination MAC address (target device)
- **addr2**: Source MAC address (potential attacker)
- **addr3**: BSSID or additional address information

### 2. MAC Frequency Tracking
- Tracks frequency of source MAC addresses (addr2)
- Uses Python's `Counter` class for efficient frequency counting
- Maintains a running count of frames per source MAC

### 3. Attacker Identification
- Identifies the most frequent source MAC as potential attacker
- Requires minimum of 2 frames to consider a MAC as suspicious
- Displays alert: "Possible attacker: XX:XX:XX:XX:XX:XX"

### 4. Additional Features
- Real-time frame logging with timestamps
- Target device tracking (shows which devices are being attacked)
- Periodic summary reports
- Attack log for forensic analysis
- Colorized console output for better visibility

## Files

### `wifi_deauth_detector.py`
Main implementation file containing the `WiFiDeauthDetector` class with:
- `log_frame_addresses()`: Extracts and logs addr1, addr2, addr3
- `identify_attacker()`: Finds most frequent source MAC
- `display_attacker_info()`: Shows attacker information
- Command-line interface for live monitoring

### `test_detector.py`
Comprehensive test suite that validates:
- MAC address frequency tracking
- Attacker identification logic
- Edge cases (empty data, single frames)
- Expected output format

### `demo.py`
Interactive demonstration script that shows:
- Simulated deauth attack scenario
- Real-time frame logging
- Attacker identification process
- Summary reporting

## Usage

### Basic Usage
```bash
# List available network interfaces
python wifi_deauth_detector.py --list

# Monitor specific interface
python wifi_deauth_detector.py -i <interface_name>

# Set custom display interval
python wifi_deauth_detector.py -i <interface_name> -t 60
```

### Testing
```bash
# Run test suite
python test_detector.py

# Run demo
python demo.py
```

## Example Output

When a deauth attack is detected:
```
[FRAME] 2025-08-03 17:30:01
  addr1 (dest): AA:BB:CC:DD:EE:11
  addr2 (src):  DE:AD:BE:EF:CA:FE
  addr3 (bssid): 00:11:22:33:44:55
  type: deauth

[ALERT] 2025-08-03 17:30:05
Possible attacker: DE:AD:BE:EF:CA:FE
Deauth frames sent: 5
Targets: AA:BB:CC:DD:EE:11, AA:BB:CC:DD:EE:22, AA:BB:CC:DD:EE:33
```

## Requirements

- Python 3.6+
- Scapy >= 2.4.5
- psutil >= 5.9.0
- colorama >= 0.4.6
- Windows with Npcap (for actual monitoring)
- Network interface with monitor mode support

## Technical Details

### 802.11 Frame Structure
The implementation correctly handles the three address fields in 802.11 frames:
- Address 1: Receiver address (target)
- Address 2: Transmitter address (source/attacker)
- Address 3: Filtering address (usually BSSID)

### Attack Detection Logic
1. Captures deauth/disassoc frames using Scapy
2. Extracts source MAC (addr2) from each frame
3. Increments counter for each source MAC
4. Identifies MAC with highest frequency as potential attacker
5. Displays alert when frequency threshold is met (≥2 frames)

### Performance Considerations
- Uses efficient Counter data structure for frequency tracking
- Minimal memory footprint with periodic cleanup options
- Real-time processing with configurable display intervals
- Thread-safe implementation for concurrent operation