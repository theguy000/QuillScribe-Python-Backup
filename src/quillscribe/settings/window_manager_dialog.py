"""
Window Manager Dialog
Dedicated dialog for window management features
"""

"""
Window Manager Dialog
Dedicated dialog for window management features
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal, QSize

from ..config_manager import ConfigManager
from ..icon_manager import get_button_icon
from .ui_components import ModernGroupBox
from .modern_buttons import ModernButton, ButtonVariant
from .modern_widgets import ModernCheckBox


class WindowManagerDialog(QDialog):
    """Dedicated window for Window Manager features and controls."""
    settings_saved = Signal()

    def __init__(self, parent=None, config_manager=None, window_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager if config_manager is not None else ConfigManager()
        self.window_manager = window_manager
        self._drag_active = False
        self._drag_offset = None
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.setWindowTitle("Window Manager")
        self.setFixedSize(400, 350)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Window Management")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # Window Behavior Group
        behavior_group = ModernGroupBox("Window Behavior")
        behavior_layout = QVBoxLayout(behavior_group)

        # Always on top
        self.always_on_top_checkbox = ModernCheckBox("Always on Top")
        self.always_on_top_checkbox.setIcon(get_button_icon('zap', 16))  # Use zap icon instead of pin
        self.always_on_top_checkbox.setIconSize(QSize(16, 16))
        behavior_layout.addWidget(self.always_on_top_checkbox)

        # Snap to edges
        self.snap_to_edges_checkbox = ModernCheckBox("Snap to Screen Edges")
        self.snap_to_edges_checkbox.setIcon(get_button_icon('dashboard', 16))  # Use dashboard icon instead of grid
        self.snap_to_edges_checkbox.setIconSize(QSize(16, 16))
        behavior_layout.addWidget(self.snap_to_edges_checkbox)

        layout.addWidget(behavior_group)

        # Window Positioning Group
        positioning_group = ModernGroupBox("Window Positioning")
        positioning_layout = QVBoxLayout(positioning_group)

        # Quick position buttons
        position_buttons_layout = QHBoxLayout()

        self.snap_left_btn = ModernButton("Left", variant=ButtonVariant.SECONDARY)
        self.snap_left_btn.setIcon(get_button_icon('arrow-left', 16))
        self.snap_left_btn.clicked.connect(lambda: self._snap_to_edge("left"))
        position_buttons_layout.addWidget(self.snap_left_btn)

        self.snap_center_btn = ModernButton("Center", variant=ButtonVariant.SECONDARY)
        self.snap_center_btn.setIcon(get_button_icon('target', 16))
        self.snap_center_btn.clicked.connect(lambda: self._snap_to_edge("center"))
        position_buttons_layout.addWidget(self.snap_center_btn)

        self.snap_right_btn = ModernButton("Right", variant=ButtonVariant.SECONDARY)
        self.snap_right_btn.setIcon(get_button_icon('arrow-right', 16))
        self.snap_right_btn.clicked.connect(lambda: self._snap_to_edge("right"))
        position_buttons_layout.addWidget(self.snap_right_btn)

        positioning_layout.addLayout(position_buttons_layout)

        # Monitor info
        self.monitor_info_label = QLabel("Current Monitor: Detecting...")
        self.monitor_info_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        positioning_layout.addWidget(self.monitor_info_label)

        layout.addWidget(self.monitor_info_label)

        # Status Group
        status_group = ModernGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel("Always-on-top status: Checking...")
        self.status_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        status_layout.addWidget(self.status_label)

        # Test button
        self.test_btn = ModernButton("Test Always-on-Top", variant=ButtonVariant.SECONDARY)
        self.test_btn.setIcon(get_button_icon('eye', 16))
        self.test_btn.clicked.connect(self._test_always_on_top)
        status_layout.addWidget(self.test_btn)

        layout.addWidget(status_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = ModernButton("Save", variant=ButtonVariant.PRIMARY)
        self.save_btn.setIcon(get_button_icon('check', 16))
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = ModernButton("Cancel", variant=ButtonVariant.GHOST)
        self.cancel_btn.setIcon(get_button_icon('x', 16))
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        # Connect window manager signals if available
        if self.window_manager:
            self.window_manager.monitor_changed.connect(self._update_monitor_info)
            self._update_monitor_info()

    def _snap_to_edge(self, edge: str):
        """Snap main window to specified edge"""
        if self.window_manager:
            self.window_manager.snap_to_edge(edge)

    def _update_monitor_info(self):
        """Update monitor information display"""
        if self.window_manager:
            current_monitor = self.window_manager.get_current_monitor()
            if current_monitor and current_monitor in self.window_manager.monitors:
                monitor_info = self.window_manager.monitors[current_monitor]
                monitor_name = monitor_info.get('name', 'Unknown')
                self.monitor_info_label.setText(f"Current Monitor: {monitor_name}")
            else:
                self.monitor_info_label.setText("Current Monitor: Unknown")

        # Update always-on-top status
        self._update_status()

    def _update_status(self):
        """Update always-on-top status display"""
        if self.window_manager:
            is_topmost = self.window_manager.is_always_on_top()
            status_text = "Active" if is_topmost else "Inactive"
            self.status_label.setText(f"Always-on-top status: {status_text}")
        else:
            self.status_label.setText("Always-on-top status: Window manager not available")

    def _test_always_on_top(self):
        """Test always-on-top functionality"""
        if self.window_manager:
            # Toggle always-on-top temporarily for testing
            current_state = self.always_on_top_checkbox.isChecked()
            self.window_manager.set_always_on_top(not current_state)

            # Update status
            self._update_status()

            # Show message
            from PySide6.QtWidgets import QMessageBox
            is_topmost = self.window_manager.is_always_on_top()
            status = "enabled" if is_topmost else "disabled"
            QMessageBox.information(self, "Always-on-Top Test",
                                  f"Always-on-top is now {status}.\n"
                                  f"Try switching to another window to test.\n"
                                  f"Click Save to keep this setting.")
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Test Failed", "Window manager is not available.")

    def load_settings(self):
        """Load window management settings"""
        always_on_top = bool(self.config_manager.get_setting("ui/always_on_top", False))
        self.always_on_top_checkbox.setChecked(always_on_top)

        snap_to_edges = bool(self.config_manager.get_setting("ui/snap_to_edges", True))
        self.snap_to_edges_checkbox.setChecked(snap_to_edges)

        # Update status display
        self._update_status()

    def save_settings(self):
        """Save window management settings"""
        # Save settings
        self.config_manager.set_setting("ui/always_on_top", self.always_on_top_checkbox.isChecked())
        self.config_manager.set_setting("ui/always_on_top", self.always_on_top_checkbox.isChecked())

        # Apply settings to window manager
        if self.window_manager:
            self.window_manager.set_always_on_top(self.always_on_top_checkbox.isChecked())
from .ui_components import ModernGroupBox
from .modern_buttons import ModernButton, ButtonVariant
from .modern_widgets import ModernCheckBox


class WindowManagerDialog(QDialog):
    """Dedicated window for Window Manager features and controls."""
    settings_saved = Signal()

    def __init__(self, parent=None, config_manager=None, window_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager if config_manager is not None else ConfigManager()
        self.window_manager = window_manager
        self._drag_active = False
        self._drag_offset = None
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.setWindowTitle("Window Manager")
        self.setFixedSize(400, 350)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Window Management")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # Window Behavior Group
        behavior_group = ModernGroupBox("Window Behavior")
        behavior_layout = QVBoxLayout(behavior_group)

        # Always on top
        self.always_on_top_checkbox = ModernCheckBox("Always on Top")
        self.always_on_top_checkbox.setIcon(get_button_icon('zap', 16))  # Use zap icon instead of pin
        self.always_on_top_checkbox.setIconSize(QSize(16, 16))
        behavior_layout.addWidget(self.always_on_top_checkbox)

        # Snap to edges
        self.snap_to_edges_checkbox = ModernCheckBox("Snap to Screen Edges")
        self.snap_to_edges_checkbox.setIcon(get_button_icon('dashboard', 16))  # Use dashboard icon instead of grid
        self.snap_to_edges_checkbox.setIconSize(QSize(16, 16))
        behavior_layout.addWidget(self.snap_to_edges_checkbox)

        layout.addWidget(behavior_group)

        # Window Positioning Group
        positioning_group = ModernGroupBox("Window Positioning")
        positioning_layout = QVBoxLayout(positioning_group)

        # Quick position buttons
        position_buttons_layout = QHBoxLayout()

        self.snap_left_btn = ModernButton("Left", variant=ButtonVariant.SECONDARY)
        self.snap_left_btn.setIcon(get_button_icon('arrow-left', 16))
        self.snap_left_btn.clicked.connect(lambda: self._snap_to_edge("left"))
        position_buttons_layout.addWidget(self.snap_left_btn)

        self.snap_center_btn = ModernButton("Center", variant=ButtonVariant.SECONDARY)
        self.snap_center_btn.setIcon(get_button_icon('target', 16))
        self.snap_center_btn.clicked.connect(lambda: self._snap_to_edge("center"))
        position_buttons_layout.addWidget(self.snap_center_btn)

        self.snap_right_btn = ModernButton("Right", variant=ButtonVariant.SECONDARY)
        self.snap_right_btn.setIcon(get_button_icon('arrow-right', 16))
        self.snap_right_btn.clicked.connect(lambda: self._snap_to_edge("right"))
        position_buttons_layout.addWidget(self.snap_right_btn)

        positioning_layout.addLayout(position_buttons_layout)

        # Monitor info
        self.monitor_info_label = QLabel("Current Monitor: Detecting...")
        self.monitor_info_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        positioning_layout.addWidget(self.monitor_info_label)

        layout.addWidget(positioning_group)

        # Status Group
        status_group = ModernGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel("Always-on-top status: Checking...")
        self.status_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        status_layout.addWidget(self.status_label)

        # Test button
        self.test_btn = ModernButton("Test Always-on-Top", variant=ButtonVariant.SECONDARY)
        self.test_btn.setIcon(get_button_icon('eye', 16))
        self.test_btn.clicked.connect(self._test_always_on_top)
        status_layout.addWidget(self.test_btn)

        layout.addWidget(status_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = ModernButton("Save", variant=ButtonVariant.PRIMARY)
        self.save_btn.setIcon(get_button_icon('check', 16))
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = ModernButton("Cancel", variant=ButtonVariant.GHOST)
        self.cancel_btn.setIcon(get_button_icon('x', 16))
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        # Connect window manager signals if available
        if self.window_manager:
            self.window_manager.monitor_changed.connect(self._update_monitor_info)
            self._update_monitor_info()

    def _snap_to_edge(self, edge: str):
        """Snap main window to specified edge"""
        if self.window_manager:
            self.window_manager.snap_to_edge(edge)

    def _update_monitor_info(self):
        """Update monitor information display"""
        if self.window_manager:
            current_monitor = self.window_manager.get_current_monitor()
            if current_monitor and current_monitor in self.window_manager.monitors:
                monitor_info = self.window_manager.monitors[current_monitor]
                monitor_name = monitor_info.get('name', 'Unknown')
                self.monitor_info_label.setText(f"Current Monitor: {monitor_name}")
            else:
                self.monitor_info_label.setText("Current Monitor: Unknown")

        # Update always-on-top status
        self._update_status()

    def _update_status(self):
        """Update always-on-top status display"""
        if self.window_manager:
            is_topmost = self.window_manager.is_always_on_top()
            status_text = "Active" if is_topmost else "Inactive"
            self.status_label.setText(f"Always-on-top status: {status_text}")
        else:
            self.status_label.setText("Always-on-top status: Window manager not available")

    def _test_always_on_top(self):
        """Test always-on-top functionality"""
        if self.window_manager:
            # Toggle always-on-top temporarily for testing
            current_state = self.always_on_top_checkbox.isChecked()
            self.window_manager.set_always_on_top(not current_state)

            # Update status
            self._update_status()

            # Show message
            from PySide6.QtWidgets import QMessageBox
            is_topmost = self.window_manager.is_always_on_top()
            status = "enabled" if is_topmost else "disabled"
            QMessageBox.information(self, "Always-on-Top Test",
                                  f"Always-on-top is now {status}.\n"
                                  f"Try switching to another window to test.\n"
                                  f"Click Save to keep this setting.")
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Test Failed", "Window manager is not available.")

    def load_settings(self):
        """Load window management settings"""
        always_on_top = bool(self.config_manager.get_setting("ui/always_on_top", False))
        self.always_on_top_checkbox.setChecked(always_on_top)

        snap_to_edges = bool(self.config_manager.get_setting("ui/snap_to_edges", True))
        self.snap_to_edges_checkbox.setChecked(snap_to_edges)

        # Update status display
        self._update_status()

    def save_settings(self):
        """Save window management settings"""
        from ..managers import get_theme_manager
        theme_manager = get_theme_manager()
        colors = theme_manager.get_theme_colors(theme_name)
        is_dark = theme_manager.is_dark_theme()
        
        # Apply background color
        bg_color = colors.get("background", "#ffffff")
        text_color = colors.get("text_primary", "#212529")
        self.setStyleSheet(f"background-color: {bg_color}; color: {text_color};")
        
        # Apply theme to all ModernButton components
        for button in self.findChildren(ModernButton):
            button.apply_theme(is_dark, colors)
            
        # Apply theme to all ModernGroupBox components
        for group_box in self.findChildren(ModernGroupBox):
            if hasattr(group_box, 'apply_theme'):
                group_box.apply_theme(is_dark, colors)
                
        # Apply theme to ModernCheckBox
        for checkbox in self.findChildren(ModernCheckBox):
             if hasattr(checkbox, 'apply_theme'):
                checkbox.apply_theme(is_dark, colors)