#!/usr/bin/env python3
"""
Main entry point for ClassisTime - A PyQt6-based class schedule application
"""

import sys
import os
from pathlib import Path

# Add the project root to the path so we can import our packages
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for the application"""
    # Import here to avoid issues with path
    from classistime.app import ClassisTimeApp
    
    # Create and run the application
    app = ClassisTimeApp(sys.argv)
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())