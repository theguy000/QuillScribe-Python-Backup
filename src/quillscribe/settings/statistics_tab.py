"""
Statistics Tab for QuillScribe Settings
Displays usage statistics, performance metrics, and transcription history
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QTextEdit, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt

from ..managers import StatisticsManager
from .ui_components import ModernButton, ModernGroupBox
from .base_tab import BaseSettingsTab


class StatisticsTab(QWidget):
    """Statistics and performance monitoring tab"""

    def __init__(self, statistics_manager: StatisticsManager, parent=None):
        super().__init__(parent)
        self.statistics_manager = statistics_manager
        self.setup_ui()
        self.load_statistics()

        # Connect to statistics updates
        self.statistics_manager.stats_updated.connect(self.load_statistics)

    def apply_theme(self, primary_color="#ffffff", secondary_color="#f8f9fa"):
        """Apply theme colors to the statistics tab"""
        # Determine if this is a dark theme
        r = int(primary_color.lstrip('#')[0:2], 16)
        g = int(primary_color.lstrip('#')[2:4], 16)
        b = int(primary_color.lstrip('#')[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        is_dark = brightness < 128

        # Apply theme to history text area
        if is_dark:
            history_style = f"""
                QTextEdit {{
                    background-color: {secondary_color};
                    border: 1px solid #495057;
                    border-radius: 4px;
                    padding: 8px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 11px;
                    color: #e9ecef;
                }}
            """
        else:
            history_style = f"""
                QTextEdit {{
                    background-color: {secondary_color};
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 8px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 11px;
                    color: #495057;
                }}
            """

        if hasattr(self, 'history_list'):
            self.history_list.setStyleSheet(history_style)

        # Apply theme to buttons using the correct signature for ModernButton
        for button in [self.refresh_button, self.export_button, self.reset_button]:
            if hasattr(button, 'apply_theme'):
                button.apply_theme(primary_color, secondary_color)

        # Apply theme to all ModernGroupBox components
        from .ui_components import ModernGroupBox
        for group_box in self.findChildren(ModernGroupBox):
            if hasattr(group_box, 'apply_theme'):
                group_box.apply_theme(primary_color, secondary_color)

        # Apply background color and text color to the tab itself
        # Use dark text for light themes, light text for dark themes
        text_color = "#e9ecef" if is_dark else "#212529"
        print(f"Statistics tab theming: is_dark={is_dark}, primary_color={primary_color}, text_color={text_color}")
        self.setStyleSheet(f"""
            StatisticsTab {{
                background-color: {primary_color};
                color: {text_color};
            }}
        """)

        # Apply text color to all labels
        self._apply_label_theming(text_color)
    
    def setup_ui(self):
        """Setup the statistics tab UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Usage Statistics Group
        usage_group = ModernGroupBox("Usage Statistics")
        usage_layout = QFormLayout(usage_group)
        
        self.total_sessions_label = QLabel("0")
        self.total_recordings_label = QLabel("0")
        self.total_duration_label = QLabel("0h 0m")
        self.success_rate_label = QLabel("0%")
        
        usage_layout.addRow("Total Sessions:", self.total_sessions_label)
        usage_layout.addRow("Total Recordings:", self.total_recordings_label)
        usage_layout.addRow("Total Duration:", self.total_duration_label)
        usage_layout.addRow("Success Rate:", self.success_rate_label)
        
        layout.addWidget(usage_group)
        
        # Performance Metrics Group
        performance_group = ModernGroupBox("Performance Metrics")
        performance_layout = QFormLayout(performance_group)
        
        self.avg_transcription_time_label = QLabel("0.0s")
        self.fastest_transcription_label = QLabel("0.0s")
        self.slowest_transcription_label = QLabel("0.0s")
        self.avg_audio_duration_label = QLabel("0.0s")
        
        performance_layout.addRow("Avg Transcription Time:", self.avg_transcription_time_label)
        performance_layout.addRow("Fastest Transcription:", self.fastest_transcription_label)
        performance_layout.addRow("Slowest Transcription:", self.slowest_transcription_label)
        performance_layout.addRow("Avg Audio Duration:", self.avg_audio_duration_label)
        
        layout.addWidget(performance_group)
        
        # Mode Usage Group
        mode_group = ModernGroupBox("Mode Usage")
        mode_layout = QFormLayout(mode_group)
        
        self.api_usage_label = QLabel("0")
        self.local_usage_label = QLabel("0")
        self.total_characters_label = QLabel("0")
        
        mode_layout.addRow("API Transcriptions:", self.api_usage_label)
        mode_layout.addRow("Local Transcriptions:", self.local_usage_label)
        mode_layout.addRow("Total Characters:", self.total_characters_label)
        
        layout.addWidget(mode_group)
        
        # Current Session Group
        session_group = ModernGroupBox("Current Session")
        session_layout = QFormLayout(session_group)
        
        self.session_duration_label = QLabel("0h 0m")
        self.session_recordings_label = QLabel("0")
        self.session_success_label = QLabel("0")
        self.session_failed_label = QLabel("0")
        
        session_layout.addRow("Session Duration:", self.session_duration_label)
        session_layout.addRow("Recordings:", self.session_recordings_label)
        session_layout.addRow("Successful:", self.session_success_label)
        session_layout.addRow("Failed:", self.session_failed_label)
        
        layout.addWidget(session_group)
        
        # Recent History Group
        history_group = ModernGroupBox("Recent History (Last 7 Days)")
        history_layout = QVBoxLayout(history_group)
        
        # History list - styling will be applied by theme system
        self.history_list = QTextEdit()
        self.history_list.setMaximumHeight(150)
        self.history_list.setReadOnly(True)
        # Initial basic styling - will be overridden by apply_theme
        self.history_list.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        history_layout.addWidget(self.history_list)
        
        layout.addWidget(history_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = ModernButton("Refresh")
        self.refresh_button.clicked.connect(self.load_statistics)
        button_layout.addWidget(self.refresh_button)
        
        self.export_button = ModernButton("Export Statistics")
        self.export_button.clicked.connect(self.export_statistics)
        button_layout.addWidget(self.export_button)
        
        self.reset_button = ModernButton("Reset Statistics")
        self.reset_button.clicked.connect(self.reset_statistics)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Store references to all our labels for easier theming
        self.all_value_labels = [
            self.total_sessions_label, self.total_recordings_label, self.total_duration_label,
            self.success_rate_label, self.avg_transcription_time_label, self.fastest_transcription_label,
            self.slowest_transcription_label, self.avg_audio_duration_label, self.api_usage_label,
            self.local_usage_label, self.total_characters_label, self.session_duration_label,
            self.session_recordings_label, self.session_success_label, self.session_failed_label
        ]
    
    def load_statistics(self):
        """Load and display current statistics"""
        stats = self.statistics_manager.get_statistics()
        session_stats = self.statistics_manager.get_session_statistics()
        
        # Usage statistics
        self.total_sessions_label.setText(str(stats['total_sessions']))
        self.total_recordings_label.setText(str(stats['total_recordings']))
        
        # Format duration
        total_minutes = int(stats['total_duration'] / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        self.total_duration_label.setText(f"{hours}h {minutes}m")
        
        # Success rate
        success_rate = self.statistics_manager.get_accuracy_rate()
        self.success_rate_label.setText(f"{success_rate:.1f}%")
        
        # Performance metrics
        perf = stats['performance_metrics']
        self.avg_transcription_time_label.setText(f"{perf['average_transcription_time']:.2f}s")
        
        if perf['fastest_transcription'] != float('inf'):
            self.fastest_transcription_label.setText(f"{perf['fastest_transcription']:.2f}s")
        else:
            self.fastest_transcription_label.setText("N/A")
            
        self.slowest_transcription_label.setText(f"{perf['slowest_transcription']:.2f}s")
        self.avg_audio_duration_label.setText(f"{perf['average_audio_duration']:.2f}s")
        
        # Mode usage
        self.api_usage_label.setText(str(stats['usage_by_mode']['api']))
        self.local_usage_label.setText(str(stats['usage_by_mode']['local']))
        self.total_characters_label.setText(f"{stats['total_characters']:,}")
        
        # Current session
        session_minutes = int(session_stats['session_duration'] / 60)
        session_hours = session_minutes // 60
        session_mins = session_minutes % 60
        self.session_duration_label.setText(f"{session_hours}h {session_mins}m")
        self.session_recordings_label.setText(str(session_stats['recordings']))
        self.session_success_label.setText(str(session_stats['successful_transcriptions']))
        self.session_failed_label.setText(str(session_stats['failed_transcriptions']))
        
        # Recent history
        self.load_recent_history()
    
    def load_recent_history(self):
        """Load and display recent transcription history"""
        history = self.statistics_manager.get_recent_history(7)
        
        if not history:
            self.history_list.setText("No recent transcriptions")
            return
        
        history_text = []
        for entry in history[:20]:  # Show last 20 entries
            timestamp = entry['timestamp'][:19].replace('T', ' ')  # Format datetime
            mode = entry['mode'].upper()
            duration = f"{entry['duration']:.1f}s"
            
            if entry['success']:
                status = "✓"
                chars = entry.get('text_length', 0)
                line = f"{timestamp} | {mode} | {duration} | {status} | {chars} chars"
            else:
                status = "✗"
                line = f"{timestamp} | {mode} | {duration} | {status} | Failed"
            
            history_text.append(line)
        
        self.history_list.setText('\n'.join(history_text))
    
    def export_statistics(self):
        """Export statistics to a file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Statistics",
            f"quillscribe_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )

        if file_path:
            if self.statistics_manager.export_statistics(file_path):
                msg = QMessageBox(self)
                msg.setWindowTitle("Export Successful")
                msg.setText(f"Statistics exported to:\n{file_path}")
                msg.setIcon(QMessageBox.Icon.Information)
                self._apply_message_box_theme(msg)
                msg.exec()
            else:
                msg = QMessageBox(self)
                msg.setWindowTitle("Export Failed")
                msg.setText("Failed to export statistics.")
                msg.setIcon(QMessageBox.Icon.Warning)
                self._apply_message_box_theme(msg)
                msg.exec()
    
    def reset_statistics(self):
        """Reset all statistics after confirmation"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Reset Statistics")
        msg.setText("Are you sure you want to reset all statistics?\n\nThis action cannot be undone.")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        self._apply_message_box_theme(msg)

        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.statistics_manager.reset_statistics()

            msg = QMessageBox(self)
            msg.setWindowTitle("Reset Complete")
            msg.setText("All statistics have been reset.")
            msg.setIcon(QMessageBox.Icon.Information)
            self._apply_message_box_theme(msg)
            msg.exec()

    def _apply_message_box_theme(self, msg_box):
        """Apply current theme to message box"""
        # Get current theme from parent dialog
        parent_dialog = self.parent()
        while parent_dialog and not hasattr(parent_dialog, 'config_manager'):
            parent_dialog = parent_dialog.parent()

        if parent_dialog and hasattr(parent_dialog, 'config_manager'):
            theme = parent_dialog.config_manager.get_setting("ui/theme", "white")

            # Theme color definitions (same as main settings dialog)
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

            if theme in THEMES:
                theme_colors = THEMES[theme]
                primary_color = theme_colors["primary"]

                # Determine if this is a dark theme
                r = int(primary_color.lstrip('#')[0:2], 16)
                g = int(primary_color.lstrip('#')[2:4], 16)
                b = int(primary_color.lstrip('#')[4:6], 16)
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                is_dark = brightness < 128

                if is_dark:
                    msg_style = f"""
                        QMessageBox {{
                            background-color: {primary_color};
                            color: #e9ecef;
                        }}
                        QMessageBox QLabel {{
                            color: #e9ecef;
                        }}
                        QMessageBox QPushButton {{
                            background-color: #495057;
                            color: #e9ecef;
                            border: 1px solid #6c757d;
                            border-radius: 4px;
                            padding: 6px 12px;
                            min-width: 60px;
                        }}
                        QMessageBox QPushButton:hover {{
                            background-color: #6c757d;
                        }}
                        QMessageBox QPushButton:pressed {{
                            background-color: #343a40;
                        }}
                    """
                else:
                    msg_style = f"""
                        QMessageBox {{
                            background-color: {primary_color};
                            color: #495057;
                        }}
                        QMessageBox QLabel {{
                            color: #495057;
                        }}
                        QMessageBox QPushButton {{
                            background-color: #e9ecef;
                            color: #495057;
                            border: 1px solid #dee2e6;
                            border-radius: 4px;
                            padding: 6px 12px;
                            min-width: 60px;
                        }}
                        QMessageBox QPushButton:hover {{
                            background-color: #f8f9fa;
                        }}
                        QMessageBox QPushButton:pressed {{
                            background-color: #dee2e6;
                        }}
                    """

                msg_box.setStyleSheet(msg_style)

    def _apply_label_theming(self, text_color):
        """Apply text color theming to all labels in the statistics tab"""
        try:
            label_count = 0

            # Apply to all QLabel widgets in the statistics tab
            for label in self.findChildren(QLabel):
                label_count += 1
                current_style = label.styleSheet()

                # Always apply the text color, overriding any existing color
                if current_style:
                    # Remove any existing color declarations and add new one
                    import re
                    # Remove existing color declarations
                    new_style = re.sub(r'color:\s*[^;]+;?', '', current_style)
                    # Clean up any double semicolons or trailing semicolons
                    new_style = re.sub(r';;+', ';', new_style).strip(';')
                    # Add the new color
                    if new_style:
                        new_style = f"{new_style}; color: {text_color};"
                    else:
                        new_style = f"color: {text_color};"
                    label.setStyleSheet(new_style)
                else:
                    # No existing style, just set color
                    label.setStyleSheet(f"color: {text_color};")

            # Also apply to form labels (the field names in QFormLayout)
            from PySide6.QtWidgets import QFormLayout
            form_label_count = 0
            for form_layout in self.findChildren(QFormLayout):
                for i in range(form_layout.rowCount()):
                    label_item = form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
                    if label_item and label_item.widget():
                        label_widget = label_item.widget()
                        if isinstance(label_widget, QLabel):
                            form_label_count += 1
                            # Force the color for form labels
                            label_widget.setStyleSheet(f"color: {text_color}; font-weight: normal;")

            # Also apply to our specific value labels to ensure they get themed
            if hasattr(self, 'all_value_labels'):
                value_label_count = 0
                for value_label in self.all_value_labels:
                    if value_label:
                        value_label_count += 1
                        value_label.setStyleSheet(f"color: {text_color}; font-weight: bold;")

        except Exception as e:
            print(f"Warning: Could not apply statistics label theming: {e}")
