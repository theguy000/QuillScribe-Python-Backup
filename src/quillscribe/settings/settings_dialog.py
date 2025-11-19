"""
Main Settings Dialog
Central dialog that manages all settings tabs
"""

import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QSizePolicy, QScrollArea, QMessageBox,
    QStackedWidget
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
    ModernKeySequenceEdit, ModernRadioButton, ModernCheckBox,
    AnimatedToggleSwitch
)


class SettingsDialog(QDialog):
    """Beautiful settings dialog with tabbed interface"""

    # Signal emitted when settings are saved
    settings_saved = Signal()

    # Theme colors are now centralized in ThemeManager
    # Access via get_theme_manager().get_theme_colors(theme_name)

    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        # Use shared config manager from parent if provided, otherwise create new one
        self.config_manager = config_manager if config_manager is not None else ConfigManager()

        # Initialize statistics manager
        self.statistics_manager = StatisticsManager(self.config_manager)
        
        # Theme application state to prevent recursion
        self._applying_theme = False

        self.setup_ui()
        self.setModal(True)

        # Connect to theme manager for live theme updates BEFORE applying initial theme
        # This ensures the dialog receives the theme_changed signal during initialization
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Apply initial theme
        initial_theme = self.config_manager.get_setting("ui/theme", "white")
        self.apply_theme(initial_theme)

    def setup_ui(self):
        self.setWindowTitle("QuillScribe Settings")
        self.setFixedSize(900, 640)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Top header bar
        header = QWidget()
        header.setObjectName("settings_header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 10, 16, 10)
        header_layout.setSpacing(8)

        title_container = QVBoxLayout()
        title_container.setContentsMargins(0, 0, 0, 0)
        title_label = QLabel("QuillScribe Settings")
        title_label.setObjectName("settings_title")
        subtitle_label = QLabel("Tune QuillScribe to match how you work.")
        subtitle_label.setObjectName("settings_subtitle")
        title_container.addWidget(title_label)
        title_container.addWidget(subtitle_label)
        header_layout.addLayout(title_container)
        header_layout.addStretch()

        self.header_close_button = QPushButton()
        self.header_close_button.setObjectName("settings_header_close")
        self.header_close_button.setText("")
        self.header_close_button.setFixedSize(28, 28)
        self.header_close_button.clicked.connect(self.reject)
        header_layout.addWidget(self.header_close_button)

        layout.addWidget(header)

        # Main content area with sidebar and content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Left sidebar navigation
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setSpacing(4)
        sidebar_layout.setContentsMargins(8, 8, 8, 8)

        # Create navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("Audio", "audio"),
            ("Whisper", "brain"),
            ("Output", "clipboard"),
            ("UI Settings", "settings"),
            ("Statistics", "dashboard")
        ]

        for idx, (text, icon_name) in enumerate(nav_items):
            btn = QPushButton(text)
            btn.setIcon(get_icon(icon_name, 16))
            btn.setIconSize(QSize(16, 16))
            btn.setCheckable(True)
            btn.setObjectName(f"nav_btn_{idx}")
            btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(40)
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()
        content_layout.addWidget(self.sidebar)

        # Right content area with stacked widget
        self.content_stack = QWidget()
        self.content_stack.setObjectName("content_stack")
        stack_layout = QVBoxLayout(self.content_stack)
        # Minimal margins so tab content aligns closely with dialog edges
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.setSpacing(0)

        # Create stacked widget to hold all pages
        from PySide6.QtWidgets import QStackedWidget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create tabs - pass audio manager to audio tab for shared state
        audio_manager = getattr(self.parent(), 'audio_manager', None) if self.parent() else None
        self.audio_tab = AudioTab(self.config_manager, audio_manager)
        self.whisper_tab = WhisperTab(self.config_manager)
        self.output_tab = OutputTab(self.config_manager)
        self.ui_tab = UITab(self.config_manager)
        self.statistics_tab = StatisticsTab(self.statistics_manager)

        # Wrap each tab in a scroll area
        self.audio_scroll = self._create_scroll_area(self.audio_tab)
        self.whisper_scroll = self._create_scroll_area(self.whisper_tab)
        self.output_scroll = self._create_scroll_area(self.output_tab)
        self.ui_scroll = self._create_scroll_area(self.ui_tab)
        self.statistics_scroll = self._create_scroll_area(self.statistics_tab)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.audio_scroll)
        self.stacked_widget.addWidget(self.whisper_scroll)
        self.stacked_widget.addWidget(self.output_scroll)
        self.stacked_widget.addWidget(self.ui_scroll)
        self.stacked_widget.addWidget(self.statistics_scroll)

        stack_layout.addWidget(self.stacked_widget)
        content_layout.addWidget(self.content_stack, 1)

        layout.addLayout(content_layout)

        # Footer action bar
        footer = QWidget()
        footer.setObjectName("settings_footer")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 8, 16, 12)
        footer_layout.setSpacing(8)
        footer_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("settings_cancel_button")

        self.save_button = QPushButton("Save Settings")
        self.save_button.setObjectName("settings_save_button")

        footer_layout.addWidget(self.cancel_button)
        footer_layout.addWidget(self.save_button)

        layout.addWidget(footer)

        # Connect buttons
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.save_and_close)

    def _on_theme_changed(self, theme_name: str, is_dark: bool):
        """Slot: handle theme_changed signal to update this dialog's theme."""
        # Avoid recursive updates
        if self._applying_theme:
            return
        
        # Save current page index before applying theme
        current_index = self.stacked_widget.currentIndex()
        
        self.apply_theme(theme_name)

        # Restore the current page after theme change
        self.stacked_widget.setCurrentIndex(current_index)

    def switch_page(self, index):
        """Switch to a different settings page"""
        self.stacked_widget.setCurrentIndex(index)
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def _create_scroll_area(self, widget):
        """Create a scroll area with custom themed scrollbars for the given widget"""
        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

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
        """
        Apply the selected theme to the dialog background and all group boxes.
        
        This method is called:
        1. During dialog initialization with the saved theme
        2. Automatically via theme_changed signal when theme is changed anywhere
        3. This ensures immediate, live theme updates across all settings tabs
        
        The method updates:
        - Dialog background gradients
        - All group boxes, modern widgets (comboboxes, switches, etc.)
        - Text colors for labels and help text
        - Icons throughout the dialog
        - Sidebar navigation
        - Scrollbar styling
        """
        # Prevent recursion during theme application
        if self._applying_theme:
            return
        
        self._applying_theme = True
        try:
            # Get theme manager for querying theme info
            theme_manager = get_theme_manager()

            # Update theme manager if theme is different
            if theme_manager.get_current_theme() != theme_name:
                self._applying_theme = False
                theme_manager.set_theme(theme_name)
                return

            # Batch UI updates for better performance
            self.setUpdatesEnabled(False)

            colors = self._get_theme_colors(theme_name)

            # Overall dialog background closer to light Tailwind surface
            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {colors["secondary"]};
                    color: {colors["text_primary"]};
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                }}
                QWidget#settings_header {{
                    background-color: {self._lighten_color(colors["secondary"], 0.02)};
                    border-bottom: 1px solid {colors["border"]};
                }}
                QLabel#settings_title {{
                    font-size: 18px;
                    font-weight: 600;
                    color: {colors["text_primary"]};
                }}
                QLabel#settings_subtitle {{
                    font-size: 12px;
                    color: {colors["text_muted"]};
                }}
                QWidget#settings_footer {{
                    background-color: {self._lighten_color(colors["secondary"], 0.02)};
                    border-top: 1px solid {colors["border"]};
                }}
                QPushButton#settings_header_close {{
                    border-radius: 14px;
                    border: none;
                    background-color: transparent;
                }}
                QPushButton#settings_header_close:hover {{
                    background-color: {self._darken_color(colors["secondary"], 0.06)};
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
            for widget in self.findChildren(AnimatedToggleSwitch):
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

            # Apply theme to sidebar navigation
            self.apply_sidebar_theme(theme_name)

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

            # Re-enable updates after batching
            self.setUpdatesEnabled(True)

        except Exception as e:
            print(f"Error applying theme '{theme_name}' to settings dialog: {e}")
            # Re-enable updates even on error
            self.setUpdatesEnabled(True)
            # Attempt fallback to default theme
            if theme_name != "white" and not self._applying_theme:
                try:
                    theme_manager = get_theme_manager()
                    theme_manager.set_theme("white")
                except Exception:
                    pass  # Avoid infinite recursion
        finally:
            self._applying_theme = False

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
            
            # Explicitly apply theme to statistics tab to update cards
            if hasattr(self, 'statistics_tab'):
                self.statistics_tab.apply_theme(colors['primary'], colors['secondary'])
        except Exception:
            pass

    def _apply_theme_to_group_boxes(self, colors):
        """Apply theme to all ModernGroupBox instances"""
        # Find all ModernGroupBox widgets in the dialog
        for widget in self.findChildren(ModernGroupBox):
            widget.apply_theme(colors["primary"], colors["secondary"])

    def _darken_color(self, hex_color, factor=0.15):
        """Darken a hex color - delegates to ThemeManager for consistency"""
        theme_manager = get_theme_manager()
        return theme_manager.darken_color(hex_color, factor)

    def _lighten_color(self, hex_color, factor=0.15):
        """Lighten a hex color - delegates to ThemeManager for consistency"""
        theme_manager = get_theme_manager()
        return theme_manager.lighten_color(hex_color, factor)

    def _apply_icon_theme(self, is_dark: bool):
        """Apply appropriate icon colors based on dark/light theme"""
        # Ensure colors are available in this method since it references them
        theme_manager = get_theme_manager()
        colors = self._get_theme_colors(theme_manager.get_current_theme())
        # Update sidebar navigation icons
        if hasattr(self, 'nav_buttons'):
            nav_icons = [
                ('audio', 16),
                ('brain', 16),
                ('clipboard', 16),
                ('settings', 16),
                ('dashboard', 16)
            ]
            for btn, (icon_name, size) in zip(self.nav_buttons, nav_icons):
                if is_dark:
                    btn.setIcon(get_icon(icon_name, size, QColor(255, 255, 255)))
                else:
                    btn.setIcon(get_icon(icon_name, size))

        # Update save and cancel button icons and styles based on theme
        if hasattr(self, 'cancel_button'):
            # Cancel button - light surface with subtle border
            self.cancel_button.setStyleSheet(f"""
                QPushButton#settings_cancel_button {{
                    background-color: transparent;
                    color: {colors['text_secondary']};
                    border-radius: 6px; /* match Tailwind rounded-md (0.375rem) */
                    border: 1px solid {colors['border']};
                    padding: 6px 16px;
                    min-height: 32px;
                    font-size: 13px;
                    font-weight: 600;
                    text-align: center;
                    outline: none;
                }}
                QPushButton#settings_cancel_button:hover {{
                    background-color: {self._lighten_color(colors['secondary'], 0.04)};
                }}
            """)
            self.cancel_button.setIcon(get_icon('cancel', 13, QColor(120, 120, 130)))
            self.cancel_button.setIconSize(QSize(13, 13))
            self.cancel_button.setFlat(False)
            self.cancel_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # Ensure icon is on the left with proper spacing
            self.cancel_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
        if hasattr(self, 'save_button'):
            # Save button - primary pill button similar to Tailwind design
            self.save_button.setStyleSheet(f"""
                QPushButton#settings_save_button {{
                    background-color: {colors['accent']};
                    color: #ffffff;
                    border: none;
                    border-radius: 6px; /* match Tailwind rounded-md (0.375rem) */
                    padding: 6px 18px;
                    min-height: 32px;
                    min-width: 100px;
                    font-size: 13px;
                    font-weight: 600;
                    text-align: center;
                    outline: none;
                }}
                QPushButton#settings_save_button:hover {{
                    background-color: {colors['accent_hover']};
                }}
            """)
            self.save_button.setIcon(get_icon('save', 13, QColor(255, 255, 255)))
            self.save_button.setIconSize(QSize(13, 13))
            self.save_button.setFlat(False)
            self.save_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # Ensure icon is on the left with proper spacing
            self.save_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

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
        """Get comprehensive color scheme for a theme from centralized ThemeManager"""
        theme_manager = get_theme_manager()
        colors = theme_manager.get_theme_colors(theme_name)
        primary_color = colors["primary"]
        secondary_color = colors["secondary"]
        is_dark = theme_manager.is_dark_theme()

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

    def apply_sidebar_theme(self, theme_name):
        """Apply theme-aware styling to sidebar navigation"""
        colors = self._get_theme_colors(theme_name)
        is_dark = self._is_dark_color(colors["primary"])

        # Create appropriate accent colors for sidebar
        if is_dark:
            sidebar_bg = self._darken_color(colors["primary"], 0.15)
            active_bg = self._lighten_color(colors["primary"], 0.2)
            hover_bg = self._lighten_color(colors["primary"], 0.1)
            separator_color = self._lighten_color(colors["primary"], 0.15)
        else:
            sidebar_bg = self._darken_color(colors["primary"], 0.04)
            active_bg = "#4A90E2"  # Accent color for active
            hover_bg = self._darken_color(colors["primary"], 0.08)
            separator_color = self._darken_color(colors["primary"], 0.08)

        # Style the sidebar container to match Tailwind-style nav (no borders)
        self.sidebar.setStyleSheet(f"""
            QWidget#sidebar {{
                background-color: {sidebar_bg};
                border: none;
            }}
        """)

        # Style the content area as a clean surface (no borders)
        self.content_stack.setStyleSheet(f"""
            QWidget#content_stack {{
                background-color: {colors["secondary"]};
                border: none;
            }}
        """)

        # Style navigation buttons
        for btn in self.nav_buttons:
            # Update icon colors based on theme
            is_dark_theme = self._is_dark_color(colors["primary"])
            btn_icon_name = None
            if "audio" in btn.text().lower():
                btn_icon_name = "audio"
            elif "whisper" in btn.text().lower():
                btn_icon_name = "brain"
            elif "output" in btn.text().lower():
                btn_icon_name = "clipboard"
            elif "ui" in btn.text().lower():
                btn_icon_name = "settings"
            elif "statistics" in btn.text().lower():
                btn_icon_name = "dashboard"
            
            if btn_icon_name:
                if is_dark_theme:
                    btn.setIcon(get_icon(btn_icon_name, 16, QColor(255, 255, 255)))
                else:
                    btn.setIcon(get_icon(btn_icon_name, 16))

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {colors["text_secondary"]};
                    border: none;
                    border-radius: 999px;
                    padding: 8px 12px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 500;
                    margin: 2px 4px;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                    color: {colors["text_primary"]};
                }}
                QPushButton:checked {{
                    background-color: {active_bg};
                    color: {"#ffffff" if not is_dark else colors["text_primary"]};
                    font-weight: 600;
                }}
                QPushButton:checked:hover {{
                    background-color: {active_bg};
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
        finally:
            # Disconnect from theme manager to avoid calls on deleted objects
            try:
                theme_manager = get_theme_manager()
                theme_manager.theme_changed.disconnect(self._on_theme_changed)
            except Exception:
                pass
        event.accept()
