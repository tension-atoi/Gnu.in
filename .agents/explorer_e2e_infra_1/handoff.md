# Handoff Report — E2E Test Suite Design for gnu.in-cockpit

This report concludes the read-only exploration and design of the headless PySide6 application execution and QProcess launch validation.

## 1. Observation

- **Application Structure**:
  - `gnu.in-cockpit/src/cockpit/__main__.py` sets the style to Fusion and sets `QT_QPA_PLATFORMTHEME` to `""`:
    - Line 7: `os.environ.setdefault("QT_QPA_PLATFORMTHEME", "")`
    - Line 23: `app.setStyle("Fusion")`
    - Line 24: `base = QFont("sans-serif", 10)`
  - `gnu.in-cockpit/src/cockpit/views/main_window.py` instantiates `self.github_panel = GitHubPanel()`, which on creation calls `self._refresh_github()`, creating a `GitHubWorker` thread that runs `GitHubClient.get_pull_requests` and `GitHubClient.get_recent_runs`.
  - When the process completes, `_finished` is triggered (Line 274), which automatically calls `self._refresh_github()` again, spawning a new worker thread.

- **Headless Execution Verification**:
  - Running a direct Python invocation without display variables (`DISPLAY`, `WAYLAND_DISPLAY`, `QT_QPA_PLATFORM`) failed with exit code `-6` (SIGABRT) and stderr:
    ```
    Failed to create wl_display (No such file or directory)
    qt.qpa.plugin: Could not load the Qt platform plugin "wayland" in "" even though it was found.
    qt.qpa.xcb: could not connect to display
    This application failed to start because no Qt platform plugin could be initialized.
    ```
  - Running PySide6 with `QT_QPA_PLATFORM=offscreen` succeeded:
    ```
    PySide6 and Cockpit imported successfully.
    Instantiating MainWindow...
    MainWindow instantiated successfully.
    Application style: fusion
    Window Title: GNU.IN Pipeline Cockpit
    Workspace Path: /home/tension_atoi/Projects/Gnu.in
    Selected Repo: gnu.in-os
    Closing window and exiting.
    QThread: Destroyed while thread '' is still running
    ```

- **E2E Test Success**:
  - A test suite executing `pytest-qt` under `uv run --with pytest --with pytest-qt --with PySide6 --with requests pytest` passed all three tests (initial state, QProcess launch, and missing display graceful abort) in `0.53s`.

---

## 2. Logic Chain

1. **Headless Execution Option**: Qt6 requires a QPA platform plugin to start. By setting `QT_QPA_PLATFORM=offscreen`, Qt uses its offscreen buffer for rendering. This bypasses the need for an X11 server or Wayland socket, enabling execution on headless servers.
2. **Warning and Hang Avoidance**:
   - Setting `QT_QPA_PLATFORMTHEME=""` prevents Qt from calling DBus to negotiate dark theme preferences with `xdg-desktop-portal` or invoking GNOME schema/GSettings.
   - Enforcing `app.setStyle("Fusion")` and `QFont("sans-serif", 10)` prevents GTK engine fallback warnings and QFontDatabase empty-description messages on bare systems.
3. **Preventing Thread Leaks**:
   - The thread warnings (`QThread: Destroyed while thread '' is still running`) occur because `GitHubPanel.refresh` runs asynchronously in `GitHubWorker` (QThread). When the test window closes and exits, the thread is still executing `gh` CLI commands or REST API requests.
   - To resolve this, `GitHubPanel.refresh` must be mocked/intercepted in tests (unless explicitly testing GitHub functionality), preventing the thread from ever spawning. If it is run, tests must explicitly wait for thread termination (`worker.quit()`, `worker.wait()`).
4. **QProcess Validation**:
   - `pytest-qt` provides a `qtbot` fixture that drives the event loop. By using `qtbot.waitUntil(lambda: win.proc is None, timeout=5000)`, the event loop processes events, allowing `QProcess` to execute, capture output streams (stdout/stderr), populate the custom `LogView` widget, and return to the idle state where UI buttons are re-enabled.

---

## 3. Caveats

- **Visual / Interaction Limitations under `offscreen`**:
  - Visual assertions and screenshots work via `offscreen`. However, window activations (`qtbot.waitActive()`) or actions expecting system window manager interactions (like window decorations or desktop overlays) are bypassed.
- **GitHub REST API and `requests` Dependency**:
  - The latest `github_client.py` imports the `requests` library at the module level. Therefore, `requests` must be added to the test dependencies.

---

## 4. Conclusion

The E2E test suite for `gnu.in-cockpit` can be run headlessly and safely by:
1. Setting `QT_QPA_PLATFORM=offscreen`, `QT_QPA_PLATFORMTHEME=""`, and `PYTEST_QT_API=pyside6`.
2. Mocking `GitHubPanel.refresh` to prevent thread leak warnings and network calls.
3. Verifying native Qt6 styling programmatically by checking `app.style().objectName()`.
4. Testing missing display robustness in a subprocess.
5. Verifying QProcess execution in tests by using `qtbot.waitUntil` to allow standard Qt event-loop processing of process signals.

---

## 5. Verification Method

To verify the test suite design:
1. Create a `tests/test_cockpit.py` in the cockpit repository.
2. Run the tests using the following command (with dependencies installed via `uv`):
   ```bash
   uv run --with pytest --with pytest-qt --with PySide6 --with requests pytest <path_to_test_file>
   ```
3. Verify that the tests run, succeed (all tests pass), and exit with code `0` with **zero** `QThread` or styling warnings in the output.
