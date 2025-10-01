"""
UI Settings Tab
Handles UI customization, themes, and window behavior
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout,
    QSlider, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeySequence

from ..config_manager import ConfigManager
from ..icon_manager import get_button_icon, get_icon
from ..managers import get_theme_manager
from .modern_widgets import ModernGroupBox, ModernComboBox, ModernCheckBox, ModernKeySequenceEdit


class UITab(QWidget):
    """UI Settings: Compact mode and visualization options"""
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        intro = QLabel("Configure UI, including Super Compact mode and microphone visualization.")
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #6c757d; font-size: 12px;")
        layout.addWidget(intro)

        box = ModernGroupBox("UI Settings")
        form = QVBoxLayout(box)
        self.compact_checkbox = ModernCheckBox("Enable Super Compact UI")
        self.compact_checkbox.setIconSize(QSize(16, 16))
        form.addWidget(self.compact_checkbox)

        tip = QLabel("In compact mode, the window is frameless with a right-aligned close button, and you can drag anywhere to move.")
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #6c757d; font-size: 11px;")
        form.addWidget(tip)

        # Add custom title bar setting
        self.custom_titlebar_checkbox = ModernCheckBox("Enable custom title bar")
        self.custom_titlebar_checkbox.setIconSize(QSize(16, 16))
        form.addWidget(self.custom_titlebar_checkbox)

        titlebar_tip = QLabel("When enabled, uses a custom title bar instead of the system default. Disable for standard OS title bar.")
        titlebar_tip.setWordWrap(True)
        titlebar_tip.setStyleSheet("color: #6c757d; font-size: 11px;")
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
        theme_help.setStyleSheet("color: #6c757d; font-size: 11px; background-color: transparent;")
        theme_form_layout.addRow("", theme_help)

        form.addLayout(theme_form_layout)

        layout.addWidget(box)

        # Visualization options moved here
        viz_group = ModernGroupBox("Visualization")
        viz_layout = QFormLayout(viz_group)
        viz_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.show_waveform_checkbox = ModernCheckBox("Show circular waveform during recording")
        self.show_waveform_checkbox.setIcon(get_button_icon('zap', 16))
        self.show_waveform_checkbox.setIconSize(QSize(16, 16))
        self.show_waveform_checkbox.setChecked(True)
        viz_layout.addRow(self.show_waveform_checkbox)

        self.animation_strength_label = QLabel("Animation Amplification:")
        self.animation_strength_label.setObjectName("animation_strength_label")
        self.animation_strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.animation_strength_slider.setRange(1, 10)
        self.animation_strength_slider.setValue(3)
        self.animation_strength_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
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
        viz_layout.addRow(self.animation_strength_label, strength_layout)
        self._style_animation_controls()

        self.strength_help = QLabel("Higher values make waveform more visible with quiet voice")
        self.strength_help.setObjectName("strength_help_label")
        self.strength_help.setWordWrap(True)
        viz_layout.addRow("", self.strength_help)

        layout.addWidget(viz_group)

        # Shortcuts & Window behavior
        shortcuts_group = ModernGroupBox("Shortcuts & Window")
        shortcuts_layout = QFormLayout(shortcuts_group)
        shortcuts_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.minimize_on_close_checkbox = ModernCheckBox("Minimize on close (instead of exiting)")
        self.minimize_on_close_checkbox.setIcon(get_button_icon('window', 16))
        self.minimize_on_close_checkbox.setIconSize(QSize(16, 16))
        self.minimize_on_close_checkbox.setChecked(True)
        self.minimize_on_close_checkbox.setToolTip("When enabled, closing the window will minimize it instead of exiting the application.")
        shortcuts_layout.addRow(self.minimize_on_close_checkbox)

        self.minimize_to_tray_checkbox = ModernCheckBox("Minimize to system tray")
        self.minimize_to_tray_checkbox.setIcon(get_button_icon('compact', 16))
        self.minimize_to_tray_checkbox.setIconSize(QSize(16, 16))
        self.minimize_to_tray_checkbox.setChecked(False)
        self.minimize_to_tray_checkbox.setToolTip("When enabled, minimizing or closing the window will hide it to the system notification area (system tray). Click the tray icon to restore the window. Takes priority over 'Minimize on close'.")

        # Check if system tray is available
        from PySide6.QtWidgets import QSystemTrayIcon
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.minimize_to_tray_checkbox.setEnabled(False)
            self.minimize_to_tray_checkbox.setToolTip("System tray is not available on this system")

        shortcuts_layout.addRow(self.minimize_to_tray_checkbox)

        # Window Management Settings
        self.always_on_top_checkbox = ModernCheckBox("Always on top")
        self.always_on_top_checkbox.setIconSize(QSize(16, 16))
        self.always_on_top_checkbox.setChecked(False)
        self.always_on_top_checkbox.setToolTip("Keep the QuillScribe window always on top of other windows")
        shortcuts_layout.addRow(self.always_on_top_checkbox)

        self.snap_to_edges_checkbox = ModernCheckBox("Snap to screen edges")
        self.snap_to_edges_checkbox.setIconSize(QSize(16, 16))
        self.snap_to_edges_checkbox.setChecked(True)
        self.snap_to_edges_checkbox.setToolTip("Automatically snap window to screen edges when dragged close to them")
        shortcuts_layout.addRow(self.snap_to_edges_checkbox)

        # Create label with icon for shortcut
        shortcut_widget = QWidget()
        shortcut_layout = QHBoxLayout(shortcut_widget)
        shortcut_layout.setContentsMargins(0, 0, 0, 0)
        shortcut_layout.setSpacing(6)

        shortcut_icon = QLabel()
        shortcut_icon.setPixmap(get_icon('keyboard', 16).pixmap(16, 16))
        shortcut_icon.setObjectName("icon_shortcut")
        shortcut_layout.addWidget(shortcut_icon)

        self.shortcut_label = QLabel("Recording shortcut:")
        self.shortcut_label.setObjectName("shortcut_label")
        shortcut_layout.addWidget(self.shortcut_label)
        shortcut_layout.addStretch()

        self.shortcut_edit = ModernKeySequenceEdit()
        shortcuts_layout.addRow(shortcut_widget, self.shortcut_edit)

        shortcut_help = QLabel("Click in the field above and press your desired key combination to record a shortcut. This shortcut toggles recording. On Windows, 'Win' refers to the Windows key.")
        shortcut_help.setWordWrap(True)
        shortcut_help.setStyleSheet("color: #6c757d; font-size: 11px; background-color: transparent;")
        shortcuts_layout.addRow("", shortcut_help)

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
        shortcut = self.config_manager.get_setting("shortcuts/record_toggle", "Meta+`")
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
        windows_shortcut = ModernKeySequenceEdit.qt_to_windows_shortcut(qt_shortcut_sequence) or "Meta+`"
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
        secondary = colors.get("secondary", "#f8f9fa")
        accent = colors.get("accent", "#4A90E2")
        accent_hover = colors.get("accent_hover", "#357ABD")

        is_dark = self._is_dark_theme(primary)
        
        # Store current theme info for value badge updates
        self._current_theme_name = theme_name
        self._current_accent = accent
        self._current_primary = primary
        
        groove_start = self._blend_hex_colors(primary, secondary, 0.6 if is_dark else 0.25)
        groove_end = self._blend_hex_colors(primary, "#000000", 0.15 if is_dark else 0.05)
        groove_border = self._blend_hex_colors(primary, "#000000" if is_dark else "#4A90E2", 0.18 if is_dark else 0.08)

        accent_fill = self._blend_hex_colors(accent, "#ffffff", 0.2 if is_dark else 0.05)
        handle_color = self._blend_hex_colors(accent, "#ffffff", 0.35 if is_dark else 0.15)
        handle_hover = self._blend_hex_colors(accent_hover, "#ffffff", 0.3 if is_dark else 0.1)
        handle_pressed = self._blend_hex_colors(accent, "#000000", 0.25)
        # Improved tick marks - taller and more visible
        tick_color = self._blend_hex_colors(secondary if not is_dark else primary, "#4a4d55" if is_dark else "#adb5bd", 0.7)

        # Get current slider value to determine sub-page visibility
        current_value = self.animation_strength_slider.value() if hasattr(self, 'animation_strength_slider') else 3
        
        # Hide sub-page (blue fill) when at minimum value (1)
        if current_value == 1:
            sub_page_bg = "transparent"
        else:
            sub_page_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {accent}, stop:1 {accent_fill})"
        
        slider_stylesheet = f"""
            QSlider::groove:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {groove_start}, stop:1 {groove_end});
                height: 10px;
                border-radius: 5px;
                border: 1px solid {groove_border};
                margin: 8px 14px;
            }}
            QSlider::sub-page:horizontal {{
                background: {sub_page_bg};
                border-radius: 5px;
                border: none;
                margin: 8px 14px;
            }}
            QSlider::add-page:horizontal {{
                background: transparent;
                border-radius: 5px;
                margin: 8px 14px;
            }}
            QSlider::handle:horizontal {{
                background: {handle_color};
                border: 2px solid {accent};
                width: 20px;
                height: 20px;
                margin: -7px -13px;
                border-radius: 10px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {handle_hover};
                border-color: {accent_hover};
                width: 22px;
                height: 22px;
                margin: -8px -14px;
            }}
            QSlider::handle:horizontal:pressed {{
                background: {handle_pressed};
                border-color: {accent_hover};
                width: 20px;
                height: 20px;
                margin: -7px -13px;
            }}
            QSlider::handle:horizontal:disabled {{
                background: {self._blend_hex_colors(handle_color, primary, 0.6)};
                border-color: {self._blend_hex_colors(accent, primary, 0.6)};
            }}
            QSlider::tick-mark:horizontal {{
                background: {tick_color};
                width: 1px;
                height: 8px;
            }}
        """

        self.animation_strength_slider.setStyleSheet(slider_stylesheet)

        heading_color = "#e5e5eb" if is_dark else "#2c3e50"
        self.animation_strength_label.setStyleSheet(
            f"QLabel {{ color: {heading_color}; font-size: 13px; font-weight: 600; }}"
        )
        
        # Style help text with theme awareness
        if hasattr(self, 'strength_help'):
            help_color = "#8a8e98" if is_dark else "#6c757d"
            self.strength_help.setStyleSheet(
                f"color: {help_color}; font-size: 11px; font-style: italic; "
                f"padding-left: 4px; background-color: transparent;"
            )

    @staticmethod
    def _blend_hex_colors(base_hex: str, blend_hex: str, factor: float) -> str:
        """Blend two hex colors by a given factor (0.0 -> base, 1.0 -> blend)."""
        factor = max(0.0, min(1.0, factor))
        try:
            base_hex = base_hex.lstrip('#')
            blend_hex = blend_hex.lstrip('#')
            br, bg, bb = int(base_hex[0:2], 16), int(base_hex[2:4], 16), int(base_hex[4:6], 16)
            rr, rg, rb = int(blend_hex[0:2], 16), int(blend_hex[2:4], 16), int(blend_hex[4:6], 16)
            r = int(br + (rr - br) * factor)
            g = int(bg + (rg - bg) * factor)
            b = int(bb + (rb - bb) * factor)
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, TypeError):
            return base_hex if base_hex.startswith('#') else f"#{base_hex}"

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
        
        # Apply different colors for extreme values
        if value == 1:
            # Minimum value - subtle gray
            label_text = "#d1d5db" if is_dark else "#6c757d"
            label_bg = self._blend_hex_colors(primary, "#6c757d", 0.25 if is_dark else 0.1)
            label_border = self._blend_hex_colors("#9ca3af", primary, 0.5)
        elif value >= 9:
            # High values - warning/attention color
            warning_color = "#f59e0b"
            label_text = "#fef3c7" if is_dark else "#c2410c"
            label_bg = self._blend_hex_colors(primary, warning_color, 0.4 if is_dark else 0.15)
            label_border = self._blend_hex_colors(warning_color, primary, 0.5)
        else:
            # Normal range - use accent color with improved light mode
            label_text = "#e9edf8" if is_dark else "#2563eb"
            label_bg = self._blend_hex_colors(primary, accent, 0.35 if is_dark else 0.15)
            label_border = self._blend_hex_colors(accent, primary, 0.5)
        
        self.animation_strength_value_label.setStyleSheet(
            f"""
            QLabel {{
                color: {label_text};
                font-size: 12px;
                font-weight: 600;
                padding: 2px 8px;
                border-radius: 10px;
                background: {label_bg};
                border: 1px solid {label_border};
                min-width: 40px;
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
        """Apply theme immediately when changed"""
        theme_data = self.theme_dropdown.currentData()
        if theme_data:
            self.config_manager.set_setting("ui/theme", theme_data)
            self.config_manager.save_settings()  # Save immediately

            # Refresh slider styling instantly for better feedback
            self._style_animation_controls(theme_data)

            # Apply theme to the parent dialog immediately
            dialog = self.parent()
            while dialog and not (hasattr(dialog, 'apply_theme') and hasattr(dialog, 'tabs')):
                dialog = dialog.parent()
            if dialog:
                dialog.apply_theme(theme_data)

                # Also apply to main window if it exists
                main_window = dialog.parent()
                if main_window and hasattr(main_window, 'apply_theme'):
                    main_window.apply_theme(theme_data)