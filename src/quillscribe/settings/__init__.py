"""
Settings module for QuillScribe
Modular settings management with separate components
"""

from .settings_dialog import SettingsDialog
from .statistics_tab import StatisticsTab
from .window_manager_dialog import WindowManagerDialog

# Import from original settings_dialog.py for now
# TODO: Move these to separate files
from ..settings_dialog import UISettingsDialog, AudioTab, WhisperTab, OutputTab, UITab

__all__ = [
    'SettingsDialog',
    'UISettingsDialog', 
    'AudioTab',
    'WhisperTab',
    'OutputTab',
    'UITab',
    'StatisticsTab',
    'WindowManagerDialog'
]
