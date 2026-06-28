# Scope: Implementation Sub-orchestrator

## Architecture
- `gnu.in-cockpit` is a native Qt6 control panel written in Python (using PySide6).
- It currently interfaces with GitHub using a wrapper around the `gh` CLI (`src/cockpit/github_client.py`).
- It has styling defined in `src/cockpit/views/main_window.py` and other views.
- We need to replace the `gh` CLI dependency with native REST API calls using `requests` or `PyGithub` authorized via a Personal Access Token (PAT).
- We need to adapt the styling of the application to match the native Qt6 color scheme and styles defined in `SysterTheme.hpp` (`surfaceUnder`, `mainSurface`, `primary`, etc.).
- We need to create an `install.sh` script to install the application locally and generate a standard `.desktop` file.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | R1: GitHub API Integration | Add PAT input field to settings, rewrite `GitHubClient` to query GitHub REST API using `requests` and token, parse git remote URL for owner/repo, create `tests/test_github_api.py`. | None | DONE (38894c54) |
| 2 | R2: UI Styling Adaptation | Extract styling parameters from `SysterTheme.hpp` and apply them to views (`main_window.py`, `github_panel.py`, etc.) using PySide6 stylesheet syntax. | None | IN_PROGRESS (c9276cb5) |
| 3 | R3: Local Install Script | Create `install.sh` at project root to deploy the application, configure dependencies using user-level python tools, and create standard `.desktop` file. | None | PLANNED |
| 4 | Phase 1: E2E Test Compatibility | Poll for `TEST_READY.md` and verify that the application passes all E2E tests (Tiers 1-4). | M1, M2, M3 | PLANNED |
| 5 | Phase 2: Adversarial Hardening | Run adversarial testing (Tier 5) to verify code correctness, safety, and robustness. | M4 | PLANNED |

## Interface Contracts
### GitHub API Integration
- `GitHubClient.get_pull_requests(cwd)`: Returns list of pull requests matching the schema `[{"number": int, "title": str, "state": str, "author": {"login": str}, "url": str}]`.
- `GitHubClient.get_recent_runs(cwd, limit)`: Returns list of workflow runs matching the schema `[{"databaseId": int, "name": str, "status": str, "conclusion": str, "url": str}]`.
- Configured token stored in `QSettings("gnu-in-labs", "pipeline-cockpit")` under key `"github_token"` (or settings UI input).
