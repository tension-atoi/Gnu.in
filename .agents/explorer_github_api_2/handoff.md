# Handoff Report — Explorer 2 (GitHub API Integration)

## 1. Observation
We observed the following files, functions, and lines in the codebase:

### A. Subprocess `gh` CLI Invocation
In `gnu.in-cockpit/src/cockpit/github_client.py`:
- **Lines 9–22 (`_run_gh`)**: Runs `gh` via `subprocess.run` with JSON serialization/deserialization:
  ```python
  result = subprocess.run(
      ["gh"] + args,
      cwd=cwd,
      capture_output=True,
      text=True,
      check=True
  )
  ```
- **Lines 25–30 (`is_installed`)**: Checks if the `gh` CLI command runs successfully:
  ```python
  subprocess.run(["gh", "--version"], capture_output=True, check=True)
  ```
- **Lines 33–35 (`get_pull_requests`)**: Fetches PRs matching original format keys:
  ```python
  return GitHubClient._run_gh(["pr", "list", "--json", "number,title,state,author,url"], cwd=cwd) or []
  ```
- **Lines 38–40 (`get_recent_runs`)**: Fetches Action runs matching original format keys:
  ```python
  return GitHubClient._run_gh(["run", "list", "--limit", str(limit), "--json", "databaseId,name,status,conclusion,url"], cwd=cwd) or []
  ```

### B. UI Invocation of GitHubClient
In `gnu.in-cockpit/src/cockpit/views/github_panel.py`:
- **Lines 17–18 (`GitHubWorker.run`)**: Calls the client without passing tokens:
  ```python
  prs = GitHubClient.get_pull_requests(self.cwd)
  runs = GitHubClient.get_recent_runs(self.cwd)
  ```
- **Lines 63–65 (`GitHubPanel.refresh`)**: Validates installation prior to fetch:
  ```python
  if not GitHubClient.is_installed():
      self.status_label.setText("gh CLI is not installed or available.")
      return
  ```

In `gnu.in-cockpit/src/cockpit/views/main_window.py`:
- **Line 33 (`Cockpit.__init__`)**: Configures QSettings storage:
  ```python
  self.settings = QSettings("gnu-in-labs", "pipeline-cockpit")
  ```
- **Lines 68–92 (`_build_config_row`)**: Currently holds Workspace, Repo combo box, and Author checkbox, but lacks a GitHub PAT input field.
- **Lines 200–202 (`_refresh_github`)**: Calls `github_panel.refresh` using only `cwd`:
  ```python
  def _refresh_github(self) -> None:
      cwd = str(self._cwd_for("repo"))
      self.github_panel.refresh(cwd)
  ```
- **Lines 300–304 (`_persist`)**: Stores settings but currently misses the PAT token:
  ```python
  def _persist(self) -> None:
      self.settings.setValue("workspace", self.ws_edit.text())
      self.settings.setValue("repo", self.repo_combo.currentText())
      self.settings.setValue("gnosis_author", self.author_cb.isChecked())
  ```

### C. Requirements and Dependencies
- **`gnu.in-cockpit/pyproject.toml`**: Currently lists only `PySide6>=6.6.0` as dependency. Does not list `requests`.
- **`SCOPE.md` Interface Contracts**:
  - `GitHubClient.get_pull_requests(cwd)`: Returns PR list conforming to original format.
  - `GitHubClient.get_recent_runs(cwd, limit)`: Returns run list conforming to original format.
- **`PROJECT.md` Interface Contracts**:
  - Standardized output keys: `number`, `title`, `state`, `author` (`{"login": ...}`), `url` for PRs; and `databaseId`, `name`, `status`, `conclusion`, `url` for runs.

---

## 2. Logic Chain

1. **Dependency Ingress**: To rewrite the client using native HTTP REST calls, `requests` is required. The `pyproject.toml` configuration needs to add `requests` as a dependency. The class method `GitHubClient.is_installed()` should be refactored to verify that `requests` is importable, replacing the check for the `gh` CLI.
2. **Git Metadata Extraction**: The REST API endpoints require the repository owner and name. We can query `git config --get remote.origin.url` (falling back to the first available remote from `git remote` if `origin` is absent) to get the remote URL, then use regular expressions (`github\.com[:/]([^/]+)/([^/]+)$`) to extract the owner and repository name.
3. **PAT Management**:
   - In `main_window.py`, we need to add a `QLineEdit` (with `EchoMode.Password` and placeholder `"ghp_..."`) for the PAT in `_build_config_row`.
   - We must store the input value in QSettings (key `"github_pat"`) within `_persist()`.
   - We must connect the token's `textChanged` signal to `_refresh_github` to trigger an auto-refresh when the PAT is updated.
   - We must pass this token down through `_refresh_github` to `github_panel.refresh()`, then to `GitHubWorker`, and finally as an argument or fallback env variable to `GitHubClient.get_pull_requests` and `GitHubClient.get_recent_runs`.
4. **Endpoint Integration & Output Mapping**:
   - The Pull Requests REST API (`GET /repos/{owner}/{repo}/pulls`) response contains `user.login` and `html_url`. These must map to `author.login` and `url` respectively to fulfill the interface contract.
   - The Actions Runs REST API (`GET /repos/{owner}/{repo}/actions/runs`) returns `workflow_runs`. The run object `id` and `html_url` must map to `databaseId` and `url` respectively to fulfill the interface contract.
5. **Robust Mock Testing**: A unit test suite in `tests/test_github_api.py` should be developed. By mocking `subprocess.run` (for git config outputs) and `requests.get` (returning fake GitHub API responses), we can prove correctness and stability without invoking actual external subprocesses or making network calls.

---

## 3. Caveats
- If the local repository lacks a git remote (e.g. fresh directory or non-git project), owner/repo parsing will fail. The `GitHubClient` methods must raise a clear `RuntimeError` that is handled by the worker and rendered in the UI lists.
- If multiple remotes exist, our fallback logic uses the first remote listed by `git remote`. In complex repository setups, this might point to a mirror instead of the main hub.
- The `requests` dependency must be installed in the executing python environment. If `requests` is not installed, `is_installed()` will return `False` and show a message to the user.

---

## 4. Conclusion
We conclude that the refactoring is highly feasible and can be achieved with the following changes:
1. **`src/cockpit/github_client.py`**:
   - Replace `subprocess` execution of `gh` CLI with `requests.get` queries.
   - Add local git parsing logic to extract owner/repo.
   - Map REST API fields (`user -> author`, `html_url -> url`, `id -> databaseId`) to conform to the contract.
2. **`src/cockpit/views/main_window.py`**:
   - Add a `pat_edit` `QLineEdit` in `_build_config_row()`.
   - Persist it using `QSettings`.
   - Pass the token value to `github_panel.refresh()`.
3. **`src/cockpit/views/github_panel.py`**:
   - Update `refresh` signature to accept a token.
   - Pass the token into the `GitHubWorker` thread, which then invokes the client.
4. **`pyproject.toml`**:
   - Add `requests` to list of dependencies.
5. **`tests/test_github_api.py`**:
   - Implement `unittest` test suite with `mock` covering all logic components (git parsing, header construction, API parsing, error responses).

---

## 5. Verification Method

To verify the implementation once complete:
1. Run the test suite:
   ```sh
   python -m unittest tests/test_github_api.py
   ```
   *Expected outcome*: Zero failures, exit code 0.
2. Verify visual layouts:
   - Launch cockpit using `python -m cockpit`.
   - Check that a token field with placeholder `ghp_...` is visible.
   - Type in a mock token and ensure it does not log cleartext characters (`Password` echo mode).
