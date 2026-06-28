## 2026-06-18T00:13:04Z

You are a worker subagent named worker_final_fixes.
Your working directory is /home/tension_atoi/Projects/Gnu.in/.agents/worker_final_fixes/.
Your mission is to resolve test suite hangs and failures, and implement installer robustness improvements.

Please perform the following tasks:
1. In gnu.in-cockpit/install.sh:
   - Change the shebang (line 1) to #!/bin/bash.
   - On line 31, change PREFIX="$(mkdir -p "$PREFIX" && cd -- "$PREFIX" && pwd)" to PREFIX="$(mkdir -p -- "$PREFIX" && cd -- "$PREFIX" && pwd)".
   - In Section 4 (Clean Pre-existing Files), add:
     chmod -R +w "$BIN_DIR/gnuin-cockpit" "$APPS_DIR/gnuin-cockpit.desktop" "$ICON_DIR/gnuin-cockpit.svg" "$VENV_DIR" 2>/dev/null || true
     just before the rm commands.
2. In gnu.in-cockpit/src/cockpit/__main__.py:
   - Inside main() (around line 34-36), after win.show(), add:
     if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
         from PySide6.QtCore import QTimer
         if win.github_panel.worker and win.github_panel.worker.isRunning():
             win.github_panel.worker.requestInterruption()
             win.github_panel.worker.quit()
             win.github_panel.worker.wait()
         QTimer.singleShot(100, app.quit)
3. In gnu.in-cockpit/tests/test_e2e_workflows.py:
   - Inside the mock_msgbox fixture, add a mock for QInputDialog.getText:
     from PySide6.QtWidgets import QInputDialog
     monkeypatch.setattr(QInputDialog, "getText", lambda *a: ("mock_build_id", True))
4. In gnu.in-cockpit/tests/test_e2e_actions.py:
   - Inside the mock_msgbox fixture, add a mock for QInputDialog.getText:
     from PySide6.QtWidgets import QInputDialog
     monkeypatch.setattr(QInputDialog, "getText", lambda *a: ("mock_build_id", True))
5. Verify the fixes by running the entire test suite:
   cd gnu.in-cockpit && .venv/bin/pytest
   Ensure all tests pass.
6. Document changes and test results in handoff.md under /home/tension_atoi/Projects/Gnu.in/.agents/worker_final_fixes/handoff.md.

MANDATORY INTEGRITY WARNING: DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
