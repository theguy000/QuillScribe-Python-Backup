"""
UI Settings Dialog
Compact frameless dialog for quick UI settings access
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QWidget, QFrame
)
from PySide6.QtCore import Qt, QSize, QEvent, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QIcon

from ..config_manager import ConfigManager
from ..icon_manager import get_button_icon, get_white_button_icon
from .modern_buttons import ModernButton, ButtonVariant
from .modern_widgets import AnimatedToggleSwitch
from ..managers import get_theme_manager


class UISettingsDialog(QDialog):
    """A super-compact, frameless settings dialog for compact mode."""
    settings_saved = Signal()

    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager if config_manager is not None else ConfigManager()
        self._drag_active = False
        self._drag_offset = None
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        self.setWindowTitle("UI Settings")
        self.setFixedSize(240, 180) # Slightly wider for better layout
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Top bar with right-aligned ✕ button
        top = QHBoxLayout()
        self.title_label = QLabel("Interface Settings")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        top.addWidget(self.title_label)
        top.addStretch()
        
        self.close_btn = ModernButton(variant=ButtonVariant.GHOST)
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setIcon(get_button_icon('x', 14))
        self.close_btn.clicked.connect(self.reject)
        # Custom styling for the close button to make it circular and subtle
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
            }
        """)
        top.addWidget(self.close_btn)
        layout.addLayout(top)

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(12)
        
        # Compact Mode Toggle Row
        compact_row = QHBoxLayout()
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        self.compact_label = QLabel("Compact Mode")
        self.compact_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        
        self.compact_desc = QLabel("Minimal frameless window")
        self.compact_desc.setStyleSheet("font-size: 11px; color: #6c757d;")
        
        info_layout.addWidget(self.compact_label)
        info_layout.addWidget(self.compact_desc)
        
        compact_row.addLayout(info_layout)
        compact_row.addStretch()
        
        self.compact_checkbox = AnimatedToggleSwitch()
        self.compact_checkbox.setChecked(bool(self.config_manager.get_setting("ui/compact_mode", False)))
        compact_row.addWidget(self.compact_checkbox)
        
        content_layout.addLayout(compact_row)
        layout.addLayout(content_layout)

        layout.addStretch()

        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        self.save_btn = ModernButton("Save Changes", variant=ButtonVariant.PRIMARY)
        self.save_btn.setFixedSize(120, 32)
        self.save_btn.clicked.connect(self.save_and_close)
        buttons.addWidget(self.save_btn)
        
        layout.addLayout(buttons)

        # Drag anywhere support
        self.installEventFilter(self)

    def apply_theme(self):
        """Apply current theme to the dialog"""
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()
        colors = theme_manager.get_theme_colors()
        
        # Dialog Background
        bg_color = colors.get("secondary", "#ffffff")
        text_primary = colors.get("text_primary", "#212529")
        text_secondary = colors.get("text_secondary", "#6c757d")
        border_color = colors.get("border", "#dee2e6")
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 12px;
            }}
        """)
        
        # Labels
        self.title_label.setStyleSheet(f"color: {text_primary}; font-size: 14px; font-weight: 600;")
        self.compact_label.setStyleSheet(f"color: {text_primary}; font-weight: 500; font-size: 13px;")
        self.compact_desc.setStyleSheet(f"color: {text_secondary}; font-size: 11px;")
        
        # Components
        self.compact_checkbox.apply_theme(is_dark, colors)
        self.save_btn.apply_theme(is_dark, colors)
        
        # Close button icon update
        if is_dark:
            self.close_btn.setIcon(get_white_button_icon('x', 14))
            self.close_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 12px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.1);
                }
            """)
        else:
            self.close_btn.setIcon(get_button_icon('x', 14))
            self.close_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 12px;
                }
                QPushButton:hover {
                    background: rgba(0, 0, 0, 0.05);
                }
            """)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            # Qt6: globalPosition returns QPointF
            try:
                global_pos = event.globalPosition().toPoint()
            except Exception:
                global_pos = event.globalPos()
            self._drag_offset = global_pos - self.frameGeometry().topLeft()
            return False
        elif event.type() == QEvent.Type.MouseMove and self._drag_active and event.buttons() & Qt.MouseButton.LeftButton:
            try:
                global_pos = event.globalPosition().toPoint()
            except Exception:
                global_pos = event.globalPos()
            self.move(global_pos - self._drag_offset)
            return True
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self._drag_active = False
            return False
        return super().eventFilter(obj, event)

    def save_and_close(self):
        self.config_manager.set_setting("ui/compact_mode", self.compact_checkbox.isChecked())
        self.config_manager.save_settings()
        self.settings_saved.emit()
        self.accept()