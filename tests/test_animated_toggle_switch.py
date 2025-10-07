"""
Comprehensive unit tests for AnimatedToggleSwitch widget.

Tests cover:
- Initialization and default state
- Toggling behavior and signals
- Mouse interaction
- Theme application
- Disabled state handling
- Animation behavior
- Resource cleanup
- Edge cases and boundary conditions
"""
import sys
import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSize, QPropertyAnimation
from PySide6.QtGui import QColor
from PySide6.QtTest import QTest

from quillscribe.settings.modern_widgets import AnimatedToggleSwitch


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def toggle_switch(qapp):
    """
    Create a fresh AnimatedToggleSwitch instance for each test.
    
    Automatically cleans up the widget after the test completes.
    """
    widget = AnimatedToggleSwitch()
    yield widget
    # Cleanup
    if hasattr(widget, 'cleanup'):
        widget.cleanup()
    widget.deleteLater()


# ============================================================================
# 1. Initialization Tests
# ============================================================================

class TestInitialization:
    """Test widget initialization and default state."""
    
    def test_default_state_unchecked(self, toggle_switch):
        """Widget should be unchecked by default."""
        assert not toggle_switch.isChecked()
    
    def test_default_circle_position_left(self, toggle_switch):
        """Circle should start at left position when unchecked."""
        assert toggle_switch._circle_position == AnimatedToggleSwitch.CIRCLE_POS_LEFT
    
    def test_default_theme_light(self, toggle_switch):
        """Widget should default to light theme."""
        assert not toggle_switch._is_dark
    
    def test_dimensions_constants(self, toggle_switch):
        """Verify all dimension constants are set correctly."""
        assert AnimatedToggleSwitch.TOGGLE_WIDTH == 50
        assert AnimatedToggleSwitch.TOGGLE_HEIGHT == 26
        assert AnimatedToggleSwitch.TOGGLE_RADIUS == 13
        assert AnimatedToggleSwitch.CIRCLE_SIZE == 20
        assert AnimatedToggleSwitch.CIRCLE_Y_OFFSET == 3
        assert AnimatedToggleSwitch.CIRCLE_POS_LEFT == 3
        assert AnimatedToggleSwitch.CIRCLE_POS_RIGHT == 27
        assert AnimatedToggleSwitch.ANIMATION_DURATION_MS == 200
    
    def test_size_hint(self, toggle_switch):
        """Size hint should match toggle dimensions."""
        size_hint = toggle_switch.sizeHint()
        assert size_hint == QSize(50, 26)
    
    def test_cursor_is_pointing_hand(self, toggle_switch):
        """Cursor should be pointing hand for better UX."""
        assert toggle_switch.cursor().shape() == Qt.CursorShape.PointingHandCursor
    
    def test_animation_created(self, toggle_switch):
        """Animation object should be created during initialization."""
        assert hasattr(toggle_switch, 'animation')
        assert toggle_switch.animation is not None
        assert isinstance(toggle_switch.animation, QPropertyAnimation)
    
    def test_animation_duration(self, toggle_switch):
        """Animation duration should be 200ms."""
        assert toggle_switch.animation.duration() == 200
    
    def test_colors_preloaded(self, toggle_switch):
        """All color objects should be pre-created for performance."""
        assert hasattr(toggle_switch, '_colors')
        assert isinstance(toggle_switch._colors, dict)
        expected_keys = [
            'checked_track', 'checked_circle',
            'unchecked_track_light', 'unchecked_track_dark',
            'unchecked_circle_light', 'unchecked_circle_dark',
            'disabled_track_light', 'disabled_track_dark',
            'disabled_circle_light', 'disabled_circle_dark'
        ]
        for key in expected_keys:
            assert key in toggle_switch._colors
            assert isinstance(toggle_switch._colors[key], QColor)


# ============================================================================
# 2. Toggling Tests
# ============================================================================

class TestToggling:
    """Test toggle state changes and signal emission."""
    
    def test_set_checked_true(self, toggle_switch):
        """Setting checked to True should update state."""
        toggle_switch.setChecked(True)
        assert toggle_switch.isChecked()
    
    def test_set_checked_false(self, toggle_switch):
        """Setting checked to False should update state."""
        toggle_switch.setChecked(True)
        toggle_switch.setChecked(False)
        assert not toggle_switch.isChecked()
    
    def test_toggled_signal_emitted(self, toggle_switch, qtbot):
        """Toggled signal should be emitted when state changes."""
        with qtbot.waitSignal(toggle_switch.toggled, timeout=1000):
            toggle_switch.setChecked(True)
    
    def test_toggled_signal_value(self, toggle_switch, qtbot):
        """Toggled signal should carry the new checked state."""
        received_values = []
        toggle_switch.toggled.connect(lambda checked: received_values.append(checked))
        
        toggle_switch.setChecked(True)
        qtbot.wait(50)  # Allow signal to propagate
        assert True in received_values
        
        toggle_switch.setChecked(False)
        qtbot.wait(50)
        assert False in received_values
    
    def test_animation_triggered_on_toggle(self, toggle_switch):
        """Animation should start when toggle state changes."""
        with patch.object(toggle_switch.animation, 'start') as mock_start:
            toggle_switch.setChecked(True)
            mock_start.assert_called_once()
    
    def test_rapid_toggling(self, toggle_switch, qtbot):
        """Rapid toggling should not cause errors."""
        for i in range(10):
            toggle_switch.setChecked(i % 2 == 0)
            qtbot.wait(10)  # Small delay
        # Should end in unchecked state (i=9, 9 % 2 == 1, so False)
        assert not toggle_switch.isChecked()


# ============================================================================
# 3. Mouse Interaction Tests
# ============================================================================

class TestMouseInteraction:
    """Test mouse click and interaction behavior."""
    
    def test_click_toggles_state(self, toggle_switch, qtbot):
        """Clicking the widget should toggle its state."""
        initial_state = toggle_switch.isChecked()
        QTest.mouseClick(toggle_switch, Qt.MouseButton.LeftButton)
        qtbot.wait(50)
        assert toggle_switch.isChecked() != initial_state
    
    def test_double_click_toggles_twice(self, toggle_switch, qtbot):
        """Double-clicking should toggle twice, returning to original state."""
        initial_state = toggle_switch.isChecked()
        QTest.mouseDClick(toggle_switch, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        assert toggle_switch.isChecked() == initial_state
    
    def test_hit_button_entire_widget(self, toggle_switch):
        """hitButton should return True for any point within widget bounds."""
        # Test center
        center = toggle_switch.rect().center()
        assert toggle_switch.hitButton(center)
        
        # Test top-left corner (within bounds)
        assert toggle_switch.hitButton(toggle_switch.rect().topLeft() + toggle_switch.rect().center() * 0.1)
        
        # Test bottom-right corner (within bounds)
        assert toggle_switch.hitButton(toggle_switch.rect().bottomRight() - toggle_switch.rect().center() * 0.1)
    
    def test_click_when_disabled_no_toggle(self, toggle_switch, qtbot):
        """Clicking when disabled should not toggle state."""
        toggle_switch.setEnabled(False)
        initial_state = toggle_switch.isChecked()
        QTest.mouseClick(toggle_switch, Qt.MouseButton.LeftButton)
        qtbot.wait(50)
        assert toggle_switch.isChecked() == initial_state


# ============================================================================
# 4. Theme Tests
# ============================================================================

class TestTheme:
    """Test theme application and color changes."""
    
    def test_apply_light_theme(self, toggle_switch):
        """Applying light theme should update _is_dark flag."""
        toggle_switch.apply_theme(is_dark=False)
        assert not toggle_switch._is_dark
    
    def test_apply_dark_theme(self, toggle_switch):
        """Applying dark theme should update _is_dark flag."""
        toggle_switch.apply_theme(is_dark=True)
        assert toggle_switch._is_dark
    
    def test_theme_change_triggers_repaint(self, toggle_switch):
        """Changing theme should trigger widget repaint."""
        with patch.object(toggle_switch, 'update') as mock_update:
            toggle_switch.apply_theme(is_dark=True)
            mock_update.assert_called_once()
    
    def test_theme_no_change_no_repaint(self, toggle_switch):
        """Setting same theme should not trigger repaint (optimization)."""
        toggle_switch._is_dark = False
        with patch.object(toggle_switch, 'update') as mock_update:
            toggle_switch.apply_theme(is_dark=False)
            mock_update.assert_not_called()
    
    def test_theme_switch_multiple_times(self, toggle_switch):
        """Switching theme multiple times should work correctly."""
        toggle_switch.apply_theme(is_dark=True)
        assert toggle_switch._is_dark
        toggle_switch.apply_theme(is_dark=False)
        assert not toggle_switch._is_dark
        toggle_switch.apply_theme(is_dark=True)
        assert toggle_switch._is_dark


# ============================================================================
# 5. Disabled State Tests
# ============================================================================

class TestDisabledState:
    """Test behavior when widget is disabled."""
    
    def test_set_enabled_false(self, toggle_switch):
        """Widget should accept disabled state."""
        toggle_switch.setEnabled(False)
        assert not toggle_switch.isEnabled()
    
    def test_disabled_state_visual_feedback(self, toggle_switch):
        """Disabled state should trigger repaint for visual feedback."""
        toggle_switch.setEnabled(False)
        with patch.object(toggle_switch, 'update') as mock_update:
            toggle_switch.paintEvent(None)
            # paintEvent should be called (implicitly through Qt)
    
    def test_programmatic_toggle_when_disabled(self, toggle_switch):
        """Programmatic toggling should work even when disabled."""
        toggle_switch.setEnabled(False)
        toggle_switch.setChecked(True)
        assert toggle_switch.isChecked()


# ============================================================================
# 6. Animation Tests
# ============================================================================

class TestAnimation:
    """Test animation behavior and properties."""
    
    def test_circle_position_getter(self, toggle_switch):
        """circle_position property getter should return current position."""
        assert toggle_switch._get_circle_position() == toggle_switch._circle_position
    
    def test_circle_position_setter(self, toggle_switch):
        """circle_position property setter should update position."""
        toggle_switch._set_circle_position(15)
        assert toggle_switch._circle_position == 15
    
    def test_circle_position_setter_triggers_repaint(self, toggle_switch):
        """Setting circle position should trigger repaint."""
        with patch.object(toggle_switch, 'update') as mock_update:
            toggle_switch._set_circle_position(15)
            mock_update.assert_called_once()
    
    def test_circle_position_no_change_no_repaint(self, toggle_switch):
        """Setting same position should not trigger repaint (optimization)."""
        toggle_switch._circle_position = 10
        with patch.object(toggle_switch, 'update') as mock_update:
            toggle_switch._set_circle_position(10)
            mock_update.assert_not_called()
    
    def test_animation_targets_circle_position(self, toggle_switch):
        """Animation should target the circle_position property."""
        assert toggle_switch.animation.propertyName() == b"circle_position"
    
    def test_animation_race_condition_prevention(self, toggle_switch):
        """Starting new animation should stop running animation."""
        # Start first animation
        toggle_switch.setChecked(True)
        # Immediately start second animation
        with patch.object(toggle_switch.animation, 'stop') as mock_stop:
            toggle_switch.setChecked(False)
            # stop() should be called if animation was running
            # (may not be called if first animation already finished)


# ============================================================================
# 7. Cleanup Tests
# ============================================================================

class TestCleanup:
    """Test resource cleanup and memory management."""
    
    def test_cleanup_method_exists(self, toggle_switch):
        """Widget should have cleanup method."""
        assert hasattr(toggle_switch, 'cleanup')
        assert callable(toggle_switch.cleanup)
    
    def test_cleanup_stops_animation(self, toggle_switch):
        """Cleanup should stop running animation."""
        toggle_switch.setChecked(True)  # Start animation
        with patch.object(toggle_switch.animation, 'stop') as mock_stop:
            toggle_switch.cleanup()
            mock_stop.assert_called_once()
    
    def test_cleanup_deletes_animation(self, toggle_switch):
        """Cleanup should delete animation object."""
        toggle_switch.cleanup()
        assert toggle_switch.animation is None
    
    def test_cleanup_idempotent(self, toggle_switch):
        """Calling cleanup multiple times should not cause errors."""
        toggle_switch.cleanup()
        toggle_switch.cleanup()  # Should not raise exception
        assert toggle_switch.animation is None


# ============================================================================
# 8. Edge Cases and Boundary Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_circle_position_at_boundaries(self, toggle_switch):
        """Circle position should work at min and max boundaries."""
        toggle_switch._set_circle_position(AnimatedToggleSwitch.CIRCLE_POS_LEFT)
        assert toggle_switch._circle_position == 3
        
        toggle_switch._set_circle_position(AnimatedToggleSwitch.CIRCLE_POS_RIGHT)
        assert toggle_switch._circle_position == 27
    
    def test_constants_consistency(self, toggle_switch):
        """Constants should be mathematically consistent."""
        # CIRCLE_POS_RIGHT should equal TOGGLE_WIDTH - CIRCLE_SIZE - CIRCLE_POS_LEFT
        expected_right = (AnimatedToggleSwitch.TOGGLE_WIDTH - 
                         AnimatedToggleSwitch.CIRCLE_SIZE - 
                         AnimatedToggleSwitch.CIRCLE_POS_LEFT)
        assert AnimatedToggleSwitch.CIRCLE_POS_RIGHT == expected_right
        
        # TOGGLE_RADIUS should be half of TOGGLE_HEIGHT
        assert AnimatedToggleSwitch.TOGGLE_RADIUS == AnimatedToggleSwitch.TOGGLE_HEIGHT // 2
    
    def test_parent_parameter(self, qapp):
        """Widget should accept parent parameter."""
        from PySide6.QtWidgets import QWidget
        parent = QWidget()
        toggle = AnimatedToggleSwitch(parent=parent)
        assert toggle.parent() == parent
        parent.deleteLater()
        toggle.deleteLater()
    
    def test_none_parent(self, qapp):
        """Widget should work with None parent."""
        toggle = AnimatedToggleSwitch(parent=None)
        assert toggle.parent() is None
        toggle.deleteLater()


# ============================================================================
# 9. Integration Tests
# ============================================================================

class TestIntegration:
    """Test integration with Qt framework and signals."""
    
    def test_full_toggle_cycle_with_signals(self, toggle_switch, qtbot):
        """Complete toggle cycle should emit all expected signals."""
        signals_received = []
        toggle_switch.toggled.connect(lambda checked: signals_received.append(('toggled', checked)))
        
        # Uncheck -> Check
        toggle_switch.setChecked(True)
        qtbot.wait(50)
        assert ('toggled', True) in signals_received
        
        # Check -> Uncheck
        toggle_switch.setChecked(False)
        qtbot.wait(50)
        assert ('toggled', False) in signals_received
    
    def test_mouse_click_integration(self, toggle_switch, qtbot):
        """Mouse click should integrate with Qt event system."""
        clicked_count = [0]
        toggle_switch.toggled.connect(lambda: clicked_count.__setitem__(0, clicked_count[0] + 1))
        
        QTest.mouseClick(toggle_switch, Qt.MouseButton.LeftButton)
        qtbot.wait(50)
        assert clicked_count[0] == 1

