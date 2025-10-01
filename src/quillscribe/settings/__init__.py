"""
Settings Module
Modular settings dialogs and tabs for QuillScribe
"""

from .ui_components import ModernButton, ModernGroupBox as BaseModernGroupBox
from .modern_widgets import (
    ModernGroupBox,
    ModernComboBox,
    ModernLineEdit,
    ModernKeySequenceEdit,
    ModernRadioButton,
    ModernCheckBox
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
    'BaseModernGroupBox',
    
    # Modern widgets
    'ModernGroupBox',
    'ModernComboBox',
    'ModernLineEdit',
    'ModernKeySequenceEdit',
    'ModernRadioButton',
    'ModernCheckBox',
    
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
