"""
Main Settings Dialog
Central dialog that manages all settings tabs
"""

import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QSizePolicy, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor

from ..config_manager import ConfigManager
from ..managers import StatisticsManager, get_theme_manager
from ..icon_manager import get_icon, get_white_button_icon, get_button_icon
from .audio_tab import AudioTab
from .whisper_tab import WhisperTab
from .output_tab import OutputTab
from .ui_tab import UITab
from .statistics_tab import StatisticsTab
from .modern_widgets import (
    ModernGroupBox, ModernComboBox, ModernLineEdit,
    ModernKeySequenceEdit, ModernRadioButton, ModernCheckBox
)


class SettingsDialog(QDialog):
    """Beautiful settings dialog with tabbed interface"""

    # Signal emitted when settings are saved
    settings_saved = Signal()

    # Theme color definitions
    THEMES = {
        "white": {"primary": "#ffffff", "secondary": "#f8f9fa"},
        "warm_gray": {"primary": "#f5f5f5", "secondary": "#fafafa"},
        "soft_beige": {"primary": "#f8f6f0", "secondary": "#fefefe"},
        "blue_gray": {"primary": "#f0f2f5", "secondary": "#f8fafc"},
        "warm_taupe": {"primary": "#f7f3f0", "secondary": "#faf9f7"},
        "soft_sage": {"primary": "#f7f9f6", "secondary": "#f8faf9"},
        # Dark theme variations
        "dark_charcoal": {"primary": "#2c2c2c", "secondary": "#1e1e1e"},
        "dark_blue": {"primary": "#1a1f2e", "secondary": "#13182a"},
        "dark_purple": {"primary": "#2d1b3d", "secondary": "#241736"},
        "dark_forest": {"primary": "#1e2a1e", "secondary": "#152015"},
        "dark_burgundy": {"primary": "#2a1a1a", "secondary": "#1f1212"}
    }

    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        # Use shared config manager from parent if provided, otherwise create new one
        self.config_manager = config_manager if config_manager is not None else ConfigManager()

        # Initialize statistics manager
        self.statistics_manager = StatisticsManager(self.config_manager)

        self.setup_ui()
        self.setModal(True)
        # Apply initial theme
        initial_theme = self.config_manager.get_setting("ui/theme", "white")
        self.apply_theme(initial_theme)

    def setup_ui(self):
        self.setWindowTitle("QuillScribe Settings")
        self.setFixedSize(600, 650)  # Increased height for better content visibility
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)  # Reduced spacing for compact layout
        layout.setContentsMargins(15, 15, 15, 15)  # Reduced margins for compact layout

        # Title - smaller for compact layout
        title = QLabel("Settings")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: 400;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title)

        # Tab widget - increased height for better usability
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabs.setMaximumHeight(450)  # Increased height for better content visibility
        # Tab styling will be set by apply_tab_theme method
        self.apply_tab_theme("white")

        # Create tabs - pass audio manager to audio tab for shared state
        audio_manager = getattr(self.parent(), 'audio_manager', None) if self.parent() else None
        self.audio_tab = AudioTab(self.config_manager, audio_manager)
        self.whisper_tab = WhisperTab(self.config_manager)
        self.output_tab = OutputTab(self.config_manager)
        self.ui_tab = UITab(self.config_manager)
        self.statistics_tab = StatisticsTab(self.statistics_manager)

        # Wrap each tab in a scroll area for compact layout
        self.audio_scroll = self._create_scroll_area(self.audio_tab)
        self.whisper_scroll = self._create_scroll_area(self.whisper_tab)
        self.output_scroll = self._create_scroll_area(self.output_tab)
        self.ui_scroll = self._create_scroll_area(self.ui_tab)
        self.statistics_scroll = self._create_scroll_area(self.statistics_tab)

        self.tabs.addTab(self.audio_scroll, "Audio")
        self.tabs.setTabIcon(self.tabs.indexOf(self.audio_scroll), get_icon('audio', 16))
        self.tabs.addTab(self.whisper_scroll, "Whisper")
        self.tabs.setTabIcon(self.tabs.indexOf(self.whisper_scroll), get_icon('brain', 16))
        self.tabs.addTab(self.output_scroll, "Output")
        self.tabs.setTabIcon(self.tabs.indexOf(self.output_scroll), get_icon('clipboard', 16))
        self.tabs.addTab(self.ui_scroll, "UI Settings")
        self.tabs.setTabIcon(self.tabs.indexOf(self.ui_scroll), get_icon('settings', 16))
        self.tabs.addTab(self.statistics_scroll, "Statistics")
        self.tabs.setTabIcon(self.tabs.indexOf(self.statistics_scroll), get_icon('dashboard', 16))

        layout.addWidget(self.tabs)

        # Buttons with compact spacing
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # Reduced button spacing for compact layout
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setIcon(get_white_button_icon('cancel', 16))
        self.cancel_button.setIconSize(QSize(16, 16))
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px 10px 36px;
                font-size: 14px;
                min-width: 80px;
                text-align: left;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)

        self.save_button = QPushButton("Save Settings")
        self.save_button.setIcon(get_white_button_icon('save', 16))
        self.save_button.setIconSize(QSize(16, 16))
        self.save_button.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 80px;
                text-align: center;
            }
            QPushButton:hover {
                background: #357ABD;
            }
        """)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        # Connect buttons
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.save_and_close)

    def _create_scroll_area(self, widget):
        """Create a scroll area with custom themed scrollbars for the given widget"""
        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Apply custom scrollbar styling (will be updated by theme)
        self._apply_scrollbar_theme(scroll_area, "white")

        return scroll_area

    def _apply_scrollbar_theme(self, scroll_area, theme_name):
        """Apply modern themed styling to scrollbar using centralized theme manager"""
        theme_manager = get_theme_manager()

        # Use the new centralized scrollbar styling system with responsive design
        theme_manager.apply_modern_scrollbar_to_widget(
            scroll_area,
            theme_name=theme_name,
            responsive=True  # Enable responsive sizing for better UX
        )

    def save_and_close(self):
        """Save all settings and close dialog"""
        try:
            self.audio_tab.save_settings()
            self.whisper_tab.save_settings()
            self.output_tab.save_settings()
            self.ui_tab.save_settings()
            self.config_manager.save_settings()

            # Emit signal to notify main window that settings were saved
            self.settings_saved.emit()

            self.accept()
        except Exception as e:
            # Could show an error dialog here
            print(f"Error saving settings: {e}")

    def apply_theme(self, theme_name):
        """Apply the selected theme to the dialog background and all group boxes"""
        # Use theme manager for consistent theming
        theme_manager = get_theme_manager()
        theme_manager.set_theme(theme_name)

        colors = self._get_theme_colors(theme_name)

        # Apply to dialog background
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors["primary"]}, stop:1 {colors["secondary"]});
                color: {colors["text_primary"]};
            }}
        """)

        # Apply to all group boxes in all tabs
        self._apply_theme_to_group_boxes(colors)

        # Apply theme to all modern widgets
        is_dark = self._is_dark_color(colors["primary"])
        # ComboBox needs accent/border injection
        for combo in self.findChildren(ModernComboBox):
            combo.apply_theme(is_dark, colors["accent"], colors["border"])
        # Other widgets keep existing signature
        for widget in self.findChildren(ModernLineEdit):
            widget.apply_theme(is_dark)
        for widget in self.findChildren(ModernKeySequenceEdit):
            widget.apply_theme(is_dark)
        for widget in self.findChildren(ModernRadioButton):
            widget.apply_theme(is_dark)
        for widget in self.findChildren(ModernCheckBox):
            widget.apply_theme(is_dark)

        # Apply unified icon theming to all components
        theme_manager.apply_icons_to_widget(self, is_dark)

        # Apply comprehensive text theming to all labels
        theme_manager.apply_text_theming_to_widget(self, theme_name)

        # Allow UI tab to refresh its custom slider styling for this theme
        if hasattr(self, 'ui_tab') and hasattr(self.ui_tab, 'apply_animation_theme'):
            self.ui_tab.apply_animation_theme(theme_name)

        # Update API key toggle icon for current theme
        if hasattr(self, 'api_key_toggle_btn'):
            self._update_api_key_toggle_icon()

        # Update important form labels for dark/light (specific styling for form labels)
        is_dark = self._is_dark_color(colors["primary"])
        label_primary = "#ffffff" if is_dark else "#495057"
        muted = "#e0e0e0" if is_dark else "#6c757d"
        for lbl in self.findChildren(QLabel):
            name = lbl.objectName()
            if name in {"form_label", "theme_label", "shortcut_label"}:
                lbl.setStyleSheet(f"QLabel {{ color: {label_primary}; font-size: 13px; font-weight: 500; background-color: transparent; }}")

        # Apply theme to tabs
        self.apply_tab_theme(theme_name)

        # Apply theme to scrollbars and their backgrounds
        scroll_areas = []
        if hasattr(self, 'audio_scroll'):
            scroll_areas.append(self.audio_scroll)
        if hasattr(self, 'whisper_scroll'):
            scroll_areas.append(self.whisper_scroll)
        if hasattr(self, 'output_scroll'):
            scroll_areas.append(self.output_scroll)
        if hasattr(self, 'ui_scroll'):
            scroll_areas.append(self.ui_scroll)
        if hasattr(self, 'statistics_scroll'):
            scroll_areas.append(self.statistics_scroll)

        for scroll_area in scroll_areas:
            # Apply modern scrollbar styling
            self._apply_scrollbar_theme(scroll_area, theme_name)

            # Apply background colors for dynamic theming
            scroll_area.setStyleSheet(scroll_area.styleSheet() + f"""
                QScrollArea {{
                    border: none;
                    background-color: {colors["primary"]};
                }}
                QScrollArea > QWidget#qt_scrollarea_viewport {{
                    background-color: {colors["primary"]};
                }}
                QWidget#qt_scrollarea_viewport {{
                    background-color: {colors["primary"]};
                }}
            """)

        # Apply theme to icons
        self._apply_icon_theme(is_dark)

        # Explicitly set background for tab content widgets to match theme
        # This ensures areas not covered by group boxes don't appear dark
        try:
            if hasattr(self, 'audio_tab'):
                self.audio_tab.setStyleSheet(f"background-color: {colors['primary']};")
            if hasattr(self, 'whisper_tab'):
                self.whisper_tab.setStyleSheet(f"background-color: {colors['primary']};")
            if hasattr(self, 'output_tab'):
                self.output_tab.setStyleSheet(f"background-color: {colors['primary']};")
            if hasattr(self, 'ui_tab'):
                self.ui_tab.setStyleSheet(f"background-color: {colors['primary']};")
        except Exception:
            pass

    def _apply_theme_to_group_boxes(self, colors):
        """Apply theme to all ModernGroupBox instances"""
        # Find all ModernGroupBox widgets in the dialog
        for widget in self.findChildren(ModernGroupBox):
            widget.apply_theme(colors["primary"], colors["secondary"])

    def _darken_color(self, hex_color, factor=0.15):
        """Darken a hex color by the given factor (0.0 to 1.0)"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')

        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Darken by reducing values
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def _lighten_color(self, hex_color, factor=0.15):
        """Lighten a hex color by the given factor (0.0 to 1.0)"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')

        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Lighten by increasing values towards 255
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def _apply_icon_theme(self, is_dark: bool):
        """Apply appropriate icon colors based on dark/light theme"""
        # Update tab icons
        if hasattr(self, 'tabs'):
            # Audio tab
            audio_index = None
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == "Audio":
                    audio_index = i
                    break
            if audio_index is not None:
                if is_dark:
                    self.tabs.setTabIcon(audio_index, get_icon('audio', 16, QColor(255, 255, 255)))
                else:
                    self.tabs.setTabIcon(audio_index, get_icon('audio', 16))

            # Whisper tab
            whisper_index = None
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == "Whisper":
                    whisper_index = i
                    break
            if whisper_index is not None:
                if is_dark:
                    self.tabs.setTabIcon(whisper_index, get_icon('brain', 16, QColor(255, 255, 255)))
                else:
                    self.tabs.setTabIcon(whisper_index, get_icon('brain', 16))

            # Output tab
            output_index = None
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == "Output":
                    output_index = i
                    break
            if output_index is not None:
                if is_dark:
                    self.tabs.setTabIcon(output_index, get_icon('clipboard', 16, QColor(255, 255, 255)))
                else:
                    self.tabs.setTabIcon(output_index, get_icon('clipboard', 16))

            # UI Settings tab
            ui_index = None
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == "UI Settings":
                    ui_index = i
                    break
            if ui_index is not None:
                if is_dark:
                    self.tabs.setTabIcon(ui_index, get_icon('settings', 16, QColor(255, 255, 255)))
                else:
                    self.tabs.setTabIcon(ui_index, get_icon('settings', 16))

        # Update save and cancel button icons and styles based on theme
        if hasattr(self, 'cancel_button'):
            # Cancel button - colored background with white icon (both themes)
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px 10px 36px;
                    font-size: 14px;
                    min-width: 80px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            # Always use white icon on grey background for maximum contrast
            self.cancel_button.setIcon(get_icon('cancel', 16, QColor(255, 255, 255)))
            self.cancel_button.setIconSize(QSize(16, 16))
        
        if hasattr(self, 'save_button'):
            # Save button - colored background with white icon (both themes)
            self.save_button.setStyleSheet("""
                QPushButton {
                    background-color: #4A90E2;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 14px;
                    min-width: 80px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #357ABD;
                }
            """)
            # Always use white icon on blue background for maximum contrast
            self.save_button.setIcon(get_icon('save', 16, QColor(255, 255, 255)))
            self.save_button.setIconSize(QSize(16, 16))

        # Update icons in tab content - these need to be updated based on theme
        try:
            # Audio tab icons
            if hasattr(self, 'audio_tab'):
                # Find and update refresh button
                for button in self.audio_tab.findChildren(QPushButton):
                    if hasattr(button, 'objectName') and 'refresh' in str(button.objectName()).lower():
                        if is_dark:
                            button.setIcon(get_white_button_icon('refresh', 16))
                        else:
                            button.setIcon(get_button_icon('refresh', 16))
                    elif 'detect' in button.text().lower():
                        if is_dark:
                            button.setIcon(get_white_button_icon('refresh', 14))
                        else:
                            button.setIcon(get_button_icon('refresh', 14))

                # Find and update checkbox icons
                for checkbox in self.audio_tab.findChildren(ModernCheckBox):
                    if 'auto' in checkbox.text().lower():
                        if is_dark:
                            checkbox.setIcon(get_white_button_icon('sound', 16))
                        else:
                            checkbox.setIcon(get_button_icon('sound', 16))

            # Whisper tab icons
            if hasattr(self, 'whisper_tab'):
                # Find and update test buttons
                for button in self.whisper_tab.findChildren(QPushButton):
                    if 'test' in button.text().lower():
                        if is_dark:
                            button.setIcon(get_white_button_icon('test', 16))
                        else:
                            button.setIcon(get_button_icon('test', 16))

                # Find and update radio button icons
                for radio in self.whisper_tab.findChildren(ModernRadioButton):
                    if 'api' in radio.text().lower():
                        if is_dark:
                            radio.setIcon(get_white_button_icon('api', 16))
                        else:
                            radio.setIcon(get_button_icon('api', 16))
                    elif 'local' in radio.text().lower():
                        if is_dark:
                            radio.setIcon(get_white_button_icon('local', 16))
                        else:
                            radio.setIcon(get_button_icon('local', 16))

                # Also recolor form-related icons
                for lbl in self.whisper_tab.findChildren(QLabel):
                    name = lbl.objectName()
                    if name == 'icon_api_key':
                        lbl.setPixmap((get_icon('key', 16, QColor(255, 255, 255)) if is_dark else get_icon('key', 16)).pixmap(16, 16))
                    elif name == 'icon_api_model':
                        lbl.setPixmap((get_icon('brain', 16, QColor(255, 255, 255)) if is_dark else get_icon('brain', 16)).pixmap(16, 16))
                    elif name == 'icon_api_language':
                        lbl.setPixmap((get_icon('language', 16, QColor(255, 255, 255)) if is_dark else get_icon('language', 16)).pixmap(16, 16))
                    elif name == 'icon_category':
                        lbl.setPixmap((get_icon('category', 16, QColor(255, 255, 255)) if is_dark else get_icon('category', 16)).pixmap(16, 16))
                    elif name == 'icon_model':
                        lbl.setPixmap((get_icon('brain', 16, QColor(255, 255, 255)) if is_dark else get_icon('brain', 16)).pixmap(16, 16))

            # Output tab icons are now handled automatically by theme manager

                # Find and update checkbox icons
                for checkbox in self.output_tab.findChildren(ModernCheckBox):
                    text = checkbox.text().lower()
                    if 'silent' in text:
                        if is_dark:
                            checkbox.setIcon(get_white_button_icon('silent', 16))
                        else:
                            checkbox.setIcon(get_button_icon('silent', 16))
                    elif 'auto clear' in text or 'clear' in text:
                        if is_dark:
                            checkbox.setIcon(get_white_button_icon('trash', 16))
                        else:
                            checkbox.setIcon(get_button_icon('trash', 16))

            # UI tab icons are now handled automatically by theme manager

                # Update theme icon and shortcut icon in the UI tab
                if hasattr(self.ui_tab, 'findChildren'):
                    for label in self.ui_tab.findChildren(QLabel):
                        # Look for the theme icon label
                        if hasattr(label, 'pixmap') and label.pixmap() is not None:
                            # Check if this is likely the theme icon (has a pixmap and is near theme-related text)
                            parent = label.parent()
                            if getattr(label, 'objectName', lambda: '')() == 'icon_theme':
                                label.setPixmap((get_icon('settings', 16, QColor(255, 255, 255)) if is_dark else get_icon('settings', 16)).pixmap(16, 16))
                            if getattr(label, 'objectName', lambda: '')() == 'icon_shortcut':
                                label.setPixmap((get_icon('keyboard', 16, QColor(255, 255, 255)) if is_dark else get_icon('keyboard', 16)).pixmap(16, 16))
        except Exception as e:
            print(f"Error updating icon theme: {e}")

    def _is_dark_color(self, hex_color):
        """Determine if a color is dark based on its luminance"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')

        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Calculate luminance using standard formula
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5

    def _get_theme_colors(self, theme_name):
        """Get comprehensive color scheme for a theme"""
        theme = self.THEMES.get(theme_name, self.THEMES["white"])
        primary_color = theme["primary"]
        secondary_color = theme["secondary"]
        is_dark = self._is_dark_color(primary_color)

        if is_dark:
            return {
                "primary": primary_color,
                "secondary": secondary_color,
                "text_primary": "#ffffff",
                "text_secondary": "#e0e0e0",
                "text_muted": "#b0b0b0",
                "border": "#555555",
                "border_light": "#666666",
                "accent": "#4A90E2",
                "accent_hover": "#5BA0F2"
            }
        else:
            return {
                "primary": primary_color,
                "secondary": secondary_color,
                "text_primary": "#2c3e50",
                "text_secondary": "#495057",
                "text_muted": "#6c757d",
                "border": "#dee2e6",
                "border_light": "#adb5bd",
                "accent": "#4A90E2",
                "accent_hover": "#357ABD"
            }

    def apply_tab_theme(self, theme_name):
        """Apply theme-aware styling to tabs"""
        colors = self._get_theme_colors(theme_name)
        is_dark = self._is_dark_color(colors["primary"])

        # Create appropriate accent colors for tabs
        if is_dark:
            active_bg = self._lighten_color(colors["primary"], 0.15)
            active_border = self._lighten_color(colors["primary"], 0.3)
            hover_bg = self._lighten_color(colors["primary"], 0.08)
        else:
            active_bg = self._darken_color(colors["primary"], 0.08)
            active_border = self._darken_color(colors["primary"], 0.2)
            hover_bg = self._darken_color(colors["primary"], 0.04)

        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {colors["border"]};
                border-radius: 8px;
                background-color: {colors["primary"]};
            }}
            QTabWidget::tab-bar {{

            }}
            QTabBar::tab {{
                background: {colors["secondary"]};
                color: {colors["text_secondary"]};
                border: 2px solid {colors["border"]};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 16px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: 500;
                outline: none;
            }}
            QTabBar::tab:selected {{
                background: {active_bg};
                color: {colors["text_primary"]};
                border-color: {active_border};
                border-bottom: 2px solid {active_bg};
                font-weight: 500;
                outline: none;
            }}
            QTabBar::tab:hover {{
                background: {hover_bg};
                color: {colors["text_primary"]};
                border-color: {colors["border_light"]};
                outline: none;
            }}
            QTabBar::tab:selected:hover {{
                background: {active_bg};
                color: {colors["text_primary"]};
                border-color: {active_border};
                outline: none;
            }}
        """)

    def closeEvent(self, event):
        """Handle dialog close event"""
        try:
            # Clean up audio tab resources
            if hasattr(self, 'audio_tab'):
                self.audio_tab.cleanup()
        except Exception as e:
            print(f"Error during SettingsDialog cleanup: {e}")
        event.accept()
