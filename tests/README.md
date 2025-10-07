# QuillScribe Test Suite

Comprehensive unit tests for QuillScribe components using pytest and pytest-qt.

## Setup

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

This installs:
- `pytest` - Testing framework
- `pytest-qt` - Qt testing utilities
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities

### Verify Installation

```bash
pytest --version
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_animated_toggle_switch.py
```

### Run Specific Test Class

```bash
pytest tests/test_animated_toggle_switch.py::TestInitialization
```

### Run Specific Test Method

```bash
pytest tests/test_animated_toggle_switch.py::TestInitialization::test_default_state_unchecked
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage Report

```bash
pytest --cov=src/quillscribe --cov-report=html
```

Then open `htmlcov/index.html` in your browser to view the coverage report.

### Run with Coverage Terminal Report

```bash
pytest --cov=src/quillscribe --cov-report=term-missing
```

## Test Structure

### Test Organization

```
tests/
├── __init__.py                          # Test package initialization
├── conftest.py                          # Shared fixtures and configuration
├── test_animated_toggle_switch.py       # AnimatedToggleSwitch widget tests
└── README.md                            # This file
```

### Test Categories

Tests are organized into logical groups:

1. **Initialization Tests** - Default state, dimensions, setup
2. **Toggling Tests** - State changes, signal emission
3. **Mouse Interaction Tests** - Click handling, hit detection
4. **Theme Tests** - Light/dark theme application
5. **Disabled State Tests** - Behavior when disabled
6. **Animation Tests** - Property animation, race conditions
7. **Cleanup Tests** - Resource cleanup, memory management
8. **Edge Cases Tests** - Boundary values, special conditions
9. **Integration Tests** - Full workflows, signal integration

## Test Coverage

### AnimatedToggleSwitch Tests (42 tests)

- ✅ Initialization and default state (10 tests)
- ✅ Toggle state changes and signals (6 tests)
- ✅ Mouse click interactions (4 tests)
- ✅ Theme application (5 tests)
- ✅ Disabled state handling (3 tests)
- ✅ Animation behavior (6 tests)
- ✅ Resource cleanup (4 tests)
- ✅ Edge cases and boundaries (4 tests)
- ✅ Integration with Qt (2 tests)

### Coverage Goals

- **Line Coverage**: >90%
- **Branch Coverage**: >85%
- **Function Coverage**: 100%

## Writing New Tests

### Test Template

```python
import pytest
from PySide6.QtWidgets import QApplication
from quillscribe.settings.modern_widgets import AnimatedToggleSwitch

@pytest.fixture
def widget(qapp):
    """Create widget instance for testing."""
    w = AnimatedToggleSwitch()
    yield w
    w.deleteLater()

class TestFeature:
    """Test a specific feature."""
    
    def test_happy_path(self, widget):
        """Test normal expected behavior."""
        # Arrange
        widget.setChecked(False)
        
        # Act
        widget.setChecked(True)
        
        # Assert
        assert widget.isChecked()
    
    def test_edge_case(self, widget):
        """Test boundary condition."""
        # Test implementation
        pass
    
    def test_error_handling(self, widget):
        """Test error scenario."""
        # Test implementation
        pass
```

### Best Practices

1. **Use AAA Pattern** - Arrange, Act, Assert
2. **Descriptive Names** - Test names should describe what they test
3. **One Assertion Per Test** - Keep tests focused
4. **Use Fixtures** - Share setup code via fixtures
5. **Mock External Dependencies** - Isolate unit under test
6. **Test Edge Cases** - Boundary values, null, empty, etc.
7. **Test Error Paths** - Invalid inputs, exceptions
8. **Clean Up Resources** - Use fixtures with cleanup

### Qt-Specific Testing

#### Using qtbot

```python
def test_signal_emission(toggle_switch, qtbot):
    """Test that signal is emitted."""
    with qtbot.waitSignal(toggle_switch.toggled, timeout=1000):
        toggle_switch.setChecked(True)
```

#### Simulating Mouse Clicks

```python
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

def test_mouse_click(toggle_switch, qtbot):
    """Test mouse click interaction."""
    QTest.mouseClick(toggle_switch, Qt.MouseButton.LeftButton)
    qtbot.wait(50)  # Allow event processing
    assert toggle_switch.isChecked()
```

#### Mocking paintEvent

```python
from unittest.mock import patch

def test_repaint_optimization(toggle_switch):
    """Test that unnecessary repaints are avoided."""
    with patch.object(toggle_switch, 'update') as mock_update:
        toggle_switch.apply_theme(is_dark=False)
        mock_update.assert_not_called()  # No change, no repaint
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest --cov=src/quillscribe --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### QApplication Already Exists Error

**Problem**: `RuntimeError: Please destroy the QApplication singleton before creating a new one`

**Solution**: Use the `qapp` fixture which provides a session-scoped QApplication:

```python
def test_my_widget(qapp):  # Use qapp fixture
    widget = MyWidget()
    # Test code
```

### Tests Hang or Timeout

**Problem**: Tests hang when waiting for signals

**Solution**: 
1. Increase timeout: `qtbot.waitSignal(signal, timeout=5000)`
2. Use `qtbot.wait(ms)` to allow event processing
3. Check that signal is actually emitted

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'quillscribe'`

**Solution**: The `conftest.py` adds `src/` to Python path. Ensure you're running pytest from the project root:

```bash
cd /path/to/quillscibe
pytest
```

### Platform-Specific Issues

**Problem**: Tests fail on headless systems (CI/CD)

**Solution**: Set Qt to use offscreen platform:

```bash
export QT_QPA_PLATFORM=offscreen
pytest
```

Or in pytest.ini:
```ini
[pytest]
addopts = --qt-qpa-platform=offscreen
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-qt documentation](https://pytest-qt.readthedocs.io/)
- [PySide6 documentation](https://doc.qt.io/qtforpython/)
- [Qt Test documentation](https://doc.qt.io/qt-6/qtest.html)

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass: `pytest`
3. Check coverage: `pytest --cov`
4. Run code quality checks: `black . && flake8`
5. Update this README if adding new test categories

