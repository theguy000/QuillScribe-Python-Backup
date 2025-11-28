"""
Statistics Tab for QuillScribe Settings
Displays usage statistics, performance metrics, and transcription history
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QTextEdit, QMessageBox, QFileDialog, QFrame, QGridLayout, QScrollArea,
    QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

from ..managers import StatisticsManager, get_theme_manager
from .ui_components import ModernGroupBox, apply_theme_recursively
from .modern_buttons import ModernButton, ButtonVariant
from .base_tab import BaseSettingsTab


class StatCard(QFrame):
    """A card widget to display a single statistic"""
    
    def __init__(self, title, value="0", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Set size policy to expand
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(140)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(Qt.GlobalColor.transparent) # Initial transparent shadow
        self.setGraphicsEffect(shadow)
        self.shadow_effect = shadow

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        
        self.value_label = QLabel(value)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.value_label.setWordWrap(True)
        
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.title_label.setWordWrap(True)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        
    def set_value(self, value):
        self.value_label.setText(str(value))
        
    def apply_theme(self, is_dark: bool, colors: dict):
        """Apply theme to the card"""
        theme_manager = get_theme_manager()
        
        # Extract colors
        primary_color = colors.get("primary", "#ffffff")
        secondary_color = colors.get("secondary", "#f8f9fa")
        text_primary = colors.get("text_primary", "#212529")
        text_secondary = colors.get("text_secondary", "#6c757d")
        
        if is_dark:
            # Dark mode: Card bg should be slightly lighter than container (secondary)
            bg_color = theme_manager.lighten_color(secondary_color, 0.05)
            border_color = colors.get("border", "transparent")
            value_color = "#ffffff"
            title_color = text_secondary
            shadow_color = "#000000"
            shadow_opacity = 80
        else:
            # Light mode: Card bg white, container is secondary (grayish)
            bg_color = "#ffffff"
            border_color = colors.get("border", "#e9ecef")
            value_color = colors.get("accent", "#212529") # Use accent or dark text
            title_color = text_secondary
            shadow_color = "#000000"
            shadow_opacity = 20
            
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 12px;
            }}
        """)
        
        # Update shadow color
        s_color = QColor(shadow_color)
        s_color.setAlpha(shadow_opacity)
        self.shadow_effect.setColor(s_color)
        
        self.value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {value_color};
            border: none;
            background: transparent;
            font-family: 'Segoe UI', sans-serif;
        """)
        
        self.title_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {title_color};
            text-transform: uppercase;
            letter-spacing: 0.8px;
            border: none;
            background: transparent;
        """)


class StatisticsTab(QWidget):
    """Statistics and performance monitoring tab"""

    def __init__(self, statistics_manager: StatisticsManager, parent=None):
        super().__init__(parent)
        self.statistics_manager = statistics_manager
        self.setup_ui()
        self.load_statistics()

        # Connect to statistics updates
        self.statistics_manager.stats_updated.connect(self.load_statistics)

    def apply_theme(self, theme_name, is_dark=None, colors=None):
        """Apply theme colors to the statistics tab"""
        theme_manager = get_theme_manager()
        
        if colors is None:
            colors = theme_manager.get_theme_colors(theme_name)
        
        if is_dark is None:
            is_dark = theme_manager.is_dark_theme()
        
        primary_color = colors.get("primary", "#ffffff")
        secondary_color = colors.get("secondary", "#f8f9fa")
        border_color = colors.get("border", "#dee2e6")
        text_primary = colors.get("text_primary", "#212529")

        # Apply theme to history text area
        if is_dark:
            history_style = f"""
                QTextEdit {{
                    background-color: {secondary_color};
                    border: 1px solid {border_color};
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
                    border: 1px solid {border_color};
                    border-radius: 4px;
                    padding: 8px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 11px;
                    color: #495057;
                }}
            """

        if hasattr(self, 'history_list'):
            self.history_list.setStyleSheet(history_style)

        # Apply theme to all child widgets (GroupBoxes, StatCards, Buttons)
        apply_theme_recursively(self, is_dark, colors)

        # Apply background color and text color to the tab itself
        text_color = "#e9ecef" if is_dark else "#212529"
        
        # Apply to the scroll area widget if it exists
        if hasattr(self, 'scroll_widget'):
            self.scroll_widget.setStyleSheet(f"""
                QWidget#stats_scroll_widget {{
                    background-color: transparent;
                }}
                QLabel {{
                    color: {text_color};
                }}
            """)
            
        self.setStyleSheet(f"""
            StatisticsTab {{
                background-color: {colors['primary']};
            }}
        """)
    
    def setup_ui(self):
        """Setup the statistics tab UI"""
        # Main layout for the tab
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create a widget to hold the content
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("stats_scroll_widget")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(16, 16, 16, 16)
        self.scroll_layout.setSpacing(16)
        
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Usage Statistics Group
        usage_group = ModernGroupBox("Usage Statistics")
        usage_layout = QGridLayout(usage_group)
        usage_layout.setSpacing(12)
        
        self.total_sessions_card = StatCard("Total Sessions")
        self.total_recordings_card = StatCard("Total Recordings")
        self.total_duration_card = StatCard("Total Duration")
        self.success_rate_card = StatCard("Success Rate")
        
        usage_layout.addWidget(self.total_sessions_card, 0, 0)
        usage_layout.addWidget(self.total_recordings_card, 0, 1)
        usage_layout.addWidget(self.total_duration_card, 1, 0)
        usage_layout.addWidget(self.success_rate_card, 1, 1)
        
        self.scroll_layout.addWidget(usage_group)
        
        # Performance Metrics Group
        performance_group = ModernGroupBox("Performance Metrics")
        performance_layout = QGridLayout(performance_group)
        performance_layout.setSpacing(12)
        
        self.avg_transcription_time_card = StatCard("Avg Time")
        self.fastest_transcription_card = StatCard("Fastest")
        self.slowest_transcription_card = StatCard("Slowest")
        self.avg_audio_duration_card = StatCard("Avg Audio")
        
        performance_layout.addWidget(self.avg_transcription_time_card, 0, 0)
        performance_layout.addWidget(self.fastest_transcription_card, 0, 1)
        performance_layout.addWidget(self.slowest_transcription_card, 1, 0)
        performance_layout.addWidget(self.avg_audio_duration_card, 1, 1)
        
        self.scroll_layout.addWidget(performance_group)
        
        # Mode Usage Group
        mode_group = ModernGroupBox("Mode Usage")
        mode_layout = QGridLayout(mode_group)
        mode_layout.setSpacing(12)
        
        self.api_usage_card = StatCard("API Mode")
        self.local_usage_card = StatCard("Local Mode")
        self.total_characters_card = StatCard("Total Chars")
        
        mode_layout.addWidget(self.api_usage_card, 0, 0)
        mode_layout.addWidget(self.local_usage_card, 0, 1)
        mode_layout.addWidget(self.total_characters_card, 1, 0, 1, 2) # Span 2 columns
        
        self.scroll_layout.addWidget(mode_group)
        
        # Current Session Group
        session_group = ModernGroupBox("Current Session")
        session_layout = QGridLayout(session_group)
        session_layout.setSpacing(12)
        
        self.session_duration_card = StatCard("Duration")
        self.session_recordings_card = StatCard("Recordings")
        self.session_success_card = StatCard("Successful")
        self.session_failed_card = StatCard("Failed")
        
        session_layout.addWidget(self.session_duration_card, 0, 0)
        session_layout.addWidget(self.session_recordings_card, 0, 1)
        session_layout.addWidget(self.session_success_card, 1, 0)
        session_layout.addWidget(self.session_failed_card, 1, 1)
        
        self.scroll_layout.addWidget(session_group)
        
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
        
        self.scroll_layout.addWidget(history_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = ModernButton("Refresh", variant=ButtonVariant.SECONDARY)
        self.refresh_button.clicked.connect(self.load_statistics)
        button_layout.addWidget(self.refresh_button)
        
        self.export_button = ModernButton("Export Statistics", variant=ButtonVariant.SECONDARY)
        self.export_button.clicked.connect(self.export_statistics)
        button_layout.addWidget(self.export_button)
        
        self.reset_button = ModernButton("Reset Statistics", variant=ButtonVariant.DANGER)
        self.reset_button.clicked.connect(self.reset_statistics)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        self.scroll_layout.addLayout(button_layout)
    
    def load_statistics(self):
        """Load and display current statistics"""
        stats = self.statistics_manager.get_statistics()
        session_stats = self.statistics_manager.get_session_statistics()
        
        # Usage statistics
        self.total_sessions_card.set_value(stats['total_sessions'])
        self.total_recordings_card.set_value(stats['total_recordings'])
        
        # Format duration
        total_minutes = int(stats['total_duration'] / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        self.total_duration_card.set_value(f"{hours}h {minutes}m")
        
        # Success rate
        success_rate = self.statistics_manager.get_accuracy_rate()
        self.success_rate_card.set_value(f"{success_rate:.1f}%")
        
        # Performance metrics
        perf = stats['performance_metrics']
        self.avg_transcription_time_card.set_value(f"{perf['average_transcription_time']:.2f}s")
        
        if perf['fastest_transcription'] != float('inf'):
            self.fastest_transcription_card.set_value(f"{perf['fastest_transcription']:.2f}s")
        else:
            self.fastest_transcription_card.set_value("N/A")
            
        self.slowest_transcription_card.set_value(f"{perf['slowest_transcription']:.2f}s")
        self.avg_audio_duration_card.set_value(f"{perf['average_audio_duration']:.2f}s")
        
        # Mode usage
        self.api_usage_card.set_value(stats['usage_by_mode']['api'])
        self.local_usage_card.set_value(stats['usage_by_mode']['local'])
        self.total_characters_card.set_value(f"{stats['total_characters']:,}")
        
        # Current session
        session_minutes = int(session_stats['session_duration'] / 60)
        session_hours = session_minutes // 60
        session_mins = session_minutes % 60
        self.session_duration_card.set_value(f"{session_hours}h {session_mins}m")
        self.session_recordings_card.set_value(session_stats['recordings'])
        self.session_success_card.set_value(session_stats['successful_transcriptions'])
        self.session_failed_card.set_value(session_stats['failed_transcriptions'])
        
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
            theme_manager = get_theme_manager()
            colors = theme_manager.get_theme_colors(theme)
            primary_color = colors.get("primary", "#ffffff")

            # Determine if this is a dark theme
            try:
                is_dark = theme_manager.is_dark_color(primary_color)
            except Exception:
                is_dark = False

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
                        border: 1px solid {colors.get("border", "#6c757d")};
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
                        border: 1px solid {colors.get("border", "#dee2e6")};
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
