"""
Base Settings Tab for QuillScribe
Provides common functionality for all settings tabs
"""

from PySide6.QtWidgets import QWidget, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt

from ..config_manager import ConfigManager
from ..managers import get_theme_manager


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
    """Create a scroll area for a settings tab widget with modern themed scrollbars"""
    scroll = QScrollArea()
    scroll.setWidget(widget)
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    # Apply modern scrollbar styling using centralized theme manager
    theme_manager = get_theme_manager()
    theme_manager.apply_modern_scrollbar_to_widget(
        scroll,
        theme_name=None,  # Use current theme
        responsive=True   # Enable responsive sizing
    )

    # Apply background colors for dynamic theming
    apply_scroll_area_background(scroll)

    return scroll


def apply_scroll_area_background(scroll_area, theme_name=None):
    """Apply background colors to a scroll area for dynamic theming"""
    theme_manager = get_theme_manager()

    if theme_name is None:
        theme_name = theme_manager.get_current_theme()

    colors = theme_manager.get_theme_colors(theme_name)

    # Apply background colors that work with dynamic theming
    background_style = f"""
        QScrollArea {{
            border: none;
            background-color: {colors["primary"]};
        }}
        QScrollArea > QWidget#qt_scrollarea_viewport {{
            background-color: {colors["primary"]};
        }}
        QWidget#qt_scrollarea_viewport {{
            background-color: {colors["primary"]};
        }}
    """

    # Combine with existing scrollbar styles
    existing_style = scroll_area.styleSheet()
    scroll_area.setStyleSheet(existing_style + background_style)
