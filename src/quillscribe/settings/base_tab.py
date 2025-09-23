"""
Base Settings Tab for QuillScribe
Provides common functionality for all settings tabs
"""

from PySide6.QtWidgets import QWidget, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt

from ..config_manager import ConfigManager


class BaseSettingsTab(QWidget):
    """Base class for all settings tabs"""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the tab UI - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement setup_ui()")
    
    def load_settings(self):
        """Load settings from config manager - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement load_settings()")
    
    def save_settings(self):
        """Save settings to config manager - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement save_settings()")
    
    def apply_theme(self, primary_color="#ffffff", secondary_color="#f8f9fa"):
        """Apply theme colors to the tab"""
        # Base implementation - can be overridden by subclasses
        pass


def create_scroll_area(widget):
    """Create a scroll area for a settings tab widget"""
    scroll = QScrollArea()
    scroll.setWidget(widget)
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    # Styling for scroll area
    scroll.setStyleSheet("""
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        QScrollArea > QWidget > QWidget {
            background-color: transparent;
        }
        QScrollArea QWidget {
            background-color: transparent;
        }
        QScrollBar:vertical {
            background: #f1f1f1;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #c1c1c1;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #a8a8a8;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        QScrollBar:horizontal {
            background: #f1f1f1;
            height: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background: #c1c1c1;
            border-radius: 6px;
            min-width: 20px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #a8a8a8;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
        }
    """)
    
    return scroll
