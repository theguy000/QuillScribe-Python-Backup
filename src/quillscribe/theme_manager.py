"""
Unified Theme Manager for QuillScribe
Handles consistent theming across all components including icons
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import QWidget, QCheckBox, QRadioButton, QTabWidget, QLabel, QPushButton, QLineEdit
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor
from .icon_manager import get_themed_button_icon, get_themed_icon


class ThemeManager(QObject):
    """Centralized theme management for consistent theming across the application"""
    
    theme_changed = Signal(str, bool)  # theme_name, is_dark
    
    def __init__(self):
        super().__init__()
        self._current_theme = "white"
        self._is_dark = False
        
        # Theme color definitions
        self.THEMES = {
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
        
        # Icon mappings for different widget types
        self.WIDGET_ICON_MAPPINGS = {
            # Checkbox text patterns to icon names
            'checkbox_patterns': {
                'compact': 'compact',
                'title': 'window',
                'titlebar': 'window',
                'waveform': 'zap',
                'minimize': 'window',
                'auto': 'sound',
                'custom': 'window',
                'silent': 'silent',
                'clear': 'trash',
                'always': 'zap',
                'snap': 'dashboard',
                'tray': 'compact'
            },
            # Radio button text patterns to icon names
            'radio_patterns': {
                'api': 'api',
                'local': 'local',
                'openai': 'api',
                'whisper': 'brain',
                'copy': 'clipboard',
                'paste': 'clipboard',
                'display': 'eye'
            },
            # Tab names to icon names
            'tab_patterns': {
                'audio': 'audio',
                'whisper': 'brain',
                'ui': 'settings',
                'output': 'clipboard',
                'statistics': 'dashboard'
            },
            # Label object names to icon names
            'label_patterns': {
                'icon_api_key': 'key',
                'icon_api_model': 'brain',
                'icon_category': 'category',
                'icon_model': 'brain',
                'icon_theme': 'settings',
                'icon_shortcut': 'keyboard'
            },
            # Button object names to icon names
            'button_patterns': {
                'minimize_btn': 'minimize',
                'close_btn': 'close',
                'settings_btn': 'settings'
            },
            # Special button patterns that need custom handling
            'special_button_patterns': {
                'api_key_toggle_btn': 'eye-toggle'  # Special case for API key visibility toggle
            }
        }
    
    def set_theme(self, theme_name: str):
        """Set the current theme and determine if it's dark"""
        if theme_name not in self.THEMES:
            theme_name = "white"
            
        self._current_theme = theme_name
        theme = self.THEMES[theme_name]
        primary_color = theme["primary"]
        
        # Determine if this is a dark theme
        r = int(primary_color.lstrip('#')[0:2], 16)
        g = int(primary_color.lstrip('#')[2:4], 16)
        b = int(primary_color.lstrip('#')[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        self._is_dark = brightness < 128
        
        # Emit theme change signal
        self.theme_changed.emit(theme_name, self._is_dark)
    
    def get_current_theme(self) -> str:
        """Get the current theme name"""
        return self._current_theme
    
    def is_dark_theme(self) -> bool:
        """Check if current theme is dark"""
        return self._is_dark
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Get theme colors for the specified or current theme"""
        if theme_name is None:
            theme_name = self._current_theme
            
        if theme_name not in self.THEMES:
            theme_name = "white"
            
        return self.THEMES[theme_name]
    
    def apply_icons_to_widget(self, widget: QWidget, is_dark: Optional[bool] = None):
        """Apply themed icons to a widget and all its children"""
        if is_dark is None:
            is_dark = self._is_dark
            
        try:
            # Update checkboxes
            for checkbox in widget.findChildren(QCheckBox):
                self._update_checkbox_icon(checkbox, is_dark)
            
            # Update radio buttons  
            for radio in widget.findChildren(QRadioButton):
                self._update_radio_icon(radio, is_dark)
            
            # Update tab widgets
            for tab_widget in widget.findChildren(QTabWidget):
                self._update_tab_icons(tab_widget, is_dark)
            
            # Update labeled icons (QLabel with object names)
            for label in widget.findChildren(QLabel):
                self._update_label_icon(label, is_dark)
                
            # Update buttons with icons
            for button in widget.findChildren(QPushButton):
                self._update_button_icon(button, is_dark)
                
        except Exception as e:
            print(f"Warning: Error applying themed icons: {e}")
    
    def _update_checkbox_icon(self, checkbox: QCheckBox, is_dark: bool):
        """Update checkbox icon based on its text"""
        text = checkbox.text().lower()
        for pattern, icon_name in self.WIDGET_ICON_MAPPINGS['checkbox_patterns'].items():
            if pattern in text:
                checkbox.setIcon(get_themed_button_icon(icon_name, 16, is_dark))
                break
    
    def _update_radio_icon(self, radio: QRadioButton, is_dark: bool):
        """Update radio button icon based on its text"""
        text = radio.text().lower()
        for pattern, icon_name in self.WIDGET_ICON_MAPPINGS['radio_patterns'].items():
            if pattern in text:
                radio.setIcon(get_themed_button_icon(icon_name, 16, is_dark))
                break
    
    def _update_tab_icons(self, tab_widget: QTabWidget, is_dark: bool):
        """Update tab icons"""
        for i in range(tab_widget.count()):
            tab_text = tab_widget.tabText(i).lower()
            for pattern, icon_name in self.WIDGET_ICON_MAPPINGS['tab_patterns'].items():
                if pattern in tab_text:
                    tab_widget.setTabIcon(i, get_themed_icon(icon_name, 16, is_dark))
                    break
    
    def _update_label_icon(self, label: QLabel, is_dark: bool):
        """Update label icon based on object name"""
        object_name = label.objectName()
        if object_name in self.WIDGET_ICON_MAPPINGS['label_patterns']:
            icon_name = self.WIDGET_ICON_MAPPINGS['label_patterns'][object_name]
            pixmap = get_themed_icon(icon_name, 16, is_dark).pixmap(16, 16)
            label.setPixmap(pixmap)
    
    def _update_button_icon(self, button: QPushButton, is_dark: bool):
        """Update button icon based on object name or text"""
        object_name = button.objectName()
        text = button.text().lower()

        # Handle special buttons that need custom logic
        if object_name == 'api_key_toggle_btn':
            # For API key toggle, preserve the current state (eye vs eye-off)
            # but update the color for the theme
            current_icon_name = 'eye-off'  # Default to hidden state
            # Try to determine current state from parent widget
            try:
                parent = button.parent()
                if parent:
                    for child in parent.findChildren(QLineEdit):
                        if child.echoMode() == QLineEdit.EchoMode.Password:
                            current_icon_name = 'eye-off'
                        else:
                            current_icon_name = 'eye'
                        break
            except:
                pass
            button.setIcon(get_themed_button_icon(current_icon_name, 16, is_dark))
            return

        # Check object name patterns
        for pattern, icon_name in self.WIDGET_ICON_MAPPINGS['button_patterns'].items():
            if pattern == object_name:
                button.setIcon(get_themed_button_icon(icon_name, 16, is_dark))
                return

        # Fallback to text-based patterns for buttons that already have icons
        if not button.icon().isNull():
            # Common button patterns
            if 'settings' in text:
                button.setIcon(get_themed_button_icon('settings', 16, is_dark))
            elif 'close' in text:
                button.setIcon(get_themed_button_icon('close', 16, is_dark))
            elif 'minimize' in text:
                button.setIcon(get_themed_button_icon('minimize', 16, is_dark))


# Global theme manager instance
theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance"""
    return theme_manager
