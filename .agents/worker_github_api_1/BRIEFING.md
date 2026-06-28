# BRIEFING — 2026-06-17T10:38:00-04:00

## Mission
Implement GitHub API Integration replacing the gh CLI dependency with native REST API calls and adding the PAT config field.

## 🔒 My Identity
- Archetype: worker
- Roles: implementer, qa, specialist
- Working directory: /home/tension_atoi/Projects/Gnu.in/.agents/worker_github_api_1/
- Original parent: 38894c54-eef8-45e6-a5e2-cf2203765329
- Milestone: GitHub API Integration

## 🔒 Key Constraints
- NO GNOME OR GTK: Never configure system themes or inject GTK_THEME.
- Qt6 Native: Use native Qt methods (e.g. QSettings, QLineEdit, QLineEdit.EchoMode.Password).

## Current Parent
- Conversation ID: 38894c54-eef8-45e6-a5e2-cf2203765329
- Updated: not yet

## Task Summary
- **What to build**: Replace `gh` CLI subprocess logic in `github_client.py` with `requests` library calls. Add a PAT field (password mode QLineEdit) in `main_window.py`, persist via QSettings, pass to `github_panel.py`, and use in REST calls. Write unit tests to verify.
- **Success criteria**: All tests pass. `requests` dependency added. Native Qt implementation. No `gh` CLI dependency.
- **Interface contracts**: /home/tension_atoi/Projects/Gnu.in/.agents/sub_orch_m1_github_api/SCOPE.md
- **Code layout**: /home/tension_atoi/Projects/Gnu.in/.agents/orchestrator/PROJECT.md

## Key Decisions Made
- Use native Qt6 APIs and requests module.

## Artifact Index
- None yet

## Change Tracker
- **Files modified**:
  - `gnu.in-cockpit/pyproject.toml` — Add requests as dependency
  - `gnu.in-cockpit/src/cockpit/github_client.py` — REST client rewrite using requests and regex remote url parsing
  - `gnu.in-cockpit/src/cockpit/views/github_panel.py` — Pass token to client and worker
  - `gnu.in-cockpit/src/cockpit/views/main_window.py` — Add GitHub PAT config input line edit with EchoMode.Password, save to QSettings, trigger refresh on editingFinished
  - `gnu.in-cockpit/tests/test_github_api.py` — Comprehensive mock-based unit tests
- **Build status**: pass
- **Pending issues**: None

## Quality Status
- **Build/test result**: pass (11 tests ran and completed successfully)
- **Lint status**: none (no linter in test environment)
- **Tests added/modified**: 11 new tests in `tests/test_github_api.py` covering all client REST mapping logic and git remote fallback queries

## Loaded Skills
- None
