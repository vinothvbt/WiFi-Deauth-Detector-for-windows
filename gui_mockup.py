#!/usr/bin/env python3
"""
Create a mockup of the GUI for documentation purposes
"""

def create_gui_mockup():
    mockup = """
WiFi Deauth Detector - GUI Layout
=================================

┌──────────────────────────────────────────────────────────┐
│                WiFi Deauthentication Attack Detector     │
│                                                          │
│                    Status: Monitoring...                 │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Detection Log:                                     │  │
│  │ Detection started...                               │  │
│  │ 🚨 Deauth packet detected - Source: AA:BB:CC...   │  │
│  │ Detection active...                                │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │ Stop Detection│  │  Open Logs   │                     │
│  └──────────────┘  └──────────────┘                     │
│                                                          │
│  Note: This is a demonstration version. In production,   │
│  this would monitor wireless traffic for deauth attacks. │
└──────────────────────────────────────────────────────────┘

"Open Logs" Popup Window:
========================

┌──────────────────────────────────────────────────────────┐
│             Last 20 Deauth Detection Logs               │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ [2025-08-03 17:30:25] INFO: Application started   │  │
│  │ [2025-08-03 17:30:26] WARNING: Deauth packet     │  │
│  │   detected | Source: AA:BB:CC:DD:EE:FF            │  │
│  │   | Target: 11:22:33:44:55:66                     │  │
│  │ [2025-08-03 17:30:27] CRITICAL: Multiple deauth  │  │
│  │   packets detected - possible attack!             │  │
│  │ [2025-08-03 17:30:28] INFO: Monitoring resumed    │  │
│  │ [2025-08-03 17:30:29] WARNING: Suspicious deauth │  │
│  │   activity | Source: FF:EE:DD:CC:BB:AA            │  │
│  │ ...                                               │  │
│  │ (Shows last 20 entries, most recent first)       │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│                    ┌──────────┐                         │
│                    │  Close   │                         │
│                    └──────────┘                         │
└──────────────────────────────────────────────────────────┘
"""
    return mockup

if __name__ == "__main__":
    print(create_gui_mockup())