"""
Whisper Settings Tab
Handles Whisper AI transcription configuration
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QButtonGroup, QStackedWidget,
    QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QSize, QTimer, Signal
from PySide6.QtGui import QKeySequence

from ..config_manager import ConfigManager
from ..managers import WhisperManager, get_theme_manager
from ..icon_manager import get_button_icon, get_themed_button_icon
from .ui_components import ModernGroupBox, ModernButton
from .modern_widgets import (
    ModernComboBox, ModernLineEdit, ModernRadioButton,
    ModernTabBar
)


class WhisperTab(QWidget):
    """Whisper settings tab"""

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.whisper_manager = WhisperManager()
        
        # Debounce timer for language changes (prevents excessive config writes)
        self.language_change_timer = QTimer()
        self.language_change_timer.setSingleShot(True)
        self.language_change_timer.setInterval(300)  # 300ms debounce delay
        self.language_change_timer.timeout.connect(self._apply_language_change)
        self.pending_language_code = None
        
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # 1. Header / Mode Selection (Tabs)
        self.mode_selector = ModernTabBar(["Cloud API", "Local Device"])
        self.mode_selector.tabChanged.connect(self.on_mode_changed)
        
        layout.addWidget(self.mode_selector)

        # 2. Content Area (Stacked Widget)
        self.content_stack = QStackedWidget()
        
        # --- Page 0: API Settings ---
        self.api_page = QWidget()
        api_page_layout = QVBoxLayout(self.api_page)
        api_page_layout.setContentsMargins(0, 10, 0, 0)
        api_page_layout.setSpacing(24)
        
        # API Key Section
        api_key_container = QWidget()
        api_key_layout = QVBoxLayout(api_key_container)
        api_key_layout.setContentsMargins(0, 0, 0, 0)
        api_key_layout.setSpacing(8)
        
        # Header
        api_header = QLabel("API Configuration")
        api_header.setStyleSheet("font-size: 14px; font-weight: 600;")
        api_key_layout.addWidget(api_header)
        
        # API Key Field
        key_label = QLabel("OpenAI API Key")
        key_label.setStyleSheet("color: #6c757d; font-size: 12px; font-weight: 500;")
        api_key_layout.addWidget(key_label)
        
        key_input_row = QHBoxLayout()
        key_input_row.setSpacing(8)
        
        self.api_key_edit = ModernLineEdit("sk-...")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.api_key_toggle_btn = QPushButton()
        self.api_key_toggle_btn.setFixedSize(32, 32)
        self.api_key_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.api_key_toggle_btn.clicked.connect(self.toggle_api_key_visibility)
        
        key_input_row.addWidget(self.api_key_edit)
        key_input_row.addWidget(self.api_key_toggle_btn)
        
        api_key_layout.addLayout(key_input_row)
        
        # Helper text
        api_help = QLabel("Get your API key from: <a href='https://platform.openai.com/api-keys' style='color: #4A90E2;'>platform.openai.com</a>")
        api_help.setOpenExternalLinks(True)
        api_help.setStyleSheet("font-size: 11px; color: #6c757d;")
        api_key_layout.addWidget(api_help)
        
        api_page_layout.addWidget(api_key_container)
        
        # Model & Language Section
        model_container = QWidget()
        model_layout = QVBoxLayout(model_container)
        model_layout.setContentsMargins(0, 0, 0, 0)
        model_layout.setSpacing(8)
        
        # Header
        model_header = QLabel("Transcription Settings")
        model_header.setStyleSheet("font-size: 14px; font-weight: 600; margin-top: 16px;")
        model_layout.addWidget(model_header)
        
        # Side-by-Side Dropdowns
        dropdowns_row = QHBoxLayout()
        dropdowns_row.setSpacing(16)
        
        # Left: Model
        model_col = QVBoxLayout()
        model_col.setSpacing(6)
        model_label = QLabel("Model")
        model_label.setStyleSheet("color: #6c757d; font-size: 12px; font-weight: 500;")
        
        self.api_model_combo = ModernComboBox()
        self.populate_api_model_combo()
        self.api_model_combo.currentIndexChanged.connect(self.on_api_model_changed)
        
        model_col.addWidget(model_label)
        model_col.addWidget(self.api_model_combo)
        dropdowns_row.addLayout(model_col)
        
        # Right: Language
        lang_col = QVBoxLayout()
        lang_col.setSpacing(6)
        lang_label = QLabel("Language")
        lang_label.setStyleSheet("color: #6c757d; font-size: 12px; font-weight: 500;")
        
        self.api_language_combo = ModernComboBox()
        self.populate_api_language_combo()
        self.api_language_combo.currentIndexChanged.connect(self.on_api_language_changed)
        
        lang_col.addWidget(lang_label)
        lang_col.addWidget(self.api_language_combo)
        dropdowns_row.addLayout(lang_col)
        
        model_layout.addLayout(dropdowns_row)
        
        # Pricing Badge
        self.api_pricing_info = QLabel()
        self.api_pricing_info.setStyleSheet("""
            color: #28a745;
            font-size: 11px;
            font-weight: 600;
            background-color: #f8fff9;
            border: 1px solid #d4edda;
            border-radius: 4px;
            padding: 4px 8px;
            margin-top: 4px;
        """)
        model_layout.addWidget(self.api_pricing_info)
        
        api_page_layout.addWidget(model_container)
        api_page_layout.addStretch()
        
        self.content_stack.addWidget(self.api_page)
        
        # --- Page 1: Local Settings ---
        self.local_page = QWidget()
        local_page_layout = QVBoxLayout(self.local_page)
        local_page_layout.setContentsMargins(0, 10, 0, 0)
        local_page_layout.setSpacing(24)
        
        from ..managers.whisper_manager import FASTER_WHISPER_AVAILABLE
        
        if not FASTER_WHISPER_AVAILABLE:
            # Error State
            error_container = QWidget()
            error_layout = QVBoxLayout(error_container)
            
            not_available_label = QLabel(
                "Local transcription requires the 'faster-whisper' package.\n"
                "Please install it to use offline capabilities."
            )
            not_available_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            not_available_label.setStyleSheet("color: #dc3545; font-weight: 500;")
            
            error_layout.addWidget(not_available_label)
            local_page_layout.addWidget(error_container)
        else:
            # Local Settings
            local_container = QWidget()
            local_layout = QVBoxLayout(local_container)
            local_layout.setContentsMargins(0, 0, 0, 0)
            local_layout.setSpacing(8)
            
            # Header
            local_header = QLabel("Model Selection")
            local_header.setStyleSheet("font-size: 14px; font-weight: 600;")
            local_layout.addWidget(local_header)
            
            # Side-by-Side Dropdowns
            local_dropdowns_row = QHBoxLayout()
            local_dropdowns_row.setSpacing(16)
            
            # Left: Category
            cat_col = QVBoxLayout()
            cat_col.setSpacing(6)
            cat_label = QLabel("Category")
            cat_label.setStyleSheet("color: #6c757d; font-size: 12px; font-weight: 500;")
            
            self.category_combo = ModernComboBox()
            self.populate_category_combo()
            self.category_combo.currentTextChanged.connect(self.on_category_changed)
            
            cat_col.addWidget(cat_label)
            cat_col.addWidget(self.category_combo)
            local_dropdowns_row.addLayout(cat_col)
            
            # Right: Model
            lmodel_col = QVBoxLayout()
            lmodel_col.setSpacing(6)
            lmodel_label = QLabel("Model")
            lmodel_label.setStyleSheet("color: #6c757d; font-size: 12px; font-weight: 500;")
            
            self.model_combo = ModernComboBox()
            self.populate_model_combo()
            self.model_combo.currentIndexChanged.connect(self.on_model_combo_changed)
            
            lmodel_col.addWidget(lmodel_label)
            lmodel_col.addWidget(self.model_combo)
            local_dropdowns_row.addLayout(lmodel_col)
            
            local_layout.addLayout(local_dropdowns_row)
            
            # Info text
            info_label = QLabel("Larger models are more accurate but require more RAM and run slower.")
            info_label.setStyleSheet("color: #6c757d; font-size: 11px; margin-top: 4px;")
            local_layout.addWidget(info_label)
            
            local_page_layout.addWidget(local_container)
            
        local_page_layout.addStretch()
        self.content_stack.addWidget(self.local_page)
        
        layout.addWidget(self.content_stack)

        # Connect theme changes
        get_theme_manager().theme_changed.connect(self._on_theme_changed)
        
        # Initial theme application
        self._on_theme_changed(get_theme_manager().is_dark_theme())
        self._update_api_key_toggle_icon()

    def _on_theme_changed(self, is_dark: bool):
        """Apply theme changes to custom widgets"""
        if hasattr(self, 'mode_selector'):
            self.mode_selector.apply_theme(is_dark)
        self._update_api_key_toggle_icon()

    def on_mode_changed(self, index: int):
        """Handle mode selection change"""
        self.content_stack.setCurrentIndex(index)
        
        mode = "api" if index == 0 else "local"
        self.whisper_manager.set_mode(mode)
        
        if mode == "api":
            # Refresh API model combo when switching to API mode
            if hasattr(self, 'api_model_combo'):
                self.populate_api_model_combo()
        else:
            pass # Local mode logic if needed

    def load_settings(self):
        """Load Whisper settings from config"""
        mode = self.config_manager.get_setting("whisper/mode", "api")
        if mode == "api":
            self.mode_selector.set_current_index(0)
        else:
            self.mode_selector.set_current_index(1)

        api_key = self.config_manager.get_setting("whisper/api_key", "")
        self.api_key_edit.setText(api_key)

        # Load selected API model
        selected_api_model = self.config_manager.get_setting("whisper/api_model", "gpt-4o-transcribe")
        if hasattr(self, 'api_model_combo'):
            # Find the matching model in the combo box
            for i in range(self.api_model_combo.count()):
                if self.api_model_combo.itemData(i) == selected_api_model:
                    self.api_model_combo.setCurrentIndex(i)
                    break

            # Update pricing display for the selected model
            self.update_pricing_display(selected_api_model)
        
        # Load selected API language
        selected_api_language = self.config_manager.get_setting("whisper/language", "en")
        if hasattr(self, 'api_language_combo'):
            # Find the matching language in the combo box
            for i in range(self.api_language_combo.count()):
                if self.api_language_combo.itemData(i) == selected_api_language:
                    self.api_language_combo.setCurrentIndex(i)
                    break

        # Load selected local model for local mode
        selected_model = self.config_manager.get_setting("whisper/local_model", "base")
        # Sync dropdowns if present
        if hasattr(self, 'category_combo') and hasattr(self, 'model_combo'):
            # First determine which category contains the selected model
            found_category = "All"
            for category in self.whisper_manager.get_model_categories():
                if selected_model in self.whisper_manager.get_models_by_category(category):
                    if category != "All":  # Prefer specific category over "All"
                        found_category = category
                        break

            # Set the category dropdown
            self.category_combo.setCurrentText(found_category)
            # Update model dropdown for that category
            self.populate_model_combo(found_category)
            # Set the specific model by finding matching item data
            for i in range(self.model_combo.count()):
                if self.model_combo.itemData(i) == selected_model:
                    self.model_combo.setCurrentIndex(i)
                    break

    def save_settings(self):
        """Save Whisper settings to config"""
        mode = "api" if self.mode_selector.current_index() == 0 else "local"
        self.config_manager.set_setting("whisper/mode", mode)
        self.config_manager.set_setting("whisper/api_key", self.api_key_edit.text())

        # Save selected API model from dropdown
        if hasattr(self, 'api_model_combo') and self.api_model_combo.currentIndex() >= 0:
            api_model_name = self.api_model_combo.currentData()  # Get actual model name from item data
            if api_model_name:
                self.config_manager.set_setting("whisper/api_model", api_model_name)
                if mode == "api":
                    try:
                        self.whisper_manager.set_api_model(api_model_name)
                    except ValueError as e:
                        print(f"Error setting API model: {e}")
        
        # Save selected API language from dropdown
        if hasattr(self, 'api_language_combo') and self.api_language_combo.currentIndex() >= 0:
            api_language_code = self.api_language_combo.currentData()  # Get actual language code from item data
            if api_language_code:
                self.config_manager.set_setting("whisper/language", api_language_code)
                if mode == "api":
                    try:
                        self.whisper_manager.set_api_language(api_language_code)
                    except ValueError as e:
                        print(f"Error setting API language: {e}")

        # Save selected local model from dropdown
        if hasattr(self, 'model_combo') and self.model_combo.currentIndex() >= 0:
            model_name = self.model_combo.currentData()  # Get actual model name from item data
            if model_name:
                self.config_manager.set_setting("whisper/local_model", model_name)
                if mode == "local":
                    self.whisper_manager.set_local_model(model_name)

    def closeEvent(self, event):
        """Handle dialog close event"""
        # Stop UI refresh timer
        if hasattr(self, 'ui_refresh_timer'):
            self.ui_refresh_timer.stop()
        event.accept()

    def populate_category_combo(self):
        """Fill the category dropdown with available categories"""
        categories = self.whisper_manager.get_model_categories()
        self.category_combo.clear()
        for category in categories:
            self.category_combo.addItem(category)
        # Set default to "All"
        self.category_combo.setCurrentText("All")

    def populate_model_combo(self, category: str = "All"):
        """Fill the model dropdown with models from selected category"""
        current_model = self.model_combo.currentText() if hasattr(self, 'model_combo') else ""
        # Only get LOCAL models, not API models
        models = self.whisper_manager.get_models_by_category(category)
        # Use local models list (API models are not included)
        local_models = models

        self.model_combo.clear()
        for model in local_models:
            # Get model info to show size
            model_info = self.whisper_manager.get_model_info(model)
            size = model_info.get('size', 'Unknown')
            memory = model_info.get('memory', 'Unknown')
            # Display format: "model_name (size, memory)"
            display_text = f"{model} ({size}, {memory})"
            # Store actual model name as item data
            self.model_combo.addItem(display_text, model)

        # Try to restore previous selection if it's still available
        if current_model and current_model in local_models:
            # Find the item with matching data (actual model name)
            for i in range(self.model_combo.count()):
                if self.model_combo.itemData(i) == current_model:
                    self.model_combo.setCurrentIndex(i)
                    break
        elif local_models:
            # If no previous selection or it's not available, select first model
            self.model_combo.setCurrentIndex(0)

    def on_category_changed(self, category: str):
        """Handle category dropdown selection change"""
        # Update the model dropdown to show models from selected category
        self.populate_model_combo(category)

    def on_model_combo_changed(self, index: int):
        """Handle model dropdown selection change"""
        # Get actual model name from item data
        model_name = self.model_combo.itemData(index)
        if model_name:
            # Persist immediately and update whisper manager
            self.config_manager.set_setting("whisper/local_model", model_name)
            self.whisper_manager.set_local_model(model_name)

    def populate_api_model_combo(self):
        """Fill the API model dropdown with available API models"""
        self.api_model_combo.clear()
        # Get available API models from whisper manager
        api_models = self.whisper_manager.available_api_models

        for model in api_models:
            # Get model info to show additional details
            model_info = self.whisper_manager.get_model_info(model)
            size = model_info.get('size', 'Unknown')
            quality = model_info.get('quality', 'Unknown')
            # Display format: "model_name (size, quality)"
            display_text = f"{model} ({size}, {quality})"
            # Store actual model name as item data
            self.api_model_combo.addItem(display_text, model)
    
    def populate_api_language_combo(self):
        """Fill the API language dropdown with available languages"""
        self.api_language_combo.clear()
        # Get available languages from whisper manager
        available_languages = self.whisper_manager.available_languages

        for code, name in available_languages:
            # Display format: "English (en)"
            display_text = f"{name} ({code})"
            # Store language code as item data
            self.api_language_combo.addItem(display_text, code)

    def on_api_model_changed(self, index: int):
        """Handle API model dropdown selection change"""
        # Get actual model name from item data
        model_name = self.api_model_combo.itemData(index)
        if model_name:
            # Persist immediately and update whisper manager
            self.config_manager.set_setting("whisper/api_model", model_name)
            try:
                self.whisper_manager.set_api_model(model_name)
            except ValueError as e:
                print(f"Error setting API model: {e}")

            # Update pricing display based on selected model
            self.update_pricing_display(model_name)
    
    def on_api_language_changed(self, index: int):
        """Handle API language dropdown selection change with debounce"""
        # Get actual language code from item data
        language_code = self.api_language_combo.itemData(index)
        if language_code:
            # Store pending change and restart debounce timer
            self.pending_language_code = language_code
            self.language_change_timer.start()  # Restart timer on each change
    
    def _apply_language_change(self):
        """Apply the pending language change (called after debounce delay)"""
        if self.pending_language_code:
            # Persist to config and update whisper manager
            self.config_manager.set_setting("whisper/language", self.pending_language_code)
            try:
                self.whisper_manager.set_api_language(self.pending_language_code)
            except ValueError as e:
                print(f"Error setting API language: {e}")
            self.pending_language_code = None

    def _update_api_key_toggle_icon(self):
        """Update the API key toggle button icon based on current state and theme"""
        # Get current theme from theme manager
        theme_manager = get_theme_manager()
        is_dark = theme_manager.is_dark_theme()

        # Apply theme-based styling to the button
        self._apply_toggle_button_theme(is_dark)

        if self.api_key_edit.echoMode() == QLineEdit.EchoMode.Password:
            # Key is hidden, show eye-off icon
            self.api_key_toggle_btn.setIcon(get_themed_button_icon('eye-off', 16, is_dark))
            self.api_key_toggle_btn.setToolTip("Show API key")
        else:
            # Key is visible, show eye icon
            self.api_key_toggle_btn.setIcon(get_themed_button_icon('eye', 16, is_dark))
            self.api_key_toggle_btn.setToolTip("Hide API key")

    def _apply_toggle_button_theme(self, is_dark: bool):
        """Apply theme-based styling to the API key toggle button"""
        if is_dark:
            # Dark theme colors
            hover_bg = "#495057"  # Darker gray for hover
            pressed_bg = "#343a40"  # Even darker for pressed
        else:
            # Light theme colors
            hover_bg = "#e9ecef"  # Light gray for hover
            pressed_bg = "#dee2e6"  # Slightly darker for pressed

        self.api_key_toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }}
            QPushButton:hover {{
                background: {hover_bg};
            }}
            QPushButton:pressed {{
                background: {pressed_bg};
            }}
        """)

    def toggle_api_key_visibility(self):
        """Toggle API key visibility between password and normal mode"""
        if self.api_key_edit.echoMode() == QLineEdit.EchoMode.Password:
            # Show the key
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            # Hide the key
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)

        # Update the icon to match the new state
        self._update_api_key_toggle_icon()

    def update_pricing_display(self, model_name: str):
        """Update pricing display based on selected model"""
        # Get model-specific pricing
        pricing_info = self.get_model_pricing(model_name)
        self.api_pricing_info.setText(pricing_info)

    def get_model_pricing(self, model_name: str) -> str:
        """Get pricing information for a specific model"""
        if model_name == "gpt-4o-mini-transcribe":
            # GPT-4o Transcribe Mini is half the price of regular GPT-4o Transcribe
            return "Pricing: ~$0.003 per minute of audio (~$0.18/hour)"
        elif model_name == "gpt-4o-transcribe":
            return "Pricing: ~$0.006 per minute of audio (~$0.36/hour)"
        else:
            # Default pricing for unknown models
            return "Pricing: ~$0.006 per minute of audio (~$0.36/hour)"