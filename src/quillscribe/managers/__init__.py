"""
QuillScribe Managers
Backend service managers for audio, transcription, output, and UI
"""

from .audio_manager import AudioManager
from .whisper_manager import WhisperManager
from .output_manager import OutputManager
from .statistics_manager import StatisticsManager
from .theme_manager import ThemeManager, get_theme_manager
from .window_manager import WindowManager
from .sound_manager import SoundManager
from .tray_manager import TrayManager

__all__ = [
    'AudioManager',
    'WhisperManager',
    'OutputManager',
    'StatisticsManager',
    'ThemeManager',
    'get_theme_manager',
    'WindowManager',
    'SoundManager',
    'TrayManager',
]

