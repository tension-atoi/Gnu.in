# E2E Test Suite Design Analysis — gnu.in-cockpit

This report documents findings and designs for running E2E tests for the PySide6 GNU.IN Cockpit application. It details headless execution, style and Wayland settings verification, graceful missing display validation, and thread lifecycle safety.

---

## 1. Headless Execution Design (pytest-qt)

To test a PySide6 GUI application in headless environments (such as CI/CD pipelines, remote VMs, or TTY sessions), the application needs a Qt Platform Abstraction (QPA) plugin that does not require an active graphical display server (X11 or Wayland).

### Headless QPA Options

1. **`offscreen` Platform (`QT_QPA_PLATFORM=offscreen`)**
   - **Recommended Choice**: Built directly into Qt. It renders all widgets to an offscreen memory buffer.
   - **Pros**: Extremely fast, no external system dependencies (like `Xvfb`), supports visual assertions, pixel grabbing, and screenshot generation (`qtbot.screenshot`).
   - **Cons**: Window activation focus tests (`qtbot.waitActive()`) are not fully supported since there is no window manager.
2. **`minimal` Platform (`QT_QPA_PLATFORM=minimal`)**
   - Renders nothing; only runs the event loop. Best for unit testing logic but less suitable for E2E visual and event flow validation.
3. **Virtual Display Compositor (`xvfb-run` or `pytest-xvfb`)**
   - Runs tests inside a virtual X11 server buffer.
   - **Pros**: Fully emulates a standard X11 display server; mouse clicks and focus events behave identically to a physical monitor.
   - **Cons**: Requires installing the system package `Xvfb` and drags in X11 dependencies.

### Environment Variable Requirements
For E2E test suites, the following environment variables should be set:
```bash
export PYTEST_QT_API=pyside6       # Force pytest-qt to use PySide6
export QT_QPA_PLATFORM=offscreen   # Run headlessly via offscreen rendering
export QT_QPA_PLATFORMTHEME=""     # Disable xdg-desktop-portal/GTK theme probes
```

### Preventing Thread Leaks (`QThread` Teardown)
The `Cockpit` application initializes `GitHubPanel`, which instantly spawns a background `GitHubWorker` (a subclass of `QThread`) to run the `gh` CLI or REST API. If the window is closed during a test, the thread keeps running, resulting in a SIGABRT or the warning:
> `QThread: Destroyed while thread '' is still running`

**Best Practice Design**:
1. **Mocking External Integrations**: Mock `GitHubPanel.refresh` in tests that do not specifically target GitHub functionality. This saves test execution time, avoids internet/CLI dependencies, and completely avoids background thread leaks.
2. **Explicit Thread Joining**: For tests that must exercise the thread, ensure that `closeEvent` or the test teardown explicitly signals the worker thread to quit and waits for it:
   ```python
   if win.github_panel.worker and win.github_panel.worker.isRunning():
       win.github_panel.worker.quit()
       win.github_panel.worker.wait(2000)
   ```

---

## 2. Style, Wayland, and Warning Verification

### Native Styling (Fusion)
- The Cockpit application enforces the **Fusion** style: `app.setStyle("Fusion")`.
- In E2E tests, this can be verified programmatically:
  ```python
  assert QApplication.style().objectName().lower() == "fusion"
  ```
- This complies with the core constraints requiring native Qt6 styling and avoiding GNOME/GTK overrides.

### Wayland Integration
- In a graphical session, the Cockpit application respects Wayland settings.
- By unsetting `QT_QPA_PLATFORMTHEME` (setting to `""`), we prevent the Qt application from attempting to connect to `xdg-desktop-portal` or invoking GNOME GSettings. This prevents theme-based hangs in headless runs.

### Warning Prevention
- **Font Warnings**: The application explicitly initializes a font with a concrete family name:
  ```python
  base = QFont("sans-serif", 10)
  app.setFont(base)
  ```
  This prevents font database engine warnings on minimalist headless environments.

---

## 3. Missing Display Graceful Handling

If the display environment is completely missing (no `DISPLAY` or `WAYLAND_DISPLAY` is set, and `QT_QPA_PLATFORM` is not set to `offscreen`), the application must fail gracefully without hanging or dragging in GTK dependencies.

- **Graceful Fail**: Since `QApplication` instantiation aborts at the C++ level (via `SIGABRT`/exit code `-6`), we cannot wrap it in a Python `try...except` to recover.
- **Verification via Subprocess**: To verify that the application fails gracefully on missing display servers without GTK/GNOME interference, the test suite should run `python -m cockpit` as a subprocess with display environments removed, asserting:
  1. The process exits with a non-zero code.
  2. The output (`stderr`) contains standard Qt platform plugin initialization errors.
  3. No `Gtk-WARNING` or GNOME `gsettings` logs are printed.

---

## 4. E2E pytest-qt Test Suite Implementation Proposal

Below is the proposed implementation of the E2E test suite (`test_cockpit.py`). It contains 3 tests validating the initial state, the `QProcess` launch, and the missing display graceful handling.

```python
import os
import sys
import pytest
import subprocess
from pathlib import Path

# Configure environment variables before imports
os.environ["PYTEST_QT_API"] = "pyside6"
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QPA_PLATFORMTHEME"] = ""

from PySide6.QtCore import Qt, QProcess
from PySide6.QtWidgets import QApplication
from cockpit.views.main_window import Cockpit
from cockpit.models.action import Action

@pytest.fixture(autouse=True)
def mock_github_refresh(monkeypatch):
    """Automatically mock GitHubPanel.refresh to avoid starting background threads in tests."""
    from cockpit.views.github_panel import GitHubPanel
    monkeypatch.setattr(GitHubPanel, "refresh", lambda self, *args, **kwargs: None)

def test_cockpit_initial_state(qtbot):
    """Test that Cockpit window initializes with correct title, theme, and style."""
    win = Cockpit()
    qtbot.addWidget(win)
    
    # 1. Verify window title
    assert win.windowTitle() == "GNU.IN Pipeline Cockpit"
    
    # 2. Verify Fusion style is applied
    assert QApplication.style().objectName().lower() == "fusion"
    
    # 3. Verify workspace path defaults to expected
    assert win.ws_edit.text() != ""
    
    # 4. Verify thread is not running (since refresh is mocked)
    assert win.github_panel.worker is None

def test_qprocess_launch_validation(qtbot):
    """Test QProcess command resolution, button state, and log streaming using a mock action."""
    win = Cockpit()
    qtbot.addWidget(win)
    
    # Clear log
    win.log.clear()
    
    # Define a safe mock action to run
    mock_action = Action(
        label="Test Echo",
        group="Checks",
        cmd="echo 'hello world'",
        cwd_kind="workspace"
    )
    
    # Trigger the action
    win.run(mock_action)
    
    # Verify the QProcess is created
    assert win.proc is not None
    assert isinstance(win.proc, QProcess)
    
    # Verify UI buttons are disabled during execution
    for btn in win.run_buttons:
        assert not btn.isEnabled()
    assert win.stop_btn.isEnabled()
    
    # Wait for QProcess to finish (processes events periodically)
    qtbot.waitUntil(lambda: win.proc is None, timeout=5000)
    
    # Verify buttons are re-enabled
    for btn in win.run_buttons:
        assert btn.isEnabled()
    assert not win.stop_btn.isEnabled()
    
    # Verify log output contains stdout and exit status
    log_text = win.log.toPlainText()
    assert "hello world" in log_text
    assert "exit 0" in log_text

def test_missing_display_graceful_abort():
    """Verify that launching the app without a display server or offscreen platform
    fails with a standard Qt platform plugin error and exit code,
    without invoking GTK/GNOME dependencies or hanging."""
    env = os.environ.copy()
    env.pop("DISPLAY", None)
    env.pop("WAYLAND_DISPLAY", None)
    env.pop("QT_QPA_PLATFORM", None)
    env.pop("GTK_THEME", None)
    env.pop("GSETTINGS_BACKEND", None)
    
    # Run cockpit as a module
    proc = subprocess.run(
        [sys.executable, "-m", "cockpit"],
        env=env,
        capture_output=True,
        text=True,
        timeout=5
    )
    
    # It must fail because no display is present
    assert proc.returncode != 0
    
    # Check that it failed because of QPA platform plugin loading, NOT a Python traceback
    has_qpa_error = (
        "Could not load the Qt platform plugin" in proc.stderr or
        "xcb: could not connect to display" in proc.stderr or
        "no Qt platform plugin could be initialized" in proc.stderr or
        "Failed to create wl_display" in proc.stderr
    )
    assert has_qpa_error, f"Expected QPA error, got: {proc.stderr}"
    
    # Check that there are no GTK-related warnings (e.g. "Gtk-WARNING") or GNOME gsettings errors
    assert "Gtk-WARNING" not in proc.stderr
    assert "gsettings" not in proc.stderr.lower()
```
