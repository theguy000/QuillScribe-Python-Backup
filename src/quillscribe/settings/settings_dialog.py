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
from ..custom_titlebar import CustomTitleBar
from .audio_tab import AudioTab
from .whisper_tab import WhisperTab
from .output_tab import OutputTab
from .ui_tab import UITab
from .statistics_tab import StatisticsTab
from .ui_components import ModernGroupBox, ModernButton
from .modern_widgets import (
    ModernComboBox, ModernLineEdit,
    ModernKeySequenceEdit, ModernRadioButton, ModernCheckBox,
    AnimatedToggleSwitch, ModernProgressBar
)


class SettingsDialog(QDialog):
    """Beautiful settings dialog with sidebar interface"""

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
        self._is_theme_connected = False
        try:
            theme_manager.theme_changed.connect(self._on_theme_changed)
            self._is_theme_connected = True
        except Exception as e:
            print(f"Error connecting theme signal: {e}")

        # Apply initial theme
        initial_theme = self.config_manager.get_setting("ui/theme", "white")
        self.apply_theme(initial_theme)

    def setup_ui(self):
        self.setWindowTitle("QuillScribe Settings")
        self.setFixedSize(900, 640)

        # Check if custom titlebar is enabled
        custom_titlebar = bool(self.config_manager.get_setting("ui/custom_titlebar", True))

        if custom_titlebar:
            # Use frameless window for custom titlebar
            self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        else:
            # Use standard dialog with system titlebar
            self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        # Main layout is now Vertical: Titlebar (optional) | [Sidebar | Content]
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Store whether custom titlebar is enabled
        self.custom_titlebar_enabled = custom_titlebar

        # Create custom titlebar if enabled
        if custom_titlebar:
            self.custom_titlebar = CustomTitleBar(self, title="QuillScribe Settings", show_minimize=True)
            main_layout.addWidget(self.custom_titlebar)
        else:
            self.custom_titlebar = None

        # Container for sidebar and content (below titlebar if custom)
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(content_container)

        # --- Left Sidebar ---
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(220) # Slightly wider for better spacing
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setSpacing(8)
        sidebar_layout.setContentsMargins(12, 24, 12, 24)

        # Sidebar Title
        title_label = QLabel("QuillScribe")
        title_label.setObjectName("sidebar_title")
        title_label.setStyleSheet("font-size: 20px; font-weight: 700; padding-left: 8px; margin-bottom: 16px;")
        sidebar_layout.addWidget(title_label)

        # Navigation Buttons
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
            btn.setIconSize(QSize(18, 18))
            btn.setCheckable(True)
            btn.setObjectName(f"nav_btn_{idx}")
            btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(42) # Taller buttons
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()
        
        # Version/Info at bottom of sidebar
        version_label = QLabel("v1.0.0")
        version_label.setObjectName("version_label")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        sidebar_layout.addWidget(version_label)

        content_layout.addWidget(self.sidebar)

        # --- Right Content Area ---
        right_container = QWidget()
        right_container.setObjectName("content_container")
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Content Header
        header = QWidget()
        header.setObjectName("settings_header")
        header.setFixedHeight(60) # Fixed height header
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(32, 0, 24, 0) # Align with content
        header_layout.setSpacing(16)

        self.page_title = QLabel("Settings")
        self.page_title.setObjectName("page_title")
        self.page_title.setStyleSheet("font-size: 18px; font-weight: 600;")
        header_layout.addWidget(self.page_title)
        
        header_layout.addStretch()

        # Only show close button in header if we don't have custom titlebar
        if not custom_titlebar:
            self.header_close_button = QPushButton()
            self.header_close_button.setObjectName("settings_header_close")
            self.header_close_button.setText("")
            self.header_close_button.setFixedSize(28, 28)
            self.header_close_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.header_close_button.clicked.connect(self.reject)
            header_layout.addWidget(self.header_close_button)
        else:
            self.header_close_button = None

        right_layout.addWidget(header)

        # 2. Main Content Stack
        self.content_stack = QWidget()
        self.content_stack.setObjectName("content_stack")
        stack_layout = QVBoxLayout(self.content_stack)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.setSpacing(0)

        # Create stacked widget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create tabs
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
        right_layout.addWidget(self.content_stack, 1) # Give it all remaining space

        # 3. Footer Action Bar
        footer = QWidget()
        footer.setObjectName("settings_footer")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(32, 16, 32, 24)
        footer_layout.setSpacing(12)
        footer_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("settings_cancel_button")
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.save_button = QPushButton("Save Settings")
        self.save_button.setObjectName("settings_save_button")
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)

        footer_layout.addWidget(self.cancel_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        footer_layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        right_layout.addWidget(footer)

        content_layout.addWidget(right_container, 1) # Content takes remaining width

        # Connect buttons
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.save_and_close)

        # Set initial page
        self.switch_page(0)

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
        
        # Update header title
        titles = ["Audio Settings", "Whisper AI", "Output Settings", "UI Customization", "Statistics"]
        if 0 <= index < len(titles):
            self.page_title.setText(titles[index])

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
                theme_manager.set_theme(theme_name)
                # Continue with applying the theme rather than returning early

            # Batch UI updates for better performance
            self.setUpdatesEnabled(False)

            colors = self._get_theme_colors(theme_name)
            is_dark = self._is_dark_color(colors["primary"])

            # Overall dialog background
            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {colors["secondary"]};
                    color: {colors["text_primary"]};
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                }}
            """)

            # Apply theme to sidebar navigation
            self.apply_sidebar_theme(theme_name)

            # Apply theme to Content Header & Footer
            header_bg = colors["secondary"] # Match content bg
            border_color = colors["border"]
            
            self.findChild(QWidget, "settings_header").setStyleSheet(f"""
                QWidget#settings_header {{
                    background-color: {header_bg};
                    border-bottom: 1px solid {border_color};
                }}
            """)
            
            self.findChild(QWidget, "settings_footer").setStyleSheet(f"""
                QWidget#settings_footer {{
                    background-color: {header_bg};
                    border-top: 1px solid {border_color};
                }}
            """)
            
            # Update titles
            self.page_title.setStyleSheet(f"color: {colors['text_primary']}; font-size: 18px; font-weight: 600;")
            
            # Close button in header (only if no custom titlebar)
            if self.header_close_button:
                self.header_close_button.setStyleSheet(f"""
                    QPushButton#settings_header_close {{
                        border-radius: 14px;
                        border: none;
                        background-color: transparent;
                    }}
                    QPushButton#settings_header_close:hover {{
                        background-color: {self._darken_color(colors["secondary"], 0.06)};
                    }}
                """)
                self.header_close_button.setIcon(get_icon('close', 14, QColor(colors['text_secondary'])))

            # Update custom titlebar theme if present
            if hasattr(self, 'custom_titlebar') and self.custom_titlebar is not None:
                self.custom_titlebar.apply_theme(is_dark)

            # Apply to all group boxes in all tabs
            self._apply_theme_to_group_boxes(colors)

            # Apply theme to all modern widgets
            # ComboBox needs accent/border injection
            for combo in self.findChildren(ModernComboBox):
                combo.apply_theme(is_dark, colors)
            # Other widgets keep existing signature
            for widget in self.findChildren(ModernLineEdit):
                widget.apply_theme(is_dark, colors)
            for widget in self.findChildren(ModernKeySequenceEdit):
                widget.apply_theme(is_dark, colors)
            theme_manager.apply_text_theming_to_widget(self, theme_name)

            # Apply theme to Audio Tab specific elements
            if hasattr(self, 'audio_tab') and hasattr(self.audio_tab, 'apply_theme'):
                self.audio_tab.apply_theme(theme_name)

            # Allow UI tab to refresh its custom slider styling for this theme
            if hasattr(self, 'ui_tab') and hasattr(self.ui_tab, 'apply_animation_theme'):
                self.ui_tab.apply_animation_theme(theme_name)

            # Update API key toggle icon for current theme
            if hasattr(self, 'api_key_toggle_btn'):
                self._update_api_key_toggle_icon()

            # Update important form labels for dark/light (specific styling for form labels)
            label_primary = "#ffffff" if is_dark else "#495057"
            muted = "#e0e0e0" if is_dark else "#6c757d"
            for lbl in self.findChildren(QLabel):
                name = lbl.objectName()
                if name in {"form_label", "theme_label", "shortcut_label"}:
                    lbl.setStyleSheet(f"QLabel {{ color: {label_primary}; font-size: 13px; font-weight: 500; background-color: transparent; }}")

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
            hover_bg = self._lighten_color(colors['secondary'], 0.04) if is_dark else self._darken_color(colors['secondary'], 0.05)
            self.cancel_button.setStyleSheet(f"""
                QPushButton#settings_cancel_button {{
                    background-color: transparent;
                    color: {colors['text_secondary']};
                    border-radius: 6px; /* match Tailwind rounded-md (0.375rem) */
                    border: 1px solid {colors['border']};
                    padding: 4px 12px;
                    min-height: 28px;
                    font-size: 13px;
                    font-weight: 600;
                    text-align: center;
                    outline: none;
                }}
                QPushButton#settings_cancel_button:hover {{
                    background-color: {hover_bg};
                }}
            """)
            self.cancel_button.setFlat(False)
            self.cancel_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        if hasattr(self, 'save_button'):
            # Save button - primary pill button similar to Tailwind design
            self.save_button.setStyleSheet(f"""
                QPushButton#settings_save_button {{
                    background-color: {colors['accent']};
                    color: #ffffff;
                    border: none;
                    border-radius: 6px; /* match Tailwind rounded-md (0.375rem) */
                    padding: 4px 14px;
                    min-height: 28px;
                    min-width: 90px;
                    font-size: 13px;
                    font-weight: 600;
                    text-align: center;
                    outline: none;
                }}
                QPushButton#settings_save_button:hover {{
                    background-color: {colors['accent_hover']};
                }}
            """)
            self.save_button.setFlat(False)
            self.save_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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
            # Calculate widget specific colors
            # Use secondary (darker) as base for widgets
            widget_bg = secondary_color
            # Hover should be slightly lighter than secondary, but not as light/different as primary
            widget_hover = theme_manager.lighten_color(secondary_color, 0.05)
            
            return {
                "primary": primary_color,
                "secondary": secondary_color,
                "text_primary": "#ffffff",
                "text_secondary": "#e0e0e0",
                "text_muted": "#b0b0b0",
                "border": "#555555",
                "border_light": "#666666",
                "accent": "#4A90E2",
                "accent_hover": "#5BA0F2",
                # Widget specific overrides
                "widget_bg": widget_bg,
                "widget_hover": widget_hover,
                "popup_bg": secondary_color, # Match button bg
                "popup_item_hover": theme_manager.lighten_color(secondary_color, 0.08)
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
                "accent_hover": "#357ABD",
                # Widget specific overrides
                "widget_bg": secondary_color, # Light grey usually
                "widget_hover": theme_manager.darken_color(secondary_color, 0.05),
                "popup_bg": "#ffffff",
                "popup_item_hover": secondary_color
            }

    def apply_sidebar_theme(self, theme_name):
        """Apply theme-aware styling to sidebar navigation"""
        colors = self._get_theme_colors(theme_name)
        is_dark = self._is_dark_color(colors["primary"])

        # Create appropriate accent colors for sidebar
        if is_dark:
            sidebar_bg = self._darken_color(colors["primary"], 0.08) # Slightly darker than content
            active_bg = self._lighten_color(colors["primary"], 0.15)
            hover_bg = self._lighten_color(colors["primary"], 0.08)
            text_color = "#e0e0e0"
            title_color = "#ffffff"
        else:
            sidebar_bg = "#f8f9fa" # Light gray sidebar
            active_bg = "#e9ecef" # Slightly darker active
            hover_bg = "#f1f3f4"
            text_color = "#495057"
            title_color = "#212529"

        # Style the sidebar container
        self.sidebar.setStyleSheet(f"""
            QWidget#sidebar {{
                background-color: {sidebar_bg};
                border-right: 1px solid {colors["border"]};
            }}
            QLabel#sidebar_title {{
                color: {title_color};
            }}
            QLabel#version_label {{
                color: {colors["text_muted"]};
            }}
        """)

        # Style the content area container
        self.findChild(QWidget, "content_container").setStyleSheet(f"""
            QWidget#content_container {{
                background-color: {colors["secondary"]};
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
                    color: {text_color};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: 500;
                    margin-bottom: 2px;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                    color: {colors["text_primary"]};
                }}
                QPushButton:checked {{
                    background-color: {active_bg};
                    color: {colors["text_primary"]};
                    font-weight: 600;
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
                if hasattr(self, '_is_theme_connected') and self._is_theme_connected:
                    theme_manager.theme_changed.disconnect(self._on_theme_changed)
                    self._is_theme_connected = False
            except Exception:
                pass
        event.accept()
