"""
Statistics Manager for QuillScribe
Tracks usage statistics, accuracy metrics, and performance monitoring
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, Signal


class StatisticsManager(QObject):
    """Manages application statistics and performance metrics"""
    
    stats_updated = Signal()
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        
        # Statistics file location
        self.stats_dir = Path.home() / ".config" / "quillscribe" / "statistics"
        self.stats_dir.mkdir(parents=True, exist_ok=True)
        self.stats_file = self.stats_dir / "usage_stats.json"
        self.history_file = self.stats_dir / "transcription_history.json"
        
        # Current session data
        self.session_start_time = time.time()
        self.current_session = {
            'start_time': self.session_start_time,
            'recordings': 0,
            'total_duration': 0.0,
            'successful_transcriptions': 0,
            'failed_transcriptions': 0,
            'api_calls': 0,
            'local_transcriptions': 0,
            'total_characters': 0,
            'average_confidence': 0.0
        }
        
        # Load existing statistics
        self.stats = self.load_statistics()
        self.history = self.load_history()
    
    def load_statistics(self) -> Dict[str, Any]:
        """Load statistics from file"""
        try:
            if self.stats_file.exists() and self.stats_file.stat().st_size > 0:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error loading statistics: JSON decode error at line {e.lineno}, column {e.colno}: {e.msg}")
            # Backup corrupted file and create new one
            if self.stats_file.exists():
                backup_file = self.stats_file.with_suffix('.json.backup')
                self.stats_file.rename(backup_file)
                print(f"Corrupted statistics file backed up to: {backup_file}")
        except Exception as e:
            print(f"Error loading statistics: {e}")
        
        # Return default statistics structure
        return {
            'total_sessions': 0,
            'total_recordings': 0,
            'total_duration': 0.0,
            'total_transcriptions': 0,
            'successful_transcriptions': 0,
            'failed_transcriptions': 0,
            'api_calls': 0,
            'local_transcriptions': 0,
            'total_characters': 0,
            'average_accuracy': 0.0,
            'performance_metrics': {
                'average_transcription_time': 0.0,
                'fastest_transcription': float('inf'),
                'slowest_transcription': 0.0,
                'average_audio_duration': 0.0
            },
            'usage_by_mode': {
                'api': 0,
                'local': 0
            },
            'daily_usage': {},
            'weekly_usage': {},
            'monthly_usage': {},
            'first_use_date': None,
            'last_use_date': None
        }
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Load transcription history from file"""
        try:
            if self.history_file.exists() and self.history_file.stat().st_size > 0:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
        except Exception as e:
            print(f"Error loading history: {e}")

        return []
    
    def save_statistics(self):
        """Save statistics to file"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving statistics: {e}")
    
    def save_history(self):
        """Save transcription history to file"""
        try:
            # Keep only last 1000 entries to prevent file from growing too large
            if len(self.history) > 1000:
                self.history = self.history[-1000:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def record_session_start(self):
        """Record the start of a new session"""
        self.session_start_time = time.time()
        self.current_session = {
            'start_time': self.session_start_time,
            'recordings': 0,
            'total_duration': 0.0,
            'successful_transcriptions': 0,
            'failed_transcriptions': 0,
            'api_calls': 0,
            'local_transcriptions': 0,
            'total_characters': 0,
            'average_confidence': 0.0
        }
    
    def record_recording_start(self):
        """Record the start of a recording"""
        self.current_session['recordings'] += 1
        self.stats['total_recordings'] += 1
        
        # Update daily usage
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.stats['daily_usage']:
            self.stats['daily_usage'][today] = 0
        self.stats['daily_usage'][today] += 1
        
        self.stats_updated.emit()
    
    def record_transcription_result(self, success: bool, mode: str, duration: float, 
                                  transcription_time: float, text: str = "", 
                                  confidence: float = 0.0):
        """Record the result of a transcription"""
        # Update session stats
        self.current_session['total_duration'] += duration
        
        if success:
            self.current_session['successful_transcriptions'] += 1
            self.stats['successful_transcriptions'] += 1
            self.current_session['total_characters'] += len(text)
            self.stats['total_characters'] += len(text)
            
            if mode == 'api':
                self.current_session['api_calls'] += 1
                self.stats['api_calls'] += 1
                self.stats['usage_by_mode']['api'] += 1
            else:
                self.current_session['local_transcriptions'] += 1
                self.stats['local_transcriptions'] += 1
                self.stats['usage_by_mode']['local'] += 1
            
            # Update performance metrics
            perf = self.stats['performance_metrics']
            perf['fastest_transcription'] = min(perf['fastest_transcription'], transcription_time)
            perf['slowest_transcription'] = max(perf['slowest_transcription'], transcription_time)
            
            # Update average transcription time
            total_transcriptions = self.stats['successful_transcriptions']
            if total_transcriptions > 1:
                perf['average_transcription_time'] = (
                    (perf['average_transcription_time'] * (total_transcriptions - 1) + transcription_time) 
                    / total_transcriptions
                )
            else:
                perf['average_transcription_time'] = transcription_time
            
            # Update average audio duration
            if total_transcriptions > 1:
                perf['average_audio_duration'] = (
                    (perf['average_audio_duration'] * (total_transcriptions - 1) + duration) 
                    / total_transcriptions
                )
            else:
                perf['average_audio_duration'] = duration
            
            # Add to history
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'mode': mode,
                'duration': duration,
                'transcription_time': transcription_time,
                'text_length': len(text),
                'confidence': confidence,
                'success': True
            }
            self.history.append(history_entry)
            
        else:
            self.current_session['failed_transcriptions'] += 1
            self.stats['failed_transcriptions'] += 1
            
            # Add failed transcription to history
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'mode': mode,
                'duration': duration,
                'transcription_time': transcription_time,
                'success': False
            }
            self.history.append(history_entry)
        
        # Update total transcriptions
        self.stats['total_transcriptions'] += 1
        
        # Update dates
        now = datetime.now().isoformat()
        if self.stats['first_use_date'] is None:
            self.stats['first_use_date'] = now
        self.stats['last_use_date'] = now
        
        # Save and emit update
        self.save_statistics()
        self.save_history()
        self.stats_updated.emit()
    
    def record_session_end(self):
        """Record the end of a session"""
        session_duration = time.time() - self.session_start_time
        self.stats['total_sessions'] += 1
        self.stats['total_duration'] += self.current_session['total_duration']
        
        self.save_statistics()
        self.stats_updated.emit()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics"""
        return self.stats.copy()
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get current session statistics"""
        session_duration = time.time() - self.session_start_time
        return {
            **self.current_session,
            'session_duration': session_duration
        }
    
    def get_recent_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent transcription history"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_history = []
        
        for entry in reversed(self.history):  # Most recent first
            try:
                entry_date = datetime.fromisoformat(entry['timestamp'])
                if entry_date >= cutoff_date:
                    recent_history.append(entry)
                else:
                    break  # History is ordered, so we can stop here
            except Exception:
                continue  # Skip malformed entries
        
        return recent_history
    
    def get_accuracy_rate(self) -> float:
        """Calculate overall accuracy rate"""
        total = self.stats['total_transcriptions']
        if total == 0:
            return 0.0
        return (self.stats['successful_transcriptions'] / total) * 100
    
    def get_daily_usage_trend(self, days: int = 30) -> Dict[str, int]:
        """Get daily usage trend for the last N days"""
        trend = {}
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            trend[date] = self.stats['daily_usage'].get(date, 0)
        return trend
    
    def reset_statistics(self):
        """Reset all statistics (keep history)"""
        self.stats = self.load_statistics()  # Reset to defaults
        self.save_statistics()
        self.stats_updated.emit()
    
    def export_statistics(self, file_path: str) -> bool:
        """Export statistics to a file"""
        try:
            export_data = {
                'statistics': self.stats,
                'current_session': self.get_session_statistics(),
                'recent_history': self.get_recent_history(30),
                'export_date': datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting statistics: {e}")
            return False
