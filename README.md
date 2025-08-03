# 🛡️ WiFi Deauth Detector — Windows App v1.0.0

A lightweight real-time WiFi deauthentication attack detector for Windows. Built for penetration testers, ethical hackers, and paranoid netizens. This app monitors the local wireless environment for signs of WiFi deauth/disassoc attacks and alerts the user via GUI or system notifications.

> ✅ Works on Windows with **Npcap** in monitor mode  
> ✅ Built for **low-end devices** — no heavy dependencies  
> ✅ **AUTO-SWITCH NETWORKS** on attack detection  
> ✅ **DISCORD WEBHOOK ALERTS** with attack details  
> ✅ Complete **GUI interface** with settings management

---

## ⚙️ Features

### 🚨 Core Detection
- **Real-time deauthentication attack detection**
- **Identifies attacking MAC address** and target
- **Timestamp tracking** for all events
- **Configurable monitoring** with start/stop controls

### 🔄 Auto Network Switching *(NEW!)*
- **Automatically switch to backup WiFi** when attack detected  
- **Configurable backup network** from available profiles
- **Optional confirmation dialog** before switching
- **Uses Windows netsh commands** for reliable switching

### 📱 Discord Webhook Integration *(NEW!)*
- **Send alerts to Discord channels** via webhooks
- **Rich embed formatting** with attack details
- **Toggle on/off** from GUI settings
- **Test webhook functionality** built-in

### 🪟 User Interface
- **Modern PyQt5 GUI** with tabbed interface
- **Real-time monitoring status** and statistics  
- **Settings management** with persistent storage
- **Event logging** with export capabilities
- **System tray integration** for background operation

### 🔔 Notifications & Logging
- **System toast notifications** on attack detection
- **Comprehensive event logging** to file
- **Attack statistics** and history tracking
- **Export logs** functionality

---

## 📸 Screenshots

### Monitor Tab - Real-time Detection
![Monitor Tab](screenshot_monitor.png)
*Main monitoring interface showing detection status, recent alerts, and attack statistics*

### Settings Tab - Configuration
![Settings Tab](screenshot_settings.png)  
*Configure auto-switching, Discord webhooks, and general preferences*

### Logs Tab - Event History
![Logs Tab](screenshot_logs.png)
*View detailed logs of all detected attacks and system events*

---

## 🛠️ Installation & Setup

### Prerequisites

1. **Windows 10/11** with Administrator privileges
2. **Npcap** installed in *"WinPcap Compatible Mode"* with *"Support raw 802.11 traffic"*
   - [Download Npcap](https://npcap.com/#download)
3. **Wireless adapter** that supports monitor mode
4. **Python 3.8+** (for source) OR use pre-built executable

### Option 1: Download Pre-built Executable *(Recommended)*

1. Download the latest release from [Releases](../../releases)
2. Extract the ZIP file
3. Run `install_and_run.bat` as Administrator
4. The app will start automatically

### Option 2: Run from Source

```bash
# Clone repository
git clone https://github.com/vinothvbt/WiFi-Deauth-Detector-for-windows.git
cd WiFi-Deauth-Detector-for-windows

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Option 3: Build Your Own Executable

```bash
# After setting up source (Option 2)
python build.py

# Executable will be created in dist/ folder
```

---

## 🚀 Quick Start Guide

### 1. Initial Setup
1. **Install Npcap** with monitor mode support
2. **Run the application** as Administrator
3. **Configure settings** in the Settings tab

### 2. Configure Auto Network Switching
1. Go to **Settings** tab
2. Check **"Enable auto-switch on attack"**
3. Select your **backup network** from dropdown
4. Choose if you want **confirmation dialogs**
5. Click **"Refresh Networks"** to update available WiFi

### 3. Setup Discord Webhooks *(Optional)*
1. Create a Discord webhook in your server
2. Copy the webhook URL
3. Paste it in **Settings** → **Discord Webhook URL**
4. Check **"Enable Discord alerts"**
5. Click **"Test Webhook"** to verify

### 4. Start Monitoring
1. Go to **Monitor** tab
2. Click **"Start Monitoring"**
3. The app will now detect deauth attacks in real-time
4. Check **Logs** tab for detailed event history

---

## ⚡ Auto-Switch Network Feature

When a deauth attack is detected:

1. **Alert triggers** — System notification + Discord webhook (if enabled)
2. **Confirmation prompt** — Optional dialog asking to switch networks
3. **Network switch** — Automatically connects to configured backup WiFi
4. **Status update** — Logs the switch attempt and result

**Supported Commands:**
- `netsh wlan show profiles` — Lists available networks
- `netsh wlan connect name="NetworkName"` — Connects to specified network

**Requirements:**
- Administrator privileges for netsh commands
- Backup network must be previously saved in Windows

---

## 🎯 Discord Webhook Integration

### Webhook Message Format

```json
{
  "embeds": [
    {
      "title": "🚨 WiFi Deauth Attack Detected!",
      "color": 16711680,
      "fields": [
        {"name": "Attacker MAC", "value": "aa:bb:cc:dd:ee:ff", "inline": true},
        {"name": "Target MAC", "value": "11:22:33:44:55:66", "inline": true},
        {"name": "Timestamp", "value": "2024-08-03 17:30:15", "inline": false}
      ],
      "footer": {"text": "WiFi Deauth Detector"}
    }
  ]
}
```

### Setting Up Discord Webhook

1. Open Discord server → Edit Channel → Integrations → Webhooks
2. Click "New Webhook"
3. Copy the webhook URL
4. Paste in app settings and test

---

## 🧪 Testing

Run the test suite to validate functionality:

```bash
python test.py
```

**Test Coverage:**
- ✅ Settings management (save/load)
- ✅ Network manager (profile detection, connection)
- ✅ Discord webhook (success/failure scenarios)
- ✅ Core application components

---

## 🔧 Development

### Project Structure

```
WiFi-Deauth-Detector-for-windows/
├── main.py              # Main application with GUI
├── test.py              # Test suite
├── build.py             # Build script for executable
├── demo.py              # Demo script for testing
├── requirements.txt     # Python dependencies
├── settings.json        # User settings (auto-generated)
├── deauth_log.txt       # Attack log file (auto-generated)
└── dist/                # Built executable (after build)
    ├── WiFiDeauthDetector
    ├── install_and_run.bat
    └── README.md
```

### Building Executable

```bash
python build.py
```

Creates a standalone executable in the `dist/` folder using PyInstaller.

### Running Tests

```bash
python test.py
```

Validates core functionality without requiring GUI or network interfaces.

---

## 💡 Usage Tips

### For Penetration Testers
- Use this tool to **detect when you're being detected** during wireless assessments
- **Monitor client disconnection patterns** during deauth attacks
- **Validate defensive measures** by testing auto-switching functionality

### For Network Defenders  
- **Deploy on critical machines** to detect wireless attacks
- **Configure Discord alerts** for real-time SOC notifications
- **Set up backup networks** for business continuity during attacks

### For Paranoid Users
- **Run continuously** to monitor your wireless environment
- **Use auto-switch** to maintain connectivity during attacks
- **Review logs** to identify patterns or persistent attackers

---

## 🛡️ Security Considerations

### Permissions Required
- **Administrator privileges** for raw packet capture (Npcap requirement)
- **Network access** for Discord webhooks and network switching
- **File system access** for logging and settings storage

### Privacy Notes
- **No data is sent externally** except Discord webhooks (if configured)
- **All logs are stored locally** in plaintext files
- **Settings are stored unencrypted** in JSON format
- **MAC addresses are logged** for attack identification

### Limitations
- **Monitor mode support** varies by wireless adapter
- **Windows-only** due to netsh dependency (netsh commands are Windows-specific)
- **Requires Npcap** for raw 802.11 frame capture
- **Simulated detection** in demo mode (real packet capture needs appropriate hardware)

---

## 🐛 Troubleshooting

### Common Issues

**Q: "No Qt platform plugin" error**
- A: Install Qt libraries or run on Windows with proper GUI support

**Q: Network switching doesn't work**
- A: Ensure app is running as Administrator and backup network is saved in Windows

**Q: Discord webhook fails**
- A: Check webhook URL format and network connectivity

**Q: No attacks detected**
- A: Verify Npcap installation and monitor mode support on your wireless adapter

**Q: App won't start**
- A: Check Python dependencies with `pip install -r requirements.txt`

### Debug Mode

Enable verbose logging by setting environment variable:
```cmd
set WIFI_DEAUTH_DEBUG=1
python main.py
```

---

## 🔄 Version History

### v1.0.0 - Initial Release
- ✅ Real-time deauth detection simulation
- ✅ Auto network switching with netsh integration  
- ✅ Discord webhook alerts with rich embeds
- ✅ Complete PyQt5 GUI with tabbed interface
- ✅ Settings management with JSON persistence
- ✅ Event logging and export functionality
- ✅ System tray integration and notifications
- ✅ Executable packaging with PyInstaller
- ✅ Comprehensive test suite

---

## 📋 TODO / Future Features

- [ ] **Real packet capture** implementation (replace simulation)
- [ ] **Multi-adapter support** for monitoring multiple interfaces
- [ ] **Machine learning** for attack pattern recognition
- [ ] **Email notifications** as alternative to Discord
- [ ] **Portable mode** without installation requirements
- [ ] **Network visualization** of detected attacks
- [ ] **Custom alert sounds** and notification styles
- [ ] **API integration** with security platforms (SIEM/SOAR)

---

## 🤝 Contributing

Contributions welcome! Please:

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'Add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Open Pull Request**

### Development Guidelines
- Follow **PEP 8** style guide for Python code
- Add **tests** for new functionality
- Update **documentation** for user-facing changes
- Test on **Windows 10/11** before submitting

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is for **educational and defensive purposes only**. Users are responsible for compliance with local laws and regulations regarding network monitoring and security testing. The authors are not responsible for any misuse or damage caused by this software.

**Use responsibly and only on networks you own or have explicit permission to monitor.**

---

## 🙏 Acknowledgments

- **Npcap Team** for Windows packet capture capabilities
- **PyQt5 Project** for cross-platform GUI framework  
- **Scapy Contributors** for packet manipulation library
- **Discord** for webhook API enabling real-time alerts
- **Security Community** for wireless attack research and defense techniques

---

*Built with ❤️ for the cybersecurity community*
