## 2026-06-17T14:38:01Z
You are the Worker for the GitHub API Integration milestone.
Your working directory is /home/tension_atoi/Projects/Gnu.in/.agents/worker_github_api_1/.
Your task is to implement the GitHub API Integration replacing the gh CLI dependency with native REST API calls and adding the PAT config field.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please refer to the following sources for details:
1. Scope document: /home/tension_atoi/Projects/Gnu.in/.agents/sub_orch_m1_github_api/SCOPE.md
2. Global project document: /home/tension_atoi/Projects/Gnu.in/.agents/orchestrator/PROJECT.md
3. Explorer Handoff Reports:
   - /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_2/handoff.md
   - /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_3/handoff.md

Proposed code files / patches:
- Patch/Proposed files in /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_3/:
  - github_client.patch
  - github_panel.patch
  - main_window.patch
  - pyproject.patch
- Proposed file in /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_1/proposed_test_github_api.py (excellent unit tests)

Please follow these exact implementation requirements:
1. Update `pyproject.toml` to add `"requests>=2.28.0"` to dependencies.
2. In `src/cockpit/github_client.py`:
   - Replace the subprocess `gh` CLI implementation with `requests` REST queries.
   - Refactor `is_installed()` to check if `requests` is importable.
   - Implement `_get_repo_info(cwd)` to get `remote.origin.url` using `git config --get remote.origin.url` (handling exceptions and fallback to listing all remotes using `git remote` and getting the first remote's URL). Use regex `r'(?:git@github\.com:|https?://github\.com/|ssh://git@github\.com/)([^/]+)/([^/.]+)(?:\.git)?'` to extract owner and repo.
   - Map pull requests REST API response fields to matching keys: `number`, `title`, `state` (upper-case), `author` (as `{"login": user["login"]}`), `url`.
   - Map action runs response fields to matching keys: `databaseId` (from `id`), `name`, `status`, `conclusion`, `url`.
3. In `src/cockpit/views/main_window.py`:
   - Add a `pat_edit` `QLineEdit` in the config row. Make it a password field (`QLineEdit.EchoMode.Password`) with a placeholder `ghp_...`.
   - Connect its `editingFinished` signal (NOT `textChanged` to avoid network spam) to `_refresh_github`.
   - Read from / persist to `QSettings` key `"github_pat"`.
   - Pass the token value to `github_panel.refresh()`.
4. In `src/cockpit/views/github_panel.py`:
   - Update `refresh` signature to accept a token.
   - Pass the token into the `GitHubWorker` thread, which then queries `get_pull_requests` and `get_recent_runs` with the token.
5. Create `tests/test_github_api.py` (and the `tests/` directory if it does not exist) containing the mock-based unit tests. Integrate the comprehensive test assertions from Explorer 1's `proposed_test_github_api.py`.

Validation and verification:
- Make sure `requests` is installed in the test execution environment.
- Run the unit tests via `python -m unittest tests/test_github_api.py` or similar command from `gnu.in-cockpit/` directory and verify they all pass.
- Write your completion report/handoff to handoff.md in your working directory. Ensure it includes the command run and test results.
- Reply to parent when done.
