#!/usr/bin/env python3
"""
Example extension for ClassisTime
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class ExampleExtension:
    def __init__(self, app):
        self.app = app
        self.widget = None
        
    def get_name(self):
        return "示例扩展"
        
    def get_description(self):
        return "这是一个示例扩展"
        
    def create_widget(self):
        """Create and return the extension widget"""
        if self.widget is None:
            self.widget = QWidget()
            layout = QVBoxLayout()
            
            label = QLabel("这是示例扩展的内容")
            label.setWordWrap(True)
            
            layout.addWidget(label)
            self.widget.setLayout(layout)
            
        return self.widget
        
    def on_load(self):
        """Called when extension is loaded"""
        print("Example extension loaded")
        
    def on_unload(self):
        """Called when extension is unloaded"""
        print("Example extension unloaded")