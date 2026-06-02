# KeyBear Companion QA Test Report

Date: 2026-06-02

Scope: qinliang PySide6 build only. The obsolete qin/Tk lightweight variant is intentionally out of scope.

## Test Matrix

- Static compile check for all root Python modules.
- Existing test-suite discovery.
- Settings load/save and normalization.
- Keyboard key-name normalization and hot-zone coverage.
- Sleep-state wake path through the Qt signal bridge.
- Tray hide/restore smoke path.
- qinliang packaging smoke path.

## Findings

### P0 - App can crash on startup when user settings file is inaccessible

Evidence:

- A GUI smoke test failed before the window opened.
- Stack trace:
  - `SettingsManager.load()`
  - `self.path.exists()`
  - `PermissionError: [WinError 5] 拒绝访问: C:\Users\Sun_Chao\AppData\Roaming\KeyBearCompanion\settings.json`

Impact:

- If `%APPDATA%\KeyBearCompanion\settings.json` exists but is locked, corrupted by permissions, or otherwise inaccessible, the app exits immediately.
- This is a real user-facing startup crash.

Fix implemented:

- Make settings existence checks, reads, and writes tolerate `OSError`.
- Fall back to a writable local `user_data/KeyBearCompanion/settings.json` path if the preferred settings file cannot be accessed.
- Added regression coverage in `qa_regression_tests.py`.

### P1 - Size preset overrides manual scale controls on save

Evidence:

- Test script saved:
  - `size_preset = small`
  - `overall_scale = 1.0`
  - `keyboard_scale = 0.95`
  - `bear_scale = 1.15`
- Actual persisted values were reset to the `small` preset:
  - `overall_scale = 0.7`
  - `keyboard_scale = 0.55`
  - `bear_scale = 0.75`

Impact:

- The settings UI exposes separate scale controls, but user edits can silently be overwritten.
- This makes size/layout tuning feel broken.

Fix implemented:

- Apply preset values when the preset combo changes in the settings window.
- Preserve explicit scale values when saving a full settings form.
- Keep `SettingsManager.update({"size_preset": ...})` useful for programmatic preset-only updates.
- Added regression coverage in `qa_regression_tests.py`.

### P1 - Existing test suite is stale and cannot run

Evidence:

- `python -m unittest discover -s tests -v` fails at import time.
- The test imports old names that no longer exist:
  - `KEYBOARD_STYLES`
  - `KEYBOARD_THEMES`

Impact:

- Current regressions are not caught by the checked-in/leftover tests.

Fix implemented:

- Add a current qinliang regression test file for settings fallback, preset behavior, key mapping, and keyboard layout coverage.
- Keep old ignored tests out of the release path.
- Added `qa_regression_tests.py` at the repository root.
- The old ignored `tests/` folder remains outside the release path and is not part of the tracked qinliang build.

### P2 - Unsupported keys are intentionally ignored but should remain documented

Evidence:

- `Key.f1`, `Key.delete`, and arrow keys normalize to `None`.

Impact:

- This is acceptable for the current simplified keyboard layout, but it may surprise users expecting every physical key to trigger a reaction.

Planned follow-up:

- Document the supported key set, or add visual support for extra keys in a future version.

## Non-Issues Confirmed

- Root Python modules compile successfully.
- `clean` and `full` keyboard densities include independent hot zones for Backspace, Enter, Space, left/right Shift, left/right Ctrl, and left/right Alt.
- Letter/digit and common special-key normalization works.
- The sleep wake path is now routed through a Qt signal bridge rather than direct cross-thread UI mutation.

## Verification After Fixes

- `python -m unittest qa_regression_tests -v`: passed, 4 tests.
- Root Python module compile check: passed.
- Mojibake scan for `settings_manager.py`, `settings_window.py`, `app.py`, and `pet_keyboard_window.py`: 0 matching bad strings.
- GUI smoke path:
  - Hide/restore path worked.
  - Forced sleep state entered.
  - Backspace after sleep reached the expected `sad` state without crashing.
