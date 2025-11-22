"""
Breathing Microphone Widget
Beautiful breathing microphone widget with smooth Siri-style ribbon animations
"""

import math
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Signal, Property, QTimer, Slot, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath

from .managers import get_theme_manager


class BreathingMicrophone(QWidget):
    """Beautiful breathing microphone widget with smooth Siri-style ribbon animations"""

    # Signal for when microphone is clicked
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.scale_factor = 1.0
        self.audio_level = 0.0
        self.is_recording = False
        self.show_waveform = True
        self.level_smoothed = 0.0
        self.animation_strength = 3.0  # Default amplification factor
        self._transition_progress = 0.0  # 0.0 = static, 1.0 = waveform

        # Colors - Initialized from theme
        self._idle_color = QColor("#DCDCDC")  # Default fallback
        self._recording_color = QColor("#FFFFFF")
        self._mic_color = QColor(self._idle_color)
        self._bg_circle_color = QColor("#808080") # Default fallback for circles
        self._bg_alpha = 50  # Default alpha for background circles

        # Make the widget clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Animation setup (disabled breathing; mic remains static)
        self.animation = QPropertyAnimation(self, b"scaleFactor")
        self.animation.setDuration(1500)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.animation.setLoopCount(-1)

        # Color animation
        self.color_animation = QPropertyAnimation(self, b"micColor")
        self.color_animation.setDuration(300)  # Smooth 300ms transition
        self.color_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Transition animation (static <-> waveform)
        self.transition_animation = QPropertyAnimation(self, b"transitionProgress")
        self.transition_animation.setDuration(400)  # Slightly slower for background
        self.transition_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Ribbon animation state (Siri-style)
        # List of dicts: phase, speed_factor, color_alpha, amplitude_factor, QColor
        # Pre-parse colors to avoid doing it in paintEvent
        self.ribbon_waves = [
            {"phase": 0.0, "speed": 1.0, "alpha": 40, "amp": 1.0, "qcolor": QColor("#00FFFF")},  # Cyan
            {"phase": 2.0, "speed": 1.2, "alpha": 60, "amp": 0.8, "qcolor": QColor("#007AFF")},  # Blue
            {"phase": 4.0, "speed": 0.8, "alpha": 30, "amp": 1.2, "qcolor": QColor("#AF52DE")},  # Purple
        ]
        
        self.wave_timer = QTimer(self)
        self.wave_timer.setInterval(16)  # ~60 FPS for smoother ribbons
        self.wave_timer.timeout.connect(self.advance_wave)

        # Theme integration
        self.current_theme_colors = {"primary": "#800080"}  # Default fallback
        theme_manager = get_theme_manager()
        theme_manager.theme_changed.connect(self.update_theme_colors)
        # Initialize with current theme
        self.update_theme_colors(theme_manager.get_current_theme(), theme_manager.is_dark_theme())

        # Drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    @Slot(str, bool)
    def update_theme_colors(self, theme_name: str, is_dark: bool):
        """Update internal color state when theme changes"""
        theme_manager = get_theme_manager()
        colors = theme_manager.get_theme_colors(theme_name)
        self.current_theme_colors = colors
        
        # Determine accent color with fallback based on theme mode
        default_accent = "#8B5CF6" if is_dark else "#4A90E2"
        accent = colors.get("accent", default_accent)
        
        # Update colors
        self._idle_color = QColor(accent)
        self._recording_color = QColor("#FFFFFF") # White when recording
        # Use accent color for background circles for a nice glow effect
        self._bg_circle_color = QColor(accent)
        
        # Pre-calculate alpha for paintEvent to avoid logic in draw loop
        # Dark theme needs less alpha for subtlety, light theme needs more
        self._bg_alpha = 40 if is_dark else 50

        # Update current mic color if not recording
        if not self.is_recording:
            self._mic_color = self._idle_color
            
        self.update()

    # Property for animation
    def getScaleFactor(self):
        return self.scale_factor

    def setScaleFactor(self, value):
        if isinstance(value, (int, float)):
            self.scale_factor = float(value)
            self.update()  # Trigger repaint

    scaleFactor = Property(float, getScaleFactor, setScaleFactor)

    # Property for color animation
    def getMicColor(self):
        return self._mic_color

    def setMicColor(self, color):
        self._mic_color = QColor(color)
        self.update()

    micColor = Property(QColor, getMicColor, setMicColor)

    # Property for transition animation
    def getTransitionProgress(self):
        return self._transition_progress

    def setTransitionProgress(self, value):
        self._transition_progress = float(value)
        self.update()

    transitionProgress = Property(float, getTransitionProgress, setTransitionProgress)

    def set_show_waveform(self, value: bool):
        """Enable/disable waveform rendering around the microphone"""
        self.show_waveform = bool(value)
        self.update()

    def set_animation_strength(self, value: float):
        """Set the animation amplification strength"""
        self.animation_strength = max(1.0, min(10.0, float(value)))
        self.update()

    def start_idle_breathing(self):
        """Mic stays static when idle (no breathing)."""
        self.animation.stop()
        self.scale_factor = 1.0
        self.update()

    def start_recording_breathing(self):
        """Enable ribbon animation while recording; mic remains static."""
        self.is_recording = True
        self.animation.stop()
        self.scale_factor = 1.0
        self.wave_timer.start()
        
        # Animate color to recording state
        self.color_animation.stop()
        self.color_animation.setStartValue(self._mic_color)
        self.color_animation.setEndValue(self._recording_color)
        self.color_animation.start()

        # Animate transition to waveform
        self.transition_animation.stop()
        self.transition_animation.setStartValue(self._transition_progress)
        self.transition_animation.setEndValue(1.0)
        self.transition_animation.start()
        
        self.update()  # Force visual refresh

    def stop_recording(self):
        """Stop recording and clear animation (mic stays static)."""
        self.is_recording = False
        # Don't stop wave timer immediately, let it run during fade out
        self.animation.stop()
        
        # Animate color to idle state
        self.color_animation.stop()
        self.color_animation.setStartValue(self._mic_color)
        self.color_animation.setEndValue(self._idle_color)
        self.color_animation.start()

        # Animate transition to static
        self.transition_animation.stop()
        self.transition_animation.setStartValue(self._transition_progress)
        self.transition_animation.setEndValue(0.0)
        self.transition_animation.start()
        
        self.update()  # Force visual refresh

    @Slot(float)
    def update_audio_level(self, level: float):
        """Update level (used for waveform only); do not scale mic with level"""
        # Additional gentle smoothing for visual stability
        level = max(0.0, min(1.0, level))
        self.level_smoothed = (0.85 * self.level_smoothed) + (0.15 * level)
        self.audio_level = self.level_smoothed

    def advance_wave(self):
        """Advance ribbon phases for organic motion."""
        # Base speed
        base_speed = 0.05
        # Audio reactivity: faster motion with louder audio
        amplified_level = min(1.0, self.audio_level * self.animation_strength)
        reactivity = amplified_level * 0.1
        
        for wave in self.ribbon_waves:
            # Each wave moves at its own speed plus shared reactivity
            speed = (base_speed * wave["speed"]) + reactivity
            wave["phase"] = (wave["phase"] + speed) % (2 * math.pi)
            
        self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse click to toggle recording."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get the center and radius
        center_x = self.width() // 2
        center_y = self.height() // 2
        base_radius = min(self.width(), self.height()) // 3
        radius = int(base_radius * self.scale_factor)

        # Base colors
        base_color = self._bg_circle_color

        # Draw Siri-style ribbons (Waveform)
        # We draw this if transition_progress > 0
        if self.show_waveform and self._transition_progress > 0.01:
            amplified_level = min(1.0, self.audio_level * self.animation_strength)
            
            # Draw multiple overlapping ribbons
            for i, wave in enumerate(self.ribbon_waves):
                path = QPainterPath()
                
                # Dynamic radius based on audio level and wave properties
                # Breathing effect: base size + audio reaction + wave variation
                wave_amp = wave["amp"] * (10 + (amplified_level * 20))
                current_radius = radius + 10 + (amplified_level * 15)
                
                # Create a "blob" or organic circle shape
                points = 90  # Increased points for smoother curves
                for j in range(points + 1):
                    angle = (j / points) * 2 * math.pi
                    
                    # Refined math for "shimmering circle" instead of "fan"
                    # Use multiple lower-amplitude sine waves for subtle complexity
                    # Base wave (slow rotation) + Detail wave (faster ripple)
                    r_mod = (math.sin(angle * 3 + wave["phase"]) * 0.5 + 
                             math.sin(angle * 6 - wave["phase"] * 2) * 0.2)
                    
                    # Scale modulation by amplitude but keep it subtle relative to radius
                    r = current_radius + (r_mod * wave_amp * 0.6)
                    
                    x = center_x + r * math.cos(angle)
                    y = center_y + r * math.sin(angle)
                    
                    if j == 0:
                        path.moveTo(x, y)
                    else:
                        path.lineTo(x, y)
                
                path.closeSubpath()
                
                # Fill with specific wave color and varying opacity
                # Use cached QColor but create a copy/modify alpha
                # Modulate alpha with audio level for "glowing" pulse
                pulse = 0.8 + (0.2 * math.sin(wave["phase"] * 2))
                
                # Scale alpha by transition_progress for fade in/out
                # Pre-calculate base alpha
                base_alpha = wave["alpha"] * 2.5 * (1.0 + amplified_level) * pulse * self._transition_progress
                alpha = int(min(200, base_alpha))
                
                # Use cached color
                color = wave["qcolor"]
                # We need to set alpha, but QColor is mutable, so we can just set it? 
                # No, we shouldn't modify the cached object if we want to be safe, 
                # but here we are in a loop and it's the only user. 
                # Actually, better to use setAlpha on the object if we reset it or just use a temp copy if needed.
                # QColor is efficient to copy.
                draw_color = QColor(color)
                draw_color.setAlpha(alpha)
                
                painter.setBrush(QBrush(draw_color))
                
                # Add a thin stroke for better definition
                stroke_alpha = min(255, int(base_alpha * 1.2))
                if stroke_alpha > 0:
                    draw_color.setAlpha(stroke_alpha)
                    painter.setPen(QPen(draw_color, 1.5, Qt.PenStyle.SolidLine))
                else:
                    painter.setPen(Qt.PenStyle.NoPen)
                
                painter.drawPath(path)

        # Draw static background circles
        # Fade out as transition_progress increases
        static_alpha_factor = 1.0 - self._transition_progress
        if static_alpha_factor > 0.01:
            outer_color = QColor(base_color)
            # Use pre-calculated alpha
            outer_color.setAlpha(int(self._bg_alpha * static_alpha_factor))
            painter.setBrush(QBrush(outer_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center_x - radius - 10, center_y - radius - 10,
                              (radius + 10) * 2, (radius + 10) * 2)

        # Draw microphone icon (always on top)
        # Use the animated color
        painter.setPen(QPen(self._mic_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(QBrush(self._mic_color))

        # Microphone body (capsule)
        mic_width = radius // 2
        mic_height = radius // 1.5
        mic_x = center_x - mic_width // 2
        mic_y = center_y - mic_height // 2 - 5

        painter.drawRoundedRect(mic_x, mic_y, mic_width, mic_height, 8, 8)

        # Microphone stand
        stand_y = mic_y + mic_height
        painter.drawLine(center_x, stand_y, center_x, stand_y + 15)
        painter.drawLine(center_x - 8, stand_y + 15, center_x + 8, stand_y + 15)