"""
Shared UI Components for QuillScribe
Common UI elements used across the application
"""

from PySide6.QtWidgets import QPushButton, QGroupBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


from ..managers import get_theme_manager





class ModernGroupBox(QGroupBox):
    """Beautiful modern group box with theme support"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.apply_default_theme()

    def apply_theme(self, is_dark: bool, colors: dict):
        """Apply theme colors to the group box"""
        if is_dark:
            self.setStyleSheet(f"""
                QGroupBox {{
                    font-family: 'Segoe UI', sans-serif;
                    font-weight: 600;
                    font-size: 16px;
                    color: #e9ecef;
                    border: none;
                    border-radius: 0px;
                    margin-top: 24px;
                    padding-top: 0px;
                    background: transparent;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 0px;
                    padding: 0 0 12px 0;
                    color: #e9ecef;
                    background: transparent;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QGroupBox {{
                    font-family: 'Segoe UI', sans-serif;
                    font-weight: 600;
                    font-size: 16px;
                    color: #212529;
                    border: none;
                    border-radius: 0px;
                    margin-top: 24px;
                    padding-top: 0px;
                    background: transparent;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 0px;
                    padding: 0 0 12px 0;
                    color: #212529;
                    background: transparent;
                }}
            """)

    def apply_default_theme(self):
        """Apply default group box theme"""
        # Default to light theme
        self.apply_theme(False, {})


def apply_theme_recursively(widget, is_dark: bool, colors: dict):
    """
    Recursively apply theme to a widget and its children.
    Only calls apply_theme on widgets that have the method.
    """
    from PySide6.QtWidgets import QWidget
    
    # Apply to self if possible
    if hasattr(widget, 'apply_theme'):
        try:
            widget.apply_theme(is_dark, colors)
        except Exception as e:
            # print(f"Error applying theme to {widget}: {e}")
            pass
            
    # Apply to children
    for child in widget.findChildren(QWidget):
        if hasattr(child, 'apply_theme'):
            try:
                child.apply_theme(is_dark, colors)
            except Exception as e:
                # print(f"Error applying theme to child {child}: {e}")
                pass
