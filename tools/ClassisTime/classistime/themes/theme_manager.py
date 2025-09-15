#!/usr/bin/env python3
"""
Theme manager for ClassisTime application
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
import json
import os
from pathlib import Path

class ThemeManager:
    """Manages application themes"""
    
    def __init__(self):
        self.themes_dir = Path(__file__).parent
        self.themes = {}
        self.load_themes()
        
    def load_themes(self):
        """Load all available themes"""
        # Add default theme
        self.themes["default"] = {
            "name": "默认主题",
            "primary_color": "#4A90E2",
            "secondary_color": "#E3F2FD",
            "background_color": "#FFFFFF",
            "text_color": "#000000",
            "accent_color": "#FF6B35"
        }
        
        # Add dark theme
        self.themes["dark"] = {
            "name": "暗色主题",
            "primary_color": "#2196F3",
            "secondary_color": "#1565C0",
            "background_color": "#36393F",
            "text_color": "#FFFFFF",
            "accent_color": "#FF5252"
        }
        
    def get_theme(self, theme_name):
        """Get theme by name"""
        return self.themes.get(theme_name, self.themes["default"])
        
    def apply_theme(self, widget, theme_name):
        """Apply a theme to a widget"""
        theme = self.get_theme(theme_name)
        
        # Apply to entire application
        if isinstance(widget, QApplication):
            palette = widget.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor(theme["background_color"]))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(theme["text_color"]))
            palette.setColor(QPalette.ColorRole.Base, QColor(theme["background_color"]))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme["secondary_color"]))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme["background_color"]))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme["text_color"]))
            palette.setColor(QPalette.ColorRole.Text, QColor(theme["text_color"]))
            palette.setColor(QPalette.ColorRole.Button, QColor(theme["secondary_color"]))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme["text_color"]))
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(theme["primary_color"]))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(theme["primary_color"]))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme["background_color"]))
            widget.setPalette(palette)
            
    def list_themes(self):
        """Return a list of available themes"""
        return [(name, theme["name"]) for name, theme in self.themes.items()]