"""
Audio Settings Tab
Handles microphone selection, testing, and audio settings
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFormLayout, QDialog, QListWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QTimer

from ..managers import AudioManager
from ..config_manager import ConfigManager
from ..icon_manager import get_button_icon, get_white_button_icon
from .modern_widgets import ModernGroupBox, ModernComboBox, ModernCheckBox, AnimatedToggleSwitch


class AudioTab(QWidget):
    """Audio settings tab"""

    def __init__(self, config_manager: ConfigManager, audio_manager: AudioManager = None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        # Use shared audio manager if provided, otherwise create new one
        self.audio_manager = audio_manager if audio_manager is not None else AudioManager()
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)  # Reduced spacing for compact scroll layout

        # Microphone selection
        mic_group = ModernGroupBox("Microphone Settings")
        mic_layout = QFormLayout(mic_group)
        mic_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Ensure form labels are visible
        mic_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: white;
                color: #2c3e50;
            }
            QLabel {
                color: #495057;
                font-size: 13px;
                font-weight: 500;
                background-color: transparent;
            }
        """)

        # Microphone selection row with refresh button
        mic_selection_layout = QHBoxLayout()
        self.mic_combo = ModernComboBox()
        self.refresh_devices()
        mic_selection_layout.addWidget(self.mic_combo)

        # Add refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setIcon(get_white_button_icon('refresh', 16))
        self.refresh_button.setIconSize(QSize(16, 16))
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_devices)
        mic_selection_layout.addWidget(self.refresh_button)

        # Add blocklist button
        self.blocklist_button = QPushButton("Blocklist")
        self.blocklist_button.setIcon(get_white_button_icon('block', 16))
        self.blocklist_button.setIconSize(QSize(16, 16))
        self.blocklist_button.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        self.blocklist_button.clicked.connect(self.show_blocklist_dialog)
        mic_selection_layout.addWidget(self.blocklist_button)

        mic_layout.addRow("Select Microphone:", mic_selection_layout)

        # Add device change connection
        self.mic_combo.currentIndexChanged.connect(self.on_device_changed)

        # Auto-select active microphone section
        auto_select_layout = QHBoxLayout()
        auto_select_layout.setSpacing(10)
        self.auto_select_checkbox = AnimatedToggleSwitch()
        self.auto_select_checkbox.setChecked(False)  # Default disabled
        self.auto_select_checkbox.toggled.connect(self.on_auto_select_toggled)
        auto_select_layout.addWidget(self.auto_select_checkbox)
        auto_select_label = QLabel("Auto-select active microphone")
        auto_select_label.setStyleSheet("color: #495057; font-size: 13px;")
        auto_select_layout.addWidget(auto_select_label, 1)

        # Add "Detect Now" button
        self.detect_now_button = QPushButton("Detect Now")
        self.detect_now_button.setIcon(get_white_button_icon('refresh', 14))
        self.detect_now_button.setIconSize(QSize(14, 14))
        self.detect_now_button.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                min-width: 60px;
            }
            QPushButton:hover {
                background: #218838;
            }
            QPushButton:disabled {
                background: #6c757d;
                color: #adb5bd;
            }
        """)
        self.detect_now_button.clicked.connect(self.detect_active_microphone_now)
        self.detect_now_button.setEnabled(True)  # Always enabled
        auto_select_layout.addWidget(self.detect_now_button)
        auto_select_layout.addStretch()

        mic_layout.addRow("", auto_select_layout)

        # Help text for auto-select
        auto_select_help = QLabel("Detects microphone with audio activity. Use 'Detect Now' while speaking into your microphone.")
        auto_select_help.setStyleSheet("""
            color: #6c757d;
            font-size: 11px;
            background-color: transparent;
        """)
        auto_select_help.setWordWrap(True)
        mic_layout.addRow("", auto_select_help)

        # Test button
        test_layout = QHBoxLayout()
        self.test_button = QPushButton("Test")
        self.test_button.setIcon(get_white_button_icon('test', 16))
        self.test_button.setIconSize(QSize(16, 16))
        self.test_button.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        self.test_button.clicked.connect(self.test_microphone)
        test_layout.addWidget(self.test_button)
        test_layout.addStretch()
        mic_layout.addRow("", test_layout)

        # Audio level meter
        self.level_label = QLabel("Audio Level:")
        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setValue(0)  # Initialize to 0
        self.level_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background-color: #f8f9fa;
                height: 24px;
                text-align: center;
                color: #495057;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #28a745, stop:0.6 #28a745, stop:0.8 #ffc107, stop:1 #dc3545);
                border-radius: 4px;
                margin: 1px;
            }
        """)
        mic_layout.addRow(self.level_label, self.level_bar)

        layout.addWidget(mic_group)

        # Sound settings
        sound_group = ModernGroupBox("Sound Settings")
        sound_layout = QFormLayout(sound_group)
        sound_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Ensure form labels are visible
        sound_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: white;
                color: #2c3e50;
            }
            QLabel {
                color: #495057;
                font-size: 13px;
                font-weight: 500;
                background-color: transparent;
            }
        """)

        # Enable notification sounds toggle
        sounds_toggle_layout = QHBoxLayout()
        sounds_toggle_layout.setSpacing(10)
        self.sounds_enabled_checkbox = AnimatedToggleSwitch()
        sounds_toggle_layout.addWidget(self.sounds_enabled_checkbox)
        sounds_label = QLabel("Enable notification sounds")
        sounds_label.setStyleSheet("color: #495057; font-size: 13px;")
        sounds_toggle_layout.addWidget(sounds_label, 1)
        sound_layout.addRow(sounds_toggle_layout)

        # Help text for sounds
        sound_help = QLabel("Play sounds when starting and stopping recording")
        sound_help.setStyleSheet("""
            color: #6c757d;
            font-size: 11px;
            background-color: transparent;
        """)
        sound_help.setWordWrap(True)
        sound_layout.addRow("", sound_help)

        layout.addWidget(sound_group)

        # Refresh timer for level meter
        self.level_timer = QTimer()
        self.level_timer.timeout.connect(self.update_level_meter)

        # Microphone testing state
        self.is_testing = False
        self.test_audio_manager = None

        # Real-time device monitoring
        self.device_monitor_timer = QTimer()
        self.device_monitor_timer.timeout.connect(self.monitor_device_changes)
        self.device_monitor_timer.start(2000)  # Check every 2 seconds
        self.last_device_list = []

        # Add minimal space for scroll layout
        layout.addStretch()

    def on_device_changed(self, index):
        """Handle microphone device selection change"""
        if index >= 0:
            device_id = self.mic_combo.currentData()
            # Apply the device change immediately to the audio manager
            self.audio_manager.set_input_device(device_id)

            # Stop current monitoring and restart with new device
            try:
                self.audio_manager.stop_monitoring()
                if device_id is not None:
                    self.audio_manager.start_monitoring()
            except Exception as e:
                print(f"Warning: Could not switch to new microphone: {e}")

    def refresh_devices(self):
        """Refresh the list of available microphones"""
        # Store current selection
        current_device_id = self.mic_combo.currentData() if self.mic_combo.count() > 0 else None

        # Update device list in audio manager
        self.audio_manager.update_available_devices()

        # Clear and repopulate combo box
        self.mic_combo.clear()
        devices = self.audio_manager.get_available_devices()

        # Get blocklist from config
        blocklist = self.config_manager.get_setting("audio/microphone_blocklist", [])

        # Remove duplicates and apply blocklist
        seen_names = set()
        filtered_devices = []

        for device in devices:
            device_name = device['name']
            device_id = device['id']

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
        if current_device_id is not None:
            for i in range(self.mic_combo.count()):
                if self.mic_combo.itemData(i) == current_device_id:
                    self.mic_combo.setCurrentIndex(i)
                    break

        # If no devices found, show helpful message
        if len(filtered_devices) == 0:
            if len(devices) > 0:
                self.mic_combo.addItem("All microphones are blocked", None)
            else:
                self.mic_combo.addItem("No microphones found", None)

        # Store current device list for comparison
        self.last_device_list = [device['id'] for device in filtered_devices]

    def test_microphone(self):
        """Test the selected microphone with continuous level monitoring"""
        if not self.is_testing:
            # Start testing
            self.is_testing = True
            self.test_button.setText("Stop Test")
            self.test_button.setStyleSheet("""
                QPushButton {
                    background: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #c82333;
                }
            """)

            # Start audio level monitoring
            current_data = self.mic_combo.currentData()
            device_id = current_data if current_data is not None else None

            try:
                self.audio_manager.set_input_device(device_id)
                # Start audio monitoring for the test
                self.audio_manager.start_monitoring()
                # Connect to level updates
                self.audio_manager.audio_level_changed.connect(self.update_test_level_meter)
                self.level_timer.start(50)  # Update every 50ms

            except Exception as e:
                self.stop_testing()
                self.show_test_error(f"Error starting test: {str(e)}")
        else:
            # Stop testing
            self.stop_testing()

    def stop_testing(self):
        """Stop microphone testing"""
        self.is_testing = False
        self.test_button.setText("Test Mic")
        self.test_button.setIcon(get_white_button_icon('test', 16))
        self.test_button.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)

        # Stop level monitoring
        self.level_timer.stop()
        try:
            self.audio_manager.audio_level_changed.disconnect(self.update_test_level_meter)
        except:
            pass  # Ignore if not connected

        # Reset level bar
        self.level_bar.setValue(0)

    def update_test_level_meter(self, level: float):
        """Update the level meter during testing"""
        # Convert level to percentage (0-100)
        level_percent = min(100, int(level * 100))
        self.level_bar.setValue(level_percent)

    def show_test_error(self, error_msg: str):
        """Show error message for testing"""
        self.test_button.setText("Error")
        self.test_button.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
        """)
        # Reset after 3 seconds
        QTimer.singleShot(3000, self.stop_testing)

    def update_level_meter(self):
        """Update audio level meter (placeholder for general monitoring)"""
        if not self.is_testing:
            self.level_bar.setValue(0)

    def on_auto_select_toggled(self, checked: bool):
        """Handle auto-select checkbox toggle"""
        # Detect now button is always enabled, no need to toggle it

        if checked:
            # Use a longer interval for automatic detection to be less intrusive
            self.device_monitor_timer.start(5000)  # Start monitoring every 5 seconds
            # Don't auto-detect immediately on toggle - let user use "Detect Now" button
        else:
            self.device_monitor_timer.stop()  # Stop monitoring

    def monitor_device_changes(self):
        """Monitor for device changes and update dropdown"""
        if not self.auto_select_checkbox.isChecked():
            return

        try:
            # Update device list
            self.audio_manager.update_available_devices()
            current_devices = self.audio_manager.get_available_devices()
            current_device_ids = [device['id'] for device in current_devices]

            # Check if device list has changed
            if current_device_ids != self.last_device_list:
                print("Device list changed, refreshing...")
                self.refresh_devices()

            # Only do intensive audio detection occasionally (every 3rd check ~ 15 seconds)
            if not hasattr(self, '_monitor_counter'):
                self._monitor_counter = 0
            self._monitor_counter += 1

            if self._monitor_counter >= 3:
                self._monitor_counter = 0
                # Try to auto-select the active microphone
                self.auto_select_active_microphone()

        except Exception as e:
            print(f"Error monitoring device changes: {e}")

    def auto_select_active_microphone(self):
        """Automatically select the currently active microphone"""
        if not self.auto_select_checkbox.isChecked():
            return

        try:
            # Get the active device ID using the audio manager
            active_device_id = self.audio_manager.get_active_device_id()

            if active_device_id is not None:
                # Find matching device in combo box
                for i in range(self.mic_combo.count()):
                    device_id = self.mic_combo.itemData(i)

                    if device_id == active_device_id:
                        if self.mic_combo.currentIndex() != i:
                            device_name = self.mic_combo.itemText(i)
                            print(f"Auto-selecting microphone: {device_name}")
                            # Temporarily disconnect signal to avoid recursion
                            self.mic_combo.currentIndexChanged.disconnect()
                            self.mic_combo.setCurrentIndex(i)
                            self.mic_combo.currentIndexChanged.connect(self.on_device_changed)
                        break
        except Exception as e:
            print(f"Error auto-selecting microphone: {e}")

    def show_blocklist_dialog(self):
        """Show dialog to manage microphone blocklist"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Microphone Blocklist")
        dialog.setModal(True)
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        # Instructions
        instructions = QLabel("Blocked microphones will not appear in the microphone selection list.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #6c757d; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(instructions)

        # Available devices section
        available_label = QLabel("Available Microphones:")
        available_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(available_label)

        available_list = QListWidget()
        available_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: #ffffff;
                selection-background-color: #ffebee;
                selection-color: #d32f2f;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f0f0f0;
                border: none;
                outline: none;
            }
            QListWidget::item:selected {
                background-color: #ffcdd2;
                color: #d32f2f;
                border: none;
                outline: none;
            }
            QListWidget::item:hover {
                background-color: #fce4ec;
            }
            QListWidget::item:focus {
                outline: none;
                border: none;
            }
        """)
        layout.addWidget(available_list)

        # Buttons for available devices
        available_buttons = QHBoxLayout()
        block_button = QPushButton("Block Selected")
        block_button.setIcon(get_button_icon('block', 16))
        block_button.clicked.connect(lambda: self._move_to_blocklist(available_list, blocked_list))
        available_buttons.addWidget(block_button)
        available_buttons.addStretch()
        layout.addLayout(available_buttons)

        # Blocked devices section
        blocked_label = QLabel("Blocked Microphones:")
        blocked_label.setStyleSheet("font-weight: bold; margin-bottom: 5px; margin-top: 10px;")
        layout.addWidget(blocked_label)

        blocked_list = QListWidget()
        blocked_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: #ffffff;
                selection-background-color: #ffebee;
                selection-color: #d32f2f;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f0f0f0;
                background-color: #ffebee;
                color: #d32f2f;
                border: none;
                outline: none;
            }
            QListWidget::item:selected {
                background-color: #ffcdd2;
                color: #d32f2f;
                border: none;
                outline: none;
            }
            QListWidget::item:hover {
                background-color: #fce4ec;
            }
            QListWidget::item:focus {
                outline: none;
                border: none;
            }
        """)
        layout.addWidget(blocked_list)

        # Buttons for blocked devices
        blocked_buttons = QHBoxLayout()
        unblock_button = QPushButton("Unblock Selected")
        unblock_button.setIcon(get_button_icon('refresh', 16))
        unblock_button.clicked.connect(lambda: self._move_from_blocklist(blocked_list, available_list))
        blocked_buttons.addWidget(unblock_button)
        blocked_buttons.addStretch()
        layout.addLayout(blocked_buttons)

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

        # Populate lists
        self._populate_blocklist_dialog(available_list, blocked_list)

        dialog.exec()

    def _populate_blocklist_dialog(self, available_list, blocked_list):
        """Populate the blocklist dialog with current devices"""
        # Get all devices (including blocked ones)
        self.audio_manager.update_available_devices()
        all_devices = self.audio_manager.get_available_devices()

        # Get current blocklist
        blocklist = self.config_manager.get_setting("audio/microphone_blocklist", [])

        # Remove duplicates from all devices
        seen_names = set()
        unique_devices = []
        for device in all_devices:
            if device['name'] not in seen_names:
                seen_names.add(device['name'])
                unique_devices.append(device)

        # Populate lists
        for device in unique_devices:
            device_name = device['name']
            if device_name in blocklist:
                blocked_list.addItem(device_name)
            else:
                available_list.addItem(device_name)

    def _move_to_blocklist(self, available_list, blocked_list):
        """Move selected device from available to blocked list"""
        current_item = available_list.currentItem()
        if current_item:
            device_name = current_item.text()
            available_list.takeItem(available_list.row(current_item))
            blocked_list.addItem(device_name)

    def _move_from_blocklist(self, blocked_list, available_list):
        """Move selected device from blocked to available list"""
        current_item = blocked_list.currentItem()
        if current_item:
            device_name = current_item.text()
            blocked_list.takeItem(blocked_list.row(current_item))
            available_list.addItem(device_name)

    def _save_blocklist(self, dialog, available_list, blocked_list):
        """Save the blocklist configuration"""
        # Build new blocklist from blocked_list widget
        new_blocklist = []
        for i in range(blocked_list.count()):
            item = blocked_list.item(i)
            new_blocklist.append(item.text())

        # Save to config
        self.config_manager.set_setting("audio/microphone_blocklist", new_blocklist)

        # Refresh the device list to apply changes
        self.refresh_devices()

        dialog.accept()

    def detect_active_microphone_now(self):
        """Manually trigger active microphone detection"""
        try:
            # Change button text to indicate detection is in progress
            self.detect_now_button.setText("Detecting...")
            self.detect_now_button.setEnabled(False)

            # Force a refresh of available devices first
            self.refresh_devices()

            # Try to detect the active microphone
            active_device_id = self.audio_manager.get_active_device_id()

            if active_device_id is not None:
                # Find matching device in combo box
                device_found = False
                for i in range(self.mic_combo.count()):
                    device_id = self.mic_combo.itemData(i)

                    if device_id == active_device_id:
                        device_name = self.mic_combo.itemText(i)
                        print(f"Manually detected active microphone: {device_name}")

                        # Temporarily disconnect signal to avoid recursion
                        self.mic_combo.currentIndexChanged.disconnect()
                        self.mic_combo.setCurrentIndex(i)
                        self.mic_combo.currentIndexChanged.connect(self.on_device_changed)
                        device_found = True
                        break

                if not device_found:
                    print("Active microphone detected but not found in dropdown")
            else:
                print("No active microphone detected - try speaking into your microphone and click 'Detect Now' again")

        except Exception as e:
            print(f"Error during manual detection: {e}")
        finally:
            # Reset button state
            self.detect_now_button.setText("Detect Now")
            self.detect_now_button.setEnabled(True)

    def load_settings(self):
        """Load audio settings from config"""
        device_id = self.config_manager.get_setting("audio/device_id")
        if device_id is not None:
            # Find and select the device in combo box
            for i in range(self.mic_combo.count()):
                if self.mic_combo.itemData(i) == device_id:
                    self.mic_combo.setCurrentIndex(i)
                    break

        # Load sounds setting
        sounds_enabled = self.config_manager.get_setting("audio/sounds_enabled", True)
        self.sounds_enabled_checkbox.setChecked(bool(sounds_enabled))

        # Load auto-select setting
        auto_select_enabled = self.config_manager.get_setting("audio/auto_select_mic", False)
        self.auto_select_checkbox.setChecked(bool(auto_select_enabled))

        # Detect now button is always enabled, no need to update state

        # If auto-select is enabled, start monitoring
        if auto_select_enabled:
            self.device_monitor_timer.start(5000)

    def save_settings(self):
        """Save audio settings to config"""
        device_id = self.mic_combo.currentData()
        self.config_manager.set_setting("audio/device_id", device_id)

        # Save sounds setting
        self.config_manager.set_setting("audio/sounds_enabled", self.sounds_enabled_checkbox.isChecked())

        # Save auto-select setting
        self.config_manager.set_setting("audio/auto_select_mic", self.auto_select_checkbox.isChecked())

    def cleanup(self):
        """Clean up timers and resources"""
        try:
            if hasattr(self, 'device_monitor_timer'):
                self.device_monitor_timer.stop()
            if hasattr(self, 'level_timer'):
                self.level_timer.stop()
            self.stop_testing()
        except Exception as e:
            print(f"Error during AudioTab cleanup: {e}")

