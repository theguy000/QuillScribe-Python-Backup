"""
Modern UI Widgets for Settings Dialog
Reusable styled components with theme support
"""

from PySide6.QtWidgets import (
    QComboBox, QLineEdit, QRadioButton, QCheckBox,
    QKeySequenceEdit, QListView, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QKeySequence

from .ui_components import ModernGroupBox as BaseModernGroupBox


class ModernGroupBox(BaseModernGroupBox):
    """Beautiful modern group box with theme support"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.apply_default_theme()

    def apply_theme(self, primary_color="#ffffff", secondary_color="#f8f9fa"):
        """Apply theme colors to the group box"""
        # Determine if this is a dark theme
        r = int(primary_color.lstrip('#')[0:2], 16)
        g = int(primary_color.lstrip('#')[2:4], 16)
        b = int(primary_color.lstrip('#')[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        is_dark = luminance < 0.5

        if is_dark:
            text_color = "#ffffff"
            border_color = "#555555"
        else:
            text_color = "#2c3e50"
            border_color = "#dee2e6"

        self.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 600;
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: {primary_color};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: {primary_color};
                color: {text_color};
            }}
        """)

    def apply_default_theme(self):
        """Apply default white theme"""
        self.apply_theme("#ffffff", "#f8f9fa")


class ModernComboBox(QComboBox):
    """Beautiful modern combo box"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Use a list view for better styling control and add subtle shadow
        self.setView(QListView(self))
        self.view().setAlternatingRowColors(True)
        try:
            shadow = QGraphicsDropShadowEffect(self.view())
            shadow.setBlurRadius(18)
            shadow.setOffset(0, 4)
            shadow.setColor(QColor(0, 0, 0, 60))
            self.view().setGraphicsEffect(shadow)
        except Exception:
            pass
        self.setIconSize(QSize(14, 14))
        self.apply_theme(is_dark=False)

    def apply_theme(self, is_dark: bool, accent: str = "#4A90E2", border: str | None = None):
        border = border or ("#555555" if is_dark else "#dee2e6")
        text_color = "#ffffff" if is_dark else "#212529"
        bg = "#2c2c2c" if is_dark else "white"
        hover_bg = "#333333" if is_dark else "#f8f9fa"
        alt_bg = "#252525" if is_dark else "#f7f7f7"
        # Fix selection text color - use white for dark accent backgrounds, dark for light backgrounds
        selection_text_color = "white"  # Accent color is always dark enough to need white text

        stylesheet = f"""
            QComboBox {{
                border: 1.5px solid {border};
                border-radius: 8px;
                padding: 4px 20px 4px 8px;
                min-height: 26px;
                font-size: 13px;
                background-color: {bg};
                color: {text_color};
                outline: none;
            }}
            QComboBox:hover {{
                border-color: {'#777777' if is_dark else '#adb5bd'};
                background-color: {hover_bg};
            }}
            QComboBox:focus {{
                outline: none;
                border: 1.5px solid {accent};
            }}
            QComboBox::drop-down {{
                border: none;
                background: transparent;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {text_color};
                width: 0px;
                height: 0px;
                margin: 6px;
            }}
            QComboBox QAbstractItemView {{
                border: 1.5px solid {border};
                border-radius: 8px;
                background-color: {bg};
                color: {text_color};
                selection-background-color: {accent};
                selection-color: {selection_text_color};
                alternate-background-color: {alt_bg};
            }}
            QComboBox QAbstractItemView::item {{
                height: 24px;
                padding: 4px 8px;
                color: {text_color};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {accent};
                color: {selection_text_color};
                outline: none;
                border: none;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {accent};
                color: {selection_text_color};
                outline: none !important;
                border: none !important;
            }}
            QListView {{
                outline: none;
                border: none;
            }}
            QListView::item {{
                outline: none !important;
                border: none !important;
            }}
            QListView::item:focus {{
                outline: none !important;
                border: none !important;
            }}
            QListView::item:selected {{
                outline: none !important;
                border: none !important;
            }}
            QScrollBar:vertical {{
                width: 0px;
            }}
            QComboBox:disabled {{
                color: {'#6c757d' if is_dark else '#868e96'};
                background-color: {'#1a1a1a' if is_dark else '#f1f3f4'};
                border-style: dashed;
                border-color: {'#404040' if is_dark else '#ced4da'};
            }}
        """
        self.setStyleSheet(stylesheet)
        try:
            # Elide long texts on the right to avoid overflow
            if hasattr(self.view(), "setTextElideMode"):
                self.view().setTextElideMode(Qt.TextElideMode.ElideRight)
        except Exception:
            pass


class ModernLineEdit(QLineEdit):
    """Beautiful modern line edit"""

    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.apply_theme(is_dark=False)

    def apply_theme(self, is_dark: bool):
        if is_dark:
            stylesheet = """
                QLineEdit {
                    border: 2px solid #555555;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 13px;
                    background-color: #2c2c2c;
                    color: #ffffff;
                    min-height: 20px;
                    outline: none;
                }
                QLineEdit:hover {
                    border-color: #777777;
                }
                QLineEdit:focus {
                    border-color: #4A90E2;
                }
                QLineEdit:disabled {
                    color: #6c757d;
                    background-color: #1a1a1a;
                    border-style: dashed;
                    border-color: #404040;
                }
            """
        else:
            stylesheet = """
                QLineEdit {
                    border: 2px solid #dee2e6;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 13px;
                    background-color: white;
                    color: #212529;
                    min-height: 20px;
                    outline: none;
                }
                QLineEdit:hover {
                    border-color: #adb5bd;
                }
                QLineEdit:focus {
                    border-color: #4A90E2;
                }
                QLineEdit:disabled {
                    color: #868e96;
                    background-color: #f1f3f4;
                    border-style: dashed;
                    border-color: #ced4da;
                }
            """
        self.setStyleSheet(stylesheet)


class ModernKeySequenceEdit(QKeySequenceEdit):
    """Beautiful modern key sequence edit for shortcuts"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.apply_theme(is_dark=False)

        # Set maximum sequence length (usually 1 shortcut is enough)
        self.setMaximumSequenceLength(1)

        # Connect to sequence changed signal for debugging
        self.keySequenceChanged.connect(self._on_sequence_changed)

        # Set placeholder text to help users
        self.clear()

    def apply_theme(self, is_dark: bool):
        if is_dark:
            self.setStyleSheet("""
                QKeySequenceEdit {
                    border: 2px solid #555555;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 13px;
                    background-color: #2c2c2c;
                    color: #f0f0f0;
                    min-height: 20px;
                    outline: none;
                }
                QKeySequenceEdit:hover {
                    border-color: #777777;
                }
                QKeySequenceEdit:focus {
                    border-color: #4A90E2;
                    border-width: 3px;
                }
            """)
        else:
            self.setStyleSheet("""
                QKeySequenceEdit {
                    border: 2px solid #dee2e6;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 13px;
                    background-color: white;
                    color: black;
                    min-height: 20px;
                    outline: none;
                }
                QKeySequenceEdit:hover {
                    border-color: #adb5bd;
                }
                QKeySequenceEdit:focus {
                    border-color: #4A90E2;
                    border-width: 3px;
                }
            """)

    def _on_sequence_changed(self, sequence):
        """Debug callback for when key sequence changes"""
        pass  # Remove debug output

    def focusInEvent(self, event):
        """Override focus in event to show helper text"""
        super().focusInEvent(event)
        # Show visual indication that it's recording
        current_stylesheet = self.styleSheet()
        if "background-color: #2c2c2c" in current_stylesheet: # Dark mode
            self.setStyleSheet(current_stylesheet.replace(
                "border-color: #4A90E2;",
                "border-color: #28a745; background-color: #1a3c22;"
            ))
        else: # Light mode
            self.setStyleSheet(current_stylesheet.replace(
                "border-color: #4A90E2;",
                "border-color: #28a745; background-color: #f8fff9;"
            ))

    def focusOutEvent(self, event):
        """Override focus out event to reset styling"""
        super().focusOutEvent(event)
        # Reset to normal styling by re-applying theme
        current_stylesheet = self.styleSheet()
        is_dark = "background-color: #1a3c22" in current_stylesheet or "background-color: #2c2c2c" in current_stylesheet
        self.apply_theme(is_dark)

    @staticmethod
    def qt_to_windows_shortcut(qt_sequence: str) -> str:
        """Convert Qt key sequence to Windows hotkey format"""
        if not qt_sequence:
            return ""

        # Qt uses "Meta" for Windows key, convert to "Win"
        result = qt_sequence.replace("Meta+", "Win+")
        result = result.replace("Ctrl+", "Ctrl+")
        result = result.replace("Alt+", "Alt+")
        result = result.replace("Shift+", "Shift+")

        return result

    @staticmethod
    def windows_to_qt_shortcut(windows_sequence: str) -> str:
        """Convert Windows hotkey format to Qt key sequence"""
        if not windows_sequence:
            return ""

        # Convert "Win" to "Meta" for Qt
        result = windows_sequence.replace("Win+", "Meta+")
        result = result.replace("Windows+", "Meta+")

        return result


class ModernRadioButton(QRadioButton):
    """Beautiful modern radio button"""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.apply_theme(is_dark=False)

    def apply_theme(self, is_dark: bool):
        if is_dark:
            stylesheet = """
                QRadioButton {
                    font-size: 13px;
                    color: #b0b0b0;
                    spacing: 8px;
                    outline: none;
                }
                QRadioButton:checked {
                    color: #ffffff; /* selected text stronger */
                    font-weight: 500;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                }
                QRadioButton::indicator:unchecked {
                    border: 2px solid #555555; /* greyed out */
                    border-radius: 8px;
                    background-color: #2c2c2c;
                }
                QRadioButton::indicator:unchecked:hover {
                    border-color: #4A90E2;
                }
                QRadioButton::indicator:checked {
                    border: 2px solid #4A90E2;
                    border-radius: 8px;
                    background-color: #4A90E2;
                }
            """
        else:
            stylesheet = """
                QRadioButton {
                    font-size: 13px;
                    color: #495057;
                    spacing: 8px;
                    outline: none;
                }
                QRadioButton:checked {
                    color: #2c3e50;
                    font-weight: 500;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                }
                QRadioButton::indicator:unchecked {
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    background-color: white;
                }
                QRadioButton::indicator:unchecked:hover {
                    border-color: #4A90E2;
                }
                QRadioButton::indicator:checked {
                    border: 2px solid #4A90E2;
                    border-radius: 8px;
                    background-color: #4A90E2;
                }
            """
        self.setStyleSheet(stylesheet)


class ModernCheckBox(QCheckBox):
    """Beautiful modern check box"""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.apply_theme(is_dark=False)

    def apply_theme(self, is_dark: bool):
        if is_dark:
            stylesheet = """
                QCheckBox {
                    font-size: 13px;
                    color: #f0f0f0;
                    spacing: 8px;
                    outline: none;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #555555;
                    border-radius: 4px;
                    background-color: #2c2c2c;
                }
                QCheckBox::indicator:unchecked:hover {
                    border-color: #4A90E2;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #4A90E2;
                    border-radius: 4px;
                    background-color: #4A90E2;
                }
                QCheckBox::indicator:checked:hover {
                    border-color: #5BA0F2;
                }
            """
        else:
            stylesheet = """
                QCheckBox {
                    font-size: 13px;
                    color: #495057;
                    spacing: 8px;
                    outline: none;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #dee2e6;
                    border-radius: 4px;
                    background-color: white;
                }
                QCheckBox::indicator:unchecked:hover {
                    border-color: #4A90E2;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #4A90E2;
                    border-radius: 4px;
                    background-color: #4A90E2;
                }
            """
        self.setStyleSheet(stylesheet)


