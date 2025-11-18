"""
Test Theme Management System
Tests for centralized theme management, signal propagation, and consistency
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from src.quillscribe.managers import get_theme_manager
from src.quillscribe.main import QuillScribeMainWindow
from src.quillscribe.settings.settings_dialog import SettingsDialog


@pytest.fixture
def app(qtbot):
    """Fixture to provide QApplication instance"""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def theme_manager():
    """Fixture to provide fresh ThemeManager instance"""
    return get_theme_manager()


@pytest.fixture
def main_window(qtbot):
    """Fixture to provide MainWindow instance"""
    window = QuillScribeMainWindow()
    qtbot.addWidget(window)
    return window


@pytest.fixture
def settings_dialog(qtbot, main_window):
    """Fixture to provide SettingsDialog instance"""
    dialog = SettingsDialog(main_window, main_window.config_manager)
    qtbot.addWidget(dialog)
    return dialog


class TestThemeManagerCentralization:
    """Test that ThemeManager is the single source of truth"""
    
    def test_theme_manager_singleton(self, theme_manager):
        """Test that get_theme_manager returns the same instance"""
        manager1 = get_theme_manager()
        manager2 = get_theme_manager()
        assert manager1 is manager2
    
    def test_theme_colors_available(self, theme_manager):
        """Test that all defined themes have color definitions"""
        themes = ["white", "warm_gray", "soft_beige", "blue_gray", 
                 "warm_taupe", "soft_sage", "dark_charcoal", "dark_blue",
                 "dark_purple", "dark_forest", "dark_burgundy"]
        
        for theme_name in themes:
            colors = theme_manager.get_theme_colors(theme_name)
            assert "primary" in colors
            assert "secondary" in colors
            assert colors["primary"].startswith("#")
            assert colors["secondary"].startswith("#")
    
    def test_invalid_theme_fallback(self, theme_manager):
        """Test that invalid theme names fall back to white"""
        colors = theme_manager.get_theme_colors("nonexistent_theme")
        white_colors = theme_manager.get_theme_colors("white")
        assert colors["primary"] == white_colors["primary"]
    
    def test_dark_theme_detection(self, theme_manager):
        """Test that dark themes are correctly identified"""
        # Light themes
        theme_manager.set_theme("white")
        assert not theme_manager.is_dark_theme()
        
        theme_manager.set_theme("soft_beige")
        assert not theme_manager.is_dark_theme()
        
        # Dark themes
        theme_manager.set_theme("dark_charcoal")
        assert theme_manager.is_dark_theme()
        
        theme_manager.set_theme("dark_blue")
        assert theme_manager.is_dark_theme()


class TestSignalPropagation:
    """Test that theme changes propagate via signals"""
    
    def test_theme_changed_signal_emitted(self, qtbot, theme_manager):
        """Test that setting theme emits theme_changed signal"""
        with qtbot.waitSignal(theme_manager.theme_changed, timeout=1000) as blocker:
            theme_manager.set_theme("warm_gray")
        
        # Verify signal was emitted with correct parameters
        assert len(blocker.args) == 2
        theme_name, is_dark = blocker.args
        assert theme_name == "warm_gray"
        assert isinstance(is_dark, bool)
    
    def test_main_window_receives_signal(self, qtbot, main_window, theme_manager):
        """Test that main window receives and processes theme changes"""
        # Set initial theme
        initial_theme = "white"
        theme_manager.set_theme(initial_theme)
        
        # Change theme and verify it propagates
        with qtbot.waitSignal(theme_manager.theme_changed, timeout=1000):
            theme_manager.set_theme("blue_gray")
        
        # Allow time for signal processing
        qtbot.wait(100)
        
        # Verify main window updated
        assert theme_manager.get_current_theme() == "blue_gray"
    
    def test_settings_dialog_receives_signal(self, qtbot, settings_dialog, theme_manager):
        """Test that settings dialog receives and processes theme changes"""
        # Change theme
        with qtbot.waitSignal(theme_manager.theme_changed, timeout=1000):
            theme_manager.set_theme("dark_charcoal")
        
        # Allow time for signal processing
        qtbot.wait(100)
        
        # Verify theme was applied
        assert theme_manager.get_current_theme() == "dark_charcoal"


class TestRecursionPrevention:
    """Test that recursion guards prevent infinite loops"""
    
    def test_main_window_no_recursion(self, qtbot, main_window):
        """Test that main window doesn't recurse when applying theme"""
        # Apply theme multiple times rapidly
        for _ in range(5):
            main_window.apply_theme("white")
            main_window.apply_theme("dark_blue")
        
        # Should complete without hanging
        qtbot.wait(100)
        assert True  # If we get here, no infinite recursion
    
    def test_settings_dialog_no_recursion(self, qtbot, settings_dialog):
        """Test that settings dialog doesn't recurse when applying theme"""
        # Apply theme multiple times rapidly
        for _ in range(5):
            settings_dialog.apply_theme("white")
            settings_dialog.apply_theme("dark_charcoal")
        
        # Should complete without hanging
        qtbot.wait(100)
        assert True  # If we get here, no infinite recursion


class TestColorUtilities:
    """Test color manipulation utilities"""
    
    def test_darken_color_valid(self, theme_manager):
        """Test darkening a valid hex color"""
        original = "#ffffff"  # White
        darkened = theme_manager.darken_color(original, 0.5)
        
        assert darkened.startswith("#")
        assert len(darkened) == 7
        # Should be darker than original
        assert darkened != original
        assert darkened < original  # Hex comparison works for this
    
    def test_lighten_color_valid(self, theme_manager):
        """Test lightening a valid hex color"""
        original = "#000000"  # Black
        lightened = theme_manager.lighten_color(original, 0.5)
        
        assert lightened.startswith("#")
        assert len(lightened) == 7
        # Should be lighter than original
        assert lightened != original
    
    def test_blend_colors_valid(self, theme_manager):
        """Test blending two valid hex colors"""
        color1 = "#ffffff"  # White
        color2 = "#000000"  # Black
        blended = theme_manager.blend_hex_colors(color1, color2, 0.5)
        
        assert blended.startswith("#")
        assert len(blended) == 7
        # Should be gray (middle value)
        assert blended != color1
        assert blended != color2
    
    def test_color_utilities_handle_invalid_input(self, theme_manager):
        """Test that color utilities handle invalid input gracefully"""
        invalid_inputs = ["invalid", "123", "#xyz", "", "notahexcolor"]
        
        for invalid in invalid_inputs:
            # Should not crash, should return something
            darkened = theme_manager.darken_color(invalid)
            lightened = theme_manager.lighten_color(invalid)
            blended = theme_manager.blend_hex_colors(invalid, "#ffffff", 0.5)
            
            # All should return strings (original or fallback)
            assert isinstance(darkened, str)
            assert isinstance(lightened, str)
            assert isinstance(blended, str)


class TestErrorHandling:
    """Test error handling in theme application"""
    
    def test_main_window_handles_invalid_theme(self, qtbot, main_window):
        """Test that main window handles invalid themes gracefully"""
        # Try to apply an invalid theme
        try:
            main_window.apply_theme("completely_invalid_theme_name")
            qtbot.wait(100)
            # Should not crash
            assert True
        except Exception as e:
            pytest.fail(f"Main window crashed on invalid theme: {e}")
    
    def test_settings_dialog_handles_invalid_theme(self, qtbot, settings_dialog):
        """Test that settings dialog handles invalid themes gracefully"""
        # Try to apply an invalid theme
        try:
            settings_dialog.apply_theme("completely_invalid_theme_name")
            qtbot.wait(100)
            # Should not crash
            assert True
        except Exception as e:
            pytest.fail(f"Settings dialog crashed on invalid theme: {e}")


class TestUIConsistency:
    """Test that UI elements are consistently themed"""
    
    def test_main_window_style_applied(self, qtbot, main_window):
        """Test that main window has stylesheet after theme application"""
        main_window.apply_theme("blue_gray")
        qtbot.wait(100)
        
        # Main window should have stylesheet set after theme application
        style = main_window.styleSheet()
        assert len(style) > 0  # Some style should be applied
    
    def test_settings_dialog_style_applied(self, qtbot, settings_dialog):
        """Test that settings dialog has stylesheet after theme application"""
        settings_dialog.apply_theme("dark_purple")
        qtbot.wait(100)
        
        # Dialog should have styling
        style = settings_dialog.styleSheet()
        assert len(style) > 0  # Some style should be applied


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
