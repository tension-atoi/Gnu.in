## 2026-06-17T15:12:30-04:00
You are a worker subagent named worker_theme_4.
Your working directory is /home/tension_atoi/Projects/Gnu.in/.agents/worker_theme_4/.
Your mission is to refactor the UI styling implementation to use the central theme module constants and fix the font size violation in the log view.

Please perform the following refactoring tasks:
1. Import `theme` inside `main_window.py`, `github_panel.py`, and `log_view.py` (from `cockpit.views import theme`). Ensure there are no unused duplicate imports of it inside method bodies.
2. In `main_window.py`:
   - Replace all hardcoded colors, border radii, and sizes in the stylesheet QSS string inside `_apply_theme` with values interpolated from `theme` constants (e.g. using an f-string with `{theme.MAIN_SURFACE}`, `{theme.RADIUS_MD}`, `{theme.PANEL_PADDING}`).
   - Update layout margins inside `__init__()` (line 43) to use `theme.PANEL_PADDING` (e.g. `outer.setContentsMargins(theme.PANEL_PADDING, theme.PANEL_PADDING, theme.PANEL_PADDING, theme.PANEL_PADDING)`).
3. In `github_panel.py`:
   - Update `_on_result()` to use `theme.COLOR_PRIMARY` and `theme.COLOR_DANGER` instead of hardcoded `QColor("#62dba6")` and `QColor("#ff6f7f")`.
   - Update layout margins inside `__init__()` to use `theme.PANEL_PADDING`.
4. In `log_view.py`:
   - Update the `COLORS` dictionary to map to `theme` constants (e.g. `"cmd": theme.WARNING`, `"out": theme.FOREGROUND`, `"err": theme.DANGER`, `"ok": theme.PRIMARY`, `"fail": theme.DANGER`, `"muted": theme.FOREGROUND_TERTIARY`).
   - Update the font point/pixel size settings inside `__init__()`: instead of `f.setPointSize(10)`, set the pixel size using `f.setPixelSize(theme.TEXT_XS)` (which corresponds to 11px, the minimum standard font size in SysterTheme).
5. Verify your changes by running the test suite:
   Run: cd gnu.in-cockpit && .venv/bin/pytest tests/test_e2e_launch.py tests/test_github_api.py
   Ensure all tests pass.
6. Verify that gnu.in-syster-app still compiles if applicable.
7. Document exact changes and test results in handoff.md under /home/tension_atoi/Projects/Gnu.in/.agents/worker_theme_4/handoff.md.

MANDATORY INTEGRITY WARNING: DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
