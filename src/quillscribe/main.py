"""
QuillScribe Main Application
Beautiful voice-to-text transcription with minimal, elegant UI
"""

import sys
import math
import time
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGraphicsDropShadowEffect, QSizePolicy, QMessageBox,
    QSystemTrayIcon, QMenu
)
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QRect, Signal, Property, QTimer, QEvent, QSize, QAbstractNativeEventFilter, QAbstractEventDispatcher, Slot, Qt
from PySide6.QtGui import (QIcon, QAction, QColor, QPalette, QPainter, QPen, QBrush,
                         QRadialGradient, QLinearGradient, QFont, QCursor,
                         QPainterPath, QRegion, QShortcut, QKeySequence, QPixmap)

try:
    import ctypes  # type: ignore
    from ctypes import wintypes  # type: ignore
except Exception:
    ctypes = None
    wintypes = None

# Windows hotkey constants
WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008


class WindowsHotkeyEventFilter(QAbstractNativeEventFilter):
    """Native event filter to listen for WM_HOTKEY messages on Windows."""

    def __init__(self, id_to_callback: dict[int, callable]):
        super().__init__()
        self.id_to_callback = id_to_callback

    def nativeEventFilter(self, eventType, message):  # noqa: N802 (Qt signature)
        if ctypes is None or sys.platform != "win32":
            return False, 0
        try:
            if eventType in ("windows_generic_MSG", "windows_dispatcher_MSG"):
                # Handle different types of message parameter that PySide6 might pass
                if hasattr(message, '__int__'):
                    # If message is an integer pointer
                    msg_ptr = ctypes.cast(int(message), ctypes.POINTER(wintypes.MSG))
                elif hasattr(message, 'value'):
                    # If message is a sip.voidptr
                    msg_ptr = ctypes.cast(message.value, ctypes.POINTER(wintypes.MSG))
                else:
                    # Try direct cast as fallback
                    msg_ptr = ctypes.cast(message, ctypes.POINTER(wintypes.MSG))

                msg = msg_ptr.contents
                if msg.message == WM_HOTKEY:
                    hotkey_id = int(msg.wParam)
                    callback = self.id_to_callback.get(hotkey_id)
                    if callback:
                        try:
                            callback()
                        except Exception as e:
                            print(f"Hotkey callback error: {e}")
                    return True, 0
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully - don't process the event
            return False, 0
        except Exception as e:
            # Only print this occasionally to avoid spam
            if not hasattr(self, '_last_error_time') or time.time() - self._last_error_time > 5:
                print(f"DEBUG: Exception in nativeEventFilter: {e}")
                self._last_error_time = time.time()
            return False, 0
        return False, 0


class WindowsGlobalHotkeyManager:
    """Registers a global hotkey using Win32 RegisterHotKey and routes WM_HOTKEY to callbacks."""

    def __init__(self, window: QMainWindow):
        if ctypes is None or sys.platform != "win32":
            raise RuntimeError("Windows hotkey manager requires Windows and ctypes")
        self.window = window
        self.user32 = ctypes.windll.user32
        self.id_counter = 1
        self.id_to_callback: dict[int, callable] = {}
        self.registered_ids: set[int] = set()
        self.event_filter = WindowsHotkeyEventFilter(self.id_to_callback)
        dispatcher = QAbstractEventDispatcher.instance()
        if dispatcher is not None:
            dispatcher.installNativeEventFilter(self.event_filter)

    # Class-level constants for hotkey mapping
    SPECIAL_CHAR_MAP = {
        "`": 0xC0, "~": 0xC0, "=": 0xBB, "+": 0xBB, "-": 0xBD, "_": 0xBD,
        "[": 0xDB, "{": 0xDB, "]": 0xDD, "}": 0xDD, "\\": 0xDC, "|": 0xDC,
        ";": 0xBA, ":": 0xBA, "'": 0xDE, '"': 0xDE, ",": 0xBC, "<": 0xBC,
        ".": 0xBE, ">": 0xBE, "/": 0xBF, "?": 0xBF,
    }

    SPECIAL_KEY_MAP = {
        "space": 0x20, "tab": 0x09, "enter": 0x0D, "return": 0x0D,
        "escape": 0x1B, "esc": 0x1B, "backspace": 0x08, "insert": 0x2D,
        "delete": 0x2E, "home": 0x24, "end": 0x23, "pageup": 0x21,
        "pagedown": 0x22, "left": 0x25, "up": 0x26, "right": 0x27,
        "down": 0x28,
    }

    def _parse_shortcut(self, shortcut_text: str) -> tuple[int, int] | None:
        if not shortcut_text:
            return None

        # Split on + and clean up tokens
        tokens = [t.strip() for t in shortcut_text.split("+") if t.strip()]
        if not tokens:
            return None

        mods = 0
        vk = None

        # Process all tokens except the last one as modifiers
        for token in tokens[:-1]:
            t = token.lower()
            if t in ("win", "windows", "meta", "super"):
                mods |= MOD_WIN
            elif t in ("ctrl", "control"):
                mods |= MOD_CONTROL
            elif t == "alt":
                mods |= MOD_ALT
            elif t == "shift":
                mods |= MOD_SHIFT

        # Process the last token as the key
        key = tokens[-1].strip()
        key_lower = key.lower()

        # Function keys F1..F24
        if key_lower.startswith("f") and key_lower[1:].isdigit():
            n = int(key_lower[1:])
            if 1 <= n <= 24:
                vk = 0x70 + (n - 1)  # VK_F1 = 0x70
        elif len(key) == 1:
            if key in self.SPECIAL_CHAR_MAP:
                vk = self.SPECIAL_CHAR_MAP[key]
            else:
                vk = ord(key.upper())
        else:
            vk = self.SPECIAL_KEY_MAP.get(key_lower)

        if vk is None:
            return None

        return mods, vk

    def register_hotkey(self, shortcut_text: str, callback: callable) -> bool:
        self.unregister_all()
        parsed = self._parse_shortcut(shortcut_text)
        if parsed is None:
            return False
        mods, vk = parsed
        hotkey_id = self.id_counter
        self.id_counter += 1
        hwnd = int(self.window.winId())

        res = int(self.user32.RegisterHotKey(hwnd, hotkey_id, mods, vk))

        if res == 0:
            # Get the last error code for debugging
            last_error = ctypes.windll.kernel32.GetLastError()
            error_messages = {
                1409: "Hot key is already registered",
                87: "The parameter is incorrect",
                1413: "Invalid hotkey"
            }
            error_msg = error_messages.get(last_error, f"Unknown error {last_error}")
            print(f"Failed to register hotkey '{shortcut_text}': {error_msg}")
            return False

        self.id_to_callback[hotkey_id] = callback
        self.registered_ids.add(hotkey_id)
        return True

    def unregister_all(self):
        if ctypes is None or sys.platform != "win32":
            return
        hwnd = int(self.window.winId())
        for hotkey_id in list(self.registered_ids):
            try:
                self.user32.UnregisterHotKey(hwnd, hotkey_id)
            except Exception:
                pass
            self.registered_ids.discard(hotkey_id)
            self.id_to_callback.pop(hotkey_id, None)

    def cleanup(self):
        """Clean up hotkey manager resources"""
        try:
            self.unregister_all()
        except Exception as e:
            print(f"Warning: Error unregistering hotkeys: {e}")

        # Remove native event filter
        try:
            dispatcher = QAbstractEventDispatcher.instance()
            if dispatcher is not None and self.event_filter is not None:
                dispatcher.removeNativeEventFilter(self.event_filter)
                self.event_filter = None
        except Exception as e:
            print(f"Warning: Error removing native event filter: {e}")

        # Clear references
        self.id_to_callback.clear()
        self.registered_ids.clear()

from .managers import (
    AudioManager, WhisperManager, OutputManager, StatisticsManager,
    ThemeManager, get_theme_manager, WindowManager, SoundManager, TrayManager
)
from .settings import SettingsDialog, UISettingsDialog, WindowManagerDialog
from .config_manager import ConfigManager
from .icon_manager import get_icon, get_button_icon, get_white_button_icon, get_themed_button_icon
from .frozen_compat import get_base_path
from .custom_titlebar import CustomTitleBar


class BreathingMicrophone(QWidget):
    """Beautiful breathing microphone widget with smooth Siri-style ribbon animations"""

    # Signal for when microphone is clicked
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.scale_factor = 1.0
        self.audio_level = 0.0
        self.is_recording = False
        self.show_waveform = True
        self.level_smoothed = 0.0
        self.animation_strength = 3.0  # Default amplification factor
        self._transition_progress = 0.0  # 0.0 = static, 1.0 = waveform

        # Colors
        self._idle_color = QColor(220, 220, 220)
        self._recording_color = QColor(255, 255, 255)
        self._mic_color = QColor(self._idle_color)

        # Make the widget clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Animation setup (disabled breathing; mic remains static)
        self.animation = QPropertyAnimation(self, b"scaleFactor")
        self.animation.setDuration(1500)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.animation.setLoopCount(-1)

        # Color animation
        self.color_animation = QPropertyAnimation(self, b"micColor")
        self.color_animation.setDuration(300)  # Smooth 300ms transition
        self.color_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Transition animation (static <-> waveform)
        self.transition_animation = QPropertyAnimation(self, b"transitionProgress")
        self.transition_animation.setDuration(400)  # Slightly slower for background
        self.transition_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Ribbon animation state (Siri-style)
        # List of dicts: phase, speed_factor, color_alpha, amplitude_factor, color_hex
        self.ribbon_waves = [
            {"phase": 0.0, "speed": 1.0, "alpha": 40, "amp": 1.0, "color": "#00FFFF"},  # Cyan
            {"phase": 2.0, "speed": 1.2, "alpha": 60, "amp": 0.8, "color": "#007AFF"},  # Blue
            {"phase": 4.0, "speed": 0.8, "alpha": 30, "amp": 1.2, "color": "#AF52DE"},  # Purple
        ]
        
        self.wave_timer = QTimer(self)
        self.wave_timer.setInterval(16)  # ~60 FPS for smoother ribbons
        self.wave_timer.timeout.connect(self.advance_wave)

        # Theme integration
        self.current_theme_colors = {"primary": "#800080"}  # Default fallback
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self.update_theme_colors)
        # Initialize with current theme
        self.update_theme_colors(theme_manager.get_current_theme(), theme_manager.is_dark_theme())

        # Drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    @Slot(str, bool)
    def update_theme_colors(self, theme_name: str, is_dark: bool):
        """Update internal color state when theme changes"""
        theme_manager = get_theme_manager()
        self.current_theme_colors = theme_manager.get_theme_colors(theme_name)
        self.update()

    # Property for animation
    def getScaleFactor(self):
        return self.scale_factor

    def setScaleFactor(self, value):
        if isinstance(value, (int, float)):
            self.scale_factor = float(value)
            self.update()  # Trigger repaint

    scaleFactor = Property(float, getScaleFactor, setScaleFactor)

    # Property for color animation
    def getMicColor(self):
        return self._mic_color

    def setMicColor(self, color):
        self._mic_color = QColor(color)
        self.update()

    micColor = Property(QColor, getMicColor, setMicColor)

    # Property for transition animation
    def getTransitionProgress(self):
        return self._transition_progress

    def setTransitionProgress(self, value):
        self._transition_progress = float(value)
        self.update()

    transitionProgress = Property(float, getTransitionProgress, setTransitionProgress)

    def set_show_waveform(self, value: bool):
        """Enable/disable waveform rendering around the microphone"""
        self.show_waveform = bool(value)
        self.update()

    def set_animation_strength(self, value: float):
        """Set the animation amplification strength"""
        self.animation_strength = max(1.0, min(10.0, float(value)))
        self.update()

    def start_idle_breathing(self):
        """Mic stays static when idle (no breathing)."""
        self.animation.stop()
        self.scale_factor = 1.0
        self.update()

    def start_recording_breathing(self):
        """Enable ribbon animation while recording; mic remains static."""
        self.is_recording = True
        self.animation.stop()
        self.scale_factor = 1.0
        self.wave_timer.start()
        
        # Animate color to recording state
        self.color_animation.stop()
        self.color_animation.setStartValue(self._mic_color)
        self.color_animation.setEndValue(self._recording_color)
        self.color_animation.start()

        # Animate transition to waveform
        self.transition_animation.stop()
        self.transition_animation.setStartValue(self._transition_progress)
        self.transition_animation.setEndValue(1.0)
        self.transition_animation.start()
        
        self.update()  # Force visual refresh

    def stop_recording(self):
        """Stop recording and clear animation (mic stays static)."""
        self.is_recording = False
        # Don't stop wave timer immediately, let it run during fade out
        self.animation.stop()
        
        # Animate color to idle state
        self.color_animation.stop()
        self.color_animation.setStartValue(self._mic_color)
        self.color_animation.setEndValue(self._idle_color)
        self.color_animation.start()

        # Animate transition to static
        self.transition_animation.stop()
        self.transition_animation.setStartValue(self._transition_progress)
        self.transition_animation.setEndValue(0.0)
        self.transition_animation.start()
        
        self.update()  # Force visual refresh

    @Slot(float)
    def update_audio_level(self, level: float):
        """Update level (used for waveform only); do not scale mic with level"""
        # Additional gentle smoothing for visual stability
        level = max(0.0, min(1.0, level))
        self.level_smoothed = (0.85 * self.level_smoothed) + (0.15 * level)
        self.audio_level = self.level_smoothed

    def advance_wave(self):
        """Advance ribbon phases for organic motion."""
        # Base speed
        base_speed = 0.05
        # Audio reactivity: faster motion with louder audio
        amplified_level = min(1.0, self.audio_level * self.animation_strength)
        reactivity = amplified_level * 0.1
        
        for wave in self.ribbon_waves:
            # Each wave moves at its own speed plus shared reactivity
            speed = (base_speed * wave["speed"]) + reactivity
            wave["phase"] = (wave["phase"] + speed) % (2 * math.pi)
            
        self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse click to toggle recording."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get the center and radius
        center_x = self.width() // 2
        center_y = self.height() // 2
        base_radius = min(self.width(), self.height()) // 3
        radius = int(base_radius * self.scale_factor)

        # Base colors
        base_color = QColor(128, 128, 128)

        # Draw Siri-style ribbons (Waveform)
        # We draw this if transition_progress > 0
        if self.show_waveform and self._transition_progress > 0.01:
            amplified_level = min(1.0, self.audio_level * self.animation_strength)
            
            # Draw multiple overlapping ribbons
            for i, wave in enumerate(self.ribbon_waves):
                path = QPainterPath()
                
                # Dynamic radius based on audio level and wave properties
                # Breathing effect: base size + audio reaction + wave variation
                wave_amp = wave["amp"] * (10 + (amplified_level * 20))
                current_radius = radius + 10 + (amplified_level * 15)
                
                # Create a "blob" or organic circle shape
                points = 90  # Increased points for smoother curves
                for j in range(points + 1):
                    angle = (j / points) * 2 * math.pi
                    
                    # Refined math for "shimmering circle" instead of "fan"
                    # Use multiple lower-amplitude sine waves for subtle complexity
                    # Base wave (slow rotation) + Detail wave (faster ripple)
                    r_mod = (math.sin(angle * 3 + wave["phase"]) * 0.5 + 
                             math.sin(angle * 6 - wave["phase"] * 2) * 0.2)
                    
                    # Scale modulation by amplitude but keep it subtle relative to radius
                    r = current_radius + (r_mod * wave_amp * 0.6)
                    
                    x = center_x + r * math.cos(angle)
                    y = center_y + r * math.sin(angle)
                    
                    if j == 0:
                        path.moveTo(x, y)
                    else:
                        path.lineTo(x, y)
                
                path.closeSubpath()
                
                # Fill with specific wave color and varying opacity
                color = QColor(wave["color"])
                # Modulate alpha with audio level for "glowing" pulse
                pulse = 0.8 + (0.2 * math.sin(wave["phase"] * 2))
                # significantly increased base alpha for visibility
                # Scale alpha by transition_progress for fade in/out
                alpha = int(wave["alpha"] * 2.5 * (1.0 + amplified_level) * pulse * self._transition_progress)
                color.setAlpha(min(200, alpha))  # Cap at 200 to keep some transparency
                
                painter.setBrush(QBrush(color))
                
                # Add a thin stroke for better definition
                stroke_color = QColor(wave["color"])
                stroke_color.setAlpha(min(255, int(alpha * 1.2)))
                painter.setPen(QPen(stroke_color, 1.5, Qt.PenStyle.SolidLine))
                
                painter.drawPath(path)

        # Draw static background circles
        # Fade out as transition_progress increases
        static_alpha_factor = 1.0 - self._transition_progress
        if static_alpha_factor > 0.01:
            outer_color = QColor(base_color)
            # Base alpha is 20, scale it down
            outer_color.setAlpha(int(20 * static_alpha_factor))
            painter.setBrush(QBrush(outer_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center_x - radius - 10, center_y - radius - 10,
                              (radius + 10) * 2, (radius + 10) * 2)

        # Draw microphone icon (always on top)
        # Use the animated color
        painter.setPen(QPen(self._mic_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(QBrush(self._mic_color))

        # Microphone body (capsule)
        mic_width = radius // 2
        mic_height = radius // 1.5
        mic_x = center_x - mic_width // 2
        mic_y = center_y - mic_height // 2 - 5

        painter.drawRoundedRect(mic_x, mic_y, mic_width, mic_height, 8, 8)

        # Microphone stand
        stand_y = mic_y + mic_height
        painter.drawLine(center_x, stand_y, center_x, stand_y + 15)
        painter.drawLine(center_x - 8, stand_y + 15, center_x + 8, stand_y + 15)


class ModernButton(QPushButton):
    """Beautiful modern button with hover effects"""

    def __init__(self, text: str, primary: bool = False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_theme(is_dark=False, compact=False)

        # Hover animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def apply_theme(self, is_dark: bool, compact: bool = False):
        if self.primary:
            # Primary button (Record/Stop)
            stylesheet = """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4A90E2, stop:1 #357ABD);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 16px;
                    font-weight: 600;
                    padding: 12px 24px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5BA0F2, stop:1 #4A90E2);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #357ABD, stop:1 #2E6BA0);
                }
            """
        else:
            # Secondary button (Settings)
            if compact:
                font_size = "11px"
                border_radius = "8px"
                padding = "6px 10px"
                min_width = "60px"
            else:
                font_size = "16px"
                border_radius = "12px"
                padding = "12px 24px"
                min_width = "120px"

            if is_dark:
                stylesheet = f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3c3c3c, stop:1 #2c2c2c);
                        color: #f0f0f0;
                        border: 2px solid #555555;
                        border-radius: {border_radius};
                        font-size: {font_size};
                        font-weight: 500;
                        padding: {padding};
                        min-width: {min_width};
                        text-align: center;
                    }}
                    QPushButton:hover {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4c4c4c, stop:1 #3c3c3c); border-color: #777777; }}
                    QPushButton:pressed {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2c2c2c, stop:1 #1c1c1c); }}
                """
            else:
                stylesheet = f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8f9fa, stop:1 #e9ecef);
                        color: #495057;
                        border: 2px solid #dee2e6;
                        border-radius: {border_radius};
                        font-size: {font_size};
                        font-weight: 500;
                        padding: {padding};
                        min-width: {min_width};
                        text-align: center;
                    }}
                    QPushButton:hover {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f1f3f4); border-color: #adb5bd; color: #495057; }}
                    QPushButton:pressed {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e9ecef, stop:1 #dee2e6); }}
                """
        self.setStyleSheet(stylesheet)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class QuillScribeMainWindow(QMainWindow):
    """Main application window with beautiful minimal UI"""

    # Theme colors are now centralized in ThemeManager
    # Access via get_theme_manager().get_theme_colors(theme_name)

    def __init__(self):
        super().__init__()
        # Initialize essential components first
        self.config_manager = ConfigManager()

        # Initialize UI state variables
        self.settings_dialog = None
        self.is_recording = False
        self.compact_mode = False
        self.is_dark = False
        self._drag_active = False
        self._drag_offset = None
        self._app_shortcut = None
        self.tray_manager = None
        self.window_manager = None
        self._force_exit = False
        
        # Exit state flags to prevent recursion
        self._exit_in_progress = False
        self._exit_completed = False
        
        # Theme application state to prevent recursion
        self._applying_theme = False

        # Lazy-loaded managers (initialized when first needed)
        self._audio_manager = None
        self._whisper_manager = None
        self._output_manager = None
        self._sound_manager = None
        self._statistics_manager = None

        # Background initialization flags
        self._audio_monitoring_started = False
        self._hotkey_setup_completed = False

        # Setup UI first for fast startup
        self.setup_ui()
        self.setup_connections()
        # Connect to theme manager for live theme updates BEFORE loading settings
        # so saved theme is applied immediately during load_settings.
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._on_theme_changed)
        self.load_settings()
        self.center_window()
        self.install_drag_filters()

        # Setup tray and window manager (lightweight)
        self.setup_tray_manager()
        self.setup_window_manager()

        # Schedule background initialization
        QTimer.singleShot(100, self._initialize_background_components)

        # Record session start
        QTimer.singleShot(200, self._record_session_start)

    @property
    def audio_manager(self):
        """Lazy-loaded audio manager"""
        if self._audio_manager is None:
            self._audio_manager = AudioManager()
        return self._audio_manager

    @property
    def whisper_manager(self):
        """Lazy-loaded whisper manager"""
        if self._whisper_manager is None:
            self._whisper_manager = WhisperManager()
        return self._whisper_manager

    @property
    def output_manager(self):
        """Lazy-loaded output manager"""
        if self._output_manager is None:
            self._output_manager = OutputManager(self.config_manager)
        return self._output_manager

    @property
    def sound_manager(self):
        """Lazy-loaded sound manager"""
        if self._sound_manager is None:
            self._sound_manager = SoundManager()
        return self._sound_manager

    @property
    def statistics_manager(self):
        """Lazy-loaded statistics manager"""
        if self._statistics_manager is None:
            self._statistics_manager = StatisticsManager(self.config_manager)
        return self._statistics_manager

    def _initialize_background_components(self):
        """Initialize components in background for better startup performance"""
        # Initialize audio manager and start monitoring
        if not self._audio_monitoring_started:
            try:
                # This will trigger lazy loading of audio_manager
                self.audio_manager.start_monitoring()
                self._audio_monitoring_started = True
            except Exception as e:
                print(f"Warning: Could not start audio monitoring: {e}")

        # Setup hotkeys
        if not self._hotkey_setup_completed:
            try:
                self._ensure_hotkey_manager()
                self.apply_hotkey_setting()
                self._hotkey_setup_completed = True
            except Exception as e:
                print(f"Warning: Could not set up hotkey: {e}")

        # Pre-initialize other managers for faster first use
        QTimer.singleShot(500, self._preload_remaining_components)

    def _preload_remaining_components(self):
        """Preload remaining components after UI is fully loaded"""
        try:
            # Trigger lazy loading of remaining managers
            _ = self.sound_manager  # Initialize sound manager
            _ = self.output_manager  # Initialize output manager
            # Note: whisper_manager is not preloaded as it's heavy and mode-dependent
        except Exception as e:
            print(f"Warning: Could not preload components: {e}")

    def _record_session_start(self):
        """Record the start of a new session"""
        try:
            self.statistics_manager.record_session_start()
        except Exception as e:
            print(f"Warning: Could not record session start: {e}")

    def _ensure_hotkey_manager(self):
        """Create platform-specific hotkey manager if not yet created."""
        if hasattr(self, "hotkey_manager") and self.hotkey_manager is not None:
            return
        self.hotkey_manager = None
        try:
            if sys.platform == "win32":
                self.hotkey_manager = WindowsGlobalHotkeyManager(self)
        except Exception:
            self.hotkey_manager = None

    def setup_ui(self):
        """Create the beautiful UI"""
        self.setWindowTitle("QuillScribe")
        self.setFixedSize(400, 500)

        # Check if custom titlebar is enabled (default to True for backward compatibility)
        custom_titlebar = bool(self.config_manager.get_setting("ui/custom_titlebar", True))

        # Get always-on-top setting to preserve it
        always_on_top = bool(self.config_manager.get_setting("ui/always_on_top", False))

        if custom_titlebar:
            # Use frameless window for custom titlebar
            base_flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        else:
            # Use standard window with system titlebar
            base_flags = Qt.WindowType.Window

        # Add always-on-top flag if needed
        if always_on_top:
            base_flags |= Qt.WindowType.WindowStaysOnTopHint

        self.setWindowFlags(base_flags)

        # Set window icon (ICO format only - guaranteed to be present)
        # This reinforces the application-level icon for this specific window
        try:
            from pathlib import Path
            # Handle both development and frozen executable environments
            base_path = get_base_path()
            if base_path is not None:
                # Running as frozen executable (Nuitka)
                ico_path = base_path / "icons" / "app_logo.ico"
            else:
                # Running from source
                ico_path = Path(__file__).parent / "icons" / "app_logo.ico"

            if ico_path.exists():
                icon = QIcon(str(ico_path))
                if not icon.isNull():
                    self.setWindowIcon(icon)
        except Exception:
            pass

        # Central widget
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)
        self.main_layout = layout

        # Store custom titlebar flag for later use
        self.custom_titlebar_enabled = custom_titlebar

        if custom_titlebar:
            # Custom titlebar mode: remove spacing and margins to accommodate titlebar
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)

            # Create and add custom titlebar
            self.custom_titlebar = CustomTitleBar(self, title="QuillScribe", show_minimize=True)
            layout.addWidget(self.custom_titlebar)

            # Main content area with original spacing
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(30)
            content_layout.setContentsMargins(40, 20, 40, 40)
            layout.addWidget(content_widget)

            # Update main_layout to point to content layout for adding widgets
            self.main_layout = content_layout
        else:
            # Standard titlebar mode: use standard spacing and margins
            layout.setSpacing(30)
            layout.setContentsMargins(40, 20, 40, 40)

            # No custom titlebar needed
            self.custom_titlebar = None

        # Topbar removed - using unified custom titlebar for both modes


        # Title - properly centered
        title = QLabel("QuillScribe")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 28px;
                font-weight: 300;
                margin-bottom: 20px;
                text-align: center;
            }
        """)
        layout.addWidget(title)
        self.title_label = title

        # Breathing microphone
        self.microphone = BreathingMicrophone()
        mic_layout = QHBoxLayout()
        mic_layout.addStretch()
        mic_layout.addWidget(self.microphone)
        mic_layout.addStretch()
        layout.addLayout(mic_layout)

        layout.addStretch()

        # Settings button only
        self.settings_button = ModernButton("Settings", primary=False)
        self.settings_button.setIcon(get_button_icon('settings', 16))
        self.settings_button.setIconSize(QSize(16, 16))
        # Ensure button doesn't expand horizontally beyond its content
        self.settings_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.settings_button, 0, Qt.AlignmentFlag.AlignCenter)
        button_layout.addStretch()
        layout.addLayout(button_layout, 0)

        # Status label (will be updated with actual shortcut after config loads)
        self.status_label = QLabel("Click microphone or press [Win + `] to start recording")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.status_label)

        # Window styling
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
            }
        """)



    def setup_connections(self):
        """Connect signals and slots"""
        self.microphone.clicked.connect(self.toggle_recording)
        self.settings_button.clicked.connect(self.show_settings)

        # Audio manager connections
        try:
            self.audio_manager.audio_level_changed.connect(self.microphone.update_audio_level)
        except Exception as e:
            print(f"Warning: Could not connect audio level signal: {e}")

        # Whisper manager connections
        self.whisper_manager.transcription_ready.connect(self.handle_transcription)
        self.whisper_manager.transcription_error.connect(self.handle_transcription_error)

        # Output manager connections
        self.output_manager.operation_complete.connect(self.update_status)
        self.output_manager.operation_failed.connect(self.handle_output_error)

    def setup_tray_manager(self):
        """Setup system tray manager"""
        try:
            self.tray_manager = TrayManager(self.config_manager, self)

            # Connect tray manager signals
            self.tray_manager.show_window_requested.connect(self.show_from_tray)
            self.tray_manager.start_recording_requested.connect(self.start_recording)
            self.tray_manager.stop_recording_requested.connect(self.stop_recording)
            self.tray_manager.settings_requested.connect(self.show_settings)
            self.tray_manager.exit_requested.connect(self.exit_application)

        except Exception as e:
            print(f"Warning: Could not setup tray manager: {e}")
            self.tray_manager = None

    def setup_window_manager(self):
        """Setup window management system"""
        try:
            self.window_manager = WindowManager(self, self.config_manager, self)

            # Connect window manager signals
            self.window_manager.monitor_changed.connect(self._on_monitor_changed)
            self.window_manager.snap_performed.connect(self._on_snap_performed)

        except Exception as e:
            print(f"Warning: Could not setup window manager: {e}")
            self.window_manager = None

    def _on_monitor_changed(self, monitor_id: str):
        """Handle monitor change event"""
        print(f"Window moved to monitor: {monitor_id}")

    def _on_snap_performed(self, edge: str):
        """Handle snap-to-edge event"""
        print(f"Window snapped to: {edge}")

    def center_window(self):
        """Center the window on screen"""
        if self.window_manager:
            # Try to restore saved position first
            self.window_manager.restore_window_position()
        else:
            # Fallback to simple centering
            screen = QApplication.primaryScreen().availableGeometry()
            size = self.geometry()
            self.move(
                (screen.width() - size.width()) // 2,
                (screen.height() - size.height()) // 2
            )

    def show_from_tray(self):
        """Show window from system tray"""
        self.show()
        self.raise_()
        self.activateWindow()
        self._refresh_taskbar_icon()
        # Keep tray icon visible for easy access

    def _refresh_taskbar_icon(self):
        """Force refresh of taskbar icon on Windows"""
        if sys.platform == "win32":
            try:
                # Get the window icon and re-set it to force Windows to update
                icon = self.windowIcon()
                if not icon.isNull():
                    self.setWindowIcon(QIcon())  # Clear
                    self.setWindowIcon(icon)  # Re-set
            except Exception:
                pass

    def hide_to_tray(self):
        """Hide window to system tray"""
        if self.tray_manager and self.tray_manager.is_available():
            self.hide()
            self.tray_manager.show_tray()
        else:
            # Fallback to regular minimize if tray not available
            self.showMinimized()

    def exit_application(self):
        """Exit the application completely"""
        # Set a flag to bypass minimize on close
        self._force_exit = True
        self.close()

    def minimize_window(self):
        """Handle minimize button click - minimize to tray or taskbar based on settings"""
        try:
            minimize_to_tray = bool(self.config_manager.get_setting("ui/minimize_to_tray", False))
        except Exception:
            minimize_to_tray = False

        # If minimize to tray is enabled, use tray; otherwise use taskbar
        if minimize_to_tray:
            self.hide_to_tray()
        else:
            self.showMinimized()

    def toggle_recording(self):
        """Toggle between recording and stop states"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start voice recording"""
        # Play start sound
        self.sound_manager.play_start_sound()

        self.is_recording = True
        self.status_label.setText(f"Recording... (Click microphone or press {self.get_formatted_shortcut()} to stop)")
        self.microphone.start_recording_breathing()

        # Update tray manager
        if self.tray_manager:
            self.tray_manager.set_recording_state(True)

        # Track recording start
        self.statistics_manager.record_recording_start()
        self._recording_start_time = time.time()

        # Start audio capture
        try:
            self.audio_manager.start_recording()
        except Exception as e:
            self.handle_recording_error(f"Failed to start recording: {str(e)}")
            self.is_recording = False
            self.status_label.setText(f"Click microphone or press {self.get_formatted_shortcut()} to start recording")
            self.microphone.stop_recording()
            # Update tray manager
            if self.tray_manager:
                self.tray_manager.set_recording_state(False)

    def stop_recording(self):
        """Stop voice recording"""
        self.is_recording = False
        self.status_label.setText("Processing...")
        self.microphone.stop_recording()

        # Update tray manager
        if self.tray_manager:
            self.tray_manager.set_recording_state(False)

        # Stop audio capture and process
        audio_data = self.audio_manager.stop_recording()
        if audio_data is not None and len(audio_data) > 0:
            self.whisper_manager.transcribe_audio(audio_data)
        else:
            # Play stop sound even when no audio data
            self.sound_manager.play_stop_sound()
            self.status_label.setText(f"No audio data recorded - Click microphone or press {self.get_formatted_shortcut()} to try again")

    def handle_transcription(self, text: str):
        """Handle transcription result"""
        if text:
            # Process the transcription through output manager
            self.output_manager.process_transcription(text)

            # Record successful transcription
            if hasattr(self, '_recording_start_time'):
                duration = time.time() - self._recording_start_time
                transcription_time = getattr(self, '_transcription_time', 0.0)
                mode = self.config_manager.get_setting("whisper/mode", "api")

                self.statistics_manager.record_transcription_result(
                    success=True,
                    mode=mode,
                    duration=duration,
                    transcription_time=transcription_time,
                    text=text
                )
        else:
            # Play stop sound even when no speech detected
            self.sound_manager.play_stop_sound()
            self.status_label.setText(f"No speech detected - Click microphone or press {self.get_formatted_shortcut()} to try again")

            # Record failed transcription (no speech)
            if hasattr(self, '_recording_start_time'):
                duration = time.time() - self._recording_start_time
                transcription_time = getattr(self, '_transcription_time', 0.0)
                mode = self.config_manager.get_setting("whisper/mode", "api")

                self.statistics_manager.record_transcription_result(
                    success=False,
                    mode=mode,
                    duration=duration,
                    transcription_time=transcription_time
                )

    def handle_transcription_error(self, error: str):
        """Handle transcription errors"""
        # Play stop sound on error too
        self.sound_manager.play_stop_sound()
        self.status_label.setText(f"Error: {error}")
        print(f"Transcription error: {error}")

        # Record failed transcription
        if hasattr(self, '_recording_start_time'):
            duration = time.time() - self._recording_start_time
            transcription_time = getattr(self, '_transcription_time', 0.0)
            mode = self.config_manager.get_setting("whisper/mode", "api")

            self.statistics_manager.record_transcription_result(
                success=False,
                mode=mode,
                duration=duration,
                transcription_time=transcription_time
            )

    def handle_output_error(self, error: str):
        """Handle output operation errors"""
        self.status_label.setText(f"Output error: {error}")
        print(f"Output error: {error}")

    def update_status(self, message: str):
        """Update status label after transcription is complete"""
        # Play stop sound when transcription is complete
        self.sound_manager.play_stop_sound()

        # Don't show the result on homepage, just reset to ready state
        self.status_label.setText(f"Click microphone or press {self.get_formatted_shortcut()} to start recording")

    def handle_recording_error(self, error: str):
        """Handle recording errors"""
        self.status_label.setText(f"Recording error: {error}")
        print(f"Recording error: {error}")

    def show_settings(self):
        """Show settings dialog"""
        if self.compact_mode:
            dialog = UISettingsDialog(self, self.config_manager)
            dialog.settings_saved.connect(self.load_settings)
            dialog.exec()
        else:
            if not self.settings_dialog:
                # Pass our config manager to ensure settings are shared
                self.settings_dialog = SettingsDialog(self, self.config_manager)
                # Connect to settings saved signal to reload settings when changed
                self.settings_dialog.settings_saved.connect(self.load_settings)
            else:
                # If dialog already exists, refresh device list when opening settings
                if hasattr(self.settings_dialog, 'audio_tab'):
                    self.settings_dialog.audio_tab.refresh_devices()
            self.settings_dialog.exec()

            # Update window manager settings after dialog closes
            if self.window_manager:
                self.window_manager.load_window_settings()

    def show_window_manager(self):
        """Show window manager dialog"""
        dialog = WindowManagerDialog(self, self.config_manager, self.window_manager)
        dialog.settings_saved.connect(self.load_settings)

        # Apply current theme to window manager dialog
        current_theme = self.config_manager.get_setting("ui/theme", "white")
        if hasattr(dialog, 'apply_theme'):
            dialog.apply_theme(current_theme)

        dialog.exec()

    def contextMenuEvent(self, event):
        """Show context menu with application options"""
        context_menu = QMenu(self)

        # Apply theme to context menu
        self._apply_context_menu_theme(context_menu)

        # Settings action
        settings_action = context_menu.addAction("Settings")
        settings_action.setIcon(get_icon('settings', 16))
        settings_action.triggered.connect(self.show_settings)

        # Window Manager action
        window_manager_action = context_menu.addAction("Window Manager")
        window_manager_action.setIcon(get_icon('monitor', 16))
        window_manager_action.triggered.connect(self.show_window_manager)

        context_menu.addSeparator()

        # Exit action
        exit_action = context_menu.addAction("Exit")
        exit_action.setIcon(get_icon('x', 16))
        exit_action.triggered.connect(self.close)

        context_menu.exec(event.globalPos())

    def _apply_context_menu_theme(self, menu):
        """Apply current theme to context menu using unified ThemeManager"""
        current_theme = self.config_manager.get_setting("ui/theme", "white")
        theme_manager = get_theme_manager()
        
        # Use unified menu stylesheet from ThemeManager
        menu_style = theme_manager.get_menu_stylesheet(current_theme)
        menu.setStyleSheet(menu_style)

    def load_settings(self):
        """Load and apply saved settings"""
        try:
            # Load Whisper settings
            whisper_mode = self.config_manager.get_setting("whisper/mode", "api")
            self.whisper_manager.set_mode(whisper_mode)

            if whisper_mode == "api":
                api_key = self.config_manager.get_setting("whisper/api_key", "")
                if api_key:
                    self.whisper_manager.set_api_key(api_key)
                # Load API model setting
                api_model = self.config_manager.get_setting("whisper/api_model")
                if api_model:
                    try:
                        self.whisper_manager.set_api_model(api_model)
                    except ValueError as e:
                        # Show user-friendly error dialog
                        QMessageBox.warning(
                            self,
                            "Invalid API Model",
                            f"The configured API model '{api_model}' is not available.\n\n"
                            f"Error: {e}\n\n"
                            f"Falling back to default model 'gpt-4o-mini-transcribe'.\n"
                            f"Please check your settings to select a valid model.",
                            QMessageBox.StandardButton.Ok
                        )

                        # Fallback to default model and clear invalid config
                        try:
                            self.whisper_manager.set_api_model("gpt-4o-mini-transcribe")
                            self.config_manager.set_setting("whisper/api_model", "gpt-4o-mini-transcribe")
                        except Exception as fallback_error:
                            QMessageBox.critical(
                                self,
                                "Critical Error",
                                f"Failed to set fallback API model: {fallback_error}\n\n"
                                f"Please check your OpenAI API configuration.",
                                QMessageBox.StandardButton.Ok
                            )
                
                # Load API language setting
                api_language = self.config_manager.get_setting("whisper/language", "en")
                if api_language:
                    try:
                        self.whisper_manager.set_api_language(api_language)
                    except ValueError as e:
                        # Invalid language code, fallback to English
                        self.whisper_manager.set_api_language("en")
                        self.config_manager.set_setting("whisper/language", "en")
            else:
                # Local model will be set below in the local model section
                pass

            # Load audio settings
            device_id = self.config_manager.get_setting("audio/device_id")
            if device_id is not None:
                self.audio_manager.set_input_device(device_id)

            # Load sound settings
            sounds_enabled = self.config_manager.get_setting("audio/sounds_enabled", True)
            self.sound_manager.set_sounds_enabled(sounds_enabled)
            # Load UI visualization settings
            show_waveform = self.config_manager.get_setting("ui/show_waveform", True)
            self.microphone.set_show_waveform(bool(show_waveform))

            # Load animation strength setting
            animation_strength = self.config_manager.get_setting("ui/animation_strength", 3.0)
            self.microphone.set_animation_strength(float(animation_strength))

            # Apply compact mode
            compact = bool(self.config_manager.get_setting("ui/compact_mode", False))
            if compact != self.compact_mode:
                self.apply_compact_mode(compact)
            else:
                # Ensure consistent UI after startup
                self.apply_compact_mode(compact)

            # Set local model name if available
            if whisper_mode == "local":
                local_model = self.config_manager.get_setting("whisper/local_model", "")
                if local_model:
                    # Convert old file names to new model names
                    self.whisper_manager.set_local_model(local_model)

            # Apply recording shortcut
            self.apply_hotkey_setting()

            # Update status label with actual shortcut
            if not self.is_recording:
                self.status_label.setText(f"Click microphone or press {self.get_formatted_shortcut()} to start recording")

            # Apply theme
            theme = self.config_manager.get_setting("ui/theme", "white")
            self.apply_theme(theme)

            # Apply custom titlebar setting (requires restart to take effect)
            custom_titlebar = bool(self.config_manager.get_setting("ui/custom_titlebar", True))
            if hasattr(self, 'custom_titlebar_enabled') and custom_titlebar != self.custom_titlebar_enabled:
                # Setting has changed - show popup that restart is required
                self.show_restart_required_popup()

        except Exception as e:
            print(f"Error loading settings: {e}")

    def show_restart_required_popup(self):
        """Show a popup dialog informing user that restart is required for title bar changes"""
        # Get current setting to show specific message
        custom_titlebar = bool(self.config_manager.get_setting("ui/custom_titlebar", True))
        action = "enabled" if custom_titlebar else "disabled"

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Restart Required")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText("Title Bar Setting Changed")
        msg_box.setInformativeText(f"The custom title bar has been {action}. Please restart QuillScribe for the changes to take effect.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Apply theme styling to the message box
        if hasattr(self, 'is_dark') and self.is_dark:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2c2c2c;
                    color: #ffffff;
                }
                QMessageBox QLabel {
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #4A90E2;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #5BA0F2;
                }
            """)
        else:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #ffffff;
                    color: #2c3e50;
                }
                QPushButton {
                    background-color: #4A90E2;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #357ABD;
                }
            """)

        msg_box.exec()

    def get_formatted_shortcut(self) -> str:
        """Get a nicely formatted shortcut string for display"""
        shortcut_text = self.config_manager.get_setting("shortcuts/record_toggle", "Meta+Shift+`")
        if not isinstance(shortcut_text, str) or not shortcut_text:
            shortcut_text = "Meta+Shift+`"

        # Convert to a more user-friendly format
        formatted = shortcut_text.replace("Meta", "Win").replace("+", " + ")
        return f"[{formatted}]"

    def apply_hotkey_setting(self):
        """Register the configured recording shortcut; fallback to app-level shortcut if global fails."""
        # Prevent multiple simultaneous registrations
        if hasattr(self, '_applying_hotkey') and self._applying_hotkey:
            return

        try:
            self._applying_hotkey = True

            # Clear existing app shortcut
            if self._app_shortcut is not None:
                try:
                    self._app_shortcut.activated.disconnect()
                except Exception:
                    pass
                self._app_shortcut.setParent(None)
                self._app_shortcut = None

            shortcut_text = self.config_manager.get_setting("shortcuts/record_toggle", "Meta+Shift+`")
            if not isinstance(shortcut_text, str) or not shortcut_text:
                shortcut_text = "Meta+Shift+`"

            # Try global first on Windows
            registered_globally = False
            if getattr(self, "hotkey_manager", None) is not None:
                try:
                    registered_globally = self.hotkey_manager.register_hotkey(shortcut_text, self.toggle_recording)
                except Exception as e:
                    print(f"Hotkey registration error: {e}")
                    registered_globally = False
        finally:
            self._applying_hotkey = False

        if not registered_globally:
            # Fallback: in-app shortcut (works when app is focused)
            # Map Win->Meta for Qt
            qt_seq_text = shortcut_text.replace("Win+", "Meta+").replace("Windows+", "Meta+")
            if "Meta+" in qt_seq_text and sys.platform == "win32":
                # Many Win+ combos are reserved; provide a safer fallback
                # Use Ctrl+Alt+<last key>
                parts = shortcut_text.split("+")
                last_key = parts[-1].strip() if parts else "F"
                qt_seq_text = f"Ctrl+Alt+{last_key}"
            try:
                self._app_shortcut = QShortcut(QKeySequence(qt_seq_text), self)
                self._app_shortcut.activated.connect(self.toggle_recording)
            except Exception as e:
                print(f"Failed to set app shortcut '{qt_seq_text}': {e}")

    def _get_theme_colors(self, theme_name: str) -> dict:
        """Get theme colors from centralized ThemeManager"""
        theme_manager = get_theme_manager()
        colors = theme_manager.get_theme_colors(theme_name)
        is_dark = theme_manager.is_dark_theme()
        
        # Add computed colors for backward compatibility
        if is_dark:
            colors["text_primary"] = "#ffffff"
            colors["text_secondary"] = "#e9ecef"
            colors["border"] = "#495057"
        else:
            colors["text_primary"] = "#212529"
            colors["text_secondary"] = "#495057"
            colors["border"] = "#dee2e6"
        
        return colors


    def apply_theme(self, theme_name):
        """
        Apply the selected theme to the main window background and text colors.
        
        This method is called:
        1. During window initialization (load_settings)
        2. When settings are saved (via settings_saved signal)
        3. Automatically via theme_changed signal for live updates
        
        The signal-based approach ensures immediate visual feedback when
        theme is changed in settings dialog, without requiring dialog close.
        """
        # Prevent recursion during theme application
        if self._applying_theme:
            return
        
        self._applying_theme = True
        try:
            # Get theme manager for querying dark/light status
            theme_manager = get_theme_manager()
            
            # Update theme manager if theme is different
            if theme_manager.get_current_theme() != theme_name:
                # Clear recursion guard before signaling; the signal handler should apply the theme
                self._applying_theme = False
                theme_manager.set_theme(theme_name)
                # Theme will be applied via signal, exit to avoid duplication
                return
            
            # Get colors from centralized theme manager
            colors = self._get_theme_colors(theme_name)
            primary_color = colors["primary"]
            secondary_color = colors["secondary"]

            # Get dark theme status from theme manager
            self.is_dark = theme_manager.is_dark_theme()

            if self.is_dark:
                text_primary = "#ffffff"
                text_secondary = "#e0e0e0"
                text_muted = "#b0b0b0"
            else:
                text_primary = "#2c3e50"
                text_secondary = "#495057"
                text_muted = "#6c757d"

            self.setStyleSheet(f"""
                QMainWindow {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {primary_color}, stop:1 {secondary_color});
                    color: {text_primary};
                }}
                QWidget#centralWidget {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {primary_color}, stop:1 {secondary_color});
                    color: {text_primary};
                }}
            """)

            # Apply theme to settings button
            self.settings_button.apply_theme(self.is_dark, self.compact_mode)
            self.settings_button.setIcon(get_themed_button_icon('settings', 16, self.is_dark))

            # Apply themed icons to all components
            theme_manager.apply_icons_to_widget(self)

            # Update tray menu theme
            if hasattr(self, 'tray_manager') and self.tray_manager:
                self.tray_manager.update_theme()


            # Update text colors for existing widgets
            if hasattr(self, 'title_label'):
                self.title_label.setStyleSheet(f"""
                    QLabel {{
                        color: {text_primary};
                        font-size: 28px;
                        font-weight: 300;
                        margin-bottom: 10px;
                        background-color: transparent;
                        text-align: center;
                    }}
                """)

            # Update custom titlebar colors
            if hasattr(self, 'custom_titlebar') and self.custom_titlebar is not None:
                self.custom_titlebar.apply_theme(self.is_dark)

            if hasattr(self, 'status_label'):
                font_size = "11px" if self.compact_mode else "14px"
                margin = "4px" if self.compact_mode else "10px"
                self.status_label.setStyleSheet(f"""
                    QLabel {{
                        color: {text_muted};
                        font-size: {font_size};
                        margin-top: {margin};
                        background-color: transparent;
                    }}
                """)
        
        except Exception as e:
            print(f"Error applying theme '{theme_name}': {e}")
            # Attempt fallback to default theme
            if theme_name != "white":
                try:
                    theme_manager = get_theme_manager()
                    theme_manager.set_theme("white")
                except Exception:
                    pass  # Avoid infinite recursion
        finally:
            self._applying_theme = False

    def _on_theme_changed(self, theme_name: str, is_dark: bool):
        """Named slot for theme_changed signal to allow safe connect/disconnect."""
        # Safe-guard: only apply if object is still alive
        try:
            self.apply_theme(theme_name)
        except RuntimeError:
            # Widget may have been destroyed; ignore
            pass

    def apply_compact_mode(self, enabled: bool):
        """Apply or remove super-compact UI mode."""
        self.compact_mode = enabled
        if enabled:
            # Ensure custom titlebar is visible in compact mode
            if hasattr(self, 'custom_titlebar') and self.custom_titlebar is not None:
                self.custom_titlebar.setVisible(True)
            # Slightly larger to allow bigger mic view box and bottom-aligned settings
            self.setFixedSize(220, 272)  # Increased height to account for titlebar
            # Tight spacing
            self.main_layout.setContentsMargins(8, 8, 8, 8)
            self.main_layout.setSpacing(6)
            # Hide big title, shrink mic and labels, enlarge viewbox by using more space
            self.title_label.setVisible(False)
            # Bigger microphone animation view box in compact mode
            self.microphone.setFixedSize(150, 150)
            # Completely remove text result/status display in compact mode
            self.status_label.setVisible(False)
            self.status_label.setStyleSheet("QLabel { color: #6c757d; font-size: 11px; margin-top: 4px; }")
            # Shrink settings button
            self.settings_button.apply_theme(self.is_dark, True)
            # Re-show to apply window flag changes
            self.show()
            # Reapply always-on-top if needed
            if hasattr(self, 'window_manager') and self.window_manager:
                self.window_manager.reapply_always_on_top()
        else:
            # Show custom titlebar in normal mode
            if hasattr(self, 'custom_titlebar') and self.custom_titlebar is not None:
                self.custom_titlebar.setVisible(True)
            # Keep frameless window flags for custom titlebar
            self.setFixedSize(400, 532)  # Slightly taller to account for custom titlebar
            self.main_layout.setContentsMargins(40, 20, 40, 40)
            self.main_layout.setSpacing(30)
            self.title_label.setVisible(True)
            self.microphone.setFixedSize(200, 200)
            self.status_label.setVisible(True)
            self.status_label.setStyleSheet("QLabel { color: #6c757d; font-size: 14px; margin-top: 10px; }")
            # Restore settings button default style
            self.settings_button.apply_theme(self.is_dark, False)
            # Re-show to apply window flag changes
            self.show()
            # Reapply always-on-top if needed
            if hasattr(self, 'window_manager') and self.window_manager:
                self.window_manager.reapply_always_on_top()

    def install_drag_filters(self):
        """Install event filters to enable drag-anywhere in compact mode."""
        try:
            # Central widget and all children
            if self.centralWidget() is not None:
                self.centralWidget().installEventFilter(self)
            for child in self.findChildren(QWidget):
                child.installEventFilter(self)
        except Exception:
            pass


    def closeEvent(self, event):
        """Handle application close event"""
        # Check if we're forcing exit (from tray menu)
        if hasattr(self, '_force_exit') and self._force_exit:
            # Proceed with actual close
            self._perform_exit(event)
            return

        try:
            minimize_on_close = bool(self.config_manager.get_setting("ui/minimize_on_close", True))
            minimize_to_tray = bool(self.config_manager.get_setting("ui/minimize_to_tray", False))
        except Exception:
            minimize_on_close = True
            minimize_to_tray = False

        # Priority: minimize to tray > minimize on close > exit
        if minimize_to_tray:
            event.ignore()
            self.hide_to_tray()
            return
        elif minimize_on_close:
            event.ignore()
            self.showMinimized()
            return

        # Proceed with actual close
        self._perform_exit(event)

    def _perform_exit(self, event=None):
        """Perform the actual application exit"""
        if self._exit_in_progress or self._exit_completed:
            return
        
        self._exit_in_progress = True
        try:
            # Record session end
            try:
                if hasattr(self, '_statistics_manager') and self._statistics_manager is not None:
                    self.statistics_manager.record_session_end()
            except Exception as e:
                print(f"Warning: Failed to record session end: {e}")

            if self.is_recording:
                self.stop_recording()
            self.audio_manager.stop_monitoring()
            self.sound_manager.cleanup()

            # Cleanup hotkey manager first (this removes the native event filter)
            if hasattr(self, "hotkey_manager") and self.hotkey_manager is not None:
                try:
                    self.hotkey_manager.cleanup()
                    self.hotkey_manager = None
                except Exception as e:
                    print(f"Warning: Error cleaning up hotkey manager: {e}")

            # Cleanup tray manager before exit
            if self.tray_manager:
                try:
                    self.tray_manager.cleanup()
                    self.tray_manager = None
                except Exception as e:
                    print(f"Warning: Error cleaning up tray manager: {e}")

            # Cleanup window manager before exit
            if self.window_manager:
                try:
                    self.window_manager.cleanup()
                    self.window_manager = None
                except Exception as e:
                    print(f"Warning: Error cleaning up window manager: {e}")

            # Save window position
            try:
                pos = self.pos()
                self.config_manager.set_setting("ui/window_x", pos.x())
                self.config_manager.set_setting("ui/window_y", pos.y())
                self.config_manager.save_settings()
            except Exception as e:
                print(f"Warning: Error saving settings: {e}")

            # Disconnect theme change listener to avoid calls on deleted objects
            try:
                theme_manager = get_theme_manager()
                theme_manager.theme_changed.disconnect(self._on_theme_changed)
            except Exception:
                pass

        except Exception as e:
            print(f"Error during exit cleanup: {e}")
        finally:
            self._exit_completed = True
            self._exit_in_progress = False
            if event is not None:
                event.accept()
            # Force application quit
            app = QApplication.instance()
            if app:
                app.quit()

    # Drag-anywhere support for compact mode
    def mousePressEvent(self, event):
        if self.compact_mode and event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            try:
                global_pos = event.globalPosition().toPoint()
            except Exception:
                global_pos = event.globalPos()
            self._drag_offset = global_pos - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.compact_mode and self._drag_active and event.buttons() & Qt.MouseButton.LeftButton:
            try:
                global_pos = event.globalPosition().toPoint()
            except Exception:
                global_pos = event.globalPos()
            self.move(global_pos - self._drag_offset)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.compact_mode and event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = False
        super().mouseReleaseEvent(event)

    def eventFilter(self, obj, event):
        """Enable dragging from any child widget while in compact mode."""
        if not self.compact_mode:
            return super().eventFilter(obj, event)
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            try:
                global_pos = event.globalPosition().toPoint()
            except Exception:
                global_pos = event.globalPos()
            self._drag_offset = global_pos - self.frameGeometry().topLeft()
            return False
        if event.type() == QEvent.Type.MouseMove and self._drag_active and event.buttons() & Qt.MouseButton.LeftButton:
            try:
                global_pos = event.globalPosition().toPoint()
            except Exception:
                global_pos = event.globalPos()
            self.move(global_pos - self._drag_offset)
            return True
        if event.type() == QEvent.Type.MouseButtonRelease:
            self._drag_active = False
            return False
        return super().eventFilter(obj, event)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set up signal handling for graceful shutdown
    import signal
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        app.quit()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Windows-specific taskbar configuration FIRST (before anything else)
    if sys.platform == "win32" and ctypes is not None:
        try:
            # Set Windows App Model ID BEFORE setting icon for proper taskbar grouping
            from ctypes import windll
            windll.shell32.SetCurrentProcessExplicitAppUserModelID("QuillScribe.VoiceTranscription.1.0")
        except Exception:
            pass

    # Set application properties
    app.setApplicationName("QuillScribe")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("QuillScribe")

    # Set application icon BEFORE creating windows (critical for Windows taskbar)
    try:
        from pathlib import Path
        # Handle both development and frozen executable environments
        base_path = get_base_path()
        if base_path is not None:
            # Running as frozen executable (Nuitka)
            ico_path = base_path / "app_logo.ico"
        else:
            # Running from source
            ico_path = Path(__file__).parent / "app_logo.ico"

        if ico_path.exists():
            icon = QIcon(str(ico_path))
            if not icon.isNull():
                app.setWindowIcon(icon)
    except Exception:
        pass

    # Ensure theme manager has the saved theme BEFORE creating windows so
    # any widget created by windows can query it safely without falling back
    # to the default theme.
    try:
        cfg = ConfigManager()
        current_theme = cfg.get_setting("ui/theme", "white")
        theme_manager = get_theme_manager()
        # set_theme will emit signal which connected windows can listen to
        theme_manager.set_theme(current_theme)
    except Exception:
        # Do not fail startup if theme application fails
        pass

    # Create and show main window
    window = QuillScribeMainWindow()

    # Connect app quit signal to window cleanup
    app.aboutToQuit.connect(lambda: window._perform_exit())

    window.show()

    # Force taskbar icon refresh on Windows after window is shown
    window._refresh_taskbar_icon()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
