#!/usr/bin/env python3
"""
Main application class for ClassisTime
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenuBar, QFileDialog, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime
from classistime.schedule import ScheduleWidget
from classistime.themes.theme_manager import ThemeManager
from classistime.extensions.extension_manager import ExtensionManager
from classistime.ui.current_schedule import CurrentScheduleWidget

class ClassisTimeApp(QApplication):
    """Main application class"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("ClassisTime")
        self.setApplicationVersion("0.1.0")
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Initialize extension manager
        self.extension_manager = ExtensionManager(self)
        
        # Create main window
        self.main_window = MainWindow(self)
        self.main_window.show()
        
        # Create current schedule widget (like ClassIsland)
        # This widget is now independent of the main window
        self.current_schedule_widget = CurrentScheduleWidget()
        self.current_schedule_widget.width_changed.connect(self.on_schedule_width_changed)
        self.current_schedule_widget.show()
        
        # Apply default theme
        self.theme_manager.apply_theme(self.main_window, "default")
        
        # Center the current schedule widget on the screen
        self.center_current_schedule_widget()
        
    def center_current_schedule_widget(self):
        """Center the current schedule widget on the primary screen"""
        screen = self.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            self.current_schedule_widget.screen_geometry = screen_geometry
            self.current_schedule_widget.center_on_screen(screen_geometry)
        
    def on_schedule_width_changed(self):
        """Handle width changes of the schedule widget"""
        # Re-center the widget when its width changes
        self.center_current_schedule_widget()

class MainWindow(QMainWindow):
    """Main window of the application"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("ClassisTime - 课程表")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)  # Renamed from 'layout' to avoid conflict
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create schedule tab
        self.schedule_widget = ScheduleWidget()
        self.tab_widget.addTab(self.schedule_widget, "课程表")
        
        # Create status bar with clock
        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage("就绪")
        self.clock_label = QLabel()
        if status_bar is not None:
            status_bar.addPermanentWidget(self.clock_label)
        
        # Add exit button to status bar
        self.exit_button = QPushButton("退出程序")
        self.exit_button.clicked.connect(self.exit_application)
        if status_bar is not None:
            status_bar.addPermanentWidget(self.exit_button)
        
        # Setup clock update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)  # Update every second
        self.update_clock()
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menu_bar = self.menuBar()
        
        if menu_bar is not None:
            # File menu
            file_menu = menu_bar.addMenu('文件')
            
            if file_menu is not None:
                exit_action = QAction('退出', self)
                exit_action.setShortcut('Ctrl+Q')
                exit_action.triggered.connect(self.close)
                file_menu.addAction(exit_action)
            
            # Extensions menu
            extensions_menu = menu_bar.addMenu('扩展')
            
            if extensions_menu is not None:
                install_ext_action = QAction('安装扩展', self)
                install_ext_action.triggered.connect(self.install_extension)
                extensions_menu.addAction(install_ext_action)
                
                manage_ext_action = QAction('管理扩展', self)
                manage_ext_action.triggered.connect(self.manage_extensions)
                extensions_menu.addAction(manage_ext_action)
            
            # View menu
            view_menu = menu_bar.addMenu('视图')
            
            if view_menu is not None:
                theme_action = QAction('主题设置', self)
                theme_action.triggered.connect(self.open_theme_settings)
                view_menu.addAction(theme_action)
                
                # Toggle current schedule visibility
                toggle_schedule_action = QAction('显示/隐藏顶部课表', self)
                toggle_schedule_action.setCheckable(True)
                toggle_schedule_action.setChecked(True)
                toggle_schedule_action.triggered.connect(self.toggle_current_schedule)
                view_menu.addAction(toggle_schedule_action)
            
            # Help menu
            help_menu = menu_bar.addMenu('帮助')
            
            if help_menu is not None:
                about_action = QAction('关于', self)
                about_action.triggered.connect(self.show_about)
                help_menu.addAction(about_action)
        
    def update_clock(self):
        """Update the clock in status bar"""
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S %A")
        self.clock_label.setText(current_time)
        
    def install_extension(self):
        """Open dialog to install extension from zip file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择扩展文件", 
            "", 
            "扩展文件 (*.zip)"
        )
        
        if file_path:
            success = self.app.extension_manager.install_extension(file_path)
            if success:
                QMessageBox.information(self, "安装成功", "扩展安装成功！")
            else:
                QMessageBox.critical(self, "安装失败", "扩展安装失败！")
                
    def manage_extensions(self):
        """Open extension management dialog"""
        # TODO: Implement extension management dialog
        QMessageBox.information(self, "扩展管理", "扩展管理功能正在开发中...")
        
    def open_theme_settings(self):
        """Open theme settings dialog"""
        # TODO: Implement theme settings dialog
        pass
        
    def toggle_current_schedule(self, checked):
        """Toggle visibility of current schedule widget"""
        if checked:
            self.app.current_schedule_widget.show()
        else:
            self.app.current_schedule_widget.hide()
            
    def exit_application(self):
        """Exit the application"""
        self.app.quit()
        
    def show_about(self):
        """Show about dialog"""
        # TODO: Implement about dialog
        pass