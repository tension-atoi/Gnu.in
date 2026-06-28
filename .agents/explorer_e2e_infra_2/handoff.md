# Handoff Report: GitHub Mocking Strategy Design

## 1. Observation
- The current implementation in `src/cockpit/github_client.py` uses `requests.get` to query the GitHub REST API (lines 84 and 122) and `subprocess.check_output` to parse local git configuration (lines 23 and 32).
  * Line 23: `url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], ...)`
  * Line 84: `response = requests.get(url, headers=headers, params=params, timeout=10)`
- The tests in `tests/test_github_api.py` and `tests/test_github_api_stress.py` run and pass successfully:
  * `python3 tests/test_github_api.py` => `Ran 15 tests in 0.004s; OK`
  * `python3 tests/test_github_api_stress.py` => `Ran 15 tests in 2.095s; OK`
- In `tests/test_github_api.py`, mocking is currently done on a per-test basis using `unittest.mock.patch` decorators:
  ```python
  @patch("cockpit.github_client.GitHubClient._get_repo_info")
  @patch("requests.get")
  def test_get_pull_requests_success(self, mock_get, mock_repo_info):
  ```
- The codebase currently lacks a unified test setup (e.g. `conftest.py` with shared pytest fixtures) to handle both `gh` CLI command mocking (via subprocess interception) and REST API call mocking.

---

## 2. Logic Chain
1. **GitHub CLI Mocking**: If the application executes `gh` commands via subprocesses, the test suite must intercept `subprocess.run` and `subprocess.check_output` to avoid invoking the real `gh` command line tool.
2. **Git Subprocess Interdependency**: Because `GitHubClient._get_repo_info` is invoked before any GitHub data retrieval to discover the owner and repository from the git remote URL (lines 67 and 105), a global subprocess mock that intercepts all commands would break git remote parsing. To prevent the client from returning early with an empty list (`[]`), the mock must selectively allow `git` commands (or return mock git output) while mocking `gh` CLI commands.
3. **REST API Client Mocking**: To test requests-based operations (Milestone 2 target), monkeypatching `requests.get` is the cleanest dependency-free approach. The mock response must return a `requests.Response` mock with `.json()` representing the expected raw GitHub REST API response.
4. **Token Verification**: Since Milestone 2 targets personal access tokens (PAT), the REST API mock must verify the request headers (e.g., matching the `Authorization: Bearer <PAT>` header) to ensure token passing works as expected, and simulate unauthorized errors (401/403) to test error handling in the UI.
5. **Dynamic Mock Injection**: To allow tests to define their own data (Focus 3), the fixtures should return a controller object exposing helper methods (like `set_prs()` and `set_runs()`). This decouples test assertions from mock setup and enables testing complex statuses (databaseId, name, status, conclusion, url).

---

## 3. Caveats
- **Read-Only Scoped**: In accordance with instructions, we did not write or modify any source code or test files inside the `gnu.in-cockpit` repository.
- **CLI Commands Assumptions**: We assumed standard `gh` CLI options (e.g., `gh pr list --json number,title,state,author,url`) as the target command schema. If the implemented CLI command arguments change, the subprocess matching string in `conftest.py` must be adjusted accordingly.

---

## 4. Conclusion
We have designed a robust, unified mocking strategy for the `gnu.in-cockpit` project's GitHub integration. It consists of:
1. A selective `subprocess` interceptor fixture (`mock_gh_cli`) that simulates `gh` CLI command stdout while preserving or mocking `git` status checks.
2. A `requests.get` interceptor fixture (`mock_github_rest_api`) that validates PAT headers and returns mock payloads for PRs and Actions runs.
3. A controller pattern that allows tests to inject custom test cases (e.g., in-progress runs, failed workflows, or missing/null fields) to verify the UI's resilience.

The design details and code examples are documented in `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_e2e_infra_2/analysis.md`.

---

## 5. Verification Method
1. **Locate Design Documents**: Inspect `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_e2e_infra_2/analysis.md` to review the proposed code for `conftest.py` and sample test cases.
2. **Execute Current Unit Tests**: Verify that unit tests are fully functional on the local system by running:
   ```bash
   python3 tests/test_github_api.py
   python3 tests/test_github_api_stress.py
   ```
3. **Implement Integration**: Create the `conftest.py` in the `tests/` directory with the proposed fixtures, write a new test file importing `github_client`, and verify that the mocked endpoints are intercepted without hitting the live network.
