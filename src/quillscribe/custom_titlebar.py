"""
Custom Titlebar Component
Reusable titlebar for frameless windows with drag support
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from pathlib import Path

from .icon_manager import get_icon, get_themed_icon
from .frozen_compat import get_base_path
from .managers import get_theme_manager


class CustomTitleBar(QWidget):
    """Custom titlebar widget for frameless windows"""

    def __init__(self, parent=None, title="QuillScribe", show_minimize=True, show_maximize=False):
        super().__init__(parent)
        self.parent_window = parent
        self.show_minimize = show_minimize
        self.show_maximize = show_maximize
        self._drag_active = False
        self._drag_offset = None

        self.setFixedHeight(32)
        self.setup_ui(title)
        self.apply_theme(is_dark=False)

    def setup_ui(self, title):
        """Setup the titlebar UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Left section: icon + title
        left_section = QWidget()
        left_layout = QHBoxLayout(left_section)
        left_layout.setContentsMargins(12, 0, 0, 0)
        left_layout.setSpacing(8)

        # Window icon
        self.icon_label = QLabel()
        try:
            base_path = get_base_path()
            if base_path is not None:
                ico_path = base_path / "icons" / "app_logo.ico"
            else:
                ico_path = Path(__file__).parent / "icons" / "app_logo.ico"

            if ico_path.exists():
                pixmap = QPixmap(str(ico_path)).scaled(
                    16, 16, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                if not pixmap.isNull():
                    self.icon_label.setPixmap(pixmap)
        except Exception:
            pass

        self.icon_label.setFixedSize(16, 16)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("QLabel { background: transparent; border: none; }")
        left_layout.addWidget(self.icon_label)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 13px;
                font-weight: 500;
                background: transparent;
            }
        """)
        left_layout.addWidget(self.title_label)
        left_layout.addStretch()
        layout.addWidget(left_section)

        # Right section: window controls
        right_section = QWidget()
        right_layout = QHBoxLayout(right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Minimize button
        if self.show_minimize:
            self.minimize_btn = QPushButton()
            self.minimize_btn.setObjectName("minimize_btn")
            self.minimize_btn.setIcon(get_icon('minimize', 16))
            self.minimize_btn.setIconSize(QSize(16, 16))
            self.minimize_btn.setFixedSize(46, 32)
            self.minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.minimize_btn.clicked.connect(self._on_minimize)
            right_layout.addWidget(self.minimize_btn)
        else:
            self.minimize_btn = None

        # Maximize button (if needed in the future)
        if self.show_maximize:
            self.maximize_btn = QPushButton()
            self.maximize_btn.setObjectName("maximize_btn")
            self.maximize_btn.setIcon(get_icon('maximize', 16))
            self.maximize_btn.setIconSize(QSize(16, 16))
            self.maximize_btn.setFixedSize(46, 32)
            self.maximize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.maximize_btn.clicked.connect(self._on_maximize)
            right_layout.addWidget(self.maximize_btn)
        else:
            self.maximize_btn = None

        # Close button
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("titlebar_close_btn")
        self.close_btn.setIcon(get_icon('close', 16))
        self.close_btn.setIconSize(QSize(16, 16))
        self.close_btn.setFixedSize(46, 32)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self._on_close)
        right_layout.addWidget(self.close_btn)

        layout.addWidget(right_section)

    def set_title(self, title: str):
        """Update the titlebar title"""
        self.title_label.setText(title)

    def apply_theme(self, is_dark: bool, theme_name: str = None):
        """Apply theme colors to the titlebar using the theme manager's colors"""
        theme_manager = get_theme_manager()
        
        # Get the actual theme name if not provided
        if theme_name is None:
            theme_name = theme_manager.get_current_theme()
        
        # Get theme colors from the centralized theme manager
        colors = theme_manager.get_theme_colors(theme_name)
        
        # Use theme colors for titlebar styling
        titlebar_bg = colors.get("secondary", colors["primary"])
        titlebar_border = colors.get("border", "#555555" if is_dark else "#d0d0d0")
        titlebar_text = colors.get("text_primary", "#ffffff" if is_dark else "#2c3e50")
        
        # Button hover uses a slightly lighter/darker version of the background
        if is_dark:
            titlebar_btn_hover = theme_manager.lighten_color(titlebar_bg, 0.1)
            titlebar_btn_pressed = theme_manager.darken_color(titlebar_bg, 0.1)
        else:
            titlebar_btn_hover = theme_manager.darken_color(titlebar_bg, 0.08)
            titlebar_btn_pressed = theme_manager.darken_color(titlebar_bg, 0.15)

        # Main titlebar styling
        self.setStyleSheet(f"""
            QWidget {{
                background: {titlebar_bg};
                border-bottom: 1px solid {titlebar_border};
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        # Title label
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {titlebar_text};
                font-size: 13px;
                font-weight: 500;
                background: transparent;
            }}
        """)

        # Button styling
        button_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
            }}
            QPushButton:hover {{
                background: {titlebar_btn_hover};
            }}
            QPushButton:pressed {{
                background: {titlebar_btn_pressed};
            }}
        """

        close_button_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
            }}
            QPushButton:hover {{
                background: #e81123;
            }}
            QPushButton:pressed {{
                background: #c50e1f;
            }}
        """

        if self.minimize_btn:
            self.minimize_btn.setStyleSheet(button_style)
            self.minimize_btn.setIcon(get_themed_icon('minimize', 16, is_dark))

        if self.maximize_btn:
            self.maximize_btn.setStyleSheet(button_style)
            self.maximize_btn.setIcon(get_themed_icon('maximize', 16, is_dark))

        self.close_btn.setStyleSheet(close_button_style)
        self.close_btn.setIcon(get_themed_icon('close', 16, is_dark))

    def _on_minimize(self):
        """Handle minimize button click"""
        if self.parent_window:
            self.parent_window.showMinimized()

    def _on_maximize(self):
        """Handle maximize/restore button click"""
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
            else:
                self.parent_window.showMaximized()

    def _on_close(self):
        """Handle close button click"""
        if self.parent_window:
            self.parent_window.close()

    # Mouse event handlers for dragging
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            try:
                global_pos = event.globalPosition().toPoint()
            except Exception:
                global_pos = event.globalPos()
            if self.parent_window:
                self._drag_offset = global_pos - self.parent_window.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self._drag_active and event.buttons() & Qt.MouseButton.LeftButton:
            if self.parent_window:
                try:
                    global_pos = event.globalPosition().toPoint()
                except Exception:
                    global_pos = event.globalPos()
                self.parent_window.move(global_pos - self._drag_offset)

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = False
