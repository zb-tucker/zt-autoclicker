"""
Build script to create standalone .exe using PyInstaller
Run this once to create the executable.
"""

import subprocess
import sys
import os

def build_exe():
    """Build the mouse clicker executable"""
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "keyboard"])
        return
    
    print("Building mouse_clicker.exe...")
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--icon=NONE",
        "--name=MouseClicker",
        "--distpath=./dist",
        "--workpath=./build",
        "--specpath=./build",
        "mouse_clicker.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✓ Build successful!")
        print("Executable location: ./dist/MouseClicker.exe")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    build_exe()
