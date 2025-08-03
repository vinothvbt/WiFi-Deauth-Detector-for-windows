# WiFi Deauth Detector - Usage Guide

## Features

- **Real-time deauth detection monitoring** (demo mode)
- **Persistent logging system** with JSON storage
- **GUI interface** with PyQt5
- **"Open Logs" button** to view recent log entries
- **Popup window** displaying last 20 log entries

## Installation

1. Install Python 3.7+ 
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the Application
```bash
python wifi_deauth_detector.py
```

### GUI Features

1. **Main Window**:
   - Start/Stop detection monitoring
   - View real-time detection events
   - Access log history

2. **Open Logs Button**:
   - Click "Open Logs" to view recent activity
   - Displays last 20 log entries in chronological order
   - Shows timestamps, log levels, and MAC addresses
   - Popup window with scrollable content

3. **Log Information**:
   - Timestamps in YYYY-MM-DD HH:MM:SS format
   - Log levels: INFO, WARNING, CRITICAL
   - MAC addresses for detected deauth packets
   - Persistent storage in `deauth_logs.json`

## Testing

Run the test suites to verify functionality:

```bash
# Test logging functionality
python test_logging.py

# Test GUI components
python test_gui_functionality.py
```

## Log File Format

Logs are stored in `deauth_logs.json` with the following structure:
```json
[
  {
    "timestamp": "2025-08-03T17:30:00.000000",
    "level": "WARNING",
    "message": "Deauth packet detected",
    "source_mac": "AA:BB:CC:DD:EE:FF",
    "target_mac": "11:22:33:44:55:66"
  }
]
```

## Development Notes

- This is currently a demonstration version
- In production, would integrate with actual packet capture
- Requires Windows with Npcap for real WiFi monitoring
- GUI designed for Windows but runs on Linux for testing