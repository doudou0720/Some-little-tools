#!/usr/bin/env python3
"""
Current schedule display widget for ClassisTime
This widget displays today's schedule at the top of the screen, similar to ClassIsland
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QSizePolicy, QScroller
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRect
from PyQt6.QtGui import QFont, QPalette
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Dict, Optional, List, cast
import json
import os
from pathlib import Path

if TYPE_CHECKING:
    from PyQt6.QtCore import QEvent
    from PyQt6.QtGui import QResizeEvent, QShowEvent
    from PyQt6.QtWidgets import QApplication

# Type aliases for better readability
ClassInfo = Dict[str, str]
ScheduleList = list[ClassInfo]

class CurrentScheduleWidget(QFrame):
    """Widget to display today's schedule at the top of the screen"""
    
    # Signal to notify when widget width changes
    width_changed = pyqtSignal()
    
    def __init__(self) -> None:
        super().__init__()
        self.setup_ui()
        self.today_schedule: ScheduleList = []
        self.load_schedule()
        self.update_current_class()
        
        # Setup timer to update current class
        self.timer: QTimer = QTimer()
        self.timer.timeout.connect(self.update_current_class)  # type: ignore
        self.timer.start(60000)  # Update every minute
        
        # Setup timer for countdown
        self.countdown_timer: QTimer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)  # type: ignore
        self.countdown_active: bool = False
        self.countdown_end_time: Optional[datetime] = None
        self.countdown_widget: Optional[QWidget] = None
        self.countdown_label: Optional[QLabel] = None
        self.current_time_label: Optional[QLabel] = None
        self.schedule_layout: QHBoxLayout
        self.container: QFrame
        self.screen_geometry: QRect = QRect()
        
    def setup_ui(self) -> None:
        """Setup the user interface"""
        # Make widget stay on top and not show in taskbar
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool  # This flag prevents the window from appearing in the taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Setup main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create container widget with reduced depth
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 180);
                border-radius: 6px;
            }
        """)
        
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(12, 4, 12, 4)  # Reduced vertical margins
        container_layout.setSpacing(12)
        
        # Schedule layout (removed title header)
        self.schedule_layout = QHBoxLayout()
        self.schedule_layout.setSpacing(12)
        self.schedule_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add widgets to container
        container_layout.addLayout(self.schedule_layout)
        
        # Add container to main layout
        main_layout.addWidget(self.container)
        
        # Allow widget to adjust its size based on content
        self.setMinimumHeight(36)  # Reduced minimum height
        self.setMaximumHeight(40)  # Set maximum height to limit depth
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        # Enable touch scrolling
        self.setup_touch_scrolling()
        
    def setup_touch_scrolling(self) -> None:
        """Setup touch scrolling for better touch screen experience"""
        # Enable kinetic scrolling for touch devices
        QScroller.grabGesture(self.container, QScroller.ScrollerGestureType.TouchGesture)
        
        # Adjust for better touch experience
        self.container.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)
        
    def load_schedule(self) -> None:
        """Load schedule data from file"""
        try:
            schedule_file = Path(__file__).parent.parent / "data" / "current_schedule.json"
            if os.path.exists(schedule_file):
                with open(schedule_file, 'r', encoding='utf-8') as f:
                    self.today_schedule = json.load(f)
            else:
                # Load sample data if no file exists
                self.load_sample_data()
                
            # Create labels for each class
            self.populate_schedule_display()
        except Exception as e:
            print(f"Error loading schedule: {e}")
            # Load sample data if there's an error
            self.load_sample_data()
            
    def load_sample_data(self) -> None:
        """Load sample schedule data"""
        # Sample data for today's schedule (without room information)
        # Added actual time information for countdown functionality
        self.today_schedule = [
            {"time": "08:00-08:45", "subject": "数学", "start_time": "08:00", "end_time": "08:45"},
            {"time": "08:55-09:40", "subject": "英语", "start_time": "08:55", "end_time": "09:40"},
            {"time": "09:50-10:35", "subject": "物理", "start_time": "09:50", "end_time": "10:35"},
            {"time": "10:45-11:30", "subject": "化学", "start_time": "10:45", "end_time": "11:30"},
            {"time": "11:40-12:25", "subject": "语文", "start_time": "11:40", "end_time": "12:25"},
            {"time": "12:35-13:20", "subject": "自习", "start_time": "12:35", "end_time": "13:20"},
        ]
        
        # Create labels for each class
        self.populate_schedule_display()
            
    def populate_schedule_display(self) -> None:
        """Populate the schedule display with data"""
        # Clear existing widgets
        for i in reversed(range(self.schedule_layout.count())): 
            item = self.schedule_layout.takeAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()
                
        # Create labels for each class
        for class_info in self.today_schedule:
            class_widget = self.create_class_widget(class_info)
            self.schedule_layout.addWidget(class_widget)
            
        # Notify that width may have changed
        self.width_changed.emit()
            
    def create_class_widget(self, class_info: ClassInfo) -> QWidget:
        """Create a widget for a single class with only subject name"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 20);
                border-radius: 4px;
                padding: 6px 12px;  /* Reduced vertical padding */
                min-height: 24px;   /* Reduced minimum height */
            }
        """)
        
        # Make widget more touch-friendly
        widget.setMinimumWidth(80)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(12, 6, 12, 6)  # Reduced vertical margins
        
        # Subject label (only info displayed)
        subject_label = QLabel(class_info["subject"])
        subject_font = QFont()
        subject_font.setPointSize(10)
        subject_font.setBold(True)
        subject_label.setFont(subject_font)
        subject_label.setStyleSheet("color: white;")
        subject_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(subject_label)
        
        return widget
        
    def update_current_class(self) -> None:
        """Highlight the current class based on system time"""
        # Get current time
        current_time = datetime.now()
        
        # Reset all widgets to default style
        for i in range(self.schedule_layout.count()):
            item = self.schedule_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setStyleSheet("""
                        QWidget {
                            background-color: rgba(255, 255, 255, 20);
                            border-radius: 4px;
                            padding: 6px 12px;  /* Reduced vertical padding */
                            min-height: 24px;   /* Reduced minimum height */
                        }
                    """)
        
        # Check for upcoming classes (within 30 seconds)
        upcoming_class_index = self.get_upcoming_class_index(current_time)
        if upcoming_class_index is not None:
            self.start_countdown(upcoming_class_index, current_time)
            return
        
        # Highlight current class (simplified logic for demo)
        # In a real app, this would compare actual times
        hour = current_time.hour
        if 8 <= hour < 9:
            self.highlight_class(0)  # First class
        elif 9 <= hour < 10:
            self.highlight_class(1)  # Second class
        elif 10 <= hour < 11:
            self.highlight_class(2)  # Third class
        elif 11 <= hour < 12:
            self.highlight_class(3)  # Fourth class
        elif 12 <= hour < 13:
            self.highlight_class(4)  # Fifth class
            
    def get_upcoming_class_index(self, current_time: datetime) -> Optional[int]:
        """Get the index of the upcoming class if it's within 30 seconds"""
        current_time_str = current_time.strftime("%H:%M")
        
        for i, class_info in enumerate(self.today_schedule):
            start_time_str = class_info["start_time"]
            
            # Convert time strings to datetime objects for comparison
            try:
                current_dt = datetime.strptime(current_time_str, "%H:%M")
                start_dt = datetime.strptime(start_time_str, "%H:%M")
                
                # Calculate time difference
                time_diff = start_dt - current_dt
                
                # Check if class is upcoming within 30 seconds
                if timedelta(seconds=0) < time_diff <= timedelta(seconds=30):
                    return i
            except ValueError:
                # Handle time parsing errors
                continue
                
        return None
        
    def start_countdown(self, class_index: int, current_time: datetime) -> None:
        """Start the countdown for an upcoming class"""
        if class_index >= len(self.today_schedule):
            return
            
        # Get the upcoming class info
        upcoming_class = self.today_schedule[class_index]
        start_time_str = upcoming_class["start_time"]
        
        try:
            # Calculate end time for countdown
            start_dt = datetime.strptime(start_time_str, "%H:%M").replace(
                year=current_time.year, 
                month=current_time.month, 
                day=current_time.day
            )
            self.countdown_end_time = start_dt
            
            # Hide all other classes
            for i in range(self.schedule_layout.count()):
                item = self.schedule_layout.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget:
                        if i == class_index:
                            widget.show()
                            # Highlight the upcoming class
                            widget.setStyleSheet("""
                                QWidget {
                                    background-color: rgba(74, 144, 226, 150);
                                    border-radius: 4px;
                                    padding: 6px 12px;  /* Reduced vertical padding */
                                    min-height: 24px;   /* Reduced minimum height */
                                }
                            """)
                        else:
                            widget.hide()
            
            # Add countdown widget next to the class
            self.add_countdown_widget(class_index, upcoming_class)
            
            # Start the countdown timer
            if not self.countdown_active:
                self.countdown_timer.start(1000)  # Update every second
                self.countdown_active = True
                
        except ValueError:
            pass
            
    def add_countdown_widget(self, class_index: int, upcoming_class: ClassInfo) -> None:
        """Add countdown widget next to the upcoming class"""
        # Remove existing countdown widget if it exists
        if self.countdown_widget:
            self.countdown_widget.setParent(None)
            self.countdown_widget.deleteLater()
            self.countdown_widget = None
            self.countdown_label = None
            self.current_time_label = None
            
        # Create countdown widget
        self.countdown_widget = QWidget()
        self.countdown_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 50, 50, 150);
                border-radius: 4px;
                padding: 6px 12px;  /* Reduced vertical padding */
                min-height: 24px;   /* Reduced minimum height */
            }
        """)
        
        # Make widget more touch-friendly
        self.countdown_widget.setMinimumWidth(80)
        
        layout = QVBoxLayout(self.countdown_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(8, 4, 8, 4)  # Reduced vertical margins
        
        # Countdown label
        self.countdown_label = QLabel()
        countdown_font = QFont()
        countdown_font.setPointSize(10)
        countdown_font.setBold(True)
        self.countdown_label.setFont(countdown_font)
        self.countdown_label.setStyleSheet("color: white;")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.countdown_label)
        
        # Add time range label
        time_range_label = QLabel(f"{upcoming_class['start_time']}-{upcoming_class['end_time']}")
        time_range_font = QFont()
        time_range_font.setPointSize(7)
        time_range_label.setFont(time_range_font)
        time_range_label.setStyleSheet("color: #CCCCCC;")
        time_range_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(time_range_label)
        
        # Add current time label
        self.current_time_label = QLabel()
        current_time_font = QFont()
        current_time_font.setPointSize(7)
        self.current_time_label.setFont(current_time_font)
        self.current_time_label.setStyleSheet("color: #CCCCCC;")
        self.current_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.current_time_label)
        
        # Insert countdown widget after the class widget
        self.schedule_layout.insertWidget(class_index + 1, self.countdown_widget)
        
        # Update countdown display
        self.update_countdown_display()
        
    def update_countdown(self) -> None:
        """Update the countdown display"""
        if not self.countdown_active or not self.countdown_end_time:
            return
            
        # Update current time display
        if self.current_time_label:
            current_time_str = datetime.now().strftime("%H:%M:%S")
            self.current_time_label.setText(current_time_str)
            
        # Update countdown
        self.update_countdown_display()
        
    def update_countdown_display(self) -> None:
        """Update the countdown label display"""
        if not self.countdown_end_time:
            return
            
        current_time = datetime.now()
        time_diff = self.countdown_end_time - current_time
        
        if time_diff.total_seconds() <= 0:
            # Countdown finished, stop timer and reset display
            self.stop_countdown()
            return
            
        # Update countdown label
        seconds_left = int(time_diff.total_seconds())
        if self.countdown_label:
            self.countdown_label.setText(f"{seconds_left}s")
            
    def stop_countdown(self) -> None:
        """Stop the countdown and restore normal display"""
        # Stop the countdown timer
        if self.countdown_active:
            self.countdown_timer.stop()
            self.countdown_active = False
            
        # Remove countdown widget if it exists
        if self.countdown_widget:
            self.countdown_widget.setParent(None)
            self.countdown_widget.deleteLater()
            self.countdown_widget = None
            self.countdown_label = None
            self.current_time_label = None
            
        # Show all classes again
        for i in range(self.schedule_layout.count()):
            item = self.schedule_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.show()
                
        # Reset styles
        self.update_current_class()
        
    def highlight_class(self, index: int) -> None:
        """Highlight a specific class"""
        if index < self.schedule_layout.count():
            item = self.schedule_layout.itemAt(index)
            if item:
                widget = item.widget()
                if widget:
                    widget.setStyleSheet("""
                        QWidget {
                            background-color: rgba(74, 144, 226, 150);
                            border-radius: 4px;
                            padding: 6px 12px;  /* Reduced vertical padding */
                            min-height: 24px;   /* Reduced minimum height */
                        }
                    """)
                
    def center_on_screen(self, screen_geometry: QRect) -> None:
        """Center the widget on the given screen"""
        # Get the current width of the widget
        widget_width = self.width()
        screen_width = screen_geometry.width()
        
        # Calculate the x position to center the widget
        x = (screen_width - widget_width) // 2
        
        # Set position at the top of the screen
        self.move(x + screen_geometry.left(), screen_geometry.top() + 10)
        
    def resizeEvent(self, a0: Optional['QResizeEvent']) -> None:
        """Handle resize events to maintain centering"""
        super().resizeEvent(a0)
        # Re-center when resized
        if not self.screen_geometry.isNull():
            self.center_on_screen(self.screen_geometry)
        self.width_changed.emit()
        
    def showEvent(self, a0: Optional['QShowEvent']) -> None:
        """Handle show events to ensure proper centering"""
        super().showEvent(a0)
        # Center on screen when shown
        if not self.screen_geometry.isNull():
            self.center_on_screen(self.screen_geometry)