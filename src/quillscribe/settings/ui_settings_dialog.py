"""
UI Settings Dialog
Compact frameless dialog for quick UI settings access
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox
)
from PySide6.QtCore import Qt, QSize, QEvent, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QIcon

from ..config_manager import ConfigManager
from ..icon_manager import get_button_icon, get_white_button_icon


class UISettingsDialog(QDialog):
    """A super-compact, frameless settings dialog for compact mode."""
    settings_saved = Signal()

    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager if config_manager is not None else ConfigManager()
        self._drag_active = False
        self._drag_offset = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("UI Settings")
        self.setFixedSize(200, 200)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)

        # Top bar with right-aligned ✕ button
        top = QHBoxLayout()
        title = QLabel("UI")
        title.setStyleSheet("QLabel { color: #2c3e50; font-size: 12px; font-weight: 600; }")
        top.addWidget(title)
        top.addStretch()
        self.close_btn = QPushButton(self)
        self.close_btn.setIcon(get_button_icon('close', 12))
        self.close_btn.setIconSize(QSize(12, 12))
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet(
            """
            QPushButton {
                background: rgba(0,0,0,0.08);
                color: #2c3e50;
                border: 1px solid #ced4da;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover { background: rgba(0,0,0,0.2); }
            """
        )
        # Use a drawn icon for perfect centering of the close "X"
        try:
            cross_size = 10
            pix = QPixmap(cross_size, cross_size)
            pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(QColor(44, 62, 80), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(2, 2, cross_size - 2, cross_size - 2)
            p.drawLine(cross_size - 2, 2, 2, cross_size - 2)
            p.end()
            self.close_btn.setIcon(QIcon(pix))
            self.close_btn.setIconSize(pix.rect().size())
            self.close_btn.setText("")
        except Exception:
            pass
        self.close_btn.clicked.connect(self.reject)
        top.addWidget(self.close_btn)
        layout.addLayout(top)

        # Content
        info = QLabel("Super Compact UI")
        info.setStyleSheet("QLabel { color: #495057; font-size: 11px; }")
        layout.addWidget(info)

        self.compact_checkbox = QCheckBox("Enable")
        self.compact_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #495057;
                spacing: 8px;
                outline: none;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #dee2e6;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:unchecked:hover {
                border-color: #4A90E2;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4A90E2;
                border-radius: 3px;
                background-color: #4A90E2;
            }
        """)
        self.compact_checkbox.setChecked(bool(self.config_manager.get_setting("ui/compact_mode", False)))
        layout.addWidget(self.compact_checkbox)

        layout.addStretch()

        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()
        save_btn = QPushButton("Save")
        save_btn.setIcon(get_white_button_icon('save', 12))
        save_btn.setIconSize(QSize(12, 12))
        save_btn.setStyleSheet(
            "QPushButton { background: #4A90E2; color: white; border: none; border-radius: 6px; padding: 6px 10px; font-size: 12px; }"
        )
        save_btn.clicked.connect(self.save_and_close)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        # Drag anywhere support
        self.installEventFilter(self)

        # Styling
        self.setStyleSheet(
            """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
            }
            """
        )

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