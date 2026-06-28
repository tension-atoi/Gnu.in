## 2026-06-17T14:42:13Z
You are Worker 2 (GitHub API Integration - Fix Phase).
Your working directory is /home/tension_atoi/Projects/Gnu.in/.agents/worker_github_api_2/.
Your task is to fix the defects identified during the verification phase.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please fix the following defects:

1. Dotted Repository Name Truncation & Host Verification Bypass (Regex Bug):
   - In `src/cockpit/github_client.py`, the regex in `_get_repo_info` excludes dots (`[^/.]+`) and lacks start/end anchors, causing repository names like `gnu.in-cockpit` to be truncated to `gnu` and allowing nested URLs from other hosts to match.
   - Fix: Use a robust regex anchored to start/end that allows dots in the repository name and requires github.com as host:
     `r'^(?:https?://github\.com/|git@github\.com:|ssh://git@github\.com/)([^/]+)/([^/]+?)(?:\.git)?\/?$'`
     Verify that this parses HTTPS/SSH formats with dots correctly and returns `(owner, repo)`.

2. Whitespace PAT Token Handling:
   - In `src/cockpit/github_client.py` and views, ensure the token is stripped (`token.strip()`). If it is empty after stripping, treat it as `None` or `""` and do NOT add the `Authorization` header.

3. QThread Concurrency & Destruction Crash:
   - In `src/cockpit/views/github_panel.py` inside `refresh(self, cwd, token)`: If `self.worker` exists and `self.worker.isRunning()`, disconnect its signals, request interruption, and wait for it to exit before starting a new worker thread. E.g.:
     ```python
     if self.worker and self.worker.isRunning():
         self.worker.disconnect()
         self.worker.quit()
         self.worker.wait()
     ```
   - In `src/cockpit/views/main_window.py` inside `closeEvent(self, event)`: Safely stop and wait for the running worker thread if it exists:
     ```python
     if hasattr(self, "github_panel") and self.github_panel.worker:
         if self.github_panel.worker.isRunning():
             self.github_panel.worker.disconnect()
             self.github_panel.worker.quit()
             self.github_panel.worker.wait()
     ```

4. Status NoneType Attribute Error:
   - In `src/cockpit/views/github_panel.py` inside `_on_result(self, data)`: The parsing of action runs calls `status.upper()`. If conclusion and status are missing or `None`, it raises an AttributeError.
   - Fix: Gracefully fallback to a default string:
     ```python
     status = run.get('conclusion') or run.get('status') or 'unknown'
     item = QListWidgetItem(f"[{status.upper()}] {run.get('name', 'Unnamed Workflow')}")
     ```

Verification and Testing:
- Run the unit tests to verify your fixes:
  `python3 -m unittest discover -s tests`
  `python3 tests/test_github_api_stress.py`
  All tests (including stress tests and dot parsing tests) must pass successfully with exit code 0.
- Write your handoff to handoff.md in your working directory and notify parent.
