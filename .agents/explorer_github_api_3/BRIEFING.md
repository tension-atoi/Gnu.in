# BRIEFING — 2026-06-17T14:37:39Z

## Mission
Investigate codebase to plan replacing the `gh` CLI with native `requests` calls for GitHub REST API, extract owner/repo, add UI token config via QSettings, and outline mock tests.

## 🔒 My Identity
- Archetype: Explorer
- Roles: Read-only investigator, analyzer
- Working directory: /home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_3/
- Original parent: 38894c54-eef8-45e6-a5e2-cf2203765329
- Milestone: GitHub API Integration

## 🔒 Key Constraints
- Read-only investigation — do NOT implement.
- Qt6 native only (no GNOME or GTK, no gsettings, etc.).
- CODE_ONLY network mode (no external network access).
- Write files only in working directory.

## Current Parent
- Conversation ID: 38894c54-eef8-45e6-a5e2-cf2203765329
- Updated: 2026-06-17T14:37:39Z

## Investigation State
- **Explored paths**:
  - `gnu.in-cockpit/src/cockpit/github_client.py`
  - `gnu.in-cockpit/src/cockpit/views/github_panel.py`
  - `gnu.in-cockpit/src/cockpit/views/main_window.py`
  - `gnu.in-cockpit/pyproject.toml`
  - `gnu.in-os/tests/integration/`
  - `.agents/explorer_github_api_2/handoff.md`
- **Key findings**:
  - `gh` CLI commands (`pr list`, `run list`) map to REST endpoints (`GET /repos/{owner}/{repo}/pulls`, `GET /repos/{owner}/{repo}/actions/runs`).
  - GitHub REST API returns `user` instead of `author`, and `html_url` instead of `url` for pulls/runs, which need structure mapping.
  - Local git remote parsing can extract owner/repo name using regex on `remote.origin.url` (or fallback remotes).
  - QLineEdit in `_build_config_row()` can persist the PAT in QSettings under `"github_pat"`.
  - Signal connection for PAT QLineEdit should use `editingFinished` rather than `textChanged` to prevent excessive background thread generation and rate limiting.
- **Unexplored areas**: None (Milestone investigation complete)

## Key Decisions Made
- Use `editingFinished` for the PAT QLineEdit instead of `textChanged`.
- Add fallback logic in `git config` lookup to query `git remote` and check the first available remote if `origin` is missing.

## Artifact Index
- `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_3/BRIEFING.md` — Agent briefing and persistent state
- `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_3/github_client.patch` — Patch for github_client.py
- `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_3/github_panel.patch` — Patch for github_panel.py
- `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_3/main_window.patch` — Patch for main_window.py
- `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_3/pyproject.patch` — Patch for pyproject.toml
- `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_3/proposed_github_client.py` — Rewritten client code
- `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_3/proposed_github_panel.py` — Rewritten panel code
- `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_github_api_3/proposed_test_github_api.py` — Unit tests code
