# Project: gnu.in-cockpit

## Architecture
- `gnu.in-cockpit`: a local control panel using Qt6 (PySide6) for managing pipelines and repos.
- Main Window (`src/cockpit/views/main_window.py`) houses log view, documentation, settings, and GitHub status.
- GitHub Client (`src/cockpit/github_client.py`) previously executed subprocess calls to the `gh` CLI. It will be refactored to use native REST API requests.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | E2E Testing Suite | Create a robust E2E test suite covering cockpit features, mock GitHub API, and install validation. | None | DONE |
| 2 | GitHub API Integration | Refactor `GitHubClient` to query GitHub REST API with requests/PAT; add mock test scripts. | None | DONE |
| 3 | UI/Theme Adaptation | Adapt native Qt6 styling/colors from `SysterTheme.hpp` (e.g. main surface, primary colors) to cockpit stylesheet. | None | DONE |
| 4 | Local installation script | Create `install.sh` to package and set up the desktop file and python dependencies. | None | DONE |
| 5 | E2E Validation & Hardening | Run the E2E test suite, fix defects, and perform adversarial coverage testing (Tier 5). | M1, M2, M3, M4 | DONE |

## Code Layout
- `src/cockpit/github_client.py` - GitHub API REST transition.
- `src/cockpit/views/main_window.py` - Main window layout & styling integration.
- `src/cockpit/views/github_panel.py` - Panel for PRs & actions.
- `tests/test_github_api.py` - GitHub client mock test.
- `install.sh` - Local deployment packaging.

## Interface Contracts
- `GitHubClient` ↔ `GitHubPanel`
  - `get_pull_requests(cwd: str) -> list[dict]`
  - `get_recent_runs(cwd: str, limit: int) -> list[dict]`
  - Standardized output keys: `number`, `title`, `state`, `author` (`{"login": ...}`), `url` for PRs; and `databaseId`, `name`, `status`, `conclusion`, `url` for runs.
