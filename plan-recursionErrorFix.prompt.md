## Plan: Fix Recursion on Exit/Statistics Save

TL;DR: We’ll add simple re-entry guards and better error handling to the statistics manager and the exit logic so that failures saving statistics can only happen once per exit, never re-trigger themselves, and don’t cause `_perform_exit` to recursively call itself. Logs stay informative but non-spammy, and the app always shuts down cleanly even if stats saving fails.

### Steps

1. Add state flags to `StatisticsManager` in `src/quillscribe/managers/statistics_manager.py` (e.g., `_saving_stats`, `_session_end_recorded`, `_consecutive_save_failures`) and initialize them in `__init__`.
2. Wrap `save_statistics` with a re-entry guard using `_saving_stats`, a `try/except/finally` block, and a small failure counter to log a clear error once and shorter messages on repeated failures.
3. Harden `record_session_end` in `StatisticsManager` to check `_session_end_recorded` at the start, set it before calling `save_statistics`, and no-op on subsequent calls.
4. In `MainWindow` (or equivalent) in `src/quillscribe/main.py`, introduce `_exit_in_progress` / `_exit_completed` flags, guard `_perform_exit` so it runs cleanup only once, and make subsequent calls return immediately.
5. Inside `_perform_exit`, wrap the `statistics_manager.record_session_end` (or `save_statistics`) call in its own `try/except` to log a single warning on failure without re-raising, then always continue with the rest of the cleanup and Qt `quit`.
6. Ensure the `aboutToQuit` connection in `main.py` (`app.aboutToQuit.connect(lambda: window._perform_exit(None))`) relies on the same `_exit_in_progress/_exit_completed` guard so that it cannot re-enter `_perform_exit` after it has already started or finished.

### Further Considerations

1. Decide whether repeated save failures should stay silent after the first logged error, or if you want a one-time in-app notification before exit.
2. Consider adding an optional fallback directory for statistics (e.g., temp folder) if the primary path is unwritable, or confirm that simply dropping stats on repeated failure is acceptable.
3. Confirm whether a single `record_session_end` per process lifetime is correct (most likely), or if there are advanced scenarios where multiple “soft” session ends in one run should be counted separately.
