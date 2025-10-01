"""
Output Settings Tab
Handles output behavior and clipboard settings
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QRadioButton, QButtonGroup, QFormLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIntValidator

from ..config_manager import ConfigManager
from ..icon_manager import get_button_icon
from .modern_widgets import ModernGroupBox, ModernRadioButton, ModernCheckBox


class OutputTab(QWidget):
    """Output settings tab"""

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)  # Reduced spacing for compact scroll layout

        # Output behavior
        output_group = ModernGroupBox("Output Behavior")
        output_layout = QVBoxLayout(output_group)

        self.output_group = QButtonGroup()
        self.copy_only = ModernRadioButton("Copy to clipboard only")
        self.copy_only.setIcon(get_button_icon('clipboard', 16))
        self.copy_only.setIconSize(QSize(16, 16))
        self.paste_only = ModernRadioButton("Paste to active app only")
        self.paste_only.setIcon(get_button_icon('paste', 16))
        self.paste_only.setIconSize(QSize(16, 16))
        self.copy_and_paste = ModernRadioButton("Copy and paste")
        self.copy_and_paste.setIcon(get_button_icon('clipboard', 16))
        self.copy_and_paste.setIconSize(QSize(16, 16))
        self.display_only = ModernRadioButton("Display only (no copy/paste)")
        self.display_only.setIcon(get_button_icon('eye', 16))
        self.display_only.setIconSize(QSize(16, 16))

        self.output_group.addButton(self.copy_only, 0)
        self.output_group.addButton(self.paste_only, 1)
        self.output_group.addButton(self.copy_and_paste, 2)
        self.output_group.addButton(self.display_only, 3)

        output_layout.addWidget(self.copy_only)
        output_layout.addWidget(self.paste_only)
        output_layout.addWidget(self.copy_and_paste)
        output_layout.addWidget(self.display_only)

        layout.addWidget(output_group)

        # Additional options
        options_group = ModernGroupBox("Additional Options")
        options_layout = QVBoxLayout(options_group)

        self.silent_mode = ModernCheckBox("Silent mode (hide transcription text)")
        self.silent_mode.setIconSize(QSize(16, 16))

        self.auto_clear = ModernCheckBox("Auto-clear after copying/pasting")
        self.auto_clear.setIconSize(QSize(16, 16))

        # Auto-clear delay setting
        auto_clear_layout = QHBoxLayout()
        auto_clear_layout.addWidget(self.auto_clear)

        # Add delay input next to auto-clear checkbox
        delay_label = QLabel("after")
        delay_label.setStyleSheet("color: #6c757d; font-size: 12px; margin-left: 10px;")

        self.auto_clear_delay = QLineEdit()
        self.auto_clear_delay.setFixedWidth(40)
        self.auto_clear_delay.setText("5")
        self.auto_clear_delay.setValidator(QIntValidator(1, 999))  # Only allow integers 1-999
        self.auto_clear_delay.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
                background-color: white;
                color: black;
            }
            QLineEdit:hover {
                border-color: #adb5bd;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
            }
        """)

        seconds_label = QLabel("seconds")
        seconds_label.setStyleSheet("color: #6c757d; font-size: 12px;")

        auto_clear_layout.addWidget(delay_label)
        auto_clear_layout.addWidget(self.auto_clear_delay)
        auto_clear_layout.addWidget(seconds_label)
        auto_clear_layout.addStretch()

        # Connect auto-clear checkbox to enable/disable delay input
        self.auto_clear.toggled.connect(self._update_auto_clear_delay_state)

        options_layout.addWidget(self.silent_mode)
        options_layout.addLayout(auto_clear_layout)

        # Help text for auto-clear
        auto_clear_help = QLabel("Note: 'Paste to active app only' always clears clipboard immediately regardless of this setting")
        auto_clear_help.setStyleSheet("""
            color: #856404;
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 8px;
            font-size: 11px;
        """)
        auto_clear_help.setWordWrap(True)
        options_layout.addWidget(auto_clear_help)

        layout.addWidget(options_group)

        # Add minimal space for scroll layout
        layout.addStretch()

    def _update_auto_clear_delay_state(self, checked: bool):
        """Enable/disable auto-clear delay input based on checkbox state"""
        self.auto_clear_delay.setEnabled(checked)

    def load_settings(self):
        """Load output settings from config"""
        output_mode = self.config_manager.get_setting("output/mode", 0)
        buttons = [self.copy_only, self.paste_only, self.copy_and_paste, self.display_only]
        if 0 <= output_mode < len(buttons):
            buttons[output_mode].setChecked(True)

        self.silent_mode.setChecked(self.config_manager.get_setting("output/silent_mode", False))
        auto_clear_enabled = self.config_manager.get_setting("output/auto_clear", False)
        self.auto_clear.setChecked(auto_clear_enabled)

        # Load auto-clear delay
        auto_clear_delay = self.config_manager.get_setting("output/auto_clear_delay", 5)
        self.auto_clear_delay.setText(str(auto_clear_delay))

        # Update delay input state based on checkbox
        self._update_auto_clear_delay_state(auto_clear_enabled)

    def save_settings(self):
        """Save output settings to config"""
        checked_button = self.output_group.checkedId()
        self.config_manager.set_setting("output/mode", checked_button)
        self.config_manager.set_setting("output/silent_mode", self.silent_mode.isChecked())
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