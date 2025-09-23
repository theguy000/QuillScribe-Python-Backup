"""
System Tray Manager for QuillScribe
Handles system tray icon, menu, and state management
"""

import sys
import os
from pathlib import Path
from typing import Optional, Callable
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon


class TrayManager(QObject):
    """Manages system tray functionality for QuillScribe"""
    
    # Signals
    show_window_requested = Signal()
    start_recording_requested = Signal()
    stop_recording_requested = Signal()
    settings_requested = Signal()
    exit_requested = Signal()
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.tray_menu: Optional[QMenu] = None
        self.is_recording = False
        self._tray_message_shown = False
        
        # Icon paths
        self.normal_icon_path = self._get_icon_path("app_logo_tray.ico")
        self.recording_icon_path = self._get_icon_path("app_logo_tray_recording.ico")
        
        self.setup_tray()
    
    def _get_icon_path(self, filename: str) -> Path:
        """Get the path to an icon file"""
        if getattr(sys, 'frozen', False):
            # Running as frozen executable
            base_path = Path(sys._MEIPASS)
        else:
            # Running from source
            base_path = Path(__file__).parent
        
        return base_path / filename
    

    def setup_tray(self):
        """Setup system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("Warning: System tray is not available on this system")
            return
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set initial icon
        self._update_tray_icon()
        
        # Create context menu
        self._create_tray_menu()
        
        # Connect signals
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        # Set tooltip
        self._update_tooltip()
    
    def _create_tray_menu(self):
        """Create the system tray context menu"""
        if not self.tray_icon:
            return

        self.tray_menu = QMenu()

        # Apply theme to tray menu
        self._apply_tray_menu_theme()

        # Show/Hide QuillScribe
        show_action = self.tray_menu.addAction("Show QuillScribe")
        show_action.triggered.connect(self.show_window_requested.emit)

        self.tray_menu.addSeparator()

        # Recording actions
        self.start_action = self.tray_menu.addAction("Start Recording")
        self.start_action.triggered.connect(self.start_recording_requested.emit)

        self.stop_action = self.tray_menu.addAction("Stop Recording")
        self.stop_action.triggered.connect(self.stop_recording_requested.emit)
        self.stop_action.setVisible(False)  # Initially hidden

        self.tray_menu.addSeparator()

        # Settings
        settings_action = self.tray_menu.addAction("Settings")
        settings_action.triggered.connect(self.settings_requested.emit)

        self.tray_menu.addSeparator()

        # Exit
        exit_action = self.tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_requested.emit)

        # Set the menu
        self.tray_icon.setContextMenu(self.tray_menu)

    def _apply_tray_menu_theme(self):
        """Apply current theme to tray menu"""
        if not hasattr(self, 'config_manager') or not self.config_manager:
            return

        current_theme = self.config_manager.get_setting("ui/theme", "white")

        # Theme color definitions (same as main application)
        THEMES = {
            "white": {"primary": "#ffffff", "secondary": "#f8f9fa"},
            "warm_gray": {"primary": "#f5f5f5", "secondary": "#fafafa"},
            "soft_beige": {"primary": "#f8f6f0", "secondary": "#fefefe"},
            "blue_gray": {"primary": "#f0f2f5", "secondary": "#f8fafc"},
            "warm_taupe": {"primary": "#f7f3f0", "secondary": "#faf9f7"},
            "soft_sage": {"primary": "#f7f9f6", "secondary": "#f8faf9"},
            # Dark theme variations
            "dark_charcoal": {"primary": "#2c2c2c", "secondary": "#1e1e1e"},
            "dark_blue": {"primary": "#1a1f2e", "secondary": "#13182a"},
            "dark_purple": {"primary": "#2d1b3d", "secondary": "#241736"},
            "dark_forest": {"primary": "#1e2a1e", "secondary": "#152015"},
            "dark_burgundy": {"primary": "#2a1a1a", "secondary": "#1f1212"}
        }

        theme = THEMES.get(current_theme, THEMES["white"])
        primary_color = theme["primary"]

        # Determine if this is a dark theme
        r = int(primary_color.lstrip('#')[0:2], 16)
        g = int(primary_color.lstrip('#')[2:4], 16)
        b = int(primary_color.lstrip('#')[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        is_dark = brightness < 128

        if is_dark:
            # Dark theme styling
            menu_style = f"""
                QMenu {{
                    background-color: {primary_color};
                    color: #e9ecef;
                    border: 1px solid #495057;
                    border-radius: 4px;
                    padding: 4px;
                }}
                QMenu::item {{
                    background-color: transparent;
                    padding: 6px 20px;
                    border-radius: 2px;
                }}
                QMenu::item:selected {{
                    background-color: #495057;
                    color: #ffffff;
                }}
                QMenu::separator {{
                    height: 1px;
                    background-color: #495057;
                    margin: 4px 8px;
                }}
            """
        else:
            # Light theme styling
            menu_style = f"""
                QMenu {{
                    background-color: {primary_color};
                    color: #212529;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 4px;
                }}
                QMenu::item {{
                    background-color: transparent;
                    padding: 6px 20px;
                    border-radius: 2px;
                }}
                QMenu::item:selected {{
                    background-color: #e9ecef;
                    color: #212529;
                }}
                QMenu::separator {{
                    height: 1px;
                    background-color: #dee2e6;
                    margin: 4px 8px;
                }}
            """

        self.tray_menu.setStyleSheet(menu_style)

    def update_theme(self):
        """Update tray menu theme when theme changes"""
        if self.tray_menu:
            self._apply_tray_menu_theme()
    
    def _update_tray_icon(self):
        """Update the tray icon based on recording state"""
        if not self.tray_icon:
            return
        
        try:
            if self.is_recording and self.recording_icon_path.exists():
                icon = QIcon(str(self.recording_icon_path))
            else:
                icon = QIcon(str(self.normal_icon_path))
            
            self.tray_icon.setIcon(icon)
        except Exception as e:
            print(f"Error updating tray icon: {e}")
    
    def _update_tooltip(self):
        """Update the tray icon tooltip"""
        if not self.tray_icon:
            return
        
        if self.is_recording:
            tooltip = "QuillScribe - Recording..."
        else:
            tooltip = "QuillScribe - Voice Transcription"
        
        self.tray_icon.setToolTip(tooltip)
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - show window
            self.show_window_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - show window
            self.show_window_requested.emit()
    
    def show_tray(self):
        """Show the tray icon"""
        if self.tray_icon and QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()
            
            # Show notification on first show
            if not self._tray_message_shown:
                self.tray_icon.showMessage(
                    "QuillScribe",
                    "Application minimized to system tray. Right-click the tray icon for options.",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
                self._tray_message_shown = True
    
    def hide_tray(self):
        """Hide the tray icon"""
        if self.tray_icon:
            self.tray_icon.hide()
    
    def set_recording_state(self, is_recording: bool):
        """Update the recording state and tray appearance"""
        if self.is_recording == is_recording:
            return
        
        self.is_recording = is_recording
        self._update_tray_icon()
        self._update_tooltip()
        
        # Update menu actions
        if self.start_action and self.stop_action:
            self.start_action.setVisible(not is_recording)
            self.stop_action.setVisible(is_recording)
    
    def is_available(self) -> bool:
        """Check if system tray is available"""
        return QSystemTrayIcon.isSystemTrayAvailable()
    
    def cleanup(self):
        """Clean up tray resources"""
        if self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon = None
        
        if self.tray_menu:
            self.tray_menu = None
