# Scope: Milestone 2 (R2: UI Styling Adaptation)

## Architecture
- Adapt the hardcoded dark colors in `gnu.in-cockpit` views to use the color palette and dimensions defined in `SysterTheme.hpp`.
- Key colors to adapt:
  - `surfaceUnder`: `#050606`
  - `mainSurface`: `#111516`
  - `elevatedPrimary`: `#171b1d`
  - `elevatedSecondary`: `#202628`
  - `borderDefault`: `#31393b`
  - `borderHeavy`: `#465154`
  - `foreground`: `#eef4f1`
  - `foregroundSecondary`: `#a6b3af`
  - `foregroundTertiary`: `#7f8d89`
  - `primary`: `#62dba6`
  - `warning`: `#e8bc62`
  - `danger`: `#ff6f7f`
- Key sizing properties:
  - `panelPadding`: 12
  - `radiusMd`: 6
  - `radiusLg`: 8
  - `radiusXl`: 10
- Files to adapt:
  - `src/cockpit/views/main_window.py`
  - `src/cockpit/views/github_panel.py`
  - `src/cockpit/views/log_view.py`

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Extract and Map Theme | Verify mapping of SysterTheme colors to QSS components in all cockpit views. | None | PLANNED |
| 2 | Apply Stylesheet Overrides | Update `main_window.py`, `github_panel.py`, `log_view.py` with the mapped colors and dimensions. | M1 | PLANNED |
| 3 | Launch Validation | Verify that the application launches without errors via `python -m cockpit`. | M2 | PLANNED |

## Interface Contracts
- The application must not import any QML or C++ code from syster-app directly; instead, the theme parameters are translated into QSS stylesheets and Python constants.
- The UI must remain clean and compile/launch successfully under PySide6.
