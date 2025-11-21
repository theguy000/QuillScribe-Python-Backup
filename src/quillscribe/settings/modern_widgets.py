"""
Modern UI Widgets for Settings Dialog
Reusable styled components with theme support
"""

from PySide6.QtWidgets import (
    QComboBox, QLineEdit, QRadioButton, QCheckBox,
    QKeySequenceEdit, QListView, QGraphicsDropShadowEffect,
    QSlider, QProgressBar, QWidget, QHBoxLayout, QButtonGroup,
    QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, Property, Signal, QRect, QTimer
from PySide6.QtGui import QColor, QKeySequence, QPainter, QPen, QBrush
from ..icon_manager import icon_manager

# ModernGroupBox is now imported directly from ui_components and used as is
# to ensure consistency across the application.



class ModernComboBox(QComboBox):
    """Beautiful modern combo box"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Use a list view for better styling control and add subtle shadow
        self.setView(QListView(self))
        # self.view().setAlternatingRowColors(True) # Disabled for cleaner look
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

    def apply_theme(self, is_dark: bool, colors: dict = None):
        # Material Design Button + Precision Popup Style
        
        # Use provided colors or fallback to defaults
        if colors:
            bg = colors.get("secondary", "#f8f9fa")
            text_color = colors.get("text_primary", "#2c3e50")
            border_color = colors.get("accent", "#4A90E2")  # Use focus color as default border
            hover_bg = colors.get("widget_hover", colors.get("secondary", "#f8f9fa")) # Use specific hover color
            hover_border = colors.get("accent", "#4A90E2")  # Use focus color (no separate hover)
            accent = colors.get("accent", "#4A90E2")
            
            popup_bg = colors.get("popup_bg", colors.get("primary", "#ffffff")) # Use specific popup bg
            popup_border = colors.get("border", "#e9ecef")
            item_hover_bg = colors.get("accent", "#4A90E2")
            item_hover_border = colors.get("accent", "#4A90E2")
            
            selection_bg = colors.get("accent", "#4A90E2")
            selection_text = "#ffffff"
            selection_border = colors.get("accent", "#4A90E2")
        else:
            # Fallback legacy logic
            if is_dark:
                bg = "#3B2E57"  # input-dark
                text_color = "#E2E8F0"  # text-dark-primary
                border_color = "#4C3D70"  # border-dark
                hover_bg = "#3B2E57"
                hover_border = "#8B5CF6"  # primary
                accent = "#8B5CF6"
                
                popup_bg = "#2A1F3D"  # surface-dark
                popup_border = "#4C3D70"
                item_hover_bg = "#8B5CF6"
                item_hover_border = "#8B5CF6"
                
                selection_bg = "#8B5CF6"
                selection_text = "#ffffff"
                selection_border = "#8B5CF6"
            else:
                bg = "#f8f9fa"
                text_color = "#2c3e50"
                border_color = "#4A90E2"  # Use focus color as default border
                hover_bg = "#e9ecef"
                hover_border = "#4A90E2"  # Use focus color (no separate hover)
                accent = "#4A90E2"
                
                popup_bg = "#ffffff"
                popup_border = "#e9ecef"
                item_hover_bg = "#4A90E2"
                item_hover_border = "#4A90E2"
                
                selection_bg = "#4A90E2"
                selection_text = "#ffffff"
                selection_border = "#4A90E2"

        # Get arrow icon path
        arrow_icon = icon_manager.get_icon_path('chevron-down-white' if is_dark else 'chevron-down')
        if arrow_icon:
            arrow_icon = arrow_icon.replace('\\', '/')
        else:
            arrow_icon = "" # Fallback or empty

        stylesheet = f"""
            /* Material Design Button Style */
            QComboBox {{
                border: 1px solid {border_color};
                border-radius: 12px;
                padding: 0px 12px 3px 12px; /* Add bottom padding to center text */
                min-height: 32px;
                max-height: 32px;
                background-color: {bg};
                color: {text_color};
                font-family: 'Segoe UI', sans-serif;
                font-weight: 500;
                font-size: 14px;
                text-align: left;
            }}
            QComboBox:hover {{
                background-color: {hover_bg};
                border: 1px solid {hover_border};
            }}
            QComboBox:focus {{
                border: 1px solid {accent};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 32px; /* Square drop-down area */
                height: 30px; /* 32px - 2px border */
                subcontrol-origin: padding;
                subcontrol-position: top right;
            }}
            QComboBox::down-arrow {{
                image: url({arrow_icon});
                width: 14px;
                height: 14px;
                background: transparent;
            }}

            /* Precision Popup Style */
            QComboBox QAbstractItemView {{
                border: 1px solid {popup_border};
                border-radius: 0px;
                background-color: {popup_bg};
                color: {text_color};
                outline: none;
                padding: 0px;
                selection-background-color: transparent; /* We handle selection manually */
            }}
            
            /* Explicitly target QListView to override system defaults */
            QComboBox QListView {{
                background-color: {popup_bg};
                outline: none;
                selection-background-color: transparent;
            }}

            QComboBox QAbstractItemView::item {{
                height: 40px;
                padding-left: 16px;
                border: none;
                border-left: 3px solid transparent;
                color: {text_color};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {item_hover_bg};
                border-left: 3px solid {item_hover_border};
                color: #ffffff;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {selection_bg};
                border-left: 3px solid {selection_border};
                color: {selection_text};
                outline: none;
            }}
            
            /* Duplicate for QListView specific targeting */
            QComboBox QListView::item:selected {{
                background-color: {selection_bg};
                border-left: 3px solid {selection_border};
                color: {selection_text};
                outline: none;
            }}
            QComboBox QListView::item:hover {{
                background-color: {item_hover_bg};
                border-left: 3px solid {item_hover_border};
                color: #ffffff;
            }}
            QScrollBar::handle:vertical {{
                background: {'#555555' if is_dark else '#ced4da'};
                border-radius: 3px;
                min-height: 20px;
            }}
            
            /* Disabled State */
            QComboBox:disabled {{
                color: {'#6c757d' if is_dark else '#868e96'};
                background-color: {'#1a1a1a' if is_dark else '#f1f3f4'};
                border-bottom: 2px solid {'#404040' if is_dark else '#ced4da'};
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

    def apply_theme(self, is_dark: bool, colors: dict = None):
        if colors:
            bg = colors.get("primary", "#ffffff")
            text_color = colors.get("text_primary", "#212529")
            border_color = colors.get("accent", "#4A90E2")
            hover_border = colors.get("accent", "#4A90E2")
            accent = colors.get("accent", "#4A90E2")
            disabled_bg = colors.get("secondary", "#f1f3f4")
            disabled_text = colors.get("text_muted", "#868e96")
            disabled_border = colors.get("border", "#ced4da")
        else:
            if is_dark:
                bg = "#3B2E57"  # input-dark
                text_color = "#E2E8F0"  # text-dark-primary
                border_color = "#8B5CF6"  # Use focus color as default border
                hover_border = "#8B5CF6"  # Use focus color (no separate hover)
                accent = "#8B5CF6"
                disabled_bg = "#1A102A"
                disabled_text = "#6c757d"
                disabled_border = "#4C3D70"
            else:
                bg = "white"
                text_color = "#212529"
                border_color = "#4A90E2"  # Use focus color as default border
                hover_border = "#4A90E2"  # Use focus color (no separate hover)
                accent = "#4A90E2"
                disabled_bg = "#f1f3f4"
                disabled_text = "#868e96"
                disabled_border = "#ced4da"

        stylesheet = f"""
            QLineEdit {{
                border: 1px solid {border_color};
                border-radius: 12px;
                padding: 0px 12px 3px 12px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                background-color: {bg};
                color: {text_color};
                min-height: 32px;
                max-height: 32px;
                outline: none;
            }}
            QLineEdit:hover {{
                border-color: {hover_border};
            }}
            QLineEdit:focus {{
                border: 1px solid {accent};
            }}
            QLineEdit:disabled {{
                color: {disabled_text};
                background-color: {disabled_bg};
                border-style: dashed;
                border-color: {disabled_border};
            }}
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

    def apply_theme(self, is_dark: bool, colors: dict = None):
        if colors:
            bg = colors.get("primary", "#ffffff")
            text_color = colors.get("text_primary", "#212529")
            border_color = colors.get("accent", "#4A90E2")  # Use focus color as default border
            hover_border = colors.get("accent", "#4A90E2")  # Use focus color (no separate hover)
            accent = colors.get("accent", "#4A90E2")
        else:
            if is_dark:
                bg = "#3B2E57"  # input-dark
                text_color = "#E2E8F0"  # text-dark-primary
                border_color = "#8B5CF6"  # Use focus color as default border
                hover_border = "#8B5CF6"  # Use focus color (no separate hover)
                accent = "#8B5CF6"
            else:
                bg = "white"
                text_color = "black"
                border_color = "#4A90E2"  # Use focus color as default border
                hover_border = "#4A90E2"  # Use focus color (no separate hover)
                accent = "#4A90E2"

        self.setStyleSheet(f"""
            QKeySequenceEdit {{
                border: 1px solid {border_color};
                border-radius: 12px;
                padding: 0px 12px 3px 12px;
                font-size: 14px;
                background-color: {bg};
                color: {text_color};
                min-height: 32px;
                max-height: 32px;
                outline: none;
            }}
            QKeySequenceEdit:hover {{
                border-color: {hover_border};
            }}
            QKeySequenceEdit:focus {{
                border: 1px solid {accent};
            }}
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

    def apply_theme(self, is_dark: bool, colors: dict = None):
        if colors:
            text_color = colors.get("text_primary", "#b0b0b0" if is_dark else "#495057")
            border_color = colors.get("border", "#555555" if is_dark else "#dee2e6")
            accent = colors.get("accent", "#4A90E2")
            hover_border = colors.get("accent", "#4A90E2")
        else:
            if is_dark:
                text_color = "#b0b0b0"
                border_color = "#555555"
                accent = "#4A90E2"
                hover_border = "#4A90E2"
            else:
                text_color = "#495057"
                border_color = "#dee2e6"
                accent = "#4A90E2"
                hover_border = "#4A90E2"

        stylesheet = f"""
            QRadioButton {{
                font-size: 13px;
                color: {text_color};
                spacing: 8px;
                outline: none;
            }}
            QRadioButton:checked {{
                color: {text_color}; /* selected text stronger */
                font-weight: 500;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
            }}
            QRadioButton::indicator:unchecked {{
                border: 2px solid {border_color}; /* greyed out */
                border-radius: 8px;
                background-color: {'#2c2c2c' if is_dark else 'white'};
            }}
            QRadioButton::indicator:unchecked:hover {{
                border-color: {hover_border};
            }}
            QRadioButton::indicator:checked {{
                border: 2px solid {accent};
                border-radius: 8px;
                background-color: {accent};
            }}
        """
        self.setStyleSheet(stylesheet)


class ModernCheckBox(QCheckBox):
    """Beautiful modern check box"""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_theme(is_dark=False)

    def apply_theme(self, is_dark: bool, colors: dict = None):
        if colors:
            text_color = colors.get("text_primary", "#f0f0f0" if is_dark else "#495057")
            border_color = colors.get("border", "#555555" if is_dark else "#dee2e6")
            accent = colors.get("accent", "#4A90E2")
            hover_border = colors.get("accent", "#4A90E2")
        else:
            if is_dark:
                text_color = "#f0f0f0"
                border_color = "#555555"
                accent = "#4A90E2"
                hover_border = "#4A90E2"
            else:
                text_color = "#495057"
                border_color = "#dee2e6"
                accent = "#4A90E2"
                hover_border = "#4A90E2"

        stylesheet = f"""
            QCheckBox {{
                font-size: 13px;
                color: {text_color};
                spacing: 8px;
                outline: none;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 2px solid {border_color};
                border-radius: 4px;
                background-color: {'#2c2c2c' if is_dark else 'white'};
            }}
            QCheckBox::indicator:unchecked:hover {{
                border-color: {hover_border};
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid {accent};
                border-radius: 4px;
                background-color: {accent};
            }}
            QCheckBox::indicator:checked:hover {{
                border-color: {accent};
            }}
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

    def apply_theme(self, is_dark: bool, colors: dict = None):
        """
        Apply theme colors to the toggle switch.

        Args:
            is_dark: True for dark theme, False for light theme
            colors: Dictionary of theme colors
        """
        # Update internal colors
        if colors:
            self._colors['checked_track'] = QColor(colors.get("accent", "#4A90E2"))
            self._colors['unchecked_track_light'] = QColor(colors.get("border", "#dee2e6"))
            self._colors['unchecked_track_dark'] = QColor(colors.get("border", "#555555"))
            # We can add more theme-aware colors here if needed
        
        # Only update if theme actually changed (optimization)
        # Or if colors are provided (force update)
        if self._is_dark != is_dark or colors:
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

    def apply_theme(self, is_dark: bool, colors: dict = None):
        if colors:
            accent = colors.get("accent", "#4A90E2")
            groove_bg = colors.get("border", "#dee2e6" if not is_dark else "#555555")
            handle_border = colors.get("border_light", "#adb5bd" if not is_dark else "#777777")
            handle_bg = "#ffffff"
        else:
            accent = "#4A90E2"
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
                min-height: 44px;
                max-height: 44px;
                padding: 2px 0px;
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
                border: 2px solid {handle_border};
                width: 24px;
                height: 24px;
                margin: -11px 0;
                border-radius: 14px;
                subcontrol-position: center;
            }}
            QSlider::handle:horizontal:hover {{
                border: 3px solid {accent};
                background: #f8f9fa;
                width: 20px;
                height: 20px;
                margin: -10px 0;
                border-radius: 13px;
                subcontrol-position: center;
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


class ModernSegmentedControl(QWidget):
    """
    iOS-style segmented control (pill toggle).
    
    A container with multiple mutually exclusive options, styled as a single
    pill-shaped element with a sliding selector.
    """
    
    selectionChanged = Signal(int)  # Emits index of selected segment
    
    def __init__(self, items: list[str], parent=None):
        super().__init__(parent)
        self._items = items
        self._buttons = []
        self._current_index = 0
        
        # Setup layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(0)
        
        # Create buttons
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._group.idClicked.connect(self._on_button_clicked)
        
        for i, text in enumerate(items):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(32)
            
            if i == 0:
                btn.setChecked(True)
                
            self._layout.addWidget(btn)
            self._group.addButton(btn, i)
            self._buttons.append(btn)
            
        self.apply_theme(is_dark=False)
        
    def _on_button_clicked(self, id: int):
        if id != self._current_index:
            self._current_index = id
            self.selectionChanged.emit(id)
            
    def set_current_index(self, index: int):
        if 0 <= index < len(self._buttons):
            self._buttons[index].setChecked(True)
            self._on_button_clicked(index)
            
    def current_index(self) -> int:
        return self._current_index

    def apply_theme(self, is_dark: bool, accent: str = "#4A90E2"):
        if is_dark:
            bg_color = "#2c2c2c"
            text_color = "#b0b0b0"
            selected_bg = "#4A90E2"
            selected_text = "#ffffff"
            border_color = "#555555"
        else:
            bg_color = "#f1f3f4"
            text_color = "#5f6368"
            selected_bg = "#ffffff"
            selected_text = "#1a73e8"
            border_color = "#e0e0e0"

        # Container style
        self.setStyleSheet(f"""
            ModernSegmentedControl {{
                background-color: {bg_color};
                border-radius: 20px; /* Half of height (40px total) */
                border: 1px solid {border_color};
            }}
        """)
        
        # Button style
        # Note: We use a specific styling trick here. 
        # The container has the background. The buttons are transparent when unchecked.
        # When checked, they get the "card" look (light mode) or "accent" look (dark mode).
        
        for i, btn in enumerate(self._buttons):
            # Determine border radius for corners
            radius_style = "border-radius: 16px;" # Inner radius
            
            if is_dark:
                # Dark mode: Selected item is accented
                btn_style = f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {text_color};
                        border: none;
                        font-weight: 600;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 13px;
                        {radius_style}
                    }}
                    QPushButton:hover {{
                        color: #ffffff;
                    }}
                    QPushButton:checked {{
                        background-color: {selected_bg};
                        color: {selected_text};
                        border: 1px solid {selected_bg};
                    }}
                """
            else:
                # Light mode: Selected item is white card with shadow
                btn_style = f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {text_color};
                        border: none;
                        font-weight: 600;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 13px;
                        {radius_style}
                    }}
                    QPushButton:hover {{
                        color: #202124;
                    }}
                    QPushButton:checked {{
                        background-color: {selected_bg};
                        color: {selected_text};
                        border: 1px solid {border_color};
                    }}
                """
            btn.setStyleSheet(btn_style)


class ModernTabBar(QWidget):
    """
    Modern tab bar with text buttons and animated underline.
    Matches the "Command Center" design style.
    """
    
    tabChanged = Signal(int)
    
    def __init__(self, items: list[str], parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._items = items
        self._buttons = []
        self._current_index = 0
        
        # Layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        # HTML uses space-x-8 which is ~32px
        self._layout.setSpacing(32)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Button Group
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._group.idClicked.connect(self._on_button_clicked)
        
        for i, text in enumerate(items):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Remove Fixed Policy to allow auto-sizing based on text
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            # btn.setFixedHeight(32) # Removed fixed height, let padding define it
            
            if i == 0:
                btn.setChecked(True)
                
            self._layout.addWidget(btn)
            self._group.addButton(btn, i)
            self._buttons.append(btn)
            
        # Underline (Indicator)
        self._indicator = QWidget(self)
        self._indicator.setFixedHeight(2) # 2px height matches border-b-2
        self._indicator.hide() # Hidden initially, shown in resizeEvent
        
        # Animation
        self._anim = QPropertyAnimation(self._indicator, b"geometry")
        self._anim.setDuration(250)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        self.apply_theme(is_dark=False)
        
    def _on_button_clicked(self, id: int):
        if id != self._current_index:
            self._current_index = id
            self.tabChanged.emit(id)
            self._animate_indicator()
            
    def set_current_index(self, index: int):
        if 0 <= index < len(self._buttons):
            self._buttons[index].setChecked(True)
            self._on_button_clicked(index)
            
    def current_index(self) -> int:
        return self._current_index

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_indicator_geometry()
        
    def showEvent(self, event):
        super().showEvent(event)
        # Delay initial geometry update to ensure buttons have size
        QTimer.singleShot(0, self._update_indicator_geometry)

    def _update_indicator_geometry(self):
        if not self._buttons:
            return
            
        btn = self._buttons[self._current_index]
        # Position indicator at bottom of button
        rect = btn.geometry()
        # Indicator should match button width and sit at the very bottom
        target_rect = QRect(rect.x(), self.height() - 2, rect.width(), 2)
        
        self._indicator.setGeometry(target_rect)
        self._indicator.show()

    def _animate_indicator(self):
        if not self._buttons:
            return
            
        btn = self._buttons[self._current_index]
        rect = btn.geometry()
        target_rect = QRect(rect.x(), self.height() - 2, rect.width(), 2)
        
        self._anim.stop()
        self._anim.setStartValue(self._indicator.geometry())
        self._anim.setEndValue(target_rect)
        self._anim.start()

    def apply_theme(self, is_dark: bool, colors: dict = None):
        if colors:
            accent = colors.get("accent", "#4A90E2")
            border_color = colors.get("border", "#dee2e6" if not is_dark else "#4C3D70")
        else:
            accent = "#4A90E2"
            border_color = "#4C3D70" if is_dark else "#dee2e6"

        if is_dark:
            text_color = "#b0b0b0"   # Secondary text
            active_color = accent    # Primary text (accent)
            hover_color = "#ffffff"  # Hover text
        else:
            text_color = "#6c757d"   # Secondary text
            active_color = accent    # Primary text (accent)
            hover_color = "#212529"  # Hover text
            
        # Container styling: Add bottom border to the whole tab bar
        self.setStyleSheet(f"""
            ModernTabBar {{
                border-bottom: 1px solid {border_color};
            }}
        """)

        # Indicator color
        self._indicator.setStyleSheet(f"background-color: {accent}; border-radius: 0px;")
        
        # Button styles
        # Matches HTML: py-3 (12px vertical)
        # px-1 was requested but caused clipping, so increased to 12px for safety
        for btn in self._buttons:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 0px;
                    color: {text_color};
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 12px 12px;
                    margin-bottom: 1px; /* Space for the container border */
                }}
                QPushButton:hover {{
                    color: {hover_color};
                    background-color: transparent;
                }}
                QPushButton:checked {{
                    color: {active_color};
                    background-color: transparent;
                    font-weight: 500;
                }}
            """)
