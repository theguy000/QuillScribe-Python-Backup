"""
UI Settings Tab
Handles UI customization, themes, and window behavior
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout,
    QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeySequence

from ..config_manager import ConfigManager
from ..icon_manager import get_button_icon, get_icon
from ..managers import get_theme_manager
from .ui_components import ModernGroupBox
from .modern_widgets import ModernComboBox, ModernCheckBox, ModernKeySequenceEdit, AnimatedToggleSwitch, ModernSlider


class UITab(QWidget):
    """UI Settings: Compact mode and visualization options"""
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        # Minimal outer margins so group boxes sit close to dialog edges
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        intro = QLabel("Configure UI, including Super Compact mode and microphone visualization.")
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #6c757d; font-size: 12px; font-family: 'Segoe UI', sans-serif;")
        layout.addWidget(intro)

        box = ModernGroupBox("UI Settings")
        form = QVBoxLayout(box)

        # Compact mode toggle
        compact_layout = QHBoxLayout()
        compact_layout.setSpacing(10)
        self.compact_checkbox = AnimatedToggleSwitch()
        compact_layout.addWidget(self.compact_checkbox)
        compact_label = QLabel("Enable Super Compact UI")
        compact_label.setStyleSheet("color: #495057; font-size: 13px; font-family: 'Segoe UI', sans-serif;")
        compact_layout.addWidget(compact_label, 1)
        form.addLayout(compact_layout)

        tip = QLabel("In compact mode, the window is frameless with a right-aligned close button, and you can drag anywhere to move.")
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #6c757d; font-size: 11px; font-family: 'Segoe UI', sans-serif;")
        form.addWidget(tip)

        # Add custom title bar setting
        titlebar_layout = QHBoxLayout()
        titlebar_layout.setSpacing(10)
        self.custom_titlebar_checkbox = AnimatedToggleSwitch()
        titlebar_layout.addWidget(self.custom_titlebar_checkbox)
        titlebar_label = QLabel("Enable custom title bar")
        titlebar_label.setStyleSheet("color: #495057; font-size: 13px; font-family: 'Segoe UI', sans-serif;")
        titlebar_layout.addWidget(titlebar_label, 1)
        form.addLayout(titlebar_layout)

        titlebar_tip = QLabel("When enabled, uses a custom title bar instead of the system default. Disable for standard OS title bar.")
        titlebar_tip.setWordWrap(True)
        titlebar_tip.setStyleSheet("color: #6c757d; font-size: 11px; font-family: 'Segoe UI', sans-serif;")
        form.addWidget(titlebar_tip)

        # Add theme selection to the same group box
        theme_form_layout = QFormLayout()
        theme_form_layout.setContentsMargins(0, 10, 0, 0)  # Add some spacing from compact mode
        theme_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Create theme dropdown widget with icon
        theme_widget = QWidget()
        theme_widget_layout = QHBoxLayout(theme_widget)
        theme_widget_layout.setContentsMargins(0, 0, 0, 0)
        theme_widget_layout.setSpacing(6)

        theme_icon = QLabel()
        theme_icon.setPixmap(get_icon('settings', 16).pixmap(16, 16))
        theme_icon.setObjectName("icon_theme")
        theme_widget_layout.addWidget(theme_icon)

        self.theme_label = QLabel("Background theme:")
        self.theme_label.setObjectName("theme_label")
        self.theme_label.setStyleSheet("font-family: 'Segoe UI', sans-serif;")
        theme_widget_layout.addWidget(self.theme_label)
        theme_widget_layout.addStretch()

        self.theme_dropdown = ModernComboBox()
        self.theme_dropdown.setMaximumWidth(200)
        self.theme_dropdown.addItem("Classic White", "white")
        self.theme_dropdown.addItem("Warm Gray", "warm_gray")
        self.theme_dropdown.addItem("Soft Beige", "soft_beige")
        self.theme_dropdown.addItem("Muted Blue-Gray", "blue_gray")
        self.theme_dropdown.addItem("Warm Taupe", "warm_taupe")
        self.theme_dropdown.addItem("Soft Sage", "soft_sage")
        # Dark themes
        self.theme_dropdown.addItem("Dark Charcoal", "dark_charcoal")
        self.theme_dropdown.addItem("Dark Blue", "dark_blue")
        self.theme_dropdown.addItem("Dark Purple", "dark_purple")
        self.theme_dropdown.addItem("Dark Forest", "dark_forest")
        self.theme_dropdown.addItem("Dark Burgundy", "dark_burgundy")

        theme_form_layout.addRow(theme_widget, self.theme_dropdown)

        theme_help = QLabel("Choose a background color theme for the application. Changes apply immediately.")
        theme_help.setWordWrap(True)
        theme_help.setStyleSheet("color: #6c757d; font-size: 11px; background-color: transparent; font-family: 'Segoe UI', sans-serif;")
        theme_form_layout.addRow("", theme_help)

        form.addLayout(theme_form_layout)

        layout.addWidget(box)

        # Visualization options moved here
        viz_group = ModernGroupBox("Visualization")
        viz_layout = QVBoxLayout(viz_group)

        # Show waveform toggle
        waveform_layout = QHBoxLayout()
        waveform_layout.setSpacing(10)
        self.show_waveform_checkbox = AnimatedToggleSwitch()
        self.show_waveform_checkbox.setChecked(True)
        waveform_layout.addWidget(self.show_waveform_checkbox)
        waveform_label = QLabel("Show circular waveform during recording")
        waveform_label.setStyleSheet("color: #495057; font-size: 13px; font-family: 'Segoe UI', sans-serif;")
        waveform_layout.addWidget(waveform_label, 1)
        viz_layout.addLayout(waveform_layout)

        # Animation strength slider
        self.animation_strength_label = QLabel("Animation Amplification:")
        self.animation_strength_label.setObjectName("animation_strength_label")
        self.animation_strength_label.setStyleSheet("color: #495057; font-size: 13px; margin-top: 10px; font-family: 'Segoe UI', sans-serif; font-weight: 600;")
        viz_layout.addWidget(self.animation_strength_label)

        self.animation_strength_slider = ModernSlider(Qt.Orientation.Horizontal)
        self.animation_strength_slider.setRange(1, 10)
        self.animation_strength_slider.setValue(3)
        self.animation_strength_slider.setTickPosition(ModernSlider.TickPosition.TicksBelow)
        self.animation_strength_slider.setTickInterval(1)
        self.animation_strength_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # Accessibility improvements
        self.animation_strength_slider.setPageStep(2)  # Page Up/Down steps
        self.animation_strength_slider.setSingleStep(1)  # Arrow key steps
        self.animation_strength_slider.setToolTip("Adjust amplification (Use arrow keys for precise control)")

        self.animation_strength_value_label = QLabel("3x")
        self.animation_strength_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.animation_strength_value_label.setMinimumWidth(40)
        self.animation_strength_value_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.animation_strength_slider.valueChanged.connect(self.update_animation_strength_label)

        strength_layout = QHBoxLayout()
        strength_layout.setSpacing(12)
        strength_layout.setContentsMargins(0, 4, 0, 4)
        strength_layout.addWidget(self.animation_strength_slider)
        strength_layout.addWidget(self.animation_strength_value_label)
        viz_layout.addLayout(strength_layout)
        self._style_animation_controls()

        self.strength_help = QLabel("Higher values make waveform more visible with quiet voice")
        self.strength_help.setObjectName("strength_help_label")
        self.strength_help.setWordWrap(True)
        self.strength_help.setStyleSheet("color: #6c757d; font-size: 11px; font-family: 'Segoe UI', sans-serif;")
        viz_layout.addWidget(self.strength_help)

        layout.addWidget(viz_group)

        # Shortcuts & Window behavior
        shortcuts_group = ModernGroupBox("Shortcuts & Window")
        shortcuts_layout = QVBoxLayout(shortcuts_group)

        # Minimize on close toggle
        minimize_close_layout = QHBoxLayout()
        minimize_close_layout.setSpacing(10)
        self.minimize_on_close_checkbox = AnimatedToggleSwitch()
        self.minimize_on_close_checkbox.setChecked(True)
        self.minimize_on_close_checkbox.setToolTip("When enabled, closing the window will minimize it instead of exiting the application.")
        minimize_close_layout.addWidget(self.minimize_on_close_checkbox)
        minimize_close_label = QLabel("Minimize on close (instead of exiting)")
        minimize_close_label.setStyleSheet("color: #495057; font-size: 13px; font-family: 'Segoe UI', sans-serif;")
        minimize_close_layout.addWidget(minimize_close_label, 1)
        shortcuts_layout.addLayout(minimize_close_layout)

        # Minimize to tray toggle
        minimize_tray_layout = QHBoxLayout()
        minimize_tray_layout.setSpacing(10)
        self.minimize_to_tray_checkbox = AnimatedToggleSwitch()
        self.minimize_to_tray_checkbox.setChecked(False)
        self.minimize_to_tray_checkbox.setToolTip("When enabled, minimizing or closing the window will hide it to the system notification area (system tray). Click the tray icon to restore the window. Takes priority over 'Minimize on close'.")

        # Check if system tray is available
        from PySide6.QtWidgets import QSystemTrayIcon
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.minimize_to_tray_checkbox.setEnabled(False)
            self.minimize_to_tray_checkbox.setToolTip("System tray is not available on this system")

        minimize_tray_layout.addWidget(self.minimize_to_tray_checkbox)
        minimize_tray_label = QLabel("Minimize to system tray")
        minimize_tray_label.setStyleSheet("color: #495057; font-size: 13px; font-family: 'Segoe UI', sans-serif;")
        minimize_tray_layout.addWidget(minimize_tray_label, 1)
        shortcuts_layout.addLayout(minimize_tray_layout)

        # Always on top toggle
        always_top_layout = QHBoxLayout()
        always_top_layout.setSpacing(10)
        self.always_on_top_checkbox = AnimatedToggleSwitch()
        self.always_on_top_checkbox.setChecked(False)
        self.always_on_top_checkbox.setToolTip("Keep the QuillScribe window always on top of other windows")
        always_top_layout.addWidget(self.always_on_top_checkbox)
        always_top_label = QLabel("Always on top")
        always_top_label.setStyleSheet("color: #495057; font-size: 13px; font-family: 'Segoe UI', sans-serif;")
        always_top_layout.addWidget(always_top_label, 1)
        shortcuts_layout.addLayout(always_top_layout)

        # Snap to edges toggle
        snap_edges_layout = QHBoxLayout()
        snap_edges_layout.setSpacing(10)
        self.snap_to_edges_checkbox = AnimatedToggleSwitch()
        self.snap_to_edges_checkbox.setChecked(True)
        self.snap_to_edges_checkbox.setToolTip("Automatically snap window to screen edges when dragged close to them")
        snap_edges_layout.addWidget(self.snap_to_edges_checkbox)
        snap_edges_label = QLabel("Snap to screen edges")
        snap_edges_label.setStyleSheet("color: #495057; font-size: 13px; font-family: 'Segoe UI', sans-serif;")
        snap_edges_layout.addWidget(snap_edges_label, 1)
        shortcuts_layout.addLayout(snap_edges_layout)

        # Recording shortcut
        self.shortcut_label = QLabel("Recording shortcut:")
        self.shortcut_label.setObjectName("shortcut_label")
        self.shortcut_label.setStyleSheet("color: #495057; font-size: 13px; margin-top: 10px; font-family: 'Segoe UI', sans-serif;")
        shortcuts_layout.addWidget(self.shortcut_label)

        self.shortcut_edit = ModernKeySequenceEdit()
        shortcuts_layout.addWidget(self.shortcut_edit)

        shortcut_help = QLabel("Click in the field above and press your desired key combination to record a shortcut. This shortcut toggles recording. On Windows, 'Win' refers to the Windows key.")
        shortcut_help.setWordWrap(True)
        shortcut_help.setStyleSheet("color: #6c757d; font-size: 11px; background-color: transparent; font-family: 'Segoe UI', sans-serif;")
        shortcuts_layout.addWidget(shortcut_help)

        layout.addWidget(shortcuts_group)
        layout.addStretch()

    def load_settings(self):
        enabled = bool(self.config_manager.get_setting("ui/compact_mode", False))
        self.compact_checkbox.setChecked(enabled)
        show_waveform = self.config_manager.get_setting("ui/show_waveform", True)
        self.show_waveform_checkbox.setChecked(bool(show_waveform))
        animation_strength = self.config_manager.get_setting("ui/animation_strength", 3)
        self.animation_strength_slider.setValue(int(animation_strength))
        self.update_animation_strength_label(int(animation_strength))
        # New settings
        minimize_on_close = bool(self.config_manager.get_setting("ui/minimize_on_close", True))
        self.minimize_on_close_checkbox.setChecked(minimize_on_close)
        minimize_to_tray = bool(self.config_manager.get_setting("ui/minimize_to_tray", False))
        self.minimize_to_tray_checkbox.setChecked(minimize_to_tray)

        # Window management settings
        always_on_top = bool(self.config_manager.get_setting("ui/always_on_top", False))
        self.always_on_top_checkbox.setChecked(always_on_top)
        snap_to_edges = bool(self.config_manager.get_setting("ui/snap_to_edges", True))
        self.snap_to_edges_checkbox.setChecked(snap_to_edges)
        shortcut = self.config_manager.get_setting("shortcuts/record_toggle", "Meta+Shift+`")
        if isinstance(shortcut, str):
            # Convert Windows format to Qt format for display
            qt_shortcut = ModernKeySequenceEdit.windows_to_qt_shortcut(shortcut)
            self.shortcut_edit.setKeySequence(QKeySequence.fromString(qt_shortcut))

        # Load custom title bar setting
        custom_titlebar = bool(self.config_manager.get_setting("ui/custom_titlebar", True))
        self.custom_titlebar_checkbox.setChecked(custom_titlebar)

        # Load theme setting
        theme = self.config_manager.get_setting("ui/theme", "white")
        index = self.theme_dropdown.findData(theme)
        if index >= 0:
            self.theme_dropdown.setCurrentIndex(index)

        # Connect theme change signal
        self.theme_dropdown.currentIndexChanged.connect(self.on_theme_changed)

    def save_settings(self):
        self.config_manager.set_setting("ui/compact_mode", self.compact_checkbox.isChecked())
        self.config_manager.set_setting("ui/show_waveform", self.show_waveform_checkbox.isChecked())
        self.config_manager.set_setting("ui/animation_strength", self.animation_strength_slider.value())
        # Save new settings
        self.config_manager.set_setting("ui/minimize_on_close", self.minimize_on_close_checkbox.isChecked())
        self.config_manager.set_setting("ui/minimize_to_tray", self.minimize_to_tray_checkbox.isChecked())

        # Save window management settings
        self.config_manager.set_setting("ui/always_on_top", self.always_on_top_checkbox.isChecked())
        self.config_manager.set_setting("ui/snap_to_edges", self.snap_to_edges_checkbox.isChecked())
        qt_shortcut_sequence = self.shortcut_edit.keySequence().toString()
        # Convert Qt format to Windows format for storage
        windows_shortcut = ModernKeySequenceEdit.qt_to_windows_shortcut(qt_shortcut_sequence) or "Meta+Shift+`"
        self.config_manager.set_setting("shortcuts/record_toggle", windows_shortcut)

        # Save custom title bar setting
        self.config_manager.set_setting("ui/custom_titlebar", self.custom_titlebar_checkbox.isChecked())

        # Save theme
        theme_data = self.theme_dropdown.currentData()
        if theme_data:
            self.config_manager.set_setting("ui/theme", theme_data)

    def update_animation_strength_label(self, value):
        """Update the value label and apply visual feedback for extreme values."""
        self.animation_strength_value_label.setText(f"{value}x")
        # Update tooltip with current value
        self.animation_strength_slider.setToolTip(f"Amplification: {value}x (Use arrow keys for precise control)")
        # Apply visual feedback styling for extreme values
        self._update_value_badge_style(value)
        # Update slider stylesheet to hide/show sub-page at minimum
        self._update_slider_fill_visibility(value)

    def apply_animation_theme(self, theme_name: str | None = None):
        """Public hook so parent dialog can restyle animation controls on theme changes."""
        self._style_animation_controls(theme_name)
        # Re-apply value badge styling for current slider value
        if hasattr(self, 'animation_strength_slider'):
            self._update_value_badge_style(self.animation_strength_slider.value())

    def _style_animation_controls(self, theme_name: str | None = None):
        """Apply cohesive styling to the animation amplification slider and badges."""
        if not hasattr(self, "animation_strength_slider"):
            return

        theme_manager = get_theme_manager()
        if theme_name is None:
            theme_name = theme_manager.get_current_theme()

        colors = theme_manager.get_theme_colors(theme_name)
        primary = colors.get("primary", "#ffffff")
        accent = colors.get("accent", "#4A90E2")
        
        is_dark = self._is_dark_theme(primary)
        
        # Store current theme info for value badge updates
        self._current_theme_name = theme_name
        self._current_accent = accent
        self._current_primary = primary
        
        # Apply theme to ModernSlider
        self.animation_strength_slider.apply_theme(is_dark, accent)

        heading_color = "#e5e5eb" if is_dark else "#2c3e50"
        self.animation_strength_label.setStyleSheet(
            f"QLabel {{ color: {heading_color}; font-size: 13px; font-weight: 600; font-family: 'Segoe UI', sans-serif; }}"
        )
        
        # Style help text with theme awareness
        if hasattr(self, 'strength_help'):
            help_color = "#8a8e98" if is_dark else "#6c757d"
            self.strength_help.setStyleSheet(
                f"color: {help_color}; font-size: 11px; "
                f"padding-left: 4px; background-color: transparent; font-family: 'Segoe UI', sans-serif;"
            )

    @staticmethod
    def _blend_hex_colors(base_hex: str, blend_hex: str, factor: float) -> str:
        """Blend two hex colors - delegates to ThemeManager for consistency."""
        theme_manager = get_theme_manager()
        return theme_manager.blend_hex_colors(base_hex, blend_hex, factor)

    def _update_slider_fill_visibility(self, value: int):
        """Update slider stylesheet to hide sub-page fill when at minimum value."""
        if not hasattr(self, 'animation_strength_slider'):
            return
        # Trigger a re-style to update sub-page visibility
        self._style_animation_controls()
    
    def _update_value_badge_style(self, value: int):
        """Apply visual feedback styling based on the current slider value."""
        if not hasattr(self, 'animation_strength_value_label'):
            return
            
        theme_manager = get_theme_manager()
        theme_name = getattr(self, '_current_theme_name', theme_manager.get_current_theme())
        colors = theme_manager.get_theme_colors(theme_name)
        primary = colors.get("primary", "#ffffff")
        accent = colors.get("accent", "#4A90E2")
        
        is_dark = self._is_dark_theme(primary)
        
        # Simple, clean badge style
        label_text = "#ffffff" if is_dark else "#333333"
        # Subtle background
        label_bg = self._blend_hex_colors(primary, "#000000", 0.1 if is_dark else 0.05)
        
        self.animation_strength_value_label.setStyleSheet(
            f"""
            QLabel {{
                color: {label_text};
                font-size: 12px;
                font-weight: 600;
                padding: 2px 8px;
                border-radius: 4px;
                background: {label_bg};
                min-width: 30px;
                font-family: 'Segoe UI', sans-serif;
            }}
            """
        )
    
    @staticmethod
    def _is_dark_theme(color_hex: str) -> bool:
        """Determine if a given color should be treated as dark."""
        try:
            color_hex = color_hex.lstrip('#')
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            return brightness < 128
        except (ValueError, TypeError):
            return False

    def on_theme_changed(self):
        """
        Apply theme immediately when changed.
        
        Uses ThemeManager.set_theme() to trigger theme_changed signal,
        which automatically propagates to all connected windows/dialogs.
        This replaces the old parent-traversal approach with signal-based
        propagation for reliable, consistent theme updates.
        """
        theme_data = self.theme_dropdown.currentData()
        if theme_data:
            # Persist theme selection immediately
            self.config_manager.set_setting("ui/theme", theme_data)
            self.config_manager.save_settings()

            # Update theme via theme manager - this emits theme_changed signal
            # which automatically propagates to SettingsDialog and MainWindow
            theme_manager = get_theme_manager()
            theme_manager.set_theme(theme_data)
            
            # Refresh local slider styling for immediate visual feedback
            self._style_animation_controls(theme_data)