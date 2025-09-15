#!/usr/bin/env python3
"""
Schedule widget for displaying class timetable
"""

from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import json
from datetime import datetime

class ScheduleWidget(QWidget):
    """Widget to display the class schedule"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_sample_data()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create timetable grid (7 days x 12 periods)
        self.cells = {}
        
        # Add headers
        days = ['时间', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
        for col, day in enumerate(days):
            header = QLabel(day)
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.setStyleSheet("background-color: #4A90E2; color: white; font-weight: bold; padding: 10px;")
            layout.addWidget(header, 0, col)
            
        # Add time periods (example for 12 periods)
        periods = [
            '08:00\n08:45',
            '08:55\n09:40',
            '09:50\n10:35',
            '10:45\n11:30',
            '11:40\n12:25',
            '12:35\n13:20',
            '13:30\n14:15',
            '14:25\n15:10',
            '15:20\n16:05',
            '16:15\n17:00',
            '17:10\n17:55',
            '18:00\n18:45'
        ]
        
        for row, period in enumerate(periods, 1):
            time_label = QLabel(period)
            time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            time_label.setStyleSheet("background-color: #F0F0F0; font-weight: bold; padding: 5px;")
            layout.addWidget(time_label, row, 0)
            
            # Add cells for each day
            for col in range(1, 8):
                cell = ScheduleCell()
                layout.addWidget(cell, row, col)
                self.cells[(row-1, col-1)] = cell
                
        self.setLayout(layout)
        
    def load_sample_data(self):
        """Load sample schedule data"""
        # Sample data - in a real app this would come from a file or database
        sample_classes = {
            (0, 0): {"name": "数学", "room": "A101"},      # Monday, Period 1
            (0, 2): {"name": "英语", "room": "B205"},      # Wednesday, Period 1
            (1, 1): {"name": "物理", "room": "C301"},      # Tuesday, Period 2
            (2, 0): {"name": "化学", "room": "D405"},      # Monday, Period 3
            (3, 3): {"name": "语文", "room": "A202"},      # Thursday, Period 4
        }
        
        for (period, day), class_info in sample_classes.items():
            if (period, day) in self.cells:
                self.cells[(period, day)].set_class(class_info["name"], class_info["room"])


class ScheduleCell(QFrame):
    """A single cell in the schedule grid"""
    
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(0)
        
        # Create layout and labels
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.class_label = QLabel()
        self.class_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.class_label.setWordWrap(True)
        font = QFont()
        font.setPointSize(10)
        self.class_label.setFont(font)
        
        self.room_label = QLabel()
        self.room_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(8)
        self.room_label.setFont(font)
        self.room_label.setStyleSheet("color: gray;")
        
        layout.addWidget(self.class_label)
        layout.addWidget(self.room_label)
        
        self.setLayout(layout)
        
    def set_class(self, class_name, room):
        """Set the class information for this cell"""
        self.class_label.setText(class_name)
        self.room_label.setText(room)
        self.setStyleSheet("background-color: #E3F2FD; border: 1px solid #BBDEFB;")
        
    def clear_class(self):
        """Clear the class information from this cell"""
        self.class_label.setText("")
        self.room_label.setText("")
        self.setStyleSheet("background-color: white; border: 1px solid #e0e0e0;")