## 2026-06-17T14:53:38Z
You are the Worker (archetype: teamwork_preview_worker).
Your working directory is /home/tension_atoi/Projects/Gnu.in/.agents/worker_styling/.
Your parent is Milestone 3 UI Styling Adaptation Sub-orchestrator.
Your task is to implement the UI styling adaptation by applying the native Qt6 colors/dimensions from SysterTheme to the cockpit views.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Detailed Instructions:
1. Initialize your BRIEFING.md and progress.md.
2. Create the file `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/views/theme.py` with the following content:
```python
from PySide6.QtGui import QColor

# --- Colors (QSS Hex Strings) ---
SURFACE_UNDER = "#050606"
MAIN_SURFACE = "#111516"
ELEVATED_PRIMARY = "#171b1d"
ELEVATED_SECONDARY = "#202628"
BORDER_DEFAULT = "#31393b"
BORDER_HEAVY = "#465154"
FOREGROUND = "#eef4f1"
FOREGROUND_SECONDARY = "#a6b3af"
FOREGROUND_TERTIARY = "#7f8d89"
PRIMARY = "#62dba6"
WARNING = "#e8bc62"
DANGER = "#ff6f7f"

# Context-specific custom additions
DANGER_BUTTON_BG = "#3a1c1c"
DANGER_BUTTON_HOVER = "#4a2020"

# --- QColor Objects (for direct widget painting) ---
COLOR_SURFACE_UNDER = QColor(SURFACE_UNDER)
COLOR_MAIN_SURFACE = QColor(MAIN_SURFACE)
COLOR_ELEVATED_PRIMARY = QColor(ELEVATED_PRIMARY)
COLOR_ELEVATED_SECONDARY = QColor(ELEVATED_SECONDARY)
COLOR_BORDER_DEFAULT = QColor(BORDER_DEFAULT)
COLOR_BORDER_HEAVY = QColor(BORDER_HEAVY)
COLOR_FOREGROUND = QColor(FOREGROUND)
COLOR_FOREGROUND_SECONDARY = QColor(FOREGROUND_SECONDARY)
COLOR_FOREGROUND_TERTIARY = QColor(FOREGROUND_TERTIARY)
COLOR_PRIMARY = QColor(PRIMARY)
COLOR_WARNING = QColor(WARNING)
COLOR_DANGER = QColor(DANGER)

# --- Dimensions ---
TOOLBAR_HEIGHT = 46
TOOLBAR_SMALL_HEIGHT = 36
TEXT_XS = 11
TEXT_SM = 12
TEXT_BASE = 14
TEXT_LG = 16
RADIUS_MD = 6
RADIUS_LG = 8
RADIUS_XL = 10
PANEL_PADDING = 12
```

3. Modify `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/views/main_window.py` to import `theme` and use these values:
   - In `_apply_theme(self)`:
     ```python
     def _apply_theme(self) -> None:
         from cockpit.views import theme
         self.setStyleSheet(
             f"QMainWindow, QWidget {{ background: {theme.MAIN_SURFACE}; color: {theme.FOREGROUND}; }}"
             f"QGroupBox {{ border: 1px solid {theme.BORDER_DEFAULT}; border-radius: {theme.RADIUS_LG}px; margin-top: 8px; padding-top: 8px; }}"
             f"QGroupBox::title {{ subcontrol-origin: margin; left: 10px; color: {theme.FOREGROUND_SECONDARY}; }}"
             f"QPushButton {{ background: {theme.ELEVATED_PRIMARY}; border: 1px solid {theme.BORDER_DEFAULT}; border-radius: {theme.RADIUS_MD}px; padding: 6px; }}"
             f"QPushButton:hover {{ background: {theme.ELEVATED_SECONDARY}; }}"
             f"QPushButton:disabled {{ color: {theme.FOREGROUND_TERTIARY}; border-color: {theme.BORDER_DEFAULT}; }}"
             f"QLineEdit, QComboBox {{ background: {theme.SURFACE_UNDER}; border: 1px solid {theme.BORDER_DEFAULT}; border-radius: {theme.RADIUS_MD}px; padding: 4px; }}"
             f"QStatusBar {{ color: {theme.FOREGROUND_SECONDARY}; }}"
         )
     ```
   - In `_build_action_panel` (lines 123-127) for danger button:
     ```python
     from cockpit.views import theme
     if action.danger:
         btn.setStyleSheet(
             f"QPushButton {{ background: {theme.DANGER_BUTTON_BG}; border: 1px solid {theme.DANGER}; }}"
             f"QPushButton:hover {{ background: {theme.DANGER_BUTTON_HOVER}; }}"
         )
     ```
   - In `_build_doc_panel` (lines 172-174) for doc browser:
     ```python
     from cockpit.views import theme
     self.doc.setStyleSheet(
         f"QTextBrowser {{ background: {theme.SURFACE_UNDER}; color: {theme.FOREGROUND}; border: 1px solid {theme.BORDER_DEFAULT}; padding: {theme.PANEL_PADDING}px; }}"
     )
     ```

4. Modify `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/views/github_panel.py` to import `theme` and use these values:
   - In `__init__`:
     - Set stylesheet:
       ```python
       from cockpit.views import theme
       self.setStyleSheet(
           f"QFrame {{ background: {theme.SURFACE_UNDER}; color: {theme.FOREGROUND}; border: 1px solid {theme.BORDER_DEFAULT}; }}"
       )
       ```
     - Set contents margins:
       ```python
       v.setContentsMargins(theme.PANEL_PADDING, theme.PANEL_PADDING, theme.PANEL_PADDING, theme.PANEL_PADDING)
       ```
     - Set header font size:
       ```python
       header.setStyleSheet(f"font-weight: 600; font-size: {theme.TEXT_BASE}px; border: none;")
       ```
     - Set refresh button styling:
       ```python
       self.refresh_btn.setStyleSheet(
           f"QPushButton {{ background: {theme.ELEVATED_PRIMARY}; border: 1px solid {theme.BORDER_DEFAULT}; border-radius: {theme.RADIUS_MD}px; padding: 4px; }}"
           f"QPushButton:hover {{ background: {theme.ELEVATED_SECONDARY}; }}"
       )
       ```
     - Set status label styling:
       ```python
       self.status_label.setStyleSheet(f"color: {theme.FOREGROUND_TERTIARY}; border: none;")
       ```
     - Set QListWidget and labels:
       ```python
       v.addWidget(QLabel("Pull Requests", styleSheet=f"font-weight: 600; margin-top: {theme.PANEL_PADDING}px; border: none;"))
       self.pr_list = QListWidget()
       self.pr_list.setStyleSheet(f"border: none; background: {theme.SURFACE_UNDER};")
       ...
       v.addWidget(QLabel("Recent Actions", styleSheet=f"font-weight: 600; margin-top: {theme.PANEL_PADDING}px; border: none;"))
       self.actions_list = QListWidget()
       self.actions_list.setStyleSheet(f"border: none; background: {theme.SURFACE_UNDER};")
       ```
   - In `_on_result` (around lines 115-119):
     ```python
     from cockpit.views import theme
     if status == "success":
         item.setForeground(theme.COLOR_PRIMARY)
     elif status == "failure":
         item.setForeground(theme.COLOR_DANGER)
     ```

5. Modify `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/views/log_view.py` to import `theme` and use these values:
   - In `COLORS` dictionary:
     ```python
     from cockpit.views import theme
     COLORS = {
         "cmd": theme.WARNING,        # accent — the command header
         "out": theme.FOREGROUND,     # stdout
         "err": theme.DANGER,         # stderr
         "ok": theme.PRIMARY,         # success exit
         "fail": theme.DANGER,        # failure exit
         "muted": theme.FOREGROUND_TERTIARY,
     }
     ```
   - In `__init__`:
     ```python
     f.setPointSize(theme.TEXT_SM)
     self.setFont(f)
     self.setStyleSheet(
         f"QPlainTextEdit {{ background: {theme.SURFACE_UNDER}; color: {theme.FOREGROUND}; border: 1px solid {theme.BORDER_DEFAULT}; }}"
     )
     ```

6. Verify that the cockpit application compiles and runs. You can run python -m cockpit or python -c "import cockpit.views.main_window" or similar check inside gnu.in-cockpit dir. Also run the test suite (e.g. pytest tests/ or python -m unittest).
7. Write your handoff.md in your working directory summarizing:
   - Files created / edited.
   - Verification commands run and their output.
   - Attest that all requirements are met and no errors occur.
