"""
Windows Global Hotkey Manager
Handles global hotkey registration and event filtering for Windows
"""

import sys
import time
import ctypes
from typing import Optional, Dict, Set, Tuple

from PySide6.QtCore import QAbstractNativeEventFilter, QAbstractEventDispatcher
from PySide6.QtWidgets import QMainWindow

try:
    from ctypes import wintypes  # type: ignore
except Exception:
    wintypes = None

# Windows hotkey constants
WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008


class WindowsHotkeyEventFilter(QAbstractNativeEventFilter):
    """Native event filter to listen for WM_HOTKEY messages on Windows."""

    def __init__(self, id_to_callback: Dict[int, callable]):
        super().__init__()
        self.id_to_callback = id_to_callback
        # Cache the pointer type to avoid repeated creation in the event loop
        if ctypes is not None and wintypes is not None:
            self.MSG_PTR = ctypes.POINTER(wintypes.MSG)
        else:
            self.MSG_PTR = None

    def nativeEventFilter(self, eventType, message):  # noqa: N802 (Qt signature)
        if self.MSG_PTR is None or sys.platform != "win32":
            return False, 0
        try:
            if eventType == "windows_generic_MSG" or eventType == "windows_dispatcher_MSG":
                # Handle different types of message parameter that PySide6 might pass
                if hasattr(message, '__int__'):
                    # If message is an integer pointer
                    msg_ptr = ctypes.cast(int(message), self.MSG_PTR)
                elif hasattr(message, 'value'):
                    # If message is a sip.voidptr
                    msg_ptr = ctypes.cast(message.value, self.MSG_PTR)
                else:
                    # Try direct cast as fallback
                    msg_ptr = ctypes.cast(message, self.MSG_PTR)

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
        self.id_to_callback: Dict[int, callable] = {}
        self.registered_ids: Set[int] = set()
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

    def _parse_shortcut(self, shortcut_text: str) -> Optional[Tuple[int, int]]:
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