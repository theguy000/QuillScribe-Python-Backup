"""
Output Settings Tab
Handles output behavior and clipboard settings
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator

from ..config_manager import ConfigManager
from .ui_components import ModernGroupBox
from .modern_widgets import ModernComboBox, AnimatedToggleSwitch, ModernLineEdit


class OutputTab(QWidget):
    """Output settings tab - Modern Layout"""

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.separators = []
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Output Mode Section ---
        mode_container = QWidget()
        mode_layout = QVBoxLayout(mode_container)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(8)

        # Header
        mode_header = QLabel("Output Behavior")
        mode_header.setObjectName("section_label")
        mode_header.setStyleSheet("font-size: 14px; font-weight: 600;")
        mode_layout.addWidget(mode_header)

        # Mode Dropdown
        self.mode_combo = ModernComboBox()
        self.mode_combo.addItem("Copy to clipboard only", 0)
        self.mode_combo.addItem("Paste to active app only", 1)
        self.mode_combo.addItem("Copy and paste", 2)
        self.mode_combo.addItem("Display only (no copy/paste)", 3)
        self.mode_combo.setFixedHeight(32)
        
        mode_layout.addWidget(self.mode_combo)
        
        # Helper text
        mode_help = QLabel("Choose how QuillScribe handles transcribed text.")
        mode_help.setObjectName("setting_desc")
        mode_help.setStyleSheet("color: #6c757d; font-size: 11px;")
        mode_layout.addWidget(mode_help)

        layout.addWidget(mode_container)

        # Separator
        self._add_separator(layout)

        # --- Clipboard Options Section ---
        clipboard_container = QWidget()
        clipboard_layout = QVBoxLayout(clipboard_container)
        clipboard_layout.setContentsMargins(0, 0, 0, 0)
        clipboard_layout.setSpacing(16)

        # Header
        clipboard_header = QLabel("Clipboard Management")
        clipboard_header.setObjectName("section_label")
        clipboard_header.setStyleSheet("font-size: 14px; font-weight: 600;")
        clipboard_layout.addWidget(clipboard_header)

        # Auto-clear Row (Unified)
        auto_clear_row = QHBoxLayout()
        auto_clear_row.setSpacing(12)
        
        # Toggle
        self.auto_clear = AnimatedToggleSwitch()
        self.auto_clear.toggled.connect(self._update_auto_clear_delay_state)
        auto_clear_row.addWidget(self.auto_clear)

        # Label and Description Container
        label_container = QVBoxLayout()
        label_container.setSpacing(2)
        
        auto_clear_label = QLabel("Auto-clear Clipboard")
        auto_clear_label.setObjectName("setting_label")
        auto_clear_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        
        auto_clear_desc = QLabel("Automatically remove text from clipboard.")
        auto_clear_desc.setObjectName("setting_desc")
        auto_clear_desc.setStyleSheet("color: #6c757d; font-size: 11px;")
        
        label_container.addWidget(auto_clear_label)
        label_container.addWidget(auto_clear_desc)
        
        auto_clear_row.addLayout(label_container)
        
        # Spacer to push delay input to the right
        auto_clear_row.addStretch()

        # Delay Input (Side-by-side)
        delay_container = QHBoxLayout()
        delay_container.setSpacing(8)

        delay_label = QLabel("Clear after")
        delay_label.setObjectName("setting_desc")
        delay_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        
        self.auto_clear_delay = ModernLineEdit()
        self.auto_clear_delay.setFixedWidth(40)
        self.auto_clear_delay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.auto_clear_delay.setValidator(QIntValidator(1, 999))
        
        seconds_label = QLabel("s")
        seconds_label.setObjectName("setting_desc")
        seconds_label.setStyleSheet("color: #6c757d; font-size: 12px;")

        delay_container.addWidget(delay_label)
        delay_container.addWidget(self.auto_clear_delay)
        delay_container.addWidget(seconds_label)

        auto_clear_row.addLayout(delay_container)

        clipboard_layout.addLayout(auto_clear_row)
        
        # Warning Note
        note_label = QLabel("Note: 'Paste to active app only' always clears the clipboard immediately.")
        note_label.setObjectName("setting_note")
        note_label.setStyleSheet("color: #856404; font-size: 11px; font-style: italic; margin-top: 4px; margin-left: 52px;") # Indent to align with text
        note_label.setWordWrap(True)
        clipboard_layout.addWidget(note_label)

        layout.addWidget(clipboard_container)
        layout.addStretch()

    def _add_separator(self, layout):
        """Add a theme-aware separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #f0f0f0; border: none; max-height: 1px;")
        layout.addWidget(line)
        self.separators.append(line)

    def _update_auto_clear_delay_state(self, checked: bool):
        """Enable/disable auto-clear delay input based on checkbox state"""
        self.auto_clear_delay.setEnabled(checked)

    def load_settings(self):
        """Load output settings from config"""
        output_mode = self.config_manager.get_setting("output/mode", 0)
        # Find index for data
        for i in range(self.mode_combo.count()):
            if self.mode_combo.itemData(i) == output_mode:
                self.mode_combo.setCurrentIndex(i)
                break

        auto_clear_enabled = self.config_manager.get_setting("output/auto_clear", False)
        self.auto_clear.setChecked(auto_clear_enabled)

        # Load auto-clear delay
        auto_clear_delay = self.config_manager.get_setting("output/auto_clear_delay", 5)
        self.auto_clear_delay.setText(str(auto_clear_delay))

        # Update delay input state based on checkbox
        self._update_auto_clear_delay_state(auto_clear_enabled)

    def save_settings(self):
        """Save output settings to config"""
        if self.mode_combo.currentIndex() >= 0:
            output_mode = self.mode_combo.currentData()
            self.config_manager.set_setting("output/mode", output_mode)
            
        self.config_manager.set_setting("output/auto_clear", self.auto_clear.isChecked())

        # Save auto-clear delay (validate input)
        try:
            delay_value = int(self.auto_clear_delay.text())
            # Ensure delay is between 1 and 999 seconds
            delay_value = max(1, min(999, delay_value))
            self.config_manager.set_setting("output/auto_clear_delay", delay_value)
        except ValueError:
            # If invalid input, use default of 5 seconds
            self.config_manager.set_setting("output/auto_clear_delay", 5)

    def apply_theme(self, theme_name):
        """Apply theme to tab specific elements"""
        from ..managers import get_theme_manager
        theme_manager = get_theme_manager()
        colors = theme_manager.get_theme_colors(theme_name)
        is_dark = theme_manager.is_dark_theme()

        # Explicitly set background color
        self.setStyleSheet(f"background-color: {colors['primary']};")

        # Update Separators
        separator_color = colors.get("border", "#404040" if is_dark else "#f0f0f0")
        for sep in self.separators:
            sep.setStyleSheet(f"background-color: {separator_color}; border: none; max-height: 1px;")

        # Update Labels
        text_primary = colors.get("text_primary", "#ffffff" if is_dark else "#212529")
        text_secondary = colors.get("text_secondary", "#e0e0e0" if is_dark else "#495057")
        text_muted = colors.get("text_muted", "#b0b0b0" if is_dark else "#6c757d")
        warning_color = "#ffc107" if is_dark else "#856404"

        for label in self.findChildren(QLabel):
            name = label.objectName()
            if name == "section_label":
                label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {text_primary};")
            elif name == "setting_label":
                label.setStyleSheet(f"font-weight: 500; font-size: 13px; color: {text_secondary};")
            elif name == "setting_desc":
                label.setStyleSheet(f"color: {text_muted}; font-size: 11px;")
            elif name == "setting_note":
                label.setStyleSheet(f"color: {warning_color}; font-size: 11px; font-style: italic; margin-top: 4px; margin-left: 52px;")

        # Unified theme application for child widgets
        from PySide6.QtWidgets import QWidget
        
        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'apply_theme'):
                try:
                    widget.apply_theme(is_dark, colors)
                except Exception:
                    pass


        # Save auto-clear delay (validate input)
        try:
            delay_value = int(self.auto_clear_delay.text())
            # Ensure delay is between 1 and 999 seconds
            delay_value = max(1, min(999, delay_value))
            self.config_manager.set_setting("output/auto_clear_delay", delay_value)
        except ValueError:
            # If invalid input, use default of 5 seconds
            self.config_manager.set_setting("output/auto_clear_delay", 5)

    def apply_theme(self, theme_name):
        """Apply theme to tab specific elements"""
        from ..managers import get_theme_manager
        theme_manager = get_theme_manager()
        colors = theme_manager.get_theme_colors(theme_name)
        is_dark = theme_manager.is_dark_theme()

        # Explicitly set background color
        self.setStyleSheet(f"background-color: {colors['primary']};")

        # Update Separators
        separator_color = colors.get("border", "#404040" if is_dark else "#f0f0f0")
        for sep in self.separators:
            sep.setStyleSheet(f"background-color: {separator_color}; border: none; max-height: 1px;")

        # Update Labels
        text_primary = colors.get("text_primary", "#ffffff" if is_dark else "#212529")
        text_secondary = colors.get("text_secondary", "#e0e0e0" if is_dark else "#495057")
        text_muted = colors.get("text_muted", "#b0b0b0" if is_dark else "#6c757d")
        warning_color = "#ffc107" if is_dark else "#856404"

        for label in self.findChildren(QLabel):
            name = label.objectName()
            if name == "section_label":
                label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {text_primary};")
            elif name == "setting_label":
                label.setStyleSheet(f"font-weight: 500; font-size: 13px; color: {text_secondary};")
            elif name == "setting_desc":
                label.setStyleSheet(f"color: {text_muted}; font-size: 11px;")
            elif name == "setting_note":
                label.setStyleSheet(f"color: {warning_color}; font-size: 11px; font-style: italic; margin-top: 4px; margin-left: 52px;")

        # Unified theme application for child widgets
        from PySide6.QtWidgets import QWidget
        
        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'apply_theme'):
                try:
                    widget.apply_theme(is_dark, colors)
                except Exception:
                    pass