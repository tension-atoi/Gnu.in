# BRIEFING — 2026-06-17T19:22:12Z

## Mission
Analyze and design the installation script install.sh and the .desktop entry for the cockpit application, complying with native Qt6 and no-GNOME/no-GTK constraints.

## 🔒 My Identity
- Archetype: explorer
- Roles: read-only investigator, analyzer, designer
- Working directory: /home/tension_atoi/Projects/Gnu.in/.agents/explorer_install/
- Original parent: db939a1d-b4f8-4ee7-9cbe-86a213c15124
- Milestone: design_installation

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- NO GNOME OR GTK dependencies or configuration changes (e.g. no gsettings, no GTK_THEME)
- Qt6 Native styling/environment configurations only (e.g. QT_STYLE_OVERRIDE=kvantum, Wayland protocols)
- Only write files within the assigned directory /home/tension_atoi/Projects/Gnu.in/.agents/explorer_install/

## Current Parent
- Conversation ID: db939a1d-b4f8-4ee7-9cbe-86a213c15124
- Updated: not yet

## Investigation State
- **Explored paths**:
  - `gnu.in-cockpit/pyproject.toml`
  - `gnu.in-cockpit/src/cockpit/__main__.py`
  - `gnu.in-cockpit/tests/test_e2e_install.py`
  - `gnu.in-cockpit/tests/test_e2e_launch.py`
  - `gnu.in-syster-app/syster-app/scripts/install-user.sh` (reference)
- **Key findings**:
  - Found that the E2E test asserts existence of `prefix/share/gnuin-cockpit/venv`, `prefix/bin/gnuin-cockpit`, `prefix/share/applications/gnuin-cockpit.desktop`, and `prefix/share/icons/hicolor/scalable/apps/gnuin-cockpit.svg`.
  - The installation script needs robust handling for Python >= 3.10, permission denied check, corrupted states (from terminated script), and read-only pre-existing launcher files.
- **Unexplored areas**: None, the design covers all requirements of the request and E2E tests.

## Key Decisions Made
- Chose to dynamically install the package `gnu.in-cockpit` in the virtualenv using `pip install "$SCRIPT_DIR"` to pull in all dependencies cleanly.
- Added a wrapper binary at `prefix/bin/gnuin-cockpit` that configures the Qt6 Wayland environment and invokes the venv's executable.
- Created a fallback embedded SVG in case the `app-icon.svg` design asset cannot be located on the filesystem.

## Artifact Index
- `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_install/proposed_install.sh` - Proposed installer implementation
- `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_install/proposed_gnuin-cockpit.desktop` - Proposed desktop file template
