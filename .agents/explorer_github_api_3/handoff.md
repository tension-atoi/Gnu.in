# Handoff Report — Explorer 3 (GitHub API Integration)

This report details the architectural and code level findings for refactoring the GitHub integration inside the `gnu.in-cockpit` application. It reconciles prior findings from Explorer 2 and provides a concrete implementation plan.

---

## 1. Observation

We directly observed the following from the codebase and previous research:

### A. Subprocess `gh` CLI Invocation
In `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/github_client.py`:
- **Line 11-17 (`_run_gh`)**: Runs the `gh` CLI as a subprocess:
  ```python
  result = subprocess.run(
      ["gh"] + args,
      cwd=cwd,
      capture_output=True,
      text=True,
      check=True
  )
  ```
- **Lines 25-30 (`is_installed`)**: Checks CLI existence via:
  ```python
  subprocess.run(["gh", "--version"], capture_output=True, check=True)
  ```
- **Lines 33-35 (`get_pull_requests`)**: Queries open pull requests:
  ```python
  return GitHubClient._run_gh(["pr", "list", "--json", "number,title,state,author,url"], cwd=cwd) or []
  ```
- **Lines 38-40 (`get_recent_runs`)**: Queries workflow runs:
  ```python
  return GitHubClient._run_gh(["run", "list", "--limit", str(limit), "--json", "databaseId,name,status,conclusion,url"], cwd=cwd) or []
  ```

### B. UI Invocation of GitHubClient
In `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/views/github_panel.py`:
- **Lines 17-18 (`GitHubWorker.run`)**: Invokes client without PAT token:
  ```python
  prs = GitHubClient.get_pull_requests(self.cwd)
  runs = GitHubClient.get_recent_runs(self.cwd)
  ```
- **Lines 63-65 (`GitHubPanel.refresh`)**: Performs installation check:
  ```python
  if not GitHubClient.is_installed():
      self.status_label.setText("gh CLI is not installed or available.")
      return
  ```

In `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/views/main_window.py`:
- **Line 33**: Instantiates settings:
  ```python
  self.settings = QSettings("gnu-in-labs", "pipeline-cockpit")
  ```
- **Lines 68-92 (`_build_config_row`)**: Renders workspace, repo combo box, and author checkbox. It does not have a field for GitHub PAT.
- **Lines 200-202 (`_refresh_github`)**: Triggers refresh using only `cwd`:
  ```python
  def _refresh_github(self) -> None:
      cwd = str(self._cwd_for("repo"))
      self.github_panel.refresh(cwd)
  ```

### C. Requirements and Dependencies
- **`gnu.in-cockpit/pyproject.toml`**: Currently lists only `PySide6>=6.6.0` as dependency. It does not list `requests`.

---

## 2. Logic Chain

1. **Dependency Transition**: Since we are replacing the `gh` CLI with native REST calls, the Python `requests` library must be added to `pyproject.toml` dependencies. The function `GitHubClient.is_installed()` should check if `requests` can be imported (`import requests`).
2. **Git Metadata Extraction**: GitHub's REST endpoints (`/repos/{owner}/{repo}/pulls` and `/repos/{owner}/{repo}/actions/runs`) require the repository owner and name. We can run `git config --get remote.origin.url` using `subprocess.check_output` targeting the `cwd` (repository path). If `origin` is missing, we list all remotes (`git remote`) and query the first available remote's URL. We parse this URL using a regular expression:
   `r'(?:git@github\.com:|https?://github\.com/|ssh://git@github\.com/)([^/]+)/([^/.]+)(?:\.git)?'`
3. **PAT UI & Storage Integration**: 
   - We must add a `QLineEdit` for the PAT in `main_window.py:_build_config_row` with password echo mode (`QLineEdit.EchoMode.Password`) and a placeholder `ghp_...`.
   - We must save it to `QSettings` (under the key `"github_pat"`) within `_persist()`.
   - To trigger refresh, we connect the `editingFinished` signal of `pat_edit` to `_refresh_github`. This is superior to `textChanged` (which would trigger on every character typed, spawning dozens of concurrent request threads and potentially hitting API rate limits).
   - In `_refresh_github`, we retrieve the PAT text and pass it to `github_panel.refresh(cwd, token)`.
4. **Data Mapping**:
   - For Pull Requests: The REST API returns the user object as `user` and URL as `html_url`. We must map these to `author: {"login": user["login"]}` and `url` respectively to fulfill the interface contract.
   - For Actions Runs: The REST API returns workflow runs. We map `id` to `databaseId` and `html_url` to `url` respectively to conform to the contract.
5. **Testing Feasibility**: Using `unittest.mock` to mock `subprocess.check_output` (returning fake git remote URLs) and `requests.get` (returning simulated REST responses) allows the unit test suite (`tests/test_github_api.py`) to run safely in offline environments and pass with exit code 0.

---

## 3. Synthesis of Findings

### Consensus
- **Requests transition**: Both Explorer 2 and 3 agree that `requests` must be added to dependencies in `pyproject.toml` and used as the HTTP client.
- **REST Endpoints**: Agreement on endpoints: `GET /repos/{owner}/{repo}/pulls` and `GET /repos/{owner}/{repo}/actions/runs`.
- **JSON Mapping**: Agreement on key mapping rules (`user -> author`, `html_url -> url`, `id -> databaseId`).
- **Persistence**: Persisting the token in `QSettings` via `"github_pat"` key.

### Resolved Conflicts
- **Input Field Event Connection**:
  - *Explorer 2's position*: Connect `pat_edit.textChanged` to `_refresh_github` to update status as the user types.
  - *Explorer 3's position*: Connect `pat_edit.editingFinished` to `_refresh_github`.
  - *Resolution*: Adopt `editingFinished`. Triggering on `textChanged` spawns a background thread and performs a network API request for every single keystroke. This causes thread congestion, UI lag, and quickly hits rate limits. `editingFinished` is fired only when the user finishes typing (defocussing the input or hitting Enter), which is standard and performant.

### Dissenting Views
- None.

### Gaps
- None.

---

## 4. Caveats

- **No Remote Configured**: If a repo has no remotes or is not a git repository, `_get_repo_info` will return `None`. `get_pull_requests` and `get_recent_runs` will gracefully return empty lists `[]` rather than throwing unhandled exceptions.
- **Authentication Fallback**: If no PAT token is provided (empty string), requests will be made without the `Authorization` header. This will succeed for public repositories but is subject to lower rate limits (60 requests/hour for unauthenticated REST requests).

---

## 5. Conclusion

We conclude that the refactoring is highly feasible, backwards compatible, and addresses performance and usability issues. The following resources have been placed in the explorer's agent directory to guide implementation:
1. `github_client.patch` - Patch for `src/cockpit/github_client.py`
2. `github_panel.patch` - Patch for `src/cockpit/views/github_panel.py`
3. `main_window.patch` - Patch for `src/cockpit/views/main_window.py`
4. `pyproject.patch` - Patch for `pyproject.toml`
5. `proposed_github_client.py` - Entire rewritten client code
6. `proposed_github_panel.py` - Entire rewritten panel code
7. `proposed_test_github_api.py` - Complete mock-based unit tests code to be created at `tests/test_github_api.py`

---

## 6. Verification Method

Once changes are applied, verify via:
1. **Unit Tests**:
   Run the mock test suite:
   ```sh
   python -m unittest tests/test_github_api.py
   ```
   *Expected result*: All tests pass, exit code 0.
2. **Visual & Behavior Check**:
   Run the cockpit panel:
   ```sh
   python -m cockpit
   ```
   Verify that:
   - A `GitHub PAT` password entry field is visible in the config row.
   - Values typed into the PAT field are masked (`EchoMode.Password`).
   - The token persists after closing and reopening the app.
   - Changing the PAT and exiting the field triggers a refresh.
