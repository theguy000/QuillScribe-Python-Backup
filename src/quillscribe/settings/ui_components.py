"""
Shared UI Components for QuillScribe
Common UI elements used across the application
"""

from PySide6.QtWidgets import QPushButton, QGroupBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


from ..managers import get_theme_manager


class ModernButton(QPushButton):
    """Beautiful modern button with hover effects"""
    
    def __init__(self, text: str, primary: bool = False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_default_theme()
    
    def apply_default_theme(self):
        """Apply default button theme"""
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #0056b3;
                }
                QPushButton:pressed {
                    background: #004085;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: #f8f9fa;
                    color: #495057;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #e9ecef;
                    border-color: #adb5bd;
                }
                QPushButton:pressed {
                    background: #dee2e6;
                }
            """)

    def apply_theme(self, primary_color="#ffffff", secondary_color="#f8f9fa"):
        """Apply theme colors to the button"""
        # Determine if this is a dark theme
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_color(primary_color)
        
        if self.primary:
            if is_dark:
                self.setStyleSheet("""
                    QPushButton {
                        background: #0d6efd;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 13px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background: #0b5ed7;
                    }
                    QPushButton:pressed {
                        background: #0a58ca;
                    }
                """)
            else:
                self.setStyleSheet("""
                    QPushButton {
                        background: #007bff;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 13px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background: #0056b3;
                    }
                    QPushButton:pressed {
                        background: #004085;
                    }
                """)
        else:
            if is_dark:
                self.setStyleSheet(f"""
                    QPushButton {{
                        background: {secondary_color};
                        color: #e9ecef;
                        border: 1px solid #495057;
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 13px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background: #495057;
                        border-color: #6c757d;
                    }}
                    QPushButton:pressed {{
                        background: #343a40;
                    }}
                """)
            else:
                self.setStyleSheet(f"""
                    QPushButton {{
                        background: {secondary_color};
                        color: #495057;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 13px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background: #e9ecef;
                        border-color: #adb5bd;
                    }}
                    QPushButton:pressed {{
                        background: #dee2e6;
                    }}
                """)


class ModernGroupBox(QGroupBox):
    """Beautiful modern group box with theme support"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.apply_default_theme()

    def apply_theme(self, primary_color="#ffffff", secondary_color="#f8f9fa"):
        """Apply theme colors to the group box"""
        # Determine if this is a dark theme
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_color(primary_color)
        
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
        self.apply_theme()
