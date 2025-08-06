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