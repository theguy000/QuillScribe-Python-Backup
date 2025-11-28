"""
UI Settings Tab
Handles UI customization, themes, and window behavior
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout,
    QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeySequence

from ..config_manager import ConfigManager
from ..icon_manager import get_button_icon, get_icon
from ..managers import get_theme_manager
from .ui_components import ModernGroupBox, apply_label_theme, apply_theme_recursively
from .modern_widgets import ModernComboBox, ModernCheckBox, ModernKeySequenceEdit, AnimatedToggleSwitch, ModernSlider


class UITab(QWidget):
    """UI Settings: Compact mode and visualization options"""
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.separators = []
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Appearance Section ---
        appearance_container = QWidget()
        appearance_layout = QVBoxLayout(appearance_container)
        appearance_layout.setContentsMargins(0, 0, 0, 0)
        appearance_layout.setSpacing(16)

        # Header
        appearance_header = QLabel("Appearance")
        appearance_header.setObjectName("section_label")
        appearance_header.setStyleSheet("font-size: 14px; font-weight: 600;")
        appearance_layout.addWidget(appearance_header)

        # Theme Row
        theme_row = QHBoxLayout()
        theme_row.setSpacing(12)
        
        theme_label_container = QVBoxLayout()
        theme_label_container.setSpacing(2)
        theme_label = QLabel("Theme")
        theme_label.setObjectName("setting_label")
        theme_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        theme_desc = QLabel("Choose the application color scheme.")
        theme_desc.setObjectName("setting_desc")
        theme_desc.setStyleSheet("color: #6c757d; font-size: 11px;")
        theme_label_container.addWidget(theme_label)
        theme_label_container.addWidget(theme_desc)
        theme_row.addLayout(theme_label_container)
        
        theme_row.addStretch()

        self.theme_dropdown = ModernComboBox()
        self.theme_dropdown.setMinimumWidth(180)
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
        self.theme_dropdown.addItem("Obsidian", "obsidian")
        
        theme_row.addWidget(self.theme_dropdown)
        appearance_layout.addLayout(theme_row)

        # Compact Mode Row
        compact_row = QHBoxLayout()
        self.compact_checkbox = AnimatedToggleSwitch()
        compact_row.addWidget(self.compact_checkbox)
        
        compact_info = QVBoxLayout()
        compact_info.setSpacing(2)
        compact_label = QLabel("Super Compact Mode")
        compact_label.setObjectName("setting_label")
        compact_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        compact_desc = QLabel("Frameless window with minimal controls.")
        compact_desc.setObjectName("setting_desc")
        compact_desc.setStyleSheet("color: #6c757d; font-size: 11px;")
        compact_info.addWidget(compact_label)
        compact_info.addWidget(compact_desc)
        compact_row.addLayout(compact_info)
        compact_row.addStretch()
        appearance_layout.addLayout(compact_row)

        # Custom Title Bar Row
        titlebar_row = QHBoxLayout()
        self.custom_titlebar_checkbox = AnimatedToggleSwitch()
        titlebar_row.addWidget(self.custom_titlebar_checkbox)
        
        titlebar_info = QVBoxLayout()
        titlebar_info.setSpacing(2)
        titlebar_label = QLabel("Custom Title Bar")
        titlebar_label.setObjectName("setting_label")
        titlebar_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        titlebar_desc = QLabel("Use the modern, integrated title bar.")
        titlebar_desc.setObjectName("setting_desc")
        titlebar_desc.setStyleSheet("color: #6c757d; font-size: 11px;")
        titlebar_info.addWidget(titlebar_label)
        titlebar_info.addWidget(titlebar_desc)
        titlebar_row.addLayout(titlebar_info)
        titlebar_row.addStretch()
        appearance_layout.addLayout(titlebar_row)

        layout.addWidget(appearance_container)
        self._add_separator(layout)

        # --- Visualization Section ---
        viz_container = QWidget()
        viz_layout = QVBoxLayout(viz_container)
        viz_layout.setContentsMargins(0, 0, 0, 0)
        viz_layout.setSpacing(16)

        # Header
        viz_header = QLabel("Visualization")
        viz_header.setObjectName("section_label")
        viz_header.setStyleSheet("font-size: 14px; font-weight: 600;")
        viz_layout.addWidget(viz_header)

        # Waveform Row
        waveform_row = QHBoxLayout()
        self.show_waveform_checkbox = AnimatedToggleSwitch()
        self.show_waveform_checkbox.setChecked(True)
        waveform_row.addWidget(self.show_waveform_checkbox)
        
        waveform_info = QVBoxLayout()
        waveform_info.setSpacing(2)
        waveform_label = QLabel("Circular Waveform")
        waveform_label.setObjectName("setting_label")
        waveform_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        waveform_desc = QLabel("Show visual feedback during recording.")
        waveform_desc.setObjectName("setting_desc")
        waveform_desc.setStyleSheet("color: #6c757d; font-size: 11px;")
        waveform_info.addWidget(waveform_label)
        waveform_info.addWidget(waveform_desc)
        waveform_row.addLayout(waveform_info)
        waveform_row.addStretch()
        viz_layout.addLayout(waveform_row)

        # Animation Strength
        strength_label = QLabel("Animation Amplification")
        strength_label.setObjectName("setting_label")
        strength_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        viz_layout.addWidget(strength_label)

        strength_row = QHBoxLayout()
        strength_row.setSpacing(12)
        
        self.animation_strength_slider = ModernSlider(Qt.Orientation.Horizontal)
        self.animation_strength_slider.setRange(1, 10)
        self.animation_strength_slider.setValue(3)
        self.animation_strength_slider.setTickPosition(ModernSlider.TickPosition.TicksBelow)
        self.animation_strength_slider.setTickInterval(1)
        self.animation_strength_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.animation_strength_slider.setPageStep(2)
        self.animation_strength_slider.setSingleStep(1)
        
        self.animation_strength_value_label = QLabel("3x")
        self.animation_strength_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.animation_strength_value_label.setMinimumWidth(40)
        self.animation_strength_value_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.animation_strength_slider.valueChanged.connect(self.update_animation_strength_label)

        strength_row.addWidget(self.animation_strength_slider)
        strength_row.addWidget(self.animation_strength_value_label)
        viz_layout.addLayout(strength_row)

        self.strength_help = QLabel("Higher values make the waveform more responsive to quiet voices.")
        self.strength_help.setObjectName("setting_desc")
        self.strength_help.setStyleSheet("color: #6c757d; font-size: 11px;")
        viz_layout.addWidget(self.strength_help)

        layout.addWidget(viz_container)
        self._add_separator(layout)

        # --- Window Behavior Section ---
        window_container = QWidget()
        window_layout = QVBoxLayout(window_container)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.setSpacing(16)

        # Header
        window_header = QLabel("Window Behavior")
        window_header.setObjectName("section_label")
        window_header.setStyleSheet("font-size: 14px; font-weight: 600;")
        window_layout.addWidget(window_header)

        # Minimize on Close
        min_close_row = QHBoxLayout()
        self.minimize_on_close_checkbox = AnimatedToggleSwitch()
        min_close_row.addWidget(self.minimize_on_close_checkbox)
        
        min_close_info = QVBoxLayout()
        min_close_info.setSpacing(2)
        min_close_label = QLabel("Minimize on Close")
        min_close_label.setObjectName("setting_label")
        min_close_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        min_close_desc = QLabel("Keep running in background when closed.")
        min_close_desc.setObjectName("setting_desc")
        min_close_desc.setStyleSheet("color: #6c757d; font-size: 11px;")
        min_close_info.addWidget(min_close_label)
        min_close_info.addWidget(min_close_desc)
        min_close_row.addLayout(min_close_info)
        min_close_row.addStretch()
        window_layout.addLayout(min_close_row)

        # Minimize to Tray
        min_tray_row = QHBoxLayout()
        self.minimize_to_tray_checkbox = AnimatedToggleSwitch()
        min_tray_row.addWidget(self.minimize_to_tray_checkbox)
        
        min_tray_info = QVBoxLayout()
        min_tray_info.setSpacing(2)
        min_tray_label = QLabel("Minimize to Tray")
        min_tray_label.setObjectName("setting_label")
        min_tray_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        min_tray_desc = QLabel("Hide to system tray icon.")
        min_tray_desc.setObjectName("setting_desc")
        min_tray_desc.setStyleSheet("color: #6c757d; font-size: 11px;")
        min_tray_info.addWidget(min_tray_label)
        min_tray_info.addWidget(min_tray_desc)
        min_tray_row.addLayout(min_tray_info)
        min_tray_row.addStretch()
        
        # Check tray availability
        from PySide6.QtWidgets import QSystemTrayIcon
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.minimize_to_tray_checkbox.setEnabled(False)
            min_tray_desc.setText("System tray not available.")
            
        window_layout.addLayout(min_tray_row)

        # Always on Top
        top_row = QHBoxLayout()
        self.always_on_top_checkbox = AnimatedToggleSwitch()
        top_row.addWidget(self.always_on_top_checkbox)
        
        top_info = QVBoxLayout()
        top_info.setSpacing(2)
        top_label = QLabel("Always on Top")
        top_label.setObjectName("setting_label")
        top_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        top_desc = QLabel("Keep window above others.")
        top_desc.setObjectName("setting_desc")
        top_desc.setStyleSheet("color: #6c757d; font-size: 11px;")
        top_info.addWidget(top_label)
        top_info.addWidget(top_desc)
        top_row.addLayout(top_info)
        top_row.addStretch()
        window_layout.addLayout(top_row)

        # Snap to Edges
        snap_row = QHBoxLayout()
        self.snap_to_edges_checkbox = AnimatedToggleSwitch()
        snap_row.addWidget(self.snap_to_edges_checkbox)
        
        snap_info = QVBoxLayout()
        snap_info.setSpacing(2)
        snap_label = QLabel("Snap to Edges")
        snap_label.setObjectName("setting_label")
        snap_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        snap_desc = QLabel("Snap window to screen edges.")
        snap_desc.setObjectName("setting_desc")
        snap_desc.setStyleSheet("color: #6c757d; font-size: 11px;")
        snap_info.addWidget(snap_label)
        snap_info.addWidget(snap_desc)
        snap_row.addLayout(snap_info)
        snap_row.addStretch()
        window_layout.addLayout(snap_row)

        layout.addWidget(window_container)
        self._add_separator(layout)

        # --- Shortcuts Section ---
        shortcut_container = QWidget()
        shortcut_layout = QVBoxLayout(shortcut_container)
        shortcut_layout.setContentsMargins(0, 0, 0, 0)
        shortcut_layout.setSpacing(16)

        # Header
        shortcut_header = QLabel("Shortcuts")
        shortcut_header.setObjectName("section_label")
        shortcut_header.setStyleSheet("font-size: 14px; font-weight: 600;")
        shortcut_layout.addWidget(shortcut_header)

        # Record Shortcut
        shortcut_label = QLabel("Toggle Recording")
        shortcut_label.setObjectName("setting_label")
        shortcut_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        shortcut_layout.addWidget(shortcut_label)

        self.shortcut_edit = ModernKeySequenceEdit()
        shortcut_layout.addWidget(self.shortcut_edit)

        shortcut_help = QLabel("Click above and press keys to set shortcut. (e.g., Win+Shift+`)")
        shortcut_help.setObjectName("setting_desc")
        shortcut_help.setStyleSheet("color: #6c757d; font-size: 11px;")
        shortcut_layout.addWidget(shortcut_help)

        layout.addWidget(shortcut_container)
        layout.addStretch()

    def _add_separator(self, layout):
        """Add a theme-aware separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        # Default light theme style
        line.setStyleSheet("background-color: #f0f0f0; border: none; max-height: 1px;")
        layout.addWidget(line)
        self.separators.append(line)

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
    def on_theme_changed(self):
        """
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
            theme_manager = get_theme_manager()
            theme_manager.set_theme(theme_data)
            
            # Refresh local slider styling for immediate visual feedback
            self._style_animation_controls(theme_data)

    def apply_theme(self, theme_name):
        """Apply theme to tab specific elements"""
        from ..managers import get_theme_manager
        theme_manager = get_theme_manager()
        colors = theme_manager.get_theme_colors(theme_name)
        is_dark = theme_manager.is_dark_theme()

        # Explicitly set background color to ensure no transparency issues
        self.setStyleSheet(f"background-color: {colors['primary']};")

        # Update Separators
        separator_color = colors.get("border", "#404040" if is_dark else "#f0f0f0")
        for sep in self.separators:
            sep.setStyleSheet(f"background-color: {separator_color}; border: none; max-height: 1px;")

        # Update Labels using shared helper
        apply_label_theme(self, is_dark, colors)

        # Unified theme application for child widgets
        apply_theme_recursively(self, is_dark, colors)

        # Update animation controls
        self._style_animation_controls(theme_name)

    def apply_animation_theme(self, theme_name: str | None = None):
        """Public hook so parent dialog can restyle animation controls on theme changes."""
        self._style_animation_controls(theme_name)
        # Re-apply value badge styling for current slider value
        if hasattr(self, 'animation_strength_slider'):
            self._update_value_badge_style(self.animation_strength_slider.value())
            
        # Also apply theme to other elements
        if theme_name:
             self.apply_theme(theme_name)

    def _style_animation_controls(self, theme_name: str | None = None):
        """Apply cohesive styling to the animation amplification slider and badges."""
        if not hasattr(self, "animation_strength_slider"):
            return

        from ..managers import get_theme_manager
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
        self.animation_strength_slider.apply_theme(is_dark, colors)

    @staticmethod
    def _blend_hex_colors(base_hex: str, blend_hex: str, factor: float) -> str:
        """Blend two hex colors - delegates to ThemeManager for consistency."""
        from ..managers import get_theme_manager
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
            
        from ..managers import get_theme_manager
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
