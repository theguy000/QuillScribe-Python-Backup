"""
Window Management System for QuillScribe
Handles window positioning, monitor awareness, snap-to-edges, and always-on-top functionality
"""

import sys
from typing import Optional
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QObject, Signal, QPoint, QSize, QTimer

try:
    if sys.platform == "win32":
        import ctypes
        user32 = ctypes.windll.user32  # type: ignore
    else:
        user32 = None
except ImportError:
    user32 = None


class WindowManager(QObject):
    """Manages window positioning, monitor awareness, and window behavior"""

    # Signals
    window_moved = Signal(QPoint)
    window_resized = Signal(QSize)
    monitor_changed = Signal(str)
    snap_performed = Signal(str)  # edge name

    def __init__(self, window: QWidget, config_manager, parent=None):
        super().__init__(parent)
        self.window = window
        self.config_manager = config_manager
        self.current_monitor_id = None
        self.snap_threshold = 20  # pixels
        self.snap_enabled = True
        self.always_on_top = False

        # Monitor tracking
        self.monitors = {}
        self.update_monitor_info()

        # Snap detection timer
        self.snap_timer = QTimer()
        self.snap_timer.setSingleShot(True)
        self.snap_timer.timeout.connect(self._check_snap_position)

        # Connect to window events
        self.window.installEventFilter(self)

        # Load settings
        self.load_window_settings()

    def update_monitor_info(self):
        """Update information about available monitors"""
        self.monitors.clear()
        app = QApplication.instance()

        for i, screen in enumerate(app.screens()):
            monitor_id = f"monitor_{i}_{screen.name()}"
            self.monitors[monitor_id] = {
                'screen': screen,
                'geometry': screen.geometry(),
                'available_geometry': screen.availableGeometry(),
                'name': screen.name(),
                'index': i
            }

    def get_current_monitor(self) -> Optional[str]:
        """Get the monitor ID where the window is currently located"""
        window_center = self.window.geometry().center()

        for monitor_id, monitor_info in self.monitors.items():
            if monitor_info['geometry'].contains(window_center):
                return monitor_id

        # Fallback to primary monitor
        primary_screen = QApplication.primaryScreen()
        for monitor_id, monitor_info in self.monitors.items():
            if monitor_info['screen'] == primary_screen:
                return monitor_id

        return None

    def save_window_position(self):
        """Save window position for the current monitor"""
        current_monitor = self.get_current_monitor()
        if not current_monitor:
            return

        pos = self.window.pos()
        size = self.window.size()

        # Save position relative to monitor
        monitor_info = self.monitors[current_monitor]
        monitor_geometry = monitor_info['geometry']

        relative_pos = QPoint(
            pos.x() - monitor_geometry.x(),
            pos.y() - monitor_geometry.y()
        )

        # Save to config
        self.config_manager.set_setting(f"window_positions/{current_monitor}/x", relative_pos.x())
        self.config_manager.set_setting(f"window_positions/{current_monitor}/y", relative_pos.y())
        self.config_manager.set_setting(f"window_positions/{current_monitor}/width", size.width())
        self.config_manager.set_setting(f"window_positions/{current_monitor}/height", size.height())

        # Save current monitor
        self.config_manager.set_setting("ui/last_monitor", current_monitor)

    def restore_window_position(self):
        """Restore window position for the current or last used monitor"""
        # Try to restore to last used monitor first
        last_monitor = self.config_manager.get_setting("ui/last_monitor", None)

        # Check if last monitor still exists
        if last_monitor and last_monitor in self.monitors:
            target_monitor = last_monitor
        else:
            # Fallback to current monitor or primary
            target_monitor = self.get_current_monitor()
            if not target_monitor:
                # Use primary monitor as final fallback
                primary_screen = QApplication.primaryScreen()
                for monitor_id, monitor_info in self.monitors.items():
                    if monitor_info['screen'] == primary_screen:
                        target_monitor = monitor_id
                        break

        if not target_monitor:
            return

        # Get saved position for this monitor
        saved_x = self.config_manager.get_setting(f"window_positions/{target_monitor}/x", None)
        saved_y = self.config_manager.get_setting(f"window_positions/{target_monitor}/y", None)
        saved_width = self.config_manager.get_setting(f"window_positions/{target_monitor}/width", None)
        saved_height = self.config_manager.get_setting(f"window_positions/{target_monitor}/height", None)

        if saved_x is not None and saved_y is not None:
            monitor_info = self.monitors[target_monitor]
            monitor_geometry = monitor_info['geometry']

            # Convert relative position to absolute
            absolute_pos = QPoint(
                monitor_geometry.x() + saved_x,
                monitor_geometry.y() + saved_y
            )

            # Ensure window is within monitor bounds
            available_geometry = monitor_info['available_geometry']
            if available_geometry.contains(absolute_pos):
                self.window.move(absolute_pos)

                # Restore size if saved
                if saved_width and saved_height:
                    self.window.resize(saved_width, saved_height)

    def snap_to_edge(self, edge: str):
        """Snap window to specified edge of current monitor"""
        current_monitor = self.get_current_monitor()
        if not current_monitor:
            return

        monitor_info = self.monitors[current_monitor]
        available_geometry = monitor_info['available_geometry']
        window_size = self.window.size()

        if edge == "left":
            new_pos = QPoint(available_geometry.left(), available_geometry.top())
        elif edge == "right":
            new_pos = QPoint(
                available_geometry.right() - window_size.width(),
                available_geometry.top()
            )
        elif edge == "top":
            new_pos = QPoint(available_geometry.left(), available_geometry.top())
        elif edge == "bottom":
            new_pos = QPoint(
                available_geometry.left(),
                available_geometry.bottom() - window_size.height()
            )
        elif edge == "center":
            new_pos = QPoint(
                available_geometry.center().x() - window_size.width() // 2,
                available_geometry.center().y() - window_size.height() // 2
            )
        else:
            return

        self.window.move(new_pos)
        self.snap_performed.emit(edge)

    def _check_snap_position(self):
        """Check if window should snap to edges"""
        if not self.snap_enabled:
            return

        current_monitor = self.get_current_monitor()
        if not current_monitor:
            return

        monitor_info = self.monitors[current_monitor]
        available_geometry = monitor_info['available_geometry']
        window_pos = self.window.pos()
        window_size = self.window.size()

        # Check proximity to edges
        left_distance = abs(window_pos.x() - available_geometry.left())
        right_distance = abs((window_pos.x() + window_size.width()) - available_geometry.right())
        top_distance = abs(window_pos.y() - available_geometry.top())
        bottom_distance = abs((window_pos.y() + window_size.height()) - available_geometry.bottom())

        # Snap to closest edge if within threshold
        if left_distance <= self.snap_threshold:
            self.snap_to_edge("left")
        elif right_distance <= self.snap_threshold:
            self.snap_to_edge("right")
        elif top_distance <= self.snap_threshold:
            self.snap_to_edge("top")
        elif bottom_distance <= self.snap_threshold:
            self.snap_to_edge("bottom")

    def set_always_on_top(self, enabled: bool):
        """Set always-on-top behavior"""
        self.always_on_top = enabled

        # Save setting first
        self.config_manager.set_setting("ui/always_on_top", enabled)

        # Apply the setting
        self._apply_always_on_top()

        # Debug output
        print(f"Always-on-top set to: {enabled}")
        from PySide6.QtCore import Qt
        current_flags = self.window.windowFlags()
        has_topmost = bool(current_flags & Qt.WindowType.WindowStaysOnTopHint)
        print(f"Window flags after change - has WindowStaysOnTopHint: {has_topmost}")

    def _apply_always_on_top(self):
        """Apply the always-on-top setting to the window"""
        if sys.platform == "win32" and user32 is not None:
            try:
                hwnd = int(self.window.winId())
                # Windows constants
                HWND_TOPMOST = -1
                HWND_NOTOPMOST = -2
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001

                if self.always_on_top:
                    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                else:
                    user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                return  # Windows API succeeded, no need for Qt approach
            except Exception as e:
                print(f"Warning: Could not set always-on-top via Windows API: {e}")
                # Fall through to Qt approach

        # Qt-based approach for all platforms (including Windows fallback)
        from PySide6.QtCore import Qt
        current_flags = self.window.windowFlags()

        if self.always_on_top:
            new_flags = current_flags | Qt.WindowType.WindowStaysOnTopHint
        else:
            new_flags = current_flags & ~Qt.WindowType.WindowStaysOnTopHint

        # Only update flags if they actually changed
        if new_flags != current_flags:
            # Store current visibility state
            was_visible = self.window.isVisible()

            self.window.setWindowFlags(new_flags)

            # Restore visibility state
            if was_visible:
                self.window.show()

    def reapply_always_on_top(self):
        """Reapply always-on-top setting (useful after window flag changes)"""
        self._apply_always_on_top()

    def set_snap_enabled(self, enabled: bool):
        """Enable or disable snap-to-edges functionality"""
        self.snap_enabled = enabled
        self.config_manager.set_setting("ui/snap_to_edges", enabled)

    def set_snap_threshold(self, threshold: int):
        """Set snap threshold in pixels"""
        self.snap_threshold = max(5, min(50, threshold))  # Clamp between 5-50 pixels
        self.config_manager.set_setting("ui/snap_threshold", self.snap_threshold)

    def is_always_on_top(self) -> bool:
        """Check if window is currently set to always-on-top"""
        if sys.platform == "win32" and user32 is not None:
            try:
                hwnd = int(self.window.winId())
                # Get extended window style
                ex_style = user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE
                WS_EX_TOPMOST = 0x00000008
                return bool(ex_style & WS_EX_TOPMOST)
            except Exception:
                pass

        # Qt-based check
        from PySide6.QtCore import Qt
        flags = self.window.windowFlags()
        return bool(flags & Qt.WindowType.WindowStaysOnTopHint)

    def load_window_settings(self):
        """Load window management settings"""
        self.always_on_top = self.config_manager.get_setting("ui/always_on_top", False)
        self.snap_enabled = self.config_manager.get_setting("ui/snap_to_edges", True)
        self.snap_threshold = self.config_manager.get_setting("ui/snap_threshold", 20)

        # Apply always on top setting
        if self.always_on_top:
            self.set_always_on_top(True)

    def eventFilter(self, obj, event):
        """Handle window events for position tracking and snapping"""
        if obj == self.window:
            if event.type() == event.Type.Move:
                # Check for monitor change
                new_monitor = self.get_current_monitor()
                if new_monitor != self.current_monitor_id:
                    self.current_monitor_id = new_monitor
                    if new_monitor:
                        self.monitor_changed.emit(new_monitor)

                # Start snap timer
                if self.snap_enabled:
                    self.snap_timer.start(100)  # 100ms delay

                self.window_moved.emit(self.window.pos())

            elif event.type() == event.Type.Resize:
                self.window_resized.emit(self.window.size())

        return super().eventFilter(obj, event)

    def cleanup(self):
        """Clean up window manager resources"""
        self.save_window_position()
        self.snap_timer.stop()
        if self.window:
            self.window.removeEventFilter(self)
