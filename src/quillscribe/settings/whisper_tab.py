"""
Whisper Settings Tab
Handles Whisper AI transcription configuration
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QButtonGroup
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QKeySequence

from ..config_manager import ConfigManager
from ..managers import WhisperManager, get_theme_manager
from ..icon_manager import get_button_icon, get_themed_button_icon
from .modern_widgets import ModernGroupBox, ModernComboBox, ModernLineEdit, ModernRadioButton


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
        self.setup_model_connections()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        # Minimal outer margins so group boxes sit close to dialog edges
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Mode selection
        mode_group = ModernGroupBox("Transcription Mode")
        mode_layout = QVBoxLayout(mode_group)

        self.mode_group = QButtonGroup()
        self.api_radio = ModernRadioButton("OpenAI Whisper API (Fast, requires internet)")
        self.api_radio.setIconSize(QSize(16, 16))
        self.local_radio = ModernRadioButton("Local Whisper.cpp (Private, works offline)")
        self.local_radio.setIconSize(QSize(16, 16))

        self.mode_group.addButton(self.api_radio, 0)
        self.mode_group.addButton(self.local_radio, 1)

        mode_layout.addWidget(self.api_radio)
        mode_layout.addWidget(self.local_radio)

        # Connect mode change
        self.mode_group.buttonToggled.connect(self.on_mode_changed)

        layout.addWidget(mode_group)

        # Group boxes will use the ModernGroupBox theming system instead of static styles

        # API settings
        self.api_group = ModernGroupBox("API Settings")
        api_layout = QFormLayout(self.api_group)
        api_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        api_layout.setFormAlignment(Qt.AlignmentFlag.AlignVCenter)
        # API group will use ModernGroupBox theming

        # API key input with icon
        api_key_widget = QWidget()
        api_key_layout = QHBoxLayout(api_key_widget)
        api_key_layout.setContentsMargins(0, 0, 0, 0)
        api_key_layout.setSpacing(6)

        api_key_icon = QLabel()
        api_key_icon.setPixmap(get_button_icon('key', 16).pixmap(16, 16))
        api_key_icon.setObjectName("icon_api_key")
        api_key_layout.addWidget(api_key_icon)

        self.api_key_edit = ModernLineEdit("sk-...")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        api_key_layout.addWidget(self.api_key_edit)

        # Add eye toggle button
        self.api_key_toggle_btn = QPushButton()
        self.api_key_toggle_btn.setObjectName("api_key_toggle_btn")
        # Icon will be set by theme manager and toggle method
        self.api_key_toggle_btn.setIconSize(QSize(16, 16))
        self.api_key_toggle_btn.setFixedSize(32, 32)
        self.api_key_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Styling will be applied by theme manager
        self.api_key_toggle_btn.setToolTip("Show/hide API key")
        self.api_key_toggle_btn.clicked.connect(self.toggle_api_key_visibility)
        api_key_layout.addWidget(self.api_key_toggle_btn)

        # Initialize the toggle button icon (will be updated by theme manager)
        self._update_api_key_toggle_icon()

        api_key_layout.addStretch()

        # Create properly aligned label for API key
        api_key_label = QLabel("OpenAI API Key:")
        api_key_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        api_key_label.setMinimumHeight(36)  # Match input box height
        api_key_label.setObjectName("form_label")

        api_layout.addRow(api_key_label, api_key_widget)

        # Helper text for API key
        api_help = QLabel("Get your API key from: https://platform.openai.com/api-keys")
        api_help.setStyleSheet("""
            color: #6c757d;
            font-size: 11px;
            background-color: transparent;
            margin-left: 22px;
        """)
        api_help.setWordWrap(True)
        api_layout.addRow("", api_help)

        # API pricing information
        self.api_pricing_info = QLabel("Pricing: ~$0.006 per minute of audio (~$0.36/hour)")
        self.api_pricing_info.setStyleSheet("""
            color: #28a745;
            font-size: 12px;
            font-weight: 600;
            background-color: #f8fff9;
            border: 1px solid #d4edda;
            border-radius: 4px;
            padding: 4px 6px;
            margin-left: 22px;
            max-width: 280px;
        """)
        self.api_pricing_info.setWordWrap(True)
        api_layout.addRow("", self.api_pricing_info)

        # API model selection with icon
        api_model_widget = QWidget()
        api_model_layout = QHBoxLayout(api_model_widget)
        api_model_layout.setContentsMargins(0, 0, 0, 0)
        api_model_layout.setSpacing(6)

        api_model_icon = QLabel()
        api_model_icon.setPixmap(get_button_icon('brain', 16).pixmap(16, 16))
        api_model_icon.setObjectName("icon_api_model")
        api_model_layout.addWidget(api_model_icon)

        self.api_model_combo = ModernComboBox()
        self.populate_api_model_combo()
        self.api_model_combo.currentIndexChanged.connect(self.on_api_model_changed)
        api_model_layout.addWidget(self.api_model_combo)
        api_model_layout.addStretch()

        # Create properly aligned label for API model
        api_model_label = QLabel("API Model:")
        api_model_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        api_model_label.setMinimumHeight(36)  # Match combo box height
        api_model_label.setObjectName("form_label")

        api_layout.addRow(api_model_label, api_model_widget)

        # Helper text for API model
        api_model_help = QLabel("Select the OpenAI Whisper model to use for transcription")
        api_model_help.setStyleSheet("""
            color: #6c757d;
            font-size: 11px;
            background-color: transparent;
            margin-left: 22px;
        """)
        api_model_help.setWordWrap(True)
        api_layout.addRow("", api_model_help)

        # API language selection with icon
        api_language_widget = QWidget()
        api_language_layout = QHBoxLayout(api_language_widget)
        api_language_layout.setContentsMargins(0, 0, 0, 0)
        api_language_layout.setSpacing(6)

        api_language_icon = QLabel()
        api_language_icon.setPixmap(get_button_icon('language', 16).pixmap(16, 16))
        api_language_icon.setObjectName("icon_api_language")
        api_language_layout.addWidget(api_language_icon)

        self.api_language_combo = ModernComboBox()
        self.populate_api_language_combo()
        self.api_language_combo.currentIndexChanged.connect(self.on_api_language_changed)
        api_language_layout.addWidget(self.api_language_combo)
        api_language_layout.addStretch()

        # Create properly aligned label for API language
        api_language_label = QLabel("Language:")
        api_language_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        api_language_label.setMinimumHeight(36)  # Match combo box height
        api_language_label.setObjectName("form_label")

        api_layout.addRow(api_language_label, api_language_widget)

        # Helper text for API language
        api_language_help = QLabel("Select the language for better transcription accuracy (100 languages supported)")
        api_language_help.setStyleSheet("""
            color: #6c757d;
            font-size: 11px;
            background-color: transparent;
            margin-left: 22px;
        """)
        api_language_help.setWordWrap(True)
        api_layout.addRow("", api_language_help)

        layout.addWidget(self.api_group)

        # Local model settings (only show if Faster-Whisper is available)
        from ..managers.whisper_manager import FASTER_WHISPER_AVAILABLE

        self.local_group = ModernGroupBox("Local Model Settings")
        local_layout = QFormLayout(self.local_group)
        local_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        local_layout.setFormAlignment(Qt.AlignmentFlag.AlignVCenter)
        # Local group will use ModernGroupBox theming

        if not FASTER_WHISPER_AVAILABLE:
            # Show message that local mode is not available
            not_available_label = QLabel("Local models not available.\nFaster-Whisper package not installed.\nPlease install it or use API mode.")
            not_available_label.setStyleSheet("""
                color: #856404;
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            """)
            local_layout.addRow(not_available_label)

        # Only show model selection UI if Faster-Whisper is available
        if FASTER_WHISPER_AVAILABLE:
            # Category dropdown for filtering models with icon
            category_widget = QWidget()
            category_layout = QHBoxLayout(category_widget)
            category_layout.setContentsMargins(0, 0, 0, 0)
            category_layout.setSpacing(6)

            category_icon = QLabel()
            category_icon.setPixmap(get_button_icon('category', 16).pixmap(16, 16))
            category_icon.setObjectName("icon_category")
            category_layout.addWidget(category_icon)

            self.category_combo = ModernComboBox()
            self.populate_category_combo()
            self.category_combo.currentTextChanged.connect(self.on_category_changed)
            category_layout.addWidget(self.category_combo)
            category_layout.addStretch()

            # Create properly aligned label for category
            category_label = QLabel("Model Category:")
            category_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            category_label.setMinimumHeight(36)  # Match combo box height
            category_label.setObjectName("form_label")

            local_layout.addRow(category_label, category_widget)

            # Helper text for category selection
            category_help = QLabel("Choose a category to filter available models by size and performance")
            category_help.setStyleSheet("""
                color: #6c757d;
                font-size: 11px;
                background-color: transparent;
                margin-left: 22px;
            """)
            category_help.setWordWrap(True)
            local_layout.addRow("", category_help)

            # Model dropdown for selecting specific model with icon
            model_widget = QWidget()
            model_layout = QHBoxLayout(model_widget)
            model_layout.setContentsMargins(0, 0, 0, 0)
            model_layout.setSpacing(6)

            model_icon = QLabel()
            model_icon.setPixmap(get_button_icon('brain', 16).pixmap(16, 16))
            model_icon.setObjectName("icon_model")
            model_layout.addWidget(model_icon)

            self.model_combo = ModernComboBox()
            self.populate_model_combo()
            self.model_combo.currentIndexChanged.connect(self.on_model_combo_changed)
            model_layout.addWidget(self.model_combo)
            model_layout.addStretch()

            # Create properly aligned label for model selection
            model_label = QLabel("Select Model:")
            model_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            model_label.setMinimumHeight(36)  # Match combo box height
            model_label.setObjectName("form_label")

            local_layout.addRow(model_label, model_widget)

            # Helper text for model selection
            model_help = QLabel("Pick a specific Whisper model for transcription based on your needs")
            model_help.setStyleSheet("""
                color: #6c757d;
                font-size: 11px;
                background-color: transparent;
                margin-left: 22px;
            """)
            model_help.setWordWrap(True)
            local_layout.addRow("", model_help)

            # Removed download UI as per guidance

        layout.addWidget(self.local_group)

        # Add minimal space for scroll layout
        layout.addStretch()

    def refresh_models_display(self):
        """Download UI removed; nothing to refresh here"""
        return


    def create_integrated_model_widget(self, model_info: dict):
        """Deprecated: download UI removed"""
        return QWidget()

    def setup_model_connections(self):
        """Deprecated: download manager removed"""
        return

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

    def process_ui_events(self):
        """Process UI events to keep interface responsive"""
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

    def on_model_selected(self, model_info: dict):
        """Deprecated: selection via download list removed"""
        return

    def download_model(self, model_file: str):
        """Deprecated: download removed"""
        return

    def cancel_download(self, model_file: str):
        """Deprecated: download removed"""
        return

    def delete_model(self, model_file: str):
        """Deprecated: download removed"""
        return

    def on_model_status_changed(self, model_name: str, status: str):
        """Deprecated: download removed"""
        return

    def on_download_progress(self, model_name: str, progress: int):
        """Deprecated: download removed"""
        return

    def on_mode_changed(self, button, checked):
        """Handle mode selection change"""
        if checked:
            if button == self.api_radio:
                self.api_group.setEnabled(True)
                self.local_group.setEnabled(False)
                self.whisper_manager.set_mode("api")
                # Refresh API model combo when switching to API mode
                if hasattr(self, 'api_model_combo'):
                    self.populate_api_model_combo()
            else:
                self.api_group.setEnabled(False)
                self.local_group.setEnabled(True)
                self.whisper_manager.set_mode("local")


    def load_settings(self):
        """Load Whisper settings from config"""
        mode = self.config_manager.get_setting("whisper/mode", "api")
        if mode == "api":
            self.api_radio.setChecked(True)
        else:
            self.local_radio.setChecked(True)

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

        # Load selected model for local mode
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
        mode = "api" if self.api_radio.isChecked() else "local"
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


    # Removed fixed size constraints to allow better layout flexibility

    def closeEvent(self, event):
        """Handle dialog close event"""
        # Stop UI refresh timer
        if hasattr(self, 'ui_refresh_timer'):
            self.ui_refresh_timer.stop()
        event.accept()