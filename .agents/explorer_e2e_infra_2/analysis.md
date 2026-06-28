# GitHub Integration Mocking Strategy

This analysis documents the design and setup for mocking the GitHub REST API and `gh` CLI commands in the `gnu.in-cockpit` project. It provides reusable mocking strategies suitable for pytest and standard unittest, allowing developers to inject mock Pull Requests (PRs) and GitHub Actions statuses to test the UI and logic under various conditions.

---

## 1. Context & Existing Architecture

The `gnu.in-cockpit` application integrates with GitHub to display open Pull Requests and recent GitHub Actions workflow runs. 

### Current State
* **API Client (`src/cockpit/github_client.py`)**: Uses the `requests` library to directly call the GitHub REST API (`https://api.github.com/repos/{owner}/{repo}/pulls` and `/actions/runs`). It parses the JSON responses and returns lists of mapped dictionaries.
* **CLI reference**: While `README.md` and project packaging metadata (`PKG-INFO`) mention managing PRs and pipelines via the `gh` CLI, the current Python code uses the REST API client. However, if a `gh` CLI fallback or command execution is implemented, it will run as subprocess calls.
* **Testing (`tests/test_github_api.py`)**: Uses `unittest.mock.patch` to patch `requests.get` and `GitHubClient._get_repo_info` at the individual test level.

To build a robust End-to-End (E2E) and integration testing infrastructure for Milestone 2, we need a unified setup (e.g., in a `conftest.py`) that handles both CLI-based subprocess execution and REST API calls.

---

## 2. Mocking the `gh` CLI (Subprocess Calls)

If the application executes `gh` CLI commands using `subprocess.run` or `subprocess.check_output`, we can intercept these calls globally.

### Crucial Dependency: Git Remote Parsing
Before calling any GitHub command, the client calls `GitHubClient._get_repo_info(cwd)` which runs `git config --get remote.origin.url` to determine the repository owner and name. If this fails or returns `None`, the client aborts immediately. Thus, our CLI mock must either mock `git` subprocess calls as well, or we must patch `_get_repo_info` directly.

### pytest Fixture Design (`conftest.py`)
This fixture intercepts `subprocess.run` and `subprocess.check_output`. If the command starts with `gh`, it returns mock JSON payloads representing CLI command outputs. If it asks for git remote configurations, it returns a mock GitHub URL. Other commands pass through to the real system.

```python
# conftest.py
import json
import subprocess
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_gh_cli(monkeypatch):
    """
    Globally intercepts and mocks 'gh' CLI and related 'git' subprocess commands.
    Provides a controller to inject mock PRs and actions runs.
    """
    mocked_data = {
        "prs": [],
        "runs": []
    }
    
    # Track executed commands for test assertions
    command_history = []

    original_run = subprocess.run
    original_check_output = subprocess.check_output

    def parse_gh_command(args):
        # Convert args list or string to string for easier matching
        cmd_str = " ".join(args) if isinstance(args, list) else args
        command_history.append(cmd_str)
        return cmd_str

    def mock_run(args, *extra_args, **kwargs):
        cmd_str = parse_gh_command(args)
        
        # Intercept gh CLI commands
        if isinstance(args, list) and args[0] == "gh":
            stdout_data = b"[]"
            if "pr list" in cmd_str:
                stdout_data = json.dumps(mocked_data["prs"]).encode("utf-8")
            elif "run list" in cmd_str or "run view" in cmd_str:
                stdout_data = json.dumps(mocked_data["runs"]).encode("utf-8")
                
            return subprocess.CompletedProcess(
                args=args,
                returncode=0,
                stdout=stdout_data,
                stderr=b""
            )
        
        # Fallback to original subprocess.run for other commands
        return original_run(args, *extra_args, **kwargs)

    def mock_check_output(args, *extra_args, **kwargs):
        cmd_str = parse_gh_command(args)
        is_text = kwargs.get("text", False)

        # Intercept gh CLI commands
        if isinstance(args, list) and args[0] == "gh":
            out_str = "[]"
            if "pr list" in cmd_str:
                out_str = json.dumps(mocked_data["prs"])
            elif "run list" in cmd_str:
                out_str = json.dumps(mocked_data["runs"])
            return out_str if is_text else out_str.encode("utf-8")

        # Intercept git remote queries to ensure get_repo_info succeeds
        if isinstance(args, list) and args[0] == "git":
            if "remote.origin.url" in cmd_str:
                url = "https://github.com/gnu-in-labs/gnu.in-cockpit.git\n"
                return url if is_text else url.encode("utf-8")
            elif "remote" in cmd_str and len(args) == 2:
                remotes = "origin\n"
                return remotes if is_text else remotes.encode("utf-8")

        # Fallback to original check_output
        return original_check_output(args, *extra_args, **kwargs)

    monkeypatch.setattr(subprocess, "run", mock_run)
    monkeypatch.setattr(subprocess, "check_output", mock_check_output)

    class CliMockController:
        def set_prs(self, prs_list):
            mocked_data["prs"] = prs_list

        def set_runs(self, runs_list):
            mocked_data["runs"] = runs_list

        @property
        def history(self):
            return command_history

    return CliMockController()
```

---

## 3. Mocking the REST API Client (Requests & PAT)

To mock the target implementation using `requests` with Personal Access Tokens (PAT), we can use a custom requests patcher using `monkeypatch` in a `conftest.py` fixture. This avoids introducing extra heavy dependencies like `responses` or `requests_mock` unless desired.

### Key Validation Aspects
1. **Repository Info Mocking**: Intercepts Git remote checks or returns dummy repo coordinates (`gnu-in-labs`, `gnu.in-cockpit`).
2. **Authorization Header**: Verifies that the client correctly forwards the token in the `Authorization: Bearer <PAT>` header if one is set.
3. **HTTP Status Handling**: Can mimic success (`200 OK`), rate limiting (`403 Forbidden` / `429 Too Many Requests`), or auth failure (`401 Unauthorized`).

### pytest Fixture Design (`conftest.py`)

```python
# conftest.py
import pytest
import requests
from unittest.mock import MagicMock

@pytest.fixture
def mock_github_rest_api(monkeypatch):
    """
    Mocks requests.get calls for the GitHub REST API.
    Enforces authorization header checks and returns custom data.
    """
    mocked_data = {
        "prs": [],
        "runs": []
    }
    
    # Store requests for validation
    request_log = []
    
    # Default behavior configuration
    config = {
        "status_code": 200,
        "error_message": "",
        "expected_token": None
    }

    def mock_get(url, headers=None, params=None, timeout=None):
        headers = headers or {}
        params = params or {}
        
        request_log.append({
            "url": url,
            "headers": headers,
            "params": params,
            "timeout": timeout
        })

        # Validate authorization token if one is expected
        if config["expected_token"]:
            auth_header = headers.get("Authorization", "")
            expected_header = f"Bearer {config['expected_token']}"
            if auth_header != expected_header:
                mock_err_response = MagicMock(spec=requests.Response)
                mock_err_response.status_code = 401
                mock_err_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                    "401 Unauthorized: Invalid or missing token"
                )
                return mock_err_response

        # Handle explicit mock error status codes (e.g. rate limit, bad request)
        if config["status_code"] != 200:
            mock_err_response = MagicMock(spec=requests.Response)
            mock_err_response.status_code = config["status_code"]
            mock_err_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                f"{config['status_code']} Error: {config['error_message']}"
            )
            return mock_err_response

        # Build successful response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200

        if "/pulls" in url:
            mock_response.json.return_value = mocked_data["prs"]
        elif "/actions/runs" in url:
            mock_response.json.return_value = {
                "workflow_runs": mocked_data["runs"]
            }
        else:
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "404 Not Found"
            )

        return mock_response

    # Inject mock GET method
    monkeypatch.setattr(requests, "get", mock_get)

    class RestMockController:
        def set_prs(self, pr_payloads):
            mocked_data["prs"] = pr_payloads

        def set_runs(self, run_payloads):
            mocked_data["runs"] = run_payloads

        def configure_error(self, status_code, message=""):
            config["status_code"] = status_code
            config["error_message"] = message

        def enforce_token(self, token):
            config["expected_token"] = token

        @property
        def log(self):
            return request_log

        def reset(self):
            mocked_data["prs"] = []
            mocked_data["runs"] = []
            config["status_code"] = 200
            config["error_message"] = ""
            config["expected_token"] = None
            request_log.clear()

    return RestMockController()
```

---

## 4. Injecting Mock PRs and Actions Statuses

Below is an illustration of how test cases can use the REST API mock fixture to inject mock pull requests and action runs (incorporating databaseId, name, status, conclusion, and url).

### Mapped Schemas (as handled by `github_client.py`)
* **Pull Requests**:
  * Raw Key -> Mapped Key
  * `number` -> `number`
  * `title` -> `title`
  * `state` -> `state` (capitalized to `"OPEN"`)
  * `user.login` -> `author.login`
  * `html_url` -> `url`
* **Actions Runs**:
  * Raw Key -> Mapped Key
  * `id` -> `databaseId`
  * `name` -> `name`
  * `status` -> `status`
  * `conclusion` -> `conclusion`
  * `html_url` -> `url`

### Example Test Suite (`tests/test_github_integration.py`)

```python
import pytest
from cockpit.github_client import GitHubClient

def test_get_pull_requests_mapped(mock_github_rest_api):
    # Arrange: Inject mock PR data
    mock_github_rest_api.set_prs([
        {
            "number": 101,
            "title": "Implement Qt6 styling",
            "state": "open",
            "user": {"login": "tension_atoi"},
            "html_url": "https://github.com/gnu-in-labs/gnu.in-cockpit/pull/101"
        }
    ])
    
    # Act: Retrieve PRs
    prs = GitHubClient.get_pull_requests("/dummy/path")
    
    # Assert: Mapped values
    assert len(prs) == 1
    assert prs[0]["number"] == 101
    assert prs[0]["title"] == "Implement Qt6 styling"
    assert prs[0]["state"] == "OPEN"
    assert prs[0]["author"]["login"] == "tension_atoi"
    assert prs[0]["url"] == "https://github.com/gnu-in-labs/gnu.in-cockpit/pull/101"


def test_get_recent_runs_status_keys(mock_github_rest_api):
    # Arrange: Inject multiple runs in different states
    mock_github_rest_api.set_runs([
        {
            "id": 1001,
            "name": "CI Build",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/gnu-in-labs/gnu.in-cockpit/actions/runs/1001"
        },
        {
            "id": 1002,
            "name": "Lints and Checks",
            "status": "completed",
            "conclusion": "failure",
            "html_url": "https://github.com/gnu-in-labs/gnu.in-cockpit/actions/runs/1002"
        },
        {
            "id": 1003,
            "name": "Coherence Check",
            "status": "in_progress",
            "conclusion": None,
            "html_url": "https://github.com/gnu-in-labs/gnu.in-cockpit/actions/runs/1003"
        }
    ])
    
    # Act: Retrieve recent runs
    runs = GitHubClient.get_recent_runs("/dummy/path", limit=5)
    
    # Assert: Verify status keys mapped
    assert len(runs) == 3
    
    # Successful run
    assert runs[0]["databaseId"] == 1001
    assert runs[0]["name"] == "CI Build"
    assert runs[0]["status"] == "completed"
    assert runs[0]["conclusion"] == "success"
    assert runs[0]["url"] == "https://github.com/gnu-in-labs/gnu.in-cockpit/actions/runs/1001"
    
    # Failed run
    assert runs[1]["databaseId"] == 1002
    assert runs[1]["conclusion"] == "failure"
    
    # In-progress run
    assert runs[2]["databaseId"] == 1003
    assert runs[2]["status"] == "in_progress"
    assert runs[2]["conclusion"] is None


def test_invalid_pat_token_handling(mock_github_rest_api):
    # Arrange: Configure mock to require a specific valid PAT
    mock_github_rest_api.enforce_token("valid_token_123")
    
    # Act & Assert: Call with incorrect token raises RuntimeError
    with pytest.raises(RuntimeError) as exc_info:
        GitHubClient.get_pull_requests("/dummy/path", token="bad_token")
    
    assert "GitHub REST API error" in str(exc_info.value)
    
    # Assert: Call with correct token succeeds
    mock_github_rest_api.set_prs([])
    prs = GitHubClient.get_pull_requests("/dummy/path", token="valid_token_123")
    assert prs == []
```

---

## 5. Testing Boundary Conditions & Robustness

A comprehensive test suite must verify the client and UI robustness under boundary conditions. The designed mock fixtures can easily simulate the following cases:

### A. Missing or Null Value Fields
GitHub API fields can sometimes be null or missing (e.g. `conclusion` of a running action, or a missing workflow name).
* **Mock Payload**:
  ```python
  mock_github_rest_api.set_runs([
      {
          "id": 9999,
          "name": None,
          "status": None,
          "conclusion": None,
          "html_url": None
      }
  ])
  ```
* **Expected UI Action**: The UI should display `[UNKNOWN] Unnamed Workflow` instead of throwing an `AttributeError` (e.g., trying to run `.upper()` on a `None` status). This is verified by `TestGitHubPanelUI.test_on_result_with_none_status`.

### B. Empty API Responses
When there are no open PRs or Actions runs in the repository.
* **Mock Payload**: `[]` for PRs and `{ "workflow_runs": [] }` for runs.
* **Expected UI Action**: The lists in `GitHubPanel` should render informative fallbacks like "No open PRs" and "No recent runs" rather than remaining blank or causing layout collapse.

### C. Rate Limiting (403 Forbidden) and Network Outages
* **Mock Action**: `mock_github_rest_api.configure_error(403, "rate limit exceeded")`
* **Expected UI Action**: The worker thread emits `error_occurred(str)`. The panel handles this by setting the status text to `"Error fetching data"` and displays the error message in the list widget, remaining responsive without freezing the GUI.

### D. Interrupted Worker Thread (QThread Cancellation)
The `GitHubPanel` uses a `QThread` (`GitHubWorker`) to fetch data asynchronously. If the user clicks "Refresh" repeatedly, or closes the window, the running worker must be cancelled to avoid race conditions and resource leaks.
* **Mock Action**: Simulate slow requests by adding a delay in the mock, and trigger another refresh.
* **Verification**: Verify that the previous worker is disconnected and stopped (`worker.quit(); worker.wait()`) before the new worker starts.

---

## 6. Layout Compliance & Key Constraints

All designed mocking assets adhere strictly to the project rules:
* **Qt6 Native Styling**: The GUI components are styled using Qt6 native fusion styling overrides (e.g. background `#0F1115`, border `#1A2026`).
* **Zero GNOME/GTK Dependencies**: The mocks and tests have zero dependency on Linux keyring interfaces or `gsettings`, relying purely on local environment passing of the Personal Access Token (PAT).
* **Location**: Since we are read-only in this step, this design will be stored in our metadata directory (`.agents/explorer_e2e_infra_2`).
