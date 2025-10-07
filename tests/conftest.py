"""
Pytest configuration and fixtures for QuillScribe tests
"""
import sys
import os
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def qapp():
    """
    Session-scoped QApplication fixture.
    
    Creates a single QApplication instance for all tests in the session.
    Qt requires a QApplication instance to exist before creating any widgets.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Note: Don't call app.quit() here as it may be needed by other tests


@pytest.fixture
def qtbot(qapp, qtbot):
    """
    Provide pytest-qt's qtbot fixture with QApplication dependency.
    
    This ensures QApplication is created before qtbot is used.
    """
    return qtbot

