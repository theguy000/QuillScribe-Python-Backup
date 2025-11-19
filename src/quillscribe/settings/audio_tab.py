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
from PySide6.QtGui import QColor

from ..managers import AudioManager
from ..config_manager import ConfigManager
from ..icon_manager import get_button_icon, get_white_button_icon
from .ui_components import ModernGroupBox, ModernButton
from .modern_widgets import ModernComboBox, ModernCheckBox, AnimatedToggleSwitch, ModernProgressBar


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
        input_label = QLabel("Microphone")
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
        self.refresh_button = QPushButton()
        self.refresh_button.setObjectName("refresh_button")
        self.refresh_button.setIcon(get_button_icon('refresh', 14))
        self.refresh_button.setFixedSize(32, 32) # Matches combo height
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.setToolTip("Refresh Device List")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #e9ecef;
            }
            QPushButton:pressed {
                background: #dee2e6;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_devices)
        combo_row.addWidget(self.refresh_button)
        
        input_layout.addLayout(combo_row)

        # Level Meter (Integrated, always visible or subtle)
        self.level_bar = ModernProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setValue(0)
        self.level_bar.setFixedHeight(4) # Very slim
        self.level_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 2px;
                background-color: #e9ecef;
                height: 4px;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 2px;
            }
        """)
        input_layout.addWidget(self.level_bar)
        
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
        self.detect_now_button = ModernButton("Detect Now", primary=False)
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

        self.blocklist_button = ModernButton("Manage", primary=False)
        self.blocklist_button.setMinimumWidth(100) # Ensure text fits
        self.blocklist_button.setFixedHeight(32)
        self.blocklist_button.clicked.connect(self.show_blocklist_dialog)
        blocklist_row.addWidget(self.blocklist_button)

        advanced_layout.addLayout(blocklist_row)

        main_layout.addWidget(advanced_group)
        main_layout.addStretch()

        # --- Timers & State ---
        # Refresh timer for level meter
        self.level_timer = QTimer()
        self.level_timer.timeout.connect(self.update_level_meter)
        
        self.start_monitoring()

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
        from ..managers import get_theme_manager
        theme_manager = get_theme_manager()
        colors = theme_manager.get_theme_colors(theme_name)
        is_dark = theme_manager.is_dark_theme()

        # Update Separators
        separator_color = "#404040" if is_dark else "#f0f0f0"
        for sep in self.separators:
            sep.setStyleSheet(f"background-color: {separator_color}; border: none; max-height: 1px;")

        # Update Labels
        text_primary = "#ffffff" if is_dark else "#212529"
        text_secondary = "#e0e0e0" if is_dark else "#495057"
        text_muted = "#b0b0b0" if is_dark else "#6c757d"

        for label in self.findChildren(QLabel):
            name = label.objectName()
            if name == "section_label":
                label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {text_primary};")
            elif name == "setting_label":
                label.setStyleSheet(f"font-weight: 500; font-size: 13px; color: {text_secondary};")
            elif name == "setting_desc":
                label.setStyleSheet(f"color: {text_muted}; font-size: 11px;")

        # Update Buttons (Detect Now & Manage) with reduced padding for 32px height
        btn_bg = colors["secondary"] if is_dark else "#f8f9fa"
        btn_border = "#495057" if is_dark else "#dee2e6"
        btn_text = "#e9ecef" if is_dark else "#495057"
        btn_hover = "#495057" if is_dark else "#e9ecef"
        
        button_style = f"""
            QPushButton {{
                background: {btn_bg};
                color: {btn_text};
                border: 1px solid {btn_border};
                border-radius: 6px;
                padding: 4px 12px; /* Reduced padding */
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {btn_hover};
            }}
            QPushButton:pressed {{
                background: {btn_bg};
            }}
        """
        self.detect_now_button.setStyleSheet(button_style)
        self.blocklist_button.setStyleSheet(button_style)

        # Update Refresh Button
        if is_dark:
            self.refresh_button.setIcon(get_white_button_icon('refresh', 14))
            self.refresh_button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: 1px solid #555555;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background: #333333;
                }
                QPushButton:pressed {
                    background: #222222;
                }
            """)
        else:
            self.refresh_button.setIcon(get_button_icon('refresh', 14))
            self.refresh_button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background: #e9ecef;
                }
                QPushButton:pressed {
                    background: #dee2e6;
                }
            """)

        # Update Level Bar Background
        bar_bg = "#2c2c2c" if is_dark else "#e9ecef"
        self.level_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 2px;
                background-color: {bar_bg};
                height: 4px;
            }}
            QProgressBar::chunk {{
                background-color: #28a745;
                border-radius: 2px;
            }}
        """)

    def start_monitoring(self):
        """Start continuous audio monitoring for the level meter"""
        try:
            # Ensure audio manager is monitoring
            self.audio_manager.start_monitoring()
            # Connect signal using UniqueConnection to avoid duplicates and disconnect warnings
            try:
                self.audio_manager.audio_level_changed.connect(self.update_level_meter_value, Qt.UniqueConnection)
            except RuntimeError:
                # Already connected
                pass
        except Exception as e:
            print(f"Error starting monitoring: {e}")

    def update_level_meter_value(self, level: float):
        """Update the level meter value directly from signal"""
        # Convert level to percentage (0-100) with some boosting for visibility
        level_percent = min(100, int(level * 100 * 1.5)) 
        self.level_bar.setValue(level_percent)
        
        # Get current theme for background color
        from ..managers import get_theme_manager
        is_dark = get_theme_manager().is_dark_theme()
        bar_bg = "#2c2c2c" if is_dark else "#e9ecef"
        
        # Dynamic color based on level
        if level_percent > 80:
            chunk_color = "#dc3545"
        elif level_percent > 60:
            chunk_color = "#ffc107"
        else:
            chunk_color = "#28a745"

        self.level_bar.setStyleSheet(f"""
            QProgressBar {{ border: none; border-radius: 2px; background-color: {bar_bg}; height: 4px; }}
            QProgressBar::chunk {{ background-color: {chunk_color}; border-radius: 2px; }}
        """)

    def update_level_meter(self):
        """Legacy slot - kept for compatibility if needed, but we use direct signal now"""
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
                if device_id is not None:
                    self.start_monitoring()
            except Exception as e:
                print(f"Warning: Could not switch to new microphone: {e}")

    def refresh_devices(self):
        """Refresh the list of available microphones"""
        # Store current selection
        current_device_id = self.mic_combo.currentData() if self.mic_combo.count() > 0 else None

        # Update device list in audio manager
        self.audio_manager.update_available_devices()

        # Block signals to prevent intermediate selection changes during repopulation
        self.mic_combo.blockSignals(True)
        try:
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
                # (Simple ID check might be enough, but let's be safe)
                self.refresh_devices()

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
            if hasattr(self, 'level_timer'):
                self.level_timer.stop()
            try:
                self.audio_manager.audio_level_changed.disconnect(self.update_level_meter_value)
            except:
                pass
        except Exception as e:
            print(f"Error during AudioTab cleanup: {e}")

