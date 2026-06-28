# Handoff Report — Explorer 1 (GitHub API Integration)

## 1. Observation
We observed and verified the following details in the codebase:

### A. Original `gh` CLI Invocation
In `gnu.in-cockpit/src/cockpit/github_client.py`:
- **`is_installed` (Lines 24-30)**: Runs `gh --version` to check if `gh` CLI is installed.
  ```python
  subprocess.run(["gh", "--version"], capture_output=True, check=True)
  ```
- **`get_pull_requests` (Lines 32-35)**: Fetches PRs as JSON matching keys: `number`, `title`, `state`, `author` (`{"login": ...}`), `url`.
  ```python
  return GitHubClient._run_gh(["pr", "list", "--json", "number,title,state,author,url"], cwd=cwd) or []
  ```
- **`get_recent_runs` (Lines 37-40)**: Fetches Actions workflow runs matching keys: `databaseId`, `name`, `status`, `conclusion`, `url`.
  ```python
  return GitHubClient._run_gh(["run", "list", "--limit", str(limit), "--json", "databaseId,name,status,conclusion,url"], cwd=cwd) or []
  ```

### B. UI Elements & Integration
In `gnu.in-cockpit/src/cockpit/views/github_panel.py`:
- **`refresh` (Lines 62-75)**: Checks `GitHubClient.is_installed()`. If it returns `True`, instantiates `GitHubWorker(cwd)` (which does not take a token).
  ```python
  if not GitHubClient.is_installed():
      self.status_label.setText("gh CLI is not installed or available.")
      return
  ...
  self.worker = GitHubWorker(cwd)
  ```
- **`GitHubWorker.run` (Lines 15-21)**: Calls the client static methods without passing PAT tokens.
  ```python
  prs = GitHubClient.get_pull_requests(self.cwd)
  runs = GitHubClient.get_recent_runs(self.cwd)
  ```

In `gnu.in-cockpit/src/cockpit/views/main_window.py`:
- **`_build_config_row` (Lines 68-92)**: Does not currently feature a QLineEdit for the Personal Access Token (PAT).
- **`_refresh_github` (Lines 200-202)**: Calls `github_panel.refresh` with only the `cwd` directory.
  ```python
  def _refresh_github(self) -> None:
      cwd = str(self._cwd_for("repo"))
      self.github_panel.refresh(cwd)
  ```
- **`_persist` (Lines 300-304)**: Saves workspace and repo selections, but does not save any GitHub PAT settings.
  ```python
  def _persist(self) -> None:
      self.settings.setValue("workspace", self.ws_edit.text())
      self.settings.setValue("repo", self.repo_combo.currentText())
      self.settings.setValue("gnosis_author", self.author_cb.isChecked())
  ```

### C. Workspace & Git Remote Config
- By running `git remote -v` in `gnu.in-os` (the primary OS repository inside the workspace), we verified it has the following config:
  `origin  https://github.com/gnu-in-labs/gnu.in-os.git`
- `gnu.in-cockpit/pyproject.toml` lists only `PySide6>=6.6.0` as dependency, omitting `requests`.

---

## 2. Logic Chain

1. **Dependency management**: To rewrite `github_client.py` using native REST API requests, we need the `requests` library. We must add `"requests>=2.28.0"` to the `dependencies` list in `pyproject.toml`.
2. **Replacement of `gh` CLI**:
   - `is_installed()` in `github_client.py` should be refactored to verify the availability/importability of the `requests` module, returning `False` if not present.
   - `get_repo_info(cwd)` will run `git config --get remote.origin.url` in the target directory to extract the HTTPS or SSH repository remote.
   - We must parse the owner and repository name cleanly. Standard URLs can be parsed by splitting on `"github.com"` and taking the subsequent tokens: e.g., `/gnu-in-labs/gnu.in-os.git` is split to extract `owner="gnu-in-labs"`, `repo="gnu.in-os"`.
3. **REST API Endpoint Matching & Field Mapping**:
   - For pull requests: Query `GET https://api.github.com/repos/{owner}/{repo}/pulls` with parameter `state=open`. The API response list contains items with `number`, `title`, `state`, `html_url`, and `user.login`. These must map to `number`, `title`, `state` (upper-cased, e.g., `"OPEN"`), `url`, and `author.login` respectively.
   - For recent runs: Query `GET https://api.github.com/repos/{owner}/{repo}/actions/runs` with parameter `per_page=limit`. The API returns a dictionary with key `workflow_runs`. We extract `id` (mapped to `databaseId`), `name`, `status`, `conclusion`, and `html_url` (mapped to `url`).
4. **Token Propagation**:
   - Add a `QLineEdit` (`self.pat_edit`) to the configuration row in `main_window.py`. Setting `EchoMode.Password` and placeholder `ghp_...` guarantees secrecy of the PAT.
   - Load and persist `self.pat_edit` to `QSettings` via key `"github_pat"`.
   - Connect the `textChanged` signal of `self.pat_edit` to `_refresh_github` so updates trigger a refresh.
   - Pass the token value from `main_window.py` to `github_panel.refresh()`, then through to the `GitHubWorker` constructor and finally into the `GitHubClient` methods.
5. **Testing & Validation**:
   - Implement `tests/test_github_api.py` with mock responses for `subprocess.run` (to mock git output) and `requests.get` (to mock GitHub API endpoints). This tests the entire parser logic and requests invocation flow without triggering real sub-processes or external network calls.

---

## 3. Caveats
- If the target workspace directory is not a git repository or lacks `remote.origin.url`, `get_repo_info` will raise a `ValueError`/`RuntimeError`. The UI currently catches this error in `GitHubWorker`'s try-except block and displays it in the QListWidget gracefully.
- The `requests` module is expected to be installed. If not, the UI will report that `requests` is not installed or available.

---

## 4. Conclusion
We conclude that the refactoring is highly feasible, backwards-compatible, and requires changes across 5 specific project files. We have created full proposed replacements for these files in our working directory:

1. **`proposed_github_client.py`** -> To replace `src/cockpit/github_client.py`
2. **`proposed_github_panel.py`** -> To replace `src/cockpit/views/github_panel.py`
3. **`proposed_main_window.py`** -> To replace `src/cockpit/views/main_window.py`
4. **`proposed_test_github_api.py`** -> To be written to `tests/test_github_api.py`
5. **`proposed_pyproject.toml`** -> To replace `pyproject.toml`

---

## 5. Verification Method

Once changes are applied by the implementer, the following verification checks should be executed:
1. Run the new mock unit test suite:
   ```sh
   python -m unittest tests/test_github_api.py
   ```
   *Expected result*: All mock unit tests pass successfully (Exit Code 0).
2. Launch the cockpit panel:
   ```sh
   python -m cockpit
   ```
   *Expected result*: The interface initializes properly in Wayland/Qt6. The "GitHub PAT" QLineEdit is visible in the config row. Characters typed into it are masked (Password mode).
