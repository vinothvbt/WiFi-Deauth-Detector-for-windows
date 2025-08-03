# WiFi Deauth Detector - Usage Instructions

## Issue 4 Implementation

This implementation provides real-time deauthentication frame detection with the following functionality:

### Features Implemented
- **Capture all packets**: Uses Scapy to capture wireless frames
- **Filter**: Specifically filters for `Dot11.type == 0 and Dot11.subtype == 12` (deauth frames)
- **Parse**: Extracts Source MAC, Destination MAC, and Timestamp
- **Print to console**: Real-time output of detected deauth frames

### Usage

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the detector**:
   ```bash
   python deauth_detector.py
   ```
   
   Note: On Windows, you need:
   - Administrator privileges
   - Npcap installed with monitor mode support
   - A wireless adapter that supports monitor mode

3. **Test the logic**:
   ```bash
   python test_deauth_detection.py
   ```

### Sample Output

When a deauth frame is detected, the output will look like:
```
[2025-08-03 17:25:49.116] DEAUTH DETECTED:
  Source MAC:      11:22:33:44:55:66
  Destination MAC: aa:bb:cc:dd:ee:ff
  Frame Type:      0
  Frame Subtype:   12
--------------------------------------------------
```

### Technical Details

- **Frame Type 0**: Management frames
- **Subtype 12**: Deauthentication frames
- **Source MAC**: The MAC address sending the deauth frame (potential attacker)
- **Destination MAC**: The MAC address receiving the deauth frame (victim)
- **Timestamp**: When the frame was captured

This implementation meets all requirements specified in Issue 4.