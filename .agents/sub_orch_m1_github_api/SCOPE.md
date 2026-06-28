# Scope: Milestone 1 (R1: GitHub API Integration)

## Architecture
- Replace the use of the `gh` CLI in `src/cockpit/github_client.py` with native HTTP REST API calls via `requests`.
- Add a settings field (e.g. QLineEdit) in the configuration row of `src/cockpit/views/main_window.py` to enter and persist the GitHub PAT.
- Parse the repository remote URL from local git repository configuration to dynamically determine the owner and repository name.
- Write `tests/test_github_api.py` to mock/test API calls without using `gh` CLI in a subprocess.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | GitHub Client Rest API rewrite | Modify `github_client.py` to use requests and extract owner/repo from git remote. | None | PLANNED |
| 2 | Add PAT input field | Add input and storage for GitHub token in `main_window.py` / `QSettings`. | None | PLANNED |
| 3 | Unit test creation | Add `tests/test_github_api.py` demonstrating successful execution (exit code 0). | M1 | PLANNED |

## Interface Contracts
- `GitHubClient.get_pull_requests(cwd)`: Returns PR list conforming to original format.
- `GitHubClient.get_recent_runs(cwd, limit)`: Returns run list conforming to original format.
