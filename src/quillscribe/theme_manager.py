"""
Unified Theme Manager for QuillScribe
Handles consistent theming across all components including icons
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import QWidget, QCheckBox, QRadioButton, QTabWidget, QLabel, QPushButton, QLineEdit, QScrollArea
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

    def apply_text_theming_to_widget(self, widget: QWidget, theme_name: Optional[str] = None):
        """Apply text color theming to all labels in a widget"""
        if theme_name is None:
            theme_name = self._current_theme

        is_dark = self._is_dark_color(self.get_theme_colors(theme_name)["primary"])

        # Determine text colors based on theme
        if is_dark:
            primary_text_color = "#ffffff"
            secondary_text_color = "#e9ecef"
            muted_text_color = "#adb5bd"
        else:
            primary_text_color = "#212529"
            secondary_text_color = "#495057"
            muted_text_color = "#6c757d"

        try:
            # Apply text theming to all labels
            for label in widget.findChildren(QLabel):
                self._apply_label_text_theming(label, primary_text_color, muted_text_color)
        except Exception as e:
            print(f"Warning: Error applying text theming: {e}")

    def _apply_label_text_theming(self, label: QLabel, primary_text_color: str, muted_text_color: str):
        """Apply text color theming to a single label"""
        current_style = label.styleSheet()

        # Skip labels that already have icons (they're handled by apply_icons_to_widget)
        if label.pixmap() and not label.pixmap().isNull():
            return

        # Determine if this is help text or regular text
        if '#6c757d' in current_style or 'color: #6c757d' in current_style:
            # This is help/muted text
            new_color = muted_text_color
        else:
            # This is regular text
            new_color = primary_text_color

        # Apply the new color
        if current_style:
            # Remove any existing color declarations and add new one
            import re
            new_style = re.sub(r'color:\s*[^;]+;?', '', current_style)
            new_style = re.sub(r';;+', ';', new_style).strip(';')
            if new_style:
                new_style = f"{new_style}; color: {new_color};"
            else:
                new_style = f"color: {new_color};"
            label.setStyleSheet(new_style)
        else:
            label.setStyleSheet(f"color: {new_color};")

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
            elif 'cancel' in text:
                button.setIcon(get_themed_button_icon('cancel', 16, is_dark))
            elif 'save' in text:
                button.setIcon(get_themed_button_icon('save', 16, is_dark))

    def get_scrollbar_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Get scrollbar colors for the specified or current theme"""
        if theme_name is None:
            theme_name = self._current_theme

        colors = self.get_theme_colors(theme_name)
        is_dark = self._is_dark_color(colors["primary"])

        if is_dark:
            # Dark theme scrollbar colors - subtle and modern
            return {
                "track_bg": "transparent",  # Invisible track background
                "handle": "#555555",  # Subtle gray handle
                "handle_hover": "#666666",  # Slightly lighter on hover
                "handle_pressed": "#444444",  # Darker when pressed
                "handle_inactive": "#3a3a3a"  # Even more subtle when inactive
            }
        else:
            # Light theme scrollbar colors - clean and modern
            return {
                "track_bg": "transparent",  # Invisible track background
                "handle": "#d0d0d0",  # Light gray handle
                "handle_hover": "#b0b0b0",  # Darker on hover
                "handle_pressed": "#a0a0a0",  # Even darker when pressed
                "handle_inactive": "#e0e0e0"  # Lighter when inactive
            }

    def get_scrollbar_sizing(self, responsive: bool = True, compact_mode: bool = False) -> Dict[str, str]:
        """
        Get appropriate scrollbar sizing based on responsive and compact mode settings.

        Args:
            responsive: Whether to use responsive sizing
            compact_mode: Whether the application is in compact mode

        Returns:
            Dictionary with sizing parameters
        """
        if compact_mode:
            # Ultra-thin scrollbars for compact mode
            return {
                "vertical_width": "4px",
                "horizontal_height": "4px",
                "handle_border_radius": "2px",
                "track_border_radius": "2px",
                "min_handle_size": "16px",
                "margin": "1px"
            }
        elif responsive:
            # Modern thin scrollbars for responsive design
            return {
                "vertical_width": "6px",
                "horizontal_height": "6px",
                "handle_border_radius": "3px",
                "track_border_radius": "3px",
                "min_handle_size": "20px",
                "margin": "2px"
            }
        else:
            # Standard desktop sizing
            return {
                "vertical_width": "10px",
                "horizontal_height": "10px",
                "handle_border_radius": "5px",
                "track_border_radius": "5px",
                "min_handle_size": "30px",
                "margin": "2px"
            }

    def get_modern_scrollbar_stylesheet(self, theme_name: Optional[str] = None,
                                      responsive: bool = True,
                                      compact_mode: bool = False) -> str:
        """
        Generate modern scrollbar stylesheet with rounded corners and smooth transitions.

        Args:
            theme_name: Theme to use (defaults to current theme)
            responsive: Whether to include responsive sizing for different viewports
            compact_mode: Whether to use ultra-compact sizing for compact UI mode

        Returns:
            Complete CSS stylesheet for modern scrollbars
        """
        if theme_name is None:
            theme_name = self._current_theme

        scrollbar_colors = self.get_scrollbar_colors(theme_name)
        sizing = self.get_scrollbar_sizing(responsive, compact_mode)

        return f"""
            /* Modern Scrollbar Styling - Consistent across all scroll areas */
            /* Note: Background colors are handled by parent components for dynamic theming */

            /* Vertical Scrollbar */
            QScrollBar:vertical {{
                background: {scrollbar_colors["track_bg"]};
                width: {sizing["vertical_width"]};
                border: none;
                border-radius: {sizing["track_border_radius"]};
                margin: {sizing["margin"]};
            }}

            QScrollBar::handle:vertical {{
                background: {scrollbar_colors["handle"]};
                min-height: {sizing["min_handle_size"]};
                border-radius: {sizing["handle_border_radius"]};
                margin: 0px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {scrollbar_colors["handle_hover"]};
            }}

            QScrollBar::handle:vertical:pressed {{
                background: {scrollbar_colors["handle_pressed"]};
            }}

            QScrollBar::handle:vertical:inactive {{
                background: {scrollbar_colors["handle_inactive"]};
            }}

            /* Hide scrollbar arrows and page areas for clean modern look */
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
                width: 0px;
            }}

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            /* Horizontal Scrollbar */
            QScrollBar:horizontal {{
                background: {scrollbar_colors["track_bg"]};
                height: {sizing["horizontal_height"]};
                border: none;
                border-radius: {sizing["track_border_radius"]};
                margin: {sizing["margin"]};
            }}

            QScrollBar::handle:horizontal {{
                background: {scrollbar_colors["handle"]};
                min-width: {sizing["min_handle_size"]};
                border-radius: {sizing["handle_border_radius"]};
                margin: 0px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background: {scrollbar_colors["handle_hover"]};
            }}

            QScrollBar::handle:horizontal:pressed {{
                background: {scrollbar_colors["handle_pressed"]};
            }}

            QScrollBar::handle:horizontal:inactive {{
                background: {scrollbar_colors["handle_inactive"]};
            }}

            /* Hide horizontal scrollbar arrows and page areas */
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
                height: 0px;
                width: 0px;
            }}

            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """

    def apply_modern_scrollbar_to_widget(self, widget: QScrollArea,
                                       theme_name: Optional[str] = None,
                                       responsive: bool = True,
                                       compact_mode: bool = False):
        """
        Apply modern scrollbar styling to a specific QScrollArea widget.

        Args:
            widget: QScrollArea widget to style
            theme_name: Theme to use (defaults to current theme)
            responsive: Whether to use responsive sizing
            compact_mode: Whether to use ultra-compact sizing for compact UI mode
        """
        if not isinstance(widget, QScrollArea):
            print(f"Warning: Expected QScrollArea, got {type(widget)}")
            return

        stylesheet = self.get_modern_scrollbar_stylesheet(theme_name, responsive, compact_mode)
        widget.setStyleSheet(stylesheet)

    def apply_scrollbars_to_all_widgets(self, parent_widget: QWidget,
                                      theme_name: Optional[str] = None,
                                      responsive: bool = True,
                                      compact_mode: bool = False):
        """
        Apply modern scrollbar styling to all QScrollArea widgets within a parent widget.

        Args:
            parent_widget: Parent widget to search for QScrollArea children
            theme_name: Theme to use (defaults to current theme)
            responsive: Whether to use responsive sizing
            compact_mode: Whether to use ultra-compact sizing
        """
        for scroll_area in parent_widget.findChildren(QScrollArea):
            self.apply_modern_scrollbar_to_widget(
                scroll_area,
                theme_name=theme_name,
                responsive=responsive,
                compact_mode=compact_mode
            )

    def _is_dark_color(self, color_hex: str) -> bool:
        """Determine if a color is dark based on its brightness"""
        try:
            # Remove # if present
            color_hex = color_hex.lstrip('#')

            # Convert to RGB
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)

            # Calculate brightness using standard formula
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            return brightness < 128
        except (ValueError, IndexError):
            # Default to light theme if color parsing fails
            return False


# Global theme manager instance
theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance"""
    return theme_manager
