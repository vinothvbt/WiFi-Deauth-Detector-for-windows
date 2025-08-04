# 🛡️ WiFi Deauth Detector — Windows App

A lightweight real-time WiFi deauthentication attack detector for Windows. Built for penetration testers, ethical hackers, and paranoid netizens. This app monitors the local wireless environment for signs of WiFi deauth/disassoc attacks and alerts the user via GUI or system notifications.

> ✅ Works on Windows with **Npcap** in monitor mode  
> ✅ Built for **low-end devices** — no heavy dependencies  
> ✅ Future plans: auto-switch networks, logging, Discord webhook alert

---

## ⚙️ Features

- 🚨 Real-time **deauthentication attack detection**
- 🧠 Identifies attacking MAC address
- 🪟 Lightweight **GUI interface** (PyQt5 or Tauri)
- 🔔 Toast/system notification alerts
- 📄 Event log for auditing
- 🔒 Future: auto-connect to backup AP on attack

---

## 📸 Screenshots

> *[Add GUI screenshots after MVP build]*

---

## 💻 Tech Stack

| Layer          | Technology     | Notes                          |
|----------------|----------------|--------------------------------|
| GUI            | PyQt5 / Tauri  | Cross-platform possible later  |
| Packet Sniffer | Scapy (Python) or custom Rust logic | Needs `Npcap` for raw access     |
| Alerts         | Plyer (Python) or Windows Toast API | System tray or pop-up alerts     |
| Network Tools  | `netsh` (Windows CLI) | Used for reconnect/network switch |

---

## 🧠 How It Works

### WiFi Deauth Attacks 101

- WiFi networks use management frames for connection control.
- Deauthentication frames (`type=0`, `subtype=12`) are **unauthenticated** and **spoofable**.
- Attackers send fake deauth frames to kick users off WiFi (DoS).

### This Tool Does:

1. Sniffs all wireless frames (via `Npcap` in monitor mode).
2. Filters for deauth frames (`Dot11Deauth`) or subtype=12.
3. Extracts **target MAC** and **attacker MAC**.
4. Alerts user and optionally logs or switches WiFi.

---

## 🛠️ Installation

### 1. Prerequisites

- **Windows 10/11**
- **Npcap** (must be installed in *"WinPcap Compatible Mode"* with *"Support raw 802.11 traffic"*)
  - [Download Npcap](https://npcap.com/#download)
- Wireless adapter that supports monitor mode (not all do)
- Python 3.10+ installed  
  OR  
- Rust toolchain (if going Rust+Tauri route)

---

### 2. Python Setup (Fast Start)

```bash
git clone https://github.com/vinothvbt/WiFi-Deauth-Detector-for-windows.git
cd WiFi-Deauth-Detector-for-windows
```

#### Option A: Automated Setup (Recommended)

**Windows:**
```cmd
setup_venv.bat
```

**Linux/macOS:**
```bash
./setup_venv.sh
```

#### Option B: Manual Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
