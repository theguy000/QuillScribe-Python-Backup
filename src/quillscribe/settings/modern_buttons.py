"""
Modern Button Module
Reusable, theme-aware button components for QuillScribe
"""

from enum import Enum
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QCursor

class ButtonVariant(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    DANGER = "danger"
    GHOST = "ghost"
    OUTLINE = "outline"

class ModernButton(QPushButton):
    """
    A modern, theme-aware button component.
    
    Usage:
        btn = ModernButton("Save", variant=ButtonVariant.PRIMARY)
        btn.apply_theme(colors)
    """
    
    def __init__(self, text: str = "", variant: ButtonVariant = ButtonVariant.SECONDARY, parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(36) # Standard height
        
        # Default styling before theme is applied
        self.setStyleSheet(self._get_default_stylesheet())

    def set_variant(self, variant: ButtonVariant):
        """Change the button variant dynamically"""
        self.variant = variant
        # Re-apply theme if we have colors stored, otherwise default
        if hasattr(self, '_last_colors') and hasattr(self, '_last_is_dark'):
            self.apply_theme(self._last_is_dark, self._last_colors)
        else:
            self.setStyleSheet(self._get_default_stylesheet())

    def apply_theme(self, is_dark: bool, colors: dict):
        """
        Apply theme colors to the button based on its variant.
        
        Args:
            is_dark: Boolean indicating if the theme is dark
            colors: Dictionary of theme colors provided by ThemeManager
        """
        self._last_colors = colors
        self._last_is_dark = is_dark
        
        # Extract base colors
        primary = colors.get("accent", "#4A90E2")
        primary_hover = colors.get("accent_hover", "#357ABD")
        secondary = colors.get("secondary", "#f8f9fa")
        text_primary = colors.get("text_primary", "#2c3e50")
        text_on_primary = "#ffffff"
        border = colors.get("border", "#dee2e6")
        
        # Determine colors based on variant
        bg_color = "transparent"
        text_color = text_primary
        border_val = "none"
        hover_bg = "transparent"
        pressed_bg = "transparent"
        
        if self.variant == ButtonVariant.PRIMARY:
            bg_color = primary
            text_color = text_on_primary
            hover_bg = primary_hover
            pressed_bg = self._adjust_color(primary, -20)
            
        elif self.variant == ButtonVariant.SECONDARY:
            bg_color = secondary
            text_color = text_primary
            border_val = f"1px solid {border}"
            hover_bg = self._adjust_color(secondary, -10) # Slightly darker
            pressed_bg = self._adjust_color(secondary, -20)
            
        elif self.variant == ButtonVariant.DANGER:
            bg_color = "#dc3545"
            text_color = "#ffffff"
            hover_bg = "#bb2d3b"
            pressed_bg = "#b02a37"
            
        elif self.variant == ButtonVariant.GHOST:
            bg_color = "transparent"
            text_color = text_primary
            hover_bg = colors.get("widget_hover", "#f1f3f4")
            pressed_bg = border
            
        elif self.variant == ButtonVariant.OUTLINE:
            bg_color = "transparent"
            text_color = primary
            border_val = f"1px solid {primary}"
            hover_bg = f"{primary}1A" # 10% opacity
            pressed_bg = f"{primary}33" # 20% opacity

        # Construct stylesheet
        stylesheet = f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: {border_val};
                border-radius: 8px;
                padding: 0 16px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 600;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
            QPushButton:pressed {{
                background-color: {pressed_bg};
            }}
            QPushButton:disabled {{
                background-color: {colors.get("secondary", "#f1f3f4")};
                color: {colors.get("text_muted", "#868e96")};
                border: 1px solid {colors.get("border", "#dee2e6")};
            }}
        """
        self.setStyleSheet(stylesheet)

    def _get_default_stylesheet(self):
        """Fallback stylesheet if no theme is applied"""
        return """
            QPushButton {
                background-color: #f8f9fa;
                color: #212529;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 0 16px;
            }
        """

    def _adjust_color(self, hex_color, amount):
        """
        Lighten or darken a hex color.
        amount: positive to lighten, negative to darken
        """
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 8: # Handle alpha if present (ignore it for calc)
            hex_color = hex_color[:6]
            
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        
        return f"#{r:02x}{g:02x}{b:02x}"
