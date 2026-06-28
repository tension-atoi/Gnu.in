# Handoff Report - Installation Analysis and Design for gnu.in-cockpit

This report contains findings, design details, and implementation proposals for the `install.sh` and desktop entry configuration of the `gnu.in-cockpit` application.

## 1. Observation

During our investigation of the codebase, we observed the following configuration and testing expectations:

1. **Python Version Requirements**:
   - In `gnu.in-cockpit/pyproject.toml` (lines 10-14):
     ```toml
     requires-python = ">=3.10"
     dependencies = [
         "PySide6>=6.6.0",
         "requests>=2.28.0",
     ]
     ```
   - In `gnu.in-cockpit/tests/test_e2e_install.py` (lines 91-92):
     ```python
     mock_python = mock_bin_dir / "python3"
     mock_python.write_text("#!/bin/sh\necho 'Python 3.9.2'")
     ```
     This indicates the installer must parse the stdout string of `python3 --version` or `python3 -V` to validate the version, rather than relying on Python interpretation of `-c` scripts during initial checks, as a mock Python script might just be a shell script returning a string.

2. **Installation Directory Layout Assertions**:
   - In `gnu.in-cockpit/tests/test_e2e_install.py` (lines 28-33):
     ```python
     prefix = tmp_path / "usr"
     subprocess.run([str(INSTALL_SH_PATH), "--prefix", str(prefix)], capture_output=True)
     venv_path = prefix / "share" / "gnuin-cockpit" / "venv"
     assert venv_path.exists()
     assert (venv_path / "bin" / "python").exists()
     ```
   - In `gnu.in-cockpit/tests/test_e2e_install.py` (lines 48-53):
     ```python
     desktop_file = prefix / "share" / "applications" / "gnuin-cockpit.desktop"
     assert desktop_file.exists()
     content = desktop_file.read_text()
     assert f"Exec={prefix}/bin/gnuin-cockpit" in content
     ```
   - In `gnu.in-cockpit/tests/test_e2e_install.py` (lines 58-60):
     ```python
     icon_file = prefix / "share" / "icons" / "hicolor" / "scalable" / "apps" / "gnuin-cockpit.svg"
     assert icon_file.exists()
     ```

3. **Graceful Error Handling and Idempotency**:
   - In `gnu.in-cockpit/tests/test_e2e_install.py` (lines 69-74):
     ```python
     res = subprocess.run([str(INSTALL_SH_PATH), "--prefix", "/usr"], capture_output=True, text=True)
     assert res.returncode != 0
     assert "permission denied" in res.stdout.lower() or "permission denied" in res.stderr.lower() or "writable" in res.stderr.lower() or "writable" in res.stdout.lower()
     ```
   - In `gnu.in-cockpit/tests/test_e2e_install.py` (lines 106-114):
     ```python
     # Re-running the script should work and overwrite previous state successfully
     res = subprocess.run([str(INSTALL_SH_PATH), "--prefix", str(prefix)], capture_output=True)
     assert res.returncode == 0
     ```
   - In `gnu.in-cockpit/tests/test_e2e_install.py` (lines 121-127):
     ```python
     readonly_file = desktop_dir / "gnuin-cockpit.desktop"
     readonly_file.write_text("[Desktop Entry]\nName=Mock")
     readonly_file.chmod(0o400) # Read-only
     res = subprocess.run([str(INSTALL_SH_PATH), "--prefix", str(prefix)], capture_output=True)
     assert res.returncode == 0 or "warning" in res.stderr.lower()
     ```

4. **Qt6 Native Styling and Theme Overrides**:
   - In `gnu.in-cockpit/data/gnuin-cockpit.desktop` (lines 11-12):
     ```ini
     # Enforce native Qt styling via Wayland where applicable
     Environment=QT_QPA_PLATFORM=wayland;QT_STYLE_OVERRIDE=kvantum
     ```
   - In `gnu.in-cockpit/src/cockpit/__main__.py` (lines 7, 23):
     ```python
     os.environ.setdefault("QT_QPA_PLATFORMTHEME", "")
     app.setStyle("Fusion")
     ```

## 2. Logic Chain

1. **Premise 1**: The installation script `install.sh` must be fully compatible with the assertions in `test_e2e_install.py`.
2. **Premise 2**: Since the E2E test runs the installer with varying arguments (specifically `--prefix`), the script must parse `--prefix` and default it to a local folder (e.g., `~/.local`).
3. **Premise 3**: Since the E2E test interrupts the script midway and re-runs it, the script must ensure no lock files or corrupted virtual environments block successive runs. This is handled by executing `rm -rf` on target paths (such as the virtual environment directory) at the beginning of the installation steps.
4. **Premise 4**: Since the E2E test writes a pre-existing read-only desktop file, the installer must cleanly remove or overwrite the target desktop file, which can be accomplished via `rm -f` (which ignores write permissions if the parent directory is writable).
5. **Premise 5**: The user has strict global rules forbidding GNOME/GTK dependencies (`gsettings`, `GTK_THEME`), requiring exclusive reliance on Qt6 Native styling and Wayland protocols.
6. **Premise 6**: The wrapper executable at `prefix/bin/gnuin-cockpit` and the desktop file must configure native environment overrides like `QT_QPA_PLATFORM=wayland` and `QT_STYLE_OVERRIDE=kvantum` without injecting any GTK or GNOME settings.
7. **Conclusion**: We can write a fully compliant, self-contained `install.sh` and `.desktop` structure. The proposed implementation has been placed in our working folder.

## 3. Caveats

- We assumed that the tests run in a environment with Pip configured to resolve dependencies offline or via a local cache if network restrictions are active during the test execution. To remain highly robust, `install.sh` executes the package installation using `pip install "$SCRIPT_DIR"` which allows the test-runner's configured pip cache/mechanism to fulfill requirements.
- We assumed that the app icon is sourced from `gnu.in-design-reference` if available. Since it may not be present in standalone checkouts, the installer includes a base64 or raw embedded SVG fallback to guarantee that the required `gnuin-cockpit.svg` icon is always deployed.

## 4. Conclusion

The design requires:
1. An `install.sh` script that supports `--prefix`, checks Python (>= 3.10) via string regex, checks directory writability, removes pre-existing files, creates a Python venv under `share/gnuin-cockpit/venv`, installs `pyside6` and the application, and deploys a wrapper script under `bin/gnuin-cockpit`.
2. A `.desktop` template that specifies `QT_QPA_PLATFORM=wayland;QT_STYLE_OVERRIDE=kvantum` under `Environment` key, and gets customized during installation with the absolute path of the wrapper script.
3. An icon deployed at `prefix/share/icons/hicolor/scalable/apps/gnuin-cockpit.svg` using design-reference assets or an embedded fallback.

The complete code for the installer has been designed and written as `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_install/proposed_install.sh`.

## 5. Verification Method

To verify the proposed implementation plan:
1. The implementer should copy `proposed_install.sh` to `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/install.sh`.
2. Make it executable: `chmod +x /home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/install.sh`.
3. Run the installation tests inside `gnu.in-cockpit` directory:
   ```bash
   cd /home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit
   pytest tests/test_e2e_install.py
   ```
4. Confirm all tests pass successfully.
