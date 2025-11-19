"""
Modern UI Widgets for Settings Dialog
Reusable styled components with theme support
"""

from PySide6.QtWidgets import (
    QComboBox, QLineEdit, QRadioButton, QCheckBox,
    QKeySequenceEdit, QListView, QGraphicsDropShadowEffect,
    QSlider, QProgressBar
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QColor, QKeySequence, QPainter, QPen, QBrush

# ModernGroupBox is now imported directly from ui_components and used as is
# to ensure consistency across the application.



class ModernComboBox(QComboBox):
    """Beautiful modern combo box"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
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
                padding: 6px 20px 6px 12px;
                min-height: 28px;
                font-family: 'Segoe UI', sans-serif;
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
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {text_color};
                width: 0px;
                height: 0px;
                margin: 8px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {border};
                border-radius: 8px;
                background-color: {bg};
                color: {text_color};
                selection-background-color: {accent};
                selection-color: {selection_text_color};
                alternate-background-color: {alt_bg};
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                height: 28px;
                padding: 4px 8px;
                color: {text_color};
                border-radius: 4px;
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
                width: 6px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background: {'#555555' if is_dark else '#ced4da'};
                border-radius: 3px;
                min-height: 20px;
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
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 13px;
                    background-color: #2c2c2c;
                    color: #ffffff;
                    min-height: 24px;
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
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 13px;
                    background-color: white;
                    color: #212529;
                    min-height: 24px;
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
        self.setCursor(Qt.CursorShape.PointingHandCursor)
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
        self.setCursor(Qt.CursorShape.PointingHandCursor)
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


class AnimatedToggleSwitch(QCheckBox):
    """
    iOS-style animated toggle switch widget.

    A modern, animated toggle switch that provides a familiar iOS-like experience
    with smooth sliding animations and theme support.

    Features:
    - Pill-shaped track (50x26px) with rounded ends
    - Sliding circular thumb (20px diameter) with smooth animation
    - 200ms InOutCubic easing for natural motion
    - Theme-aware colors (light/dark mode support)
    - Disabled state with grayed-out appearance
    - Maintains QCheckBox API compatibility

    Usage:
        toggle = AnimatedToggleSwitch()
        toggle.setChecked(True)
        toggle.toggled.connect(lambda checked: print(f"Toggled: {checked}"))
        toggle.apply_theme(is_dark=False)
    """

    # Class constants for dimensions and timing
    TOGGLE_WIDTH = 50
    TOGGLE_HEIGHT = 26
    TOGGLE_RADIUS = 13  # Half of height for perfect pill shape
    CIRCLE_SIZE = 20
    CIRCLE_Y_OFFSET = 3  # Vertical centering offset
    CIRCLE_POS_LEFT = 3  # Left position when unchecked
    CIRCLE_POS_RIGHT = 27  # Right position when checked (50 - 20 - 3)
    ANIMATION_DURATION_MS = 200

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Animation state
        self._circle_position = self.CIRCLE_POS_LEFT
        self._is_dark = False

        # Pre-create QColor objects for performance (avoid creating in paintEvent)
        self._colors = {
            'checked_track': QColor("#4A90E2"),
            'checked_circle': QColor("#ffffff"),
            'unchecked_track_light': QColor("#dee2e6"),
            'unchecked_track_dark': QColor("#555555"),
            'unchecked_circle_light': QColor("#ffffff"),
            'unchecked_circle_dark': QColor("#cccccc"),
            'disabled_track_light': QColor("#e9ecef"),
            'disabled_track_dark': QColor("#3a3a3a"),
            'disabled_circle_light': QColor("#adb5bd"),
            'disabled_circle_dark': QColor("#666666"),
        }

        # Setup animation
        self.animation = QPropertyAnimation(self, b"circle_position")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.setDuration(self.ANIMATION_DURATION_MS)

        # Connect state changes to animation
        self.toggled.connect(self._animate_toggle)

        # Set initial position based on checked state
        self._circle_position = self.CIRCLE_POS_RIGHT if self.isChecked() else self.CIRCLE_POS_LEFT

    def _animate_toggle(self, checked: bool):
        """
        Animate the toggle switch when state changes.

        Args:
            checked: New checked state
        """
        # Stop any running animation to prevent race conditions
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        # Animate from current position to target position
        target_pos = self.CIRCLE_POS_RIGHT if checked else self.CIRCLE_POS_LEFT
        self.animation.setStartValue(self._circle_position)
        self.animation.setEndValue(target_pos)
        self.animation.start()

    def _get_circle_position(self) -> int:
        """
        Get the current circle position for animation.

        Returns:
            Current X position of the circle
        """
        return self._circle_position

    def _set_circle_position(self, pos: int):
        """
        Set the circle position and trigger repaint.

        Args:
            pos: New X position for the circle
        """
        # Only update if position actually changed (optimization)
        if self._circle_position != pos:
            self._circle_position = pos
            self.update()

    # Qt Property for animation system
    circle_position = Property(int, _get_circle_position, _set_circle_position)

    def apply_theme(self, is_dark: bool):
        """
        Apply theme colors to the toggle switch.

        Args:
            is_dark: True for dark theme, False for light theme
        """
        # Only update if theme actually changed (optimization)
        if self._is_dark != is_dark:
            self._is_dark = is_dark
            self.update()

    def sizeHint(self) -> QSize:
        """Return the recommended size for the widget."""
        return QSize(self.TOGGLE_WIDTH, self.TOGGLE_HEIGHT)

    def hitButton(self, pos) -> bool:
        """
        Override to make the entire widget clickable.

        By default, QCheckBox only responds to clicks on the indicator.
        We want the entire toggle to be clickable for better UX.

        Args:
            pos: Mouse position

        Returns:
            True if position is within widget bounds
        """
        return self.contentsRect().contains(pos)

    def paintEvent(self, event):
        """
        Custom paint event to draw the iOS-style toggle switch.

        Draws:
        1. Rounded rectangle track (pill-shaped background)
        2. Circular thumb that slides left/right

        Colors change based on:
        - Checked state (blue when checked, gray when unchecked)
        - Theme (light/dark mode)
        - Enabled state (grayed out when disabled)

        Args:
            event: Paint event (unused, required by Qt)
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Determine colors based on state
        if not self.isEnabled():
            # Disabled state - grayed out
            if self._is_dark:
                track_color = self._colors['disabled_track_dark']
                circle_color = self._colors['disabled_circle_dark']
            else:
                track_color = self._colors['disabled_track_light']
                circle_color = self._colors['disabled_circle_light']
        elif self.isChecked():
            # Checked state - blue track, white circle
            track_color = self._colors['checked_track']
            circle_color = self._colors['checked_circle']
        else:
            # Unchecked state - gray track, white/gray circle
            if self._is_dark:
                track_color = self._colors['unchecked_track_dark']
                circle_color = self._colors['unchecked_circle_dark']
            else:
                track_color = self._colors['unchecked_track_light']
                circle_color = self._colors['unchecked_circle_light']

        # Draw track (rounded rectangle / pill shape)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(
            0, 0,
            self.TOGGLE_WIDTH, self.TOGGLE_HEIGHT,
            self.TOGGLE_RADIUS, self.TOGGLE_RADIUS
        )

        # Draw circle (sliding thumb)
        painter.setBrush(QBrush(circle_color))
        painter.drawEllipse(
            self._circle_position,
            self.CIRCLE_Y_OFFSET,
            self.CIRCLE_SIZE,
            self.CIRCLE_SIZE
        )

    def cleanup(self) -> None:
        """
        Clean up animation resources.

        Should be called when the widget is being destroyed to prevent
        memory leaks. Stops any running animation and deletes the
        animation object.
        """
        if hasattr(self, 'animation') and self.animation:
            self.animation.stop()
            self.animation.deleteLater()
            self.animation = None


class ModernSlider(QSlider):
    """Beautiful modern slider"""

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_theme(is_dark=False)

    def apply_theme(self, is_dark: bool, accent: str = "#4A90E2"):
        if is_dark:
            groove_bg = "#555555"
            handle_border = "#777777"
            handle_bg = "#ffffff"
        else:
            groove_bg = "#dee2e6"
            handle_border = "#adb5bd"
            handle_bg = "#ffffff"

        self.setStyleSheet(f"""
            QSlider {{
                min-height: 40px;
                max-height: 40px;
                padding: 0px;
                border: none;
            }}
            QSlider::groove:horizontal {{
                background: {groove_bg};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: {accent};
                border-radius: 3px;
            }}
            QSlider::add-page:horizontal {{
                background: {groove_bg};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {handle_bg};
                border: 1px solid {handle_border};
                width: 24px;
                height: 24px;
                margin: -9px 0;
                border-radius: 12px;
                
            }}
            QSlider::handle:horizontal:hover {{
                border: 1px solid {accent};
                background: #f8f9fa;
            }}
        """)


class ModernProgressBar(QProgressBar):
    """Beautiful modern progress bar"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.apply_theme(is_dark=False)

    def apply_theme(self, is_dark: bool, accent: str = "#28a745"):
        if is_dark:
            bg_color = "#2c2c2c"
            border_color = "#555555"
        else:
            bg_color = "#f8f9fa"
            border_color = "#dee2e6"

        self.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {border_color};
                border-radius: 6px;
                background-color: {bg_color};
                height: 12px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {accent};
                border-radius: 5px;
            }}
        """)

