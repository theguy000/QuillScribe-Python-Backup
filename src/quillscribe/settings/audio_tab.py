"""
Audio Settings Tab
Handles microphone selection, testing, and audio settings
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFormLayout, QDialog, QListWidget, QSizePolicy,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QColor, QPainter, QBrush

from ..managers import AudioManager, get_theme_manager
from ..config_manager import ConfigManager
from ..icon_manager import get_button_icon, get_white_button_icon
from .ui_components import ModernGroupBox
from .modern_buttons import ModernButton, ButtonVariant
from .modern_widgets import ModernComboBox, ModernCheckBox, AnimatedToggleSwitch, ModernProgressBar, SegmentedProgressBar




class AudioTab(QWidget):
    """Audio settings tab - Modern Minimalist Layout"""

    def __init__(self, config_manager: ConfigManager, audio_manager: AudioManager = None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        # Use shared audio manager if provided, otherwise create new one
        self.audio_manager = audio_manager if audio_manager is not None else AudioManager()
        self.separators = [] # Track separators for theming
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup the modern minimalist UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Input Device Section ---
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        # Header row with Label
        header_layout = QHBoxLayout()
        input_label = QLabel("Primary Microphone")
        input_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #212529;
        """)
        input_label.setObjectName("section_label") # For theming
        header_layout.addWidget(input_label)
        header_layout.addStretch()
        input_layout.addLayout(header_layout)

        # Combo row with Refresh button side-by-side
        combo_row = QHBoxLayout()
        combo_row.setSpacing(8)

        # Microphone Dropdown (Full width, prominent)
        self.mic_combo = ModernComboBox()
        self.mic_combo.setFixedHeight(32)
        self.mic_combo.currentIndexChanged.connect(self.on_device_changed)
        combo_row.addWidget(self.mic_combo, 1) # Stretch factor 1

        # Refresh button (Icon only, subtle)
        self.refresh_button = ModernButton(variant=ButtonVariant.GHOST)
        self.refresh_button.setObjectName("refresh_button")
        self.refresh_button.setIcon(get_button_icon('refresh', 14))
        self.refresh_button.setFixedSize(32, 32) # Matches combo height
        self.refresh_button.setToolTip("Refresh Device List")
        self.refresh_button.clicked.connect(self.refresh_devices)
        combo_row.addWidget(self.refresh_button)
        
        input_layout.addLayout(combo_row)

        # Level Meter Row (Meter + Test Button)
        meter_row = QHBoxLayout()
        meter_row.setSpacing(12)

        # Level Meter (Segmented)
        self.level_bar = SegmentedProgressBar()
        self.level_bar.setFixedHeight(24) # Match button height roughly or slightly smaller
        meter_row.addWidget(self.level_bar, 1) # Stretch to fill available space
        
        # Test Microphone Button
        self.test_mic_button = ModernButton("Test Microphone", variant=ButtonVariant.SECONDARY)
        self.test_mic_button.setFixedSize(140, 32) # Increased width to prevent cutoff
        self.test_mic_button.clicked.connect(self.on_test_mic_clicked)
        meter_row.addWidget(self.test_mic_button)

        input_layout.addLayout(meter_row)
        
        main_layout.addWidget(input_container)

        # --- Advanced Settings Section (Subtle) ---
        advanced_group = ModernGroupBox("Advanced Settings")
        advanced_layout = QVBoxLayout(advanced_group)
        advanced_layout.setSpacing(16)
        advanced_layout.setContentsMargins(0, 12, 0, 0) # Adjust for ModernGroupBox title

        # Auto-select Row
        auto_select_row = QHBoxLayout()
        self.auto_select_checkbox = AnimatedToggleSwitch()
        self.auto_select_checkbox.toggled.connect(self.on_auto_select_toggled)
        auto_select_row.addWidget(self.auto_select_checkbox)
        
        auto_select_info = QVBoxLayout()
        auto_select_info.setSpacing(2)
        auto_select_label = QLabel("Auto-select Active Microphone")
        auto_select_label.setObjectName("setting_label")
        auto_select_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        auto_select_desc = QLabel("Automatically switch to the microphone detecting speech.")
        auto_select_desc.setObjectName("setting_desc")
        auto_select_desc.setStyleSheet("color: #6c757d; font-size: 11px;")
        auto_select_info.addWidget(auto_select_label)
        auto_select_info.addWidget(auto_select_desc)
        auto_select_row.addLayout(auto_select_info)
        auto_select_row.addStretch()

        # Detect Now Button (No icon, larger size)
        self.detect_now_button = ModernButton("Detect Now", variant=ButtonVariant.SECONDARY)
        self.detect_now_button.setMinimumWidth(110) # Ensure text fits
        self.detect_now_button.setFixedHeight(32)
        self.detect_now_button.clicked.connect(self.detect_active_microphone_now)
        auto_select_row.addWidget(self.detect_now_button)
        
        advanced_layout.addLayout(auto_select_row)

        # Separator 1
        self._add_separator(advanced_layout)

        # Sounds Row
        sounds_row = QHBoxLayout()
        self.sounds_enabled_checkbox = AnimatedToggleSwitch()
        sounds_row.addWidget(self.sounds_enabled_checkbox)
        
        sounds_info = QVBoxLayout()
        sounds_info.setSpacing(2)
        sounds_label = QLabel("Notification Sounds")
        sounds_label.setObjectName("setting_label")
        sounds_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        sounds_desc = QLabel("Play audio cues when recording starts or stops.")
        sounds_desc.setObjectName("setting_desc")
        sounds_desc.setStyleSheet("color: #6c757d; font-size: 11px;")
        sounds_info.addWidget(sounds_label)
        sounds_info.addWidget(sounds_desc)
        sounds_row.addLayout(sounds_info)
        sounds_row.addStretch()
        
        advanced_layout.addLayout(sounds_row)

        # Separator 2
        self._add_separator(advanced_layout)

        # Blocklist Row
        blocklist_row = QHBoxLayout()
        blocklist_info = QVBoxLayout()
        blocklist_info.setSpacing(2)
        blocklist_label = QLabel("Microphone Blocklist")
        blocklist_label.setObjectName("setting_label")
        blocklist_label.setStyleSheet("font-weight: 500; font-size: 13px;")
        blocklist_desc = QLabel("Manage ignored devices.")
        blocklist_desc.setObjectName("setting_desc")
        blocklist_desc.setStyleSheet("color: #6c757d; font-size: 11px;")
        blocklist_info.addWidget(blocklist_label)
        blocklist_info.addWidget(blocklist_desc)
        blocklist_row.addLayout(blocklist_info)
        blocklist_row.addStretch()

        self.blocklist_button = ModernButton("Manage", variant=ButtonVariant.SECONDARY)
        self.blocklist_button.setMinimumWidth(100) # Ensure text fits
        self.blocklist_button.setFixedHeight(32)
        self.blocklist_button.clicked.connect(self.show_blocklist_dialog)
        blocklist_row.addWidget(self.blocklist_button)

        advanced_layout.addLayout(blocklist_row)

        main_layout.addWidget(advanced_group)
        main_layout.addStretch()

        # --- Timers & State ---
        self._is_testing = False # Track testing state
        # self.start_monitoring() # Don't start immediately, wait for Test button

        # Real-time device monitoring
        self.device_monitor_timer = QTimer()
        self.device_monitor_timer.timeout.connect(self.monitor_device_changes)
        self.device_monitor_timer.start(2000)  # Check every 2 seconds
        self.last_device_list = []

        # Initialize device list
        self.refresh_devices()

    def _add_separator(self, layout):
        """Add a theme-aware separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        # Default light theme style
        line.setStyleSheet("background-color: #f0f0f0; border: none; max-height: 1px;")
        layout.addWidget(line)
        self.separators.append(line)

    def apply_theme(self, theme_name):
        """Apply theme to tab specific elements"""
        theme_manager = get_theme_manager()
        colors = theme_manager.get_theme_colors(theme_name)
        is_dark = theme_manager.is_dark_theme()

        # Explicitly set background color
        self.setStyleSheet(f"background-color: {colors['primary']};")

        # Update Separators
        separator_color = colors.get("border", "#404040" if is_dark else "#f0f0f0")
        for sep in self.separators:
            sep.setStyleSheet(f"background-color: {separator_color}; border: none; max-height: 1px;")

        # Update Labels
        text_primary = colors.get("text_primary", "#ffffff" if is_dark else "#212529")
        text_secondary = colors.get("text_secondary", "#e0e0e0" if is_dark else "#495057")
        text_muted = colors.get("text_muted", "#b0b0b0" if is_dark else "#6c757d")

        for label in self.findChildren(QLabel):
            name = label.objectName()
            if name == "section_label":
                label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {text_primary};")
            elif name == "setting_label":
                label.setStyleSheet(f"font-weight: 500; font-size: 13px; color: {text_secondary};")
            elif name == "setting_desc":
                label.setStyleSheet(f"color: {text_muted}; font-size: 11px;")

        # Unified theme application for child widgets
        from PySide6.QtWidgets import QWidget
        
        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'apply_theme'):
                try:
                    widget.apply_theme(is_dark, colors)
                except Exception:
                    pass

        # Update Buttons (Detect Now & Manage)
        # ModernButton handles its own styling via apply_theme
        pass

        # Update Refresh Button
        # Rely on ModernButton's built-in theming for consistency
        # If specific overrides are needed, apply them here, but avoid full re-styling
        pass

        if is_dark:
            self.refresh_button.setIcon(get_white_button_icon('refresh', 14))
        else:
            self.refresh_button.setIcon(get_button_icon('refresh', 14))

        # Update Level Bar
        self.level_bar.apply_theme(is_dark, colors)

    def start_monitoring(self):
        """Start continuous audio monitoring for the level meter"""
        try:
            # Ensure audio manager is monitoring
            self.audio_manager.start_monitoring()
            # Connect signal using UniqueConnection to avoid duplicates and disconnect warnings
            try:
                # Check if already connected to avoid runtime warnings
                if not hasattr(self, '_is_level_connected'):
                    self._is_level_connected = False
                
                if not self._is_level_connected:
                    self.audio_manager.audio_level_changed.connect(self.update_level_meter_value, Qt.UniqueConnection)
                    self._is_level_connected = True
            except RuntimeError:
                # Already connected
                self._is_level_connected = True
                pass
        except Exception as e:
            print(f"Error starting monitoring: {e}")

    def update_level_meter_value(self, level: float):
        """Update the level meter value directly from signal"""
        if not self._is_testing:
            self.level_bar.setValue(0)
            return

        # Convert level to percentage (0-100) with some boosting for visibility
        level_percent = min(100, int(level * 100 * 1.5)) 
        self.level_bar.setValue(level_percent)

    def on_test_mic_clicked(self):
        """Handle Test Microphone button click"""
        self._is_testing = not self._is_testing
        
        if self._is_testing:
            self.test_mic_button.setText("Stop Test")
            self.start_monitoring()
        else:
            self.test_mic_button.setText("Test Microphone")
            self.level_bar.setValue(0)
            
            # Stop monitoring to save resources, unless auto-select needs it
            if not self.auto_select_checkbox.isChecked():
                try:
                    self.audio_manager.stop_monitoring()
                except Exception:
                    pass



    def on_device_changed(self, index):
        """Handle microphone device selection change"""
        if index >= 0:
            device_id = self.mic_combo.currentData()
            # Apply the device change immediately to the audio manager
            self.audio_manager.set_input_device(device_id)

            # Restart monitoring with new device
            try:
                self.audio_manager.stop_monitoring()
                if device_id is not None and (self._is_testing or self.auto_select_checkbox.isChecked()):
                    self.start_monitoring()
            except Exception as e:
                print(f"Warning: Could not switch to new microphone: {e}")

    def refresh_devices(self, devices=None):
        """Refresh the list of available microphones"""
        # Handle signal argument (False) from clicked connection
        if isinstance(devices, bool):
            devices = None

        # Store current selection
        current_device_id = self.mic_combo.currentData() if self.mic_combo.count() > 0 else None

        try:
            # Update device list in audio manager if not provided
            if devices is None:
                self.audio_manager.update_available_devices()
                devices = self.audio_manager.get_available_devices()

            # Block signals to prevent intermediate selection changes during repopulation
            self.mic_combo.blockSignals(True)
            
            # Clear and repopulate combo box
            self.mic_combo.clear()

            # Get blocklist from config
            blocklist = self.config_manager.get_setting("audio/microphone_blocklist", [])

            # Remove duplicates and apply blocklist
            seen_names = set()
            filtered_devices = []

            for device in devices:
                device_name = device['name']
                
                # Skip if device is in blocklist
                if device_name in blocklist:
                    continue

                # Skip if we've already seen this device name (remove duplicates)
                if device_name in seen_names:
                    continue

                seen_names.add(device_name)
                filtered_devices.append(device)

            for device in filtered_devices:
                self.mic_combo.addItem(f"{device['name']}", device['id'])

            # Try to restore previous selection
            selection_restored = False
            if current_device_id is not None:
                for i in range(self.mic_combo.count()):
                    if self.mic_combo.itemData(i) == current_device_id:
                        self.mic_combo.setCurrentIndex(i)
                        selection_restored = True
                        break
            
            # If no selection was restored but we have devices, select the first one (or default)
            if not selection_restored and self.mic_combo.count() > 0:
                 self.mic_combo.setCurrentIndex(0)

            # If no devices found, show helpful message
            if len(filtered_devices) == 0:
                if len(devices) > 0:
                    self.mic_combo.addItem("All microphones are blocked", None)
                else:
                    self.mic_combo.addItem("No microphones found", None)

            # Store RAW device list for comparison in monitor_device_changes
            # This prevents infinite refresh loops caused by filtering
            self.last_device_list = [device['id'] for device in devices]
            
        except Exception as e:
            print(f"Error refreshing devices: {e}")
        finally:
            self.mic_combo.blockSignals(False)

    def on_auto_select_toggled(self, checked: bool):
        """Handle auto-select checkbox toggle"""
        self.detect_now_button.setEnabled(checked)
        if checked:
            self.device_monitor_timer.start(5000)
        else:
            self.device_monitor_timer.stop()

    def monitor_device_changes(self):
        """Monitor for device changes and update dropdown"""
        # Always check for device list changes regardless of auto-select
        try:
            self.audio_manager.update_available_devices()
            current_devices = self.audio_manager.get_available_devices()
            current_device_ids = [device['id'] for device in current_devices]

            if current_device_ids != self.last_device_list:
                # Only refresh if the list content actually changed
                # Pass the already fetched devices to avoid double-fetching
                self.refresh_devices(current_devices)

            # Auto-select logic
            if self.auto_select_checkbox.isChecked():
                if not hasattr(self, '_monitor_counter'):
                    self._monitor_counter = 0
                self._monitor_counter += 1

                if self._monitor_counter >= 3:
                    self._monitor_counter = 0
                    self.auto_select_active_microphone()

        except Exception as e:
            print(f"Error monitoring device changes: {e}")

    def auto_select_active_microphone(self):
        """Automatically select the currently active microphone"""
        if not self.auto_select_checkbox.isChecked():
            return

        try:
            active_device_id = self.audio_manager.get_active_device_id()

            if active_device_id is not None:
                for i in range(self.mic_combo.count()):
                    device_id = self.mic_combo.itemData(i)
                    if device_id == active_device_id:
                        if self.mic_combo.currentIndex() != i:
                            # Temporarily disconnect to avoid loop
                            self.mic_combo.currentIndexChanged.disconnect()
                            self.mic_combo.setCurrentIndex(i)
                            self.mic_combo.currentIndexChanged.connect(self.on_device_changed)
                        break
        except Exception as e:
            print(f"Error auto-selecting microphone: {e}")

    def detect_active_microphone_now(self):
        """Manually trigger active microphone detection"""
        try:
            self.detect_now_button.setText("Detecting...")
            self.detect_now_button.setEnabled(False)
            self.refresh_devices()
            
            # Force a quick check
            active_device_id = self.audio_manager.get_active_device_id()
            
            if active_device_id:
                 for i in range(self.mic_combo.count()):
                    if self.mic_combo.itemData(i) == active_device_id:
                        self.mic_combo.setCurrentIndex(i)
                        break
            
        except Exception as e:
            print(f"Error during manual detection: {e}")
        finally:
            self.detect_now_button.setText("Detect Now")
            self.detect_now_button.setEnabled(True)

    def show_blocklist_dialog(self):
        """Show dialog to manage microphone blocklist"""
        # Reuse existing logic, just ensure it looks good
        # For brevity, I'm keeping the logic but ensuring it uses the same style
        dialog = QDialog(self)
        dialog.setWindowTitle("Microphone Blocklist")
        dialog.setModal(True)
        dialog.resize(600, 400)
        layout = QVBoxLayout(dialog)
        
        # ... (Keep the rest of the dialog logic similar to before but maybe clean up styles if needed)
        # For now, let's copy the implementation from the previous version but clean it up
        
        instructions = QLabel("Blocked microphones will not appear in the selection list.")
        instructions.setStyleSheet("color: #6c757d; margin-bottom: 10px;")
        layout.addWidget(instructions)

        lists_layout = QHBoxLayout()
        
        # Available
        av_layout = QVBoxLayout()
        av_layout.addWidget(QLabel("Available:"))
        available_list = QListWidget()
        av_layout.addWidget(available_list)
        lists_layout.addLayout(av_layout)

        # Buttons
        btns_layout = QVBoxLayout()
        btns_layout.addStretch()
        btn_block = QPushButton(">>")
        btn_block.setFixedWidth(40)
        btn_block.clicked.connect(lambda: self._move_to_blocklist(available_list, blocked_list))
        btns_layout.addWidget(btn_block)
        
        btn_unblock = QPushButton("<<")
        btn_unblock.setFixedWidth(40)
        btn_unblock.clicked.connect(lambda: self._move_from_blocklist(blocked_list, available_list))
        btns_layout.addWidget(btn_unblock)
        btns_layout.addStretch()
        lists_layout.addLayout(btns_layout)

        # Blocked
        bl_layout = QVBoxLayout()
        bl_layout.addWidget(QLabel("Blocked:"))
        blocked_list = QListWidget()
        bl_layout.addWidget(blocked_list)
        lists_layout.addLayout(bl_layout)

        layout.addLayout(lists_layout)

        # Dialog buttons
        dialog_buttons = QHBoxLayout()
        dialog_buttons.addStretch()
        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self._save_blocklist(dialog, available_list, blocked_list))
        dialog_buttons.addWidget(save_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        dialog_buttons.addWidget(cancel_button)
        layout.addLayout(dialog_buttons)

        self._populate_blocklist_dialog(available_list, blocked_list)
        dialog.exec()

    def _populate_blocklist_dialog(self, available_list, blocked_list):
        self.audio_manager.update_available_devices()
        all_devices = self.audio_manager.get_available_devices()
        blocklist = self.config_manager.get_setting("audio/microphone_blocklist", [])
        
        seen = set()
        for device in all_devices:
            name = device['name']
            if name in seen: continue
            seen.add(name)
            
            if name in blocklist:
                blocked_list.addItem(name)
            else:
                available_list.addItem(name)

    def _move_to_blocklist(self, source, dest):
        row = source.currentRow()
        if row >= 0:
            item = source.takeItem(row)
            dest.addItem(item)

    def _move_from_blocklist(self, source, dest):
        self._move_to_blocklist(source, dest)

    def _save_blocklist(self, dialog, available, blocked):
        new_blocklist = []
        for i in range(blocked.count()):
            new_blocklist.append(blocked.item(i).text())
        
        self.config_manager.set_setting("audio/microphone_blocklist", new_blocklist)
        self.refresh_devices()
        dialog.accept()

    def load_settings(self):
        """Load audio settings from config"""
        device_id = self.config_manager.get_setting("audio/device_id")
        if device_id is not None:
            for i in range(self.mic_combo.count()):
                if self.mic_combo.itemData(i) == device_id:
                    self.mic_combo.setCurrentIndex(i)
                    break

        sounds_enabled = self.config_manager.get_setting("audio/sounds_enabled", True)
        self.sounds_enabled_checkbox.setChecked(bool(sounds_enabled))

        auto_select_enabled = self.config_manager.get_setting("audio/auto_select_mic", False)
        self.auto_select_checkbox.setChecked(bool(auto_select_enabled))
        self.detect_now_button.setEnabled(bool(auto_select_enabled))

    def save_settings(self):
        """Save audio settings to config"""
        # This is usually called by the parent dialog on accept
        device_id = self.mic_combo.currentData()
        self.config_manager.set_setting("audio/device_id", device_id)
        self.config_manager.set_setting("audio/sounds_enabled", self.sounds_enabled_checkbox.isChecked())
        self.config_manager.set_setting("audio/auto_select_mic", self.auto_select_checkbox.isChecked())

    def cleanup(self):
        """Clean up timers and resources"""
        try:
            if hasattr(self, 'device_monitor_timer'):
                self.device_monitor_timer.stop()
            
            # Only disconnect if we know we are connected
            if hasattr(self, '_is_level_connected') and self._is_level_connected:
                try:
                    self.audio_manager.audio_level_changed.disconnect(self.update_level_meter_value)
                    self._is_level_connected = False
                except Exception:
                    pass
        except Exception as e:
            print(f"Error during AudioTab cleanup: {e}")

