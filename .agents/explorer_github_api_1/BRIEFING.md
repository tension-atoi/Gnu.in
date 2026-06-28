# BRIEFING — 2026-06-17T14:37:45Z

## Mission
Investigate the gnu.in-cockpit codebase to replace `gh` CLI usage with native `requests` calls to the GitHub REST API, extract repository details from git remote, allow storing GitHub PAT via QSettings/QLineEdit, and design mock tests.

## 🔒 My Identity
- Archetype: Explorer
- Roles: Read-only investigator, analyzer
- Working directory: /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_1/
- Original parent: 38894c54-eef8-45e6-a5e2-cf2203765329
- Milestone: GitHub API Integration

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- NO GNOME OR GTK (User Preference)
- Qt6 Native (User Preference)

## Current Parent
- Conversation ID: 38894c54-eef8-45e6-a5e2-cf2203765329
- Updated: 2026-06-17T14:37:45Z

## Investigation State
- **Explored paths**:
  - `src/cockpit/github_client.py`
  - `src/cockpit/views/github_panel.py`
  - `src/cockpit/views/main_window.py`
  - `pyproject.toml`
  - `.agents/explorer_github_api_2/handoff.md`
- **Key findings**:
  - `GitHubClient` currently invokes `gh` CLI as subprocess and parses command outputs.
  - UI panels (`github_panel`, `main_window`) do not handle GitHub PAT.
  - `pyproject.toml` needs `requests` added to dependencies.
  - Mock tests can be implemented using standard Python `unittest.mock` patching `requests.get` and `subprocess.run`.
- **Unexplored areas**: None.

## Key Decisions Made
- Reconciled Explorer 2's regex logic by designing a split-based git remote URL parser that strips `.git` and handles dots in repository names cleanly.
- Added `requests` dependency directly in `proposed_pyproject.toml`.
- Masked PAT input field in `main_window.py` using `EchoMode.Password` for security.

## Artifact Index
- /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_1/ORIGINAL_REQUEST.md — Original request containing agent tasks
- /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_1/progress.md — Agent liveness heartbeat
- /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_1/proposed_github_client.py — Proposed updated client
- /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_1/proposed_github_panel.py — Proposed updated panel
- /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_1/proposed_main_window.py — Proposed updated main window
- /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_1/proposed_test_github_api.py — Proposed unit test suite
- /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_1/proposed_pyproject.toml — Proposed pyproject.toml update
- /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_1/handoff.md — Handoff report with findings and logic chain
