# BRIEFING — 2026-06-17T14:42:13Z

## Mission
Fix the 4 identified defects in the GitHub API integration (regex, token whitespace handling, QThread crashes, and NoneType status parsing) and verify them using unit tests and stress tests.

## 🔒 My Identity
- Archetype: worker
- Roles: implementer, qa, specialist
- Working directory: /home/tension_atoi/Projects/Gnu.in/.agents/worker_github_api_2/
- Original parent: 38894c54-eef8-45e6-a5e2-cf2203765329
- Milestone: Fix defects identified during verification phase

## 🔒 Key Constraints
- NO GNOME OR GTK: The user's system must remain free of GNOME or GTK dependencies.
- Qt6 Native: The system and application ecosystem relies exclusively on Qt6.

## Current Parent
- Conversation ID: 38894c54-eef8-45e6-a5e2-cf2203765329
- Updated: 2026-06-17T14:46:00Z

## Task Summary
- **What to build**: Fix 4 GitHub API integration defects (Dotted Repository Name regex, Whitespace PAT token handling, QThread concurrency & destruction crash, Status NoneType attribute error).
- **Success criteria**: All defects resolved; unit and stress tests pass with exit code 0.
- **Interface contracts**: src/cockpit/github_client.py, src/cockpit/views/github_panel.py, src/cockpit/views/main_window.py
- **Code layout**: src/cockpit/

## Key Decisions Made
- Anchored regex `r'^(?:https?://github\.com/|git@github\.com:|ssh://git@github\.com/)([^/]+)/([^/]+?)(?:\.git)?\/?$'` to strictly match github.com remote URLs and allow dotted repo names.
- Ensured whitespace PAT tokens are stripped and not added to authorization headers.
- Implemented robust worker thread termination in `refresh()` and `closeEvent()` using `disconnect(receiver)` fallback to handle PySide6's strict `QObject.disconnect` signature.
- Added default parsing fallbacks for missing or None values in workflows.

## Artifact Index
- none

## Change Tracker
- **Files modified**:
  - `gnu.in-cockpit/src/cockpit/github_client.py` — regex pattern fix and token stripping
  - `gnu.in-cockpit/src/cockpit/views/github_panel.py` — thread safety/interruption, token stripping, and fallback parsing
  - `gnu.in-cockpit/src/cockpit/views/main_window.py` — thread cleanup in closeEvent
  - `gnu.in-cockpit/tests/test_github_api_stress.py` — added UI integration tests for QThread cleanup and NoneType status fallbacks
- **Build status**: pass
- **Pending issues**: none

## Quality Status
- **Build/test result**: pass (30 tests in unittest discover, 15 tests in test_github_api_stress.py)
- **Lint status**: clean
- **Tests added/modified**: `TestGitHubPanelUI` inside `test_github_api_stress.py`

## Loaded Skills
- none
