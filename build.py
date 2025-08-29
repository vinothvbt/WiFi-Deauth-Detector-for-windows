#!/usr/bin/env python3
"""
Build script for WiFi Deauth Detector
Creates executable with PyInstaller
"""

import os
import sys
import subprocess
import shutil

def build_exe():
    """Build executable using PyInstaller"""
    print("Building WiFi Deauth Detector executable...")
    
    # PyInstaller command - use : separator for Linux/Mac, ; for Windows
    separator = ";" if os.name == 'nt' else ":"
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "WiFiDeauthDetector",
        "--add-data", f"requirements.txt{separator}.",
        "main.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Build completed successfully!")
        print("📁 Executable created in 'dist' folder")
        
        # Copy readme to dist folder
        if os.path.exists("README.md"):
            shutil.copy2("README.md", "dist/")
            print("📋 README.md copied to dist folder")
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        return False
    except FileNotFoundError:
        print("\n❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False
    
    return True

def create_installer():
    """Create a simple batch installer"""
    installer_content = '''@echo off
echo Installing WiFi Deauth Detector v2.0...
echo.
echo Features:
echo - Works on ANY Windows laptop (no special hardware)
echo - Normal mode operation (no monitor mode required)
echo - Real-time WiFi connection monitoring
echo - Auto network switching on suspicious activity
echo - Discord webhook alerts
echo.
echo Requirements:
echo - Windows 10/11
echo - Standard WiFi adapter (any brand/model)
echo - No administrator privileges required
echo.
pause
echo.
echo Starting WiFi Deauth Detector...
WiFiDeauthDetector.exe
'''
    
    with open("dist/install_and_run.bat", "w") as f:
        f.write(installer_content)
    
    print("📦 Installer script created: dist/install_and_run.bat")

if __name__ == "__main__":
    print("🛠️  WiFi Deauth Detector Build Script")
    print("=" * 40)
    
    if build_exe():
        create_installer()
        print("\n🎉 Build process completed!")
        print("\nFiles in dist/ folder:")
        if os.path.exists("dist"):
            for file in os.listdir("dist"):
                print(f"  📄 {file}")
    else:
        print("\n💥 Build failed!")
        sys.exit(1)