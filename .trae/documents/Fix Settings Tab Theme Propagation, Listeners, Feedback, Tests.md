## Goal
Resolve theme application issues in the Settings tab by centralizing theme state, wiring reliable change listeners, guaranteeing consistent styling across all controls, adding lightweight visual feedback during transitions, handling errors robustly, and validating with unit tests — without regressing existing functionality or performance.

## Root Cause Summary
- Theme changes rely on direct calls (e.g., `dialog.apply_theme(...)`) instead of subscribing to the global `ThemeManager.theme_changed` signal; consumers for the signal are largely absent, leading to inconsistent propagation.
- Duplicate theme maps exist in multiple places (`SettingsDialog`, `MainWindow`) which diverge from `ThemeManager.THEMES`, causing mismatch and fragile updates.
- Some components recompute dark/light using local helpers rather than the centralized manager, increasing drift risk and redundant work.

## Key Objectives
1. Ensure theme properties propagate to all Settings tab components via a single source of truth.
2. Implement robust theme change listeners with reentrancy guards and coalescing to avoid redundant work.
3. Verify consistency for text, backgrounds, buttons, interactive elements, borders, and dividers.
4. Add subtle visual feedback during transitions without blocking the UI or harming performance.
5. Provide error handling for invalid/unavailable themes and failed applications.
6. Add unit tests covering theme transitions and consistency.

## Implementation Plan
### 1) Signal Wiring and State Management
- Connect `SettingsDialog` to `ThemeManager.theme_changed` and implement a slot `on_theme_changed(theme_name: str, is_dark: bool)` that applies styles without re-triggering the signal.
  - Use a boolean guard (`self._applying_theme`) to avoid recursion because `apply_theme` currently calls `theme_manager.set_theme(...)`.
  - Defer heavy UI updates using `QTimer.singleShot(0, ...)` to coalesce rapid changes and keep the UI responsive.
- Connect `UITab` (and other tabs that need theme-dependent restyling) to the same signal to re-style their specific controls (`apply_animation_theme`, etc.).
- Ensure `ThemeManager` remains the single source of truth; do not recompute dark/light in tabs where `theme_manager.is_dark_theme()` is available.

### 2) Centralize Theme Colors and Consumption
- Replace `SettingsDialog._get_theme_colors(...)` to delegate to `ThemeManager.get_theme_colors(...)` and remove reliance on local `THEMES` for correctness.
- Ensure `MainWindow.apply_theme(theme_name)` also consumes colors via `ThemeManager.get_theme_colors(...)` and uses `is_dark` from `ThemeManager` instead of a local map.
- Keep existing public surface (`apply_theme(theme_name)`) intact to avoid regressions, but switch internal implementation to the centralized manager.

### 3) Propagation Across Components (Settings Tab)
- In `SettingsDialog.apply_theme(theme_name)`:
  - Batch updates: `self.setUpdatesEnabled(False)` → apply styles → `self.setUpdatesEnabled(True)`.
  - Text: call `theme_manager.apply_text_theming_to_widget(self, theme_name)` to update label colors consistently.
  - Backgrounds: apply dialog gradient and explicitly set tab backgrounds already present; ensure scroll area backgrounds use `BaseSettingsTab.apply_scroll_area_background(...)`.
  - Buttons and interactive elements: continue icon refresh via `theme_manager.apply_icons_to_widget(self, is_dark)` and refresh nav buttons in `apply_sidebar_theme(theme_name)`.
  - Borders/dividers: verify group boxes use the right border colors; adjust `ModernGroupBox.apply_theme(...)` invocations where needed for border and header contrast.
  - Scrollbars: replace per-widget styling with `theme_manager.apply_scrollbars_to_all_widgets(self, theme_name)` to cover all scroll areas.
  - Explicitly call each tab’s `apply_theme(...)` when present to propagate per-tab adjustments (`statistics_tab.py:30`, `base_tab.py:34`, `ui_components.py:58/150`).

### 4) Visual Feedback During Transitions
- Add a lightweight fade on `self.content_stack` and `self.sidebar` using `QGraphicsOpacityEffect` + `QPropertyAnimation` (~150–200ms) when receiving `theme_changed`.
- Set `Qt.WaitCursor` briefly during the transition, clear afterwards.
- Update `UITab` slider styling instantly (already implemented) to provide immediate feedback.

### 5) Error Handling
- Validate theme names before applying; if invalid, use `ThemeManager` fallback to `"white"` and log a warning.
- Wrap theme application blocks in try/except; on failure, present a `QMessageBox` in the Settings dialog, revert to last-known-good theme, and continue.
- Harden `ThemeManager.set_theme(...)` against bad inputs (already defaults); ensure consumers rely on `get_theme_colors(...)` for consistent keys.

### 6) Performance Considerations
- Temporarily disable updates while applying batched stylesheet changes (`setUpdatesEnabled(False/True)`).
- Avoid repeated `setStyleSheet` calls on the same widget; construct styles once per section and set them in one pass.
- Coalesce multiple theme changes occurring within a short window via a single-shot timer.
- Icon updates: only refresh icons for widgets that currently have one or match patterns; skip redundant updates when state did not change.

### 7) Unit Tests (pytest-qt)
- Add `tests/test_settings_theme.py`:
  - Test signal propagation: simulate dropdown change in `UITab`, assert `SettingsDialog` restyles and `ThemeManager.theme_changed` is observed.
  - Verify text colors: labels reflect expected `text_primary`/`text_muted` after theme change.
  - Verify backgrounds: dialog and scroll areas include correct `primary`/`secondary` gradient and background.
  - Verify buttons/interactive: nav buttons styles reflect active/hover colors, icons match dark/light.
  - Verify borders/dividers: group boxes set border colors based on theme.
  - Visual feedback: opacity animation runs and returns to 1.0; cursor resets.
  - Error handling: force invalid theme selection, ensure fallback and warning without crash.
  - Performance guard: multiple rapid changes coalesce to a single application run (using a spy on the slot and style setters).

## Files to Update (primary touchpoints)
- `src\quillscribe\managers\theme_manager.py`:
  - `ThemeManager` at `src\quillscribe\managers\theme_manager.py:13` (ensure robust `set_theme` at `95–113`, consumption via `get_theme_colors`, and scrollbar helpers `467–506`).
- `src\quillscribe\settings\settings_dialog.py`:
  - `apply_theme` at `src\quillscribe\settings\settings_dialog.py:267` (refactor to centralized colors, batching, tabs propagation).
  - `_apply_scrollbar_theme` at `src\quillscribe\settings\settings_dialog.py:239` (delegate to manager or call ‘apply_scrollbars_to_all_widgets’).
  - `_get_theme_colors` at `src\quillscribe\settings\settings_dialog.py:588` (delegate to manager).
  - `apply_sidebar_theme` at `src\quillscribe\settings\settings_dialog.py:620` (verify styles for dark/light).
- `src\quillscribe\settings\ui_tab.py`:
  - `on_theme_changed` at `src\quillscribe\settings\ui_tab.py:517–537` (persist and rely on signal-driven propagation; connect to `theme_changed`).
  - `apply_animation_theme` at `src\quillscribe\settings\ui_tab.py:318` (respond to theme change).
- `src\quillscribe\settings\base_tab.py`:
  - `create_scroll_area` and `apply_scroll_area_background` at `src\quillscribe\settings\base_tab.py:40–88` (ensure manager-driven backgrounds).
- `src\quillscribe\main.py`:
  - `apply_theme` at `src\quillscribe\main.py:1670` (use centralized colors and `is_dark`).
- Add tests: `tests/test_settings_theme.py` using `pytest-qt` and existing `conftest.py`.

## Documentation
- Add concise docstrings to new slots and updated methods: describe parameters, signal wiring, and error handling behavior.
- Keep inline code self-documenting; avoid verbose comments.

## Risk & Rollback
- Changes are additive with guards; if issues arise, revert listener wiring and keep direct calls while retaining centralized color consumption.

## Acceptance Criteria
- Theme changes propagate reliably to all Settings controls via listeners.
- Consistent styling for text, backgrounds, buttons, borders, dividers.
- Visual feedback is present and unobtrusive.
- No performance regression (measured by reduced redundant style applications in tests).
- Unit tests pass and cover the listed scenarios.