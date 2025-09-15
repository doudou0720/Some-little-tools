#!/usr/bin/env python3
"""
Nuitka build script for ClassisTime
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def build():
    """Build the application using Nuitka"""
    print("Building ClassisTime with Nuitka...")
    
    # Determine the appropriate command based on the OS
    if platform.system() == "Windows":
        cmd = [
            sys.executable, "-m", "nuitka",
            "--standalone",
            "--onefile",
            "--enable-plugin=tk-inter",
            "--windows-console-mode=disable",
            "--windows-icon-from-ico=icon.ico",  # You'll need to add an icon.ico file
            "--output-dir=dist",
            "main.py"
        ]
    else:
        cmd = [
            sys.executable, "-m", "nuitka",
            "--standalone",
            "--onefile",
            "--enable-plugin=tk-inter",
            "--output-dir=dist",
            "main.py"
        ]
    
    # Try to install Nuitka if not available
    try:
        import nuitka
    except ImportError:
        print("Installing Nuitka...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "nuitka"])
    
    # Run the build command
    try:
        print(f"Executing: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        print("Build completed successfully!")
        print("Output file can be found in the 'dist' directory.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Nuitka not found. Please install it with: pip install nuitka")
        sys.exit(1)

if __name__ == "__main__":
    build()