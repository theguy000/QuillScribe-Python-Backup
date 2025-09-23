"""
Main Settings Dialog for QuillScribe
Modular settings management with tabbed interface
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton,
    QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from ..config_manager import ConfigManager
from ..statistics_manager import StatisticsManager
from ..icon_manager import get_icon, get_white_button_icon, get_themed_button_icon, get_themed_icon
from ..theme_manager import get_theme_manager
from .base_tab import create_scroll_area
from .statistics_tab import StatisticsTab


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
        self.setFixedSize(650, 700)  # Increased size for statistics tab
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)  # Further reduced spacing from 8 to 6
        layout.setContentsMargins(15, 8, 15, 15)  # Further reduced top margin from 10 to 8

        # Title with reduced spacing and smaller font
        title = QLabel("Settings")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 16px;
                font-weight: 400;
                margin-bottom: 0px;
                padding-bottom: 0px;
            }
        """)
        layout.addWidget(title)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabs.setMaximumHeight(500)  # Increased for statistics content
        self.apply_tab_theme("white")

        # Create tabs - import from existing settings_dialog.py for now
        # TODO: Move individual tabs to separate files
        from ..settings_dialog import AudioTab, WhisperTab, OutputTab, UITab
        
        audio_manager = getattr(self.parent(), 'audio_manager', None) if self.parent() else None
        self.audio_tab = AudioTab(self.config_manager, audio_manager)
        self.whisper_tab = WhisperTab(self.config_manager)
        self.output_tab = OutputTab(self.config_manager)
        self.ui_tab = UITab(self.config_manager)
        self.statistics_tab = StatisticsTab(self.statistics_manager)

        # Wrap each tab in a scroll area
        self.audio_scroll = create_scroll_area(self.audio_tab)
        self.whisper_scroll = create_scroll_area(self.whisper_tab)
        self.output_scroll = create_scroll_area(self.output_tab)
        self.ui_scroll = create_scroll_area(self.ui_tab)
        self.statistics_scroll = create_scroll_area(self.statistics_tab)

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

        # Connect to theme changes from UI tab after everything is set up
        if hasattr(self.ui_tab, 'theme_dropdown'):
            self.ui_tab.theme_dropdown.currentIndexChanged.connect(self._on_theme_changed_from_ui_tab)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setIcon(get_white_button_icon('cancel', 16))
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save Settings")
        self.save_button.setIcon(get_white_button_icon('save', 16))
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def apply_theme(self, theme_name: str):
        """Apply theme to the dialog"""
        if theme_name not in self.THEMES:
            theme_name = "white"

        # Use theme manager for consistent theming
        theme_manager = get_theme_manager()
        theme_manager.set_theme(theme_name)

        theme = self.THEMES[theme_name]
        primary_color = theme["primary"]
        secondary_color = theme["secondary"]

        # Get dark theme status from theme manager
        is_dark = theme_manager.is_dark_theme()

        # Apply theme to tabs
        self.apply_tab_theme(theme_name)

        # Apply theme to individual tabs
        # Statistics tab has its own apply_theme method
        if hasattr(self.statistics_tab, 'apply_theme'):
            self.statistics_tab.apply_theme(primary_color, secondary_color)

        # Apply theme to the original tabs using the same approach as the original dialog
        # We'll replicate the key parts of the original theming system here
        self._apply_original_tab_theming(theme_name)

        # Apply unified icon theming to all components
        theme_manager.apply_icons_to_widget(self, is_dark)

        # Apply icon theming for SVG icons (legacy method for any missed icons)
        self._apply_icon_theming(is_dark)

        # Update scroll area backgrounds for dynamic theming
        self._update_scroll_area_backgrounds(theme_name)

        # Apply button theming (icons and colors)
        self._apply_button_theming(is_dark)

        # Apply text theming to all labels
        theme_manager.apply_text_theming_to_widget(self, theme_name)

        # Explicitly set background and text colors for tab content widgets to match theme
        # Use darker text for light themes to ensure better legibility
        text_color = "#e9ecef" if is_dark else "#212529"
        try:
            tab_style = f"""
                background-color: {primary_color};
                color: {text_color};
            """
            self.audio_tab.setStyleSheet(tab_style)
            self.whisper_tab.setStyleSheet(tab_style)
            self.output_tab.setStyleSheet(tab_style)
            self.ui_tab.setStyleSheet(tab_style)

            # Apply label theming to all tabs
            for tab in [self.audio_tab, self.whisper_tab, self.output_tab, self.ui_tab]:
                self._apply_label_theming(tab, text_color)

        except Exception as e:
            print(f"Warning: Could not apply tab background theme: {e}")

        # Apply theme to dialog background
        # Use the is_dark variable already calculated above
        if is_dark:
            dialog_style = f"""
                QDialog {{
                    background-color: {primary_color};
                    color: #e9ecef;
                }}
                QLabel {{
                    color: #e9ecef;
                }}
                QPushButton {{
                    background-color: #495057;
                    color: #e9ecef;
                    border: 1px solid #6c757d;
                    border-radius: 4px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: #6c757d;
                }}
                QPushButton:pressed {{
                    background-color: #343a40;
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
                QPushButton {{
                    background-color: #e9ecef;
                    color: #495057;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: #f8f9fa;
                }}
                QPushButton:pressed {{
                    background-color: #dee2e6;
                }}
            """

        self.setStyleSheet(dialog_style)

    def apply_tab_theme(self, theme_name: str):
        """Apply theme to tab widget"""
        if theme_name not in self.THEMES:
            theme_name = "white"
        
        theme = self.THEMES[theme_name]
        primary_color = theme["primary"]
        secondary_color = theme["secondary"]
        
        # Determine if this is a dark theme
        r = int(primary_color.lstrip('#')[0:2], 16)
        g = int(primary_color.lstrip('#')[2:4], 16)
        b = int(primary_color.lstrip('#')[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        is_dark = brightness < 128
        
        if is_dark:
            tab_style = f"""
                QTabWidget::pane {{
                    border: 1px solid #495057;
                    background-color: {secondary_color};
                }}
                QTabBar::tab {{
                    background-color: #495057;
                    color: #e9ecef;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }}
                QTabBar::tab:selected {{
                    background-color: {secondary_color};
                    color: #ffffff;
                    border: 1px solid #6c757d;
                    border-bottom: none;
                }}
                QTabBar::tab:hover {{
                    background-color: #6c757d;
                }}
            """
        else:
            tab_style = f"""
                QTabWidget::pane {{
                    border: 1px solid #dee2e6;
                    background-color: {secondary_color};
                }}
                QTabBar::tab {{
                    background-color: #e9ecef;
                    color: #495057;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }}
                QTabBar::tab:selected {{
                    background-color: {secondary_color};
                    color: #2c3e50;
                    border: 1px solid #dee2e6;
                    border-bottom: none;
                    font-weight: 500;
                }}
                QTabBar::tab:hover {{
                    background-color: #f8f9fa;
                }}
            """
        
        self.tabs.setStyleSheet(tab_style)

    def save_settings(self):
        """Save all settings"""
        # Save settings from each tab
        self.audio_tab.save_settings()
        self.whisper_tab.save_settings()
        self.output_tab.save_settings()
        self.ui_tab.save_settings()
        
        # Statistics tab doesn't have settings to save
        
        self.settings_saved.emit()
        self.accept()

    def _apply_label_theming(self, tab_widget, text_color):
        """Apply text color theming to all labels in a tab"""
        try:
            # Find all QLabel widgets in the tab and apply text color
            from PySide6.QtWidgets import QLabel
            for label in tab_widget.findChildren(QLabel):
                # Skip labels that already have specific styling (like help text)
                current_style = label.styleSheet()
                if 'color:' not in current_style or '#6c757d' in current_style:
                    # Apply theme color, but preserve other styling
                    if '#6c757d' in current_style:
                        # This is help text, use a muted version of the theme color
                        if text_color == "#e9ecef":  # Dark theme
                            muted_color = "#adb5bd"
                        else:  # Light theme
                            muted_color = "#6c757d"
                        new_style = current_style.replace('#6c757d', muted_color)
                        label.setStyleSheet(new_style)
                    else:
                        # Regular label, apply theme color
                        if current_style:
                            label.setStyleSheet(f"{current_style}; color: {text_color};")
                        else:
                            label.setStyleSheet(f"color: {text_color};")
        except Exception as e:
            print(f"Warning: Could not apply label theming: {e}")

    def _apply_original_tab_theming(self, theme_name: str):
        """Apply theming to original tabs using the same approach as OriginalSettingsDialog"""
        try:
            # Import the original theming functions
            from ..settings_dialog import SettingsDialog as OriginalSettingsDialog

            # Get theme colors using the original method
            temp_dialog = OriginalSettingsDialog.__new__(OriginalSettingsDialog)
            colors = temp_dialog._get_theme_colors(theme_name)
            is_dark = temp_dialog._is_dark_color(colors["primary"])

            # Apply to all group boxes in all tabs (same as original)
            from ..ui_components import ModernGroupBox
            for widget in [self.audio_tab, self.whisper_tab, self.output_tab, self.ui_tab]:
                for group_box in widget.findChildren(ModernGroupBox):
                    group_box.apply_theme(colors["primary"], colors["secondary"])

            # Apply theme to modern widgets that actually exist in ui_components
            # Note: Only ModernButton and ModernGroupBox are available in ui_components.py
            # Other modern widgets are defined in settings_dialog.py
            try:
                # Import the modern widgets from the original settings_dialog
                from ..settings_dialog import ModernComboBox, ModernLineEdit, ModernKeySequenceEdit, ModernRadioButton, ModernCheckBox

                for widget in [self.audio_tab, self.whisper_tab, self.output_tab, self.ui_tab]:
                    # ComboBox needs accent/border injection
                    for combo in widget.findChildren(ModernComboBox):
                        combo.apply_theme(is_dark, colors["accent"], colors["border"])
                    # Other widgets keep existing signature
                    for modern_widget in widget.findChildren(ModernLineEdit):
                        modern_widget.apply_theme(is_dark)
                    for modern_widget in widget.findChildren(ModernKeySequenceEdit):
                        modern_widget.apply_theme(is_dark)
                    for modern_widget in widget.findChildren(ModernRadioButton):
                        modern_widget.apply_theme(is_dark)
                    for modern_widget in widget.findChildren(ModernCheckBox):
                        modern_widget.apply_theme(is_dark)
            except ImportError as e:
                print(f"Note: Some modern widgets not available for theming: {e}")

        except Exception as e:
            print(f"Warning: Could not apply original tab theming: {e}")

    def _on_theme_changed_from_ui_tab(self):
        """Handle theme change from UI tab dropdown"""
        try:
            theme_data = self.ui_tab.theme_dropdown.currentData()
            if theme_data:
                # Apply theme to this dialog immediately
                self.apply_theme(theme_data)

                # Also apply to main window if it exists
                main_window = self.parent()
                if main_window and hasattr(main_window, 'apply_theme'):
                    main_window.apply_theme(theme_data)
        except Exception as e:
            print(f"Warning: Could not handle theme change: {e}")

    def _update_scroll_area_backgrounds(self, theme_name: str):
        """Update scroll area backgrounds for dynamic theming"""
        from .base_tab import apply_scroll_area_background

        # Find all scroll areas in the dialog and update their backgrounds
        for scroll_area in self.findChildren(QScrollArea):
            apply_scroll_area_background(scroll_area, theme_name)

    def _apply_button_theming(self, is_dark: bool):
        """Apply themed icons to buttons"""
        from ..icon_manager import get_themed_button_icon

        # Update cancel and save button icons
        if hasattr(self, 'cancel_button'):
            self.cancel_button.setIcon(get_themed_button_icon('cancel', 16, is_dark))
        if hasattr(self, 'save_button'):
            self.save_button.setIcon(get_themed_button_icon('save', 16, is_dark))

    def _apply_icon_theming(self, is_dark: bool):
        """Apply appropriate icon colors based on dark/light theme"""
        try:
            from ..icon_manager import get_icon, get_button_icon, get_white_button_icon, get_themed_button_icon, get_themed_icon
            from PySide6.QtGui import QColor

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

                # Statistics tab
                stats_index = None
                for i in range(self.tabs.count()):
                    if self.tabs.tabText(i) == "Statistics":
                        stats_index = i
                        break
                if stats_index is not None:
                    if is_dark:
                        self.tabs.setTabIcon(stats_index, get_icon('dashboard', 16, QColor(255, 255, 255)))
                    else:
                        self.tabs.setTabIcon(stats_index, get_icon('dashboard', 16))

            # Update icons in tabs content
            self._apply_tab_content_icon_theming(is_dark)

        except Exception as e:
            print(f"Warning: Could not apply icon theming: {e}")

    def _apply_tab_content_icon_theming(self, is_dark: bool):
        """Apply icon theming to content within tabs"""
        try:
            from ..icon_manager import get_button_icon, get_white_button_icon
            from ..settings_dialog import ModernRadioButton, ModernCheckBox

            # Output tab icons are now handled automatically by theme manager

            # UI tab icons are now handled automatically by theme manager

        except Exception as e:
            print(f"Warning: Could not apply tab content icon theming: {e}")


# Import UISettingsDialog from the original file for now
# TODO: Move to separate file
from ..settings_dialog import UISettingsDialog
