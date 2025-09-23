"""
Window Manager Dialog for QuillScribe
Provides window management controls and settings
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton,
    QComboBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..config_manager import ConfigManager
from ..window_manager import WindowManager
from ..ui_components import ModernButton, ModernGroupBox
from ..icon_manager import get_button_icon
from ..theme_manager import get_theme_manager


class WindowManagerDialog(QDialog):
    """Window management dialog with always-on-top and positioning controls"""
    
    settings_saved = Signal()
    
    def __init__(self, parent=None, config_manager=None, window_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.window_manager = window_manager
        self.parent_window = parent
        
        self.setWindowTitle("Window Manager")
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
        self.load_settings()

        # Apply initial theme
        if self.config_manager:
            theme = self.config_manager.get_setting("ui/theme", "white")
            self.apply_theme(theme)
    
    def setup_ui(self):
        """Setup the window manager dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Window Management")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Window Behavior Group
        behavior_group = ModernGroupBox("Window Behavior")
        behavior_layout = QVBoxLayout(behavior_group)
        
        # Always on top
        self.always_on_top_checkbox = QCheckBox("Always on Top")
        behavior_layout.addWidget(self.always_on_top_checkbox)
        
        # Snap to edges
        self.snap_to_edges_checkbox = QCheckBox("Snap to Screen Edges")
        self.snap_to_edges_checkbox.setIcon(get_button_icon('dashboard', 16))
        behavior_layout.addWidget(self.snap_to_edges_checkbox)
        
        layout.addWidget(behavior_group)
        
        # Position Controls Group
        position_group = ModernGroupBox("Position Controls")
        position_layout = QVBoxLayout(position_group)
        
        # Quick position buttons
        position_buttons_layout = QHBoxLayout()
        
        self.top_left_button = ModernButton("Top Left")
        self.top_left_button.clicked.connect(lambda: self.move_to_position("top_left"))
        position_buttons_layout.addWidget(self.top_left_button)
        
        self.top_right_button = ModernButton("Top Right")
        self.top_right_button.clicked.connect(lambda: self.move_to_position("top_right"))
        position_buttons_layout.addWidget(self.top_right_button)
        
        position_layout.addLayout(position_buttons_layout)
        
        position_buttons_layout2 = QHBoxLayout()
        
        self.bottom_left_button = ModernButton("Bottom Left")
        self.bottom_left_button.clicked.connect(lambda: self.move_to_position("bottom_left"))
        position_buttons_layout2.addWidget(self.bottom_left_button)
        
        self.bottom_right_button = ModernButton("Bottom Right")
        self.bottom_right_button.clicked.connect(lambda: self.move_to_position("bottom_right"))
        position_buttons_layout2.addWidget(self.bottom_right_button)
        
        position_layout.addLayout(position_buttons_layout2)
        
        # Center button
        self.center_button = ModernButton("Center")
        self.center_button.clicked.connect(lambda: self.move_to_position("center"))
        position_layout.addWidget(self.center_button)
        
        layout.addWidget(position_group)
        
        # Status Group
        status_group = ModernGroupBox("Status")
        status_layout = QFormLayout(status_group)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        status_layout.addRow("Window Status:", self.status_label)
        
        layout.addWidget(status_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_button = ModernButton("Apply", primary=True)
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.close_button = ModernButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)

        # Apply theme manager for icon theming and connect to theme changes
        theme_manager = get_theme_manager()
        theme_manager.apply_icons_to_widget(self)

        # Connect to theme changes for dynamic theming
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def load_settings(self):
        """Load current window management settings"""
        if self.config_manager:
            always_on_top = bool(self.config_manager.get_setting("ui/always_on_top", False))
            self.always_on_top_checkbox.setChecked(always_on_top)
            
            snap_to_edges = bool(self.config_manager.get_setting("ui/snap_to_edges", True))
            self.snap_to_edges_checkbox.setChecked(snap_to_edges)
        
        # Update status
        self.update_status()
    
    def apply_settings(self):
        """Apply window management settings"""
        if self.config_manager:
            # Save settings
            self.config_manager.set_setting("ui/always_on_top", self.always_on_top_checkbox.isChecked())
            self.config_manager.set_setting("ui/snap_to_edges", self.snap_to_edges_checkbox.isChecked())
            self.config_manager.save_settings()
        
        # Apply to window manager
        if self.window_manager:
            try:
                always_on_top_enabled = self.always_on_top_checkbox.isChecked()
                print(f"Applying always-on-top setting: {always_on_top_enabled}")

                self.window_manager.set_always_on_top(always_on_top_enabled)

                # Verify the setting was applied
                actual_state = self.window_manager.is_always_on_top()
                print(f"Always-on-top state after setting: {actual_state}")

                self.status_label.setText("Settings applied successfully")
                self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")

                # Update status to reflect actual state
                self.update_status()

            except Exception as e:
                print(f"Error applying always-on-top setting: {e}")
                self.status_label.setText(f"Error: {str(e)}")
                self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        
        self.settings_saved.emit()
    
    def move_to_position(self, position: str):
        """Move window to specified position"""
        if not self.parent_window:
            return

        try:
            # Temporarily disable snap detection to prevent interference
            snap_was_enabled = False
            if self.window_manager and hasattr(self.window_manager, 'snap_enabled'):
                snap_was_enabled = self.window_manager.snap_enabled
                self.window_manager.snap_enabled = False

            # Use direct positioning since window manager doesn't have move_to_position method
            screen = self.parent_window.screen().availableGeometry()
            window_size = self.parent_window.size()

            if position == "top_left":
                new_x = screen.x()
                new_y = screen.y()
            elif position == "top_right":
                new_x = screen.x() + screen.width() - window_size.width()
                new_y = screen.y()
            elif position == "bottom_left":
                new_x = screen.x()
                new_y = screen.y() + screen.height() - window_size.height()
            elif position == "bottom_right":
                new_x = screen.x() + screen.width() - window_size.width()
                new_y = screen.y() + screen.height() - window_size.height()
            elif position == "center":
                new_x = screen.x() + (screen.width() - window_size.width()) // 2
                new_y = screen.y() + (screen.height() - window_size.height()) // 2
            else:
                return

            # Debug output
            print(f"Moving window to position {position}: ({new_x}, {new_y})")
            print(f"Screen geometry: {screen}")
            print(f"Window size: {window_size}")

            self.parent_window.move(new_x, new_y)

            # Re-enable snap detection after a short delay
            if self.window_manager and snap_was_enabled:
                from PySide6.QtCore import QTimer
                QTimer.singleShot(500, lambda: setattr(self.window_manager, 'snap_enabled', True))

            self.status_label.setText(f"Moved to {position.replace('_', ' ').title()}")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")

        except Exception as e:
            self.status_label.setText(f"Error moving window: {str(e)}")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
    
    def update_status(self):
        """Update the status display"""
        if self.window_manager:
            try:
                is_on_top = self.window_manager.is_always_on_top()
                if is_on_top:
                    self.status_label.setText("Always on top: Enabled")
                else:
                    self.status_label.setText("Always on top: Disabled")
                self.status_label.setStyleSheet("color: #17a2b8; font-weight: bold;")
            except Exception:
                self.status_label.setText("Status unknown")
                self.status_label.setStyleSheet("color: #6c757d; font-weight: bold;")
        else:
            self.status_label.setText("Window manager not available")
            self.status_label.setStyleSheet("color: #6c757d; font-weight: bold;")

    def apply_theme(self, theme_name: str):
        """Apply theme to the window manager dialog using theme manager"""
        # Get theme manager but don't call set_theme to avoid recursion
        theme_manager = get_theme_manager()
        colors = theme_manager.get_theme_colors(theme_name)

        # Determine if dark theme manually to avoid recursion
        primary_color = colors["primary"]
        r = int(primary_color.lstrip('#')[0:2], 16)
        g = int(primary_color.lstrip('#')[2:4], 16)
        b = int(primary_color.lstrip('#')[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        is_dark = brightness < 128

        secondary_color = colors["secondary"]

        # Apply theme to dialog background
        if is_dark:
            dialog_style = f"""
                QDialog {{
                    background-color: {primary_color};
                    color: #e9ecef;
                }}
                QLabel {{
                    color: #e9ecef;
                }}
                QCheckBox {{
                    color: #e9ecef;
                }}
            """
        else:
            dialog_style = f"""
                QDialog {{
                    background-color: {primary_color};
                    color: #495057;
                }}
                QLabel {{
                    color: #495057;
                }}
                QCheckBox {{
                    color: #495057;
                }}
            """

        self.setStyleSheet(dialog_style)

        # Apply theme to buttons using ModernButton's apply_theme method
        for button in [self.top_left_button, self.top_right_button, self.bottom_left_button,
                      self.bottom_right_button, self.center_button, self.apply_button, self.close_button]:
            if hasattr(button, 'apply_theme'):
                button.apply_theme(primary_color, secondary_color)

        # Apply theme to group boxes using ModernGroupBox's apply_theme method
        from ..ui_components import ModernGroupBox
        for group_box in self.findChildren(ModernGroupBox):
            if hasattr(group_box, 'apply_theme'):
                group_box.apply_theme(primary_color, secondary_color)

        # Apply themed icons without calling theme manager methods that might cause recursion
        try:
            theme_manager.apply_icons_to_widget(self, is_dark)
        except Exception as e:
            print(f"Warning: Error applying themed icons: {e}")

    def _on_theme_changed(self, theme_name: str, is_dark: bool):
        """Handle theme change signal for dynamic theming"""
        self.apply_theme(theme_name)
