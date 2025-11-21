"""
Settings Module
Modular settings dialogs and tabs for QuillScribe
"""

from .ui_components import ModernGroupBox
from .modern_buttons import ModernButton
from .modern_widgets import (
    ModernComboBox,
    ModernLineEdit,
    ModernKeySequenceEdit,
    ModernRadioButton,
    ModernCheckBox,
    AnimatedToggleSwitch
)

from .audio_tab import AudioTab
from .whisper_tab import WhisperTab
from .output_tab import OutputTab
from .ui_tab import UITab
from .statistics_tab import StatisticsTab
from .settings_dialog import SettingsDialog
from .window_manager_dialog import WindowManagerDialog
from .ui_settings_dialog import UISettingsDialog

__all__ = [
    # UI Components
    'ModernButton',
    'ModernGroupBox',

    # Modern widgets
    'ModernComboBox',
    'ModernLineEdit',
    'ModernKeySequenceEdit',
    'ModernRadioButton',
    'ModernCheckBox',
    'AnimatedToggleSwitch',

    # Tabs
    'AudioTab',
    'WhisperTab',
    'OutputTab',
    'UITab',
    'StatisticsTab',

    # Dialogs
    'SettingsDialog',
    'WindowManagerDialog',
    'UISettingsDialog',
]
