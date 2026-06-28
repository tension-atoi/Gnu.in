# Handoff Report: UI Styling Adaptation (Explorer 2)

## 1. Observation
After reviewing the project files:
- `systertheme.hpp` (`/home/tension_atoi/Projects/Gnu.in/gnu.in-syster-app/syster-app/src/systertheme.hpp`)
- `main_window.py` (`/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/views/main_window.py`)
- `github_panel.py` (`/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/views/github_panel.py`)
- `log_view.py` (`/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/views/log_view.py`)

I have identified the following hardcoded styles currently defined in the views:

### main_window.py Hardcoded Styles
* **Line 124-127 (`_build_action_panel`)**:
  ```python
  if action.danger:
      btn.setStyleSheet(
          "QPushButton{background:#3a1c1c;border:1px solid #E5484D;}"
          "QPushButton:hover{background:#4a2020;}"
      )
  ```
* **Line 172-174 (`_build_doc_panel`)**:
  ```python
  self.doc.setStyleSheet(
      "QTextBrowser{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;padding:10px;}"
  )
  ```
* **Line 334-344 (`_apply_theme`)**:
  ```python
  self.setStyleSheet(
      "QMainWindow,QWidget{background:#15191E;color:#D7DCE2;}"
      "QGroupBox{border:1px solid #1A2026;border-radius:8px;margin-top:8px;padding-top:8px;}"
      "QGroupBox::title{subcontrol-origin:margin;left:10px;color:#A1A6AD;}"
      "QPushButton{background:#1A2026;border:1px solid #2B3037;border-radius:6px;padding:6px;}"
      "QPushButton:hover{background:#222a32;}"
      "QPushButton:disabled{color:#555b62;border-color:#222;}"
      "QLineEdit,QComboBox{background:#0F1115;border:1px solid #2B3037;border-radius:5px;padding:4px;}"
      "QStatusBar{color:#A1A6AD;}"
  )
  ```

### github_panel.py Hardcoded Styles
* **Line 35-37 (`__init__`)**:
  ```python
  self.setStyleSheet(
      "QFrame{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;}"
  )
  ```
* **Line 39 (`__init__`)**:
  ```python
  v.setContentsMargins(10, 10, 10, 10)
  ```
* **Line 42 (`__init__`)**:
  ```python
  header.setStyleSheet("font-weight:600; font-size: 14px; border:none;")
  ```
* **Line 46-49 (`__init__`)**:
  ```python
  self.refresh_btn.setStyleSheet(
      "QPushButton{background:#1A2026;border:1px solid #2B3037;border-radius:6px;padding:4px;}"
      "QPushButton:hover{background:#222a32;}"
  )
  ```
* **Line 53 (`__init__`)**:
  ```python
  self.status_label.setStyleSheet("color:#7C828A; border:none;")
  ```
* **Line 56 (`__init__`)**:
  ```python
  v.addWidget(QLabel("Pull Requests", styleSheet="font-weight:600; margin-top:10px; border:none;"))
  ```
* **Line 58 (`__init__`)**:
  ```python
  self.pr_list.setStyleSheet("border:none; background:#0F1115;")
  ```
* **Line 61 (`__init__`)**:
  ```python
  v.addWidget(QLabel("Recent Actions", styleSheet="font-weight:600; margin-top:10px; border:none;"))
  ```
* **Line 63 (`__init__`)**:
  ```python
  self.actions_list.setStyleSheet("border:none; background:#0F1115;")
  ```
* **Line 116 (`_on_result`)**:
  ```python
  item.setForeground(Qt.GlobalColor.green)
  ```
* **Line 118 (`_on_result`)**:
  ```python
  item.setForeground(Qt.GlobalColor.red)
  ```

### log_view.py Hardcoded Styles
* **Line 7-14 (`COLORS` definition)**:
  ```python
  COLORS = {
      "cmd": "#FF8E40",      # accent — the command header
      "out": "#D7DCE2",      # stdout
      "err": "#E5707A",      # stderr
      "ok": "#8DA982",       # success exit
      "fail": "#E5484D",     # failure exit
      "muted": "#7C828A",
  }
  ```
* **Line 21 (`__init__`)**:
  ```python
  f.setPointSize(10)
  ```
* **Line 23-25 (`__init__`)**:
  ```python
  self.setStyleSheet(
      "QPlainTextEdit{background:#0F1115;color:#D7DCE2;border:1px solid #1A2026;}"
  )
  ```

---

## 2. Logic Chain
We can map each hardcoded visual value to the corresponding native properties in `systertheme.hpp`:

| Category | Hardcoded Value in Cockpit | Closest SysterTheme Property | Value in SysterTheme | Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Window Background** | `#15191E` | `mainSurface` | `#111516` | Main background for the primary views and window. |
| **Inset/Panel Background** | `#0F1115` | `surfaceUnder` | `#050606` | Inset backgrounds like textboxes and listviews need a deeper, inset color. |
| **Text Foreground** | `#D7DCE2`, `#C7CDD4` | `foreground` | `#eef4f1` | Standard primary readable text. |
| **Muted Text** | `#A1A6AD` | `foregroundSecondary` | `#a6b3af` | Secondary/header text. |
| **Highly Muted Text** | `#7C828A` | `foregroundTertiary` | `#7f8d89` | Tertiary/log metadata text. |
| **Button Base Background** | `#1A2026` | `elevatedPrimary` | `#171b1d` | Non-flat controls sitting on top of the main surface. |
| **Button Hover Background** | `#222a32` | `elevatedSecondary` | `#202628` | Hover state background. |
| **Standard Border** | `#1A2026`, `#2B3037` | `borderDefault` | `#31393b` | General outlines and borders. |
| **Large Border Radius** | `8px` | `radiusLg` | `8` | Large container borders (e.g. QGroupBox). |
| **Medium Border Radius** | `5px`, `6px` | `radiusMd` | `6` | Interactive widget corners (buttons/inputs). |
| **Panel Padding** | `10px` | `panelPadding` | `12` | Spacing around margins/padding. |
| **Font Size (Base)** | `14px` | `textBase` | `14` | Title / header font size. |
| **Font Size (Small)** | `10` (points) | `textSm` / `textXs` | `12` / `11` | Monospace log viewport size. `textSm` (12) is the closest. |
| **Success / Clean Exit** | `Qt.GlobalColor.green`, `#8DA982` | `primary` | `#62dba6` | Visual success indicator color. |
| **Failure / Danger** | `Qt.GlobalColor.red`, `#E5484D`, `#E5707A` | `danger` | `#ff6f7f` | Visual failure/cancellation indicators. |
| **Log Command Highlight** | `#FF8E40` | `warning` | `#e8bc62` | Accent color for log header lines. |

---

## 3. Caveats
- No code was modified during this investigation phase.
- Command execution (`run_command` tests) was skipped due to local terminal permission/timeout constraints, but the findings were manually verified directly from the source code.
- Some visual elements (e.g., `#3a1c1c` / `#4a2020` for danger buttons) don't have a direct 1:1 color in SysterTheme. Defining specific contextual extensions (like `DANGER_BUTTON_BG`) inside the Python theme module is recommended to prevent hardcoding.

---

## 4. Conclusion & Recommendations
We recommend a clean **translation strategy** based on a centralized Python theme module.

### Centralized Theme Module: `src/cockpit/views/theme.py`
We should create a shared module that exposes:
1. Hex string constants (for QSS interpolation).
2. `QColor` instances (for native QListWidgetItem foreground operations).
3. Integer dimensions (for font sizes, border-radius, margins).

#### Proposed File Content for `src/cockpit/views/theme.py`:
```python
# src/cockpit/views/theme.py
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

### Proposed Changes to Views

#### 1. `main_window.py`
Replace `_apply_theme` stylesheet with:
```python
    def _apply_theme(self) -> None:
        self.setStyleSheet(
            f"QMainWindow, QWidget {{ background: {MAIN_SURFACE}; color: {FOREGROUND}; }}"
            f"QGroupBox {{ border: 1px solid {BORDER_DEFAULT}; border-radius: {RADIUS_LG}px; margin-top: 8px; padding-top: 8px; }}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 10px; color: {FOREGROUND_SECONDARY}; }}"
            f"QPushButton {{ background: {ELEVATED_PRIMARY}; border: 1px solid {BORDER_DEFAULT}; border-radius: {RADIUS_MD}px; padding: 6px; }}"
            f"QPushButton:hover {{ background: {ELEVATED_SECONDARY}; }}"
            f"QPushButton:disabled {{ color: {FOREGROUND_TERTIARY}; border-color: {BORDER_DEFAULT}; }}"
            f"QLineEdit, QComboBox {{ background: {SURFACE_UNDER}; border: 1px solid {BORDER_DEFAULT}; border-radius: {RADIUS_MD}px; padding: 4px; }}"
            f"QStatusBar {{ color: {FOREGROUND_SECONDARY}; }}"
        )
```

Modify the danger button style in `_build_action_panel`:
```python
                if action.danger:
                    btn.setStyleSheet(
                        f"QPushButton {{ background: {DANGER_BUTTON_BG}; border: 1px solid {DANGER}; }}"
                        f"QPushButton:hover {{ background: {DANGER_BUTTON_HOVER}; }}"
                    )
```

Modify `_build_doc_panel` stylesheet:
```python
        self.doc.setStyleSheet(
            f"QTextBrowser {{ background: {SURFACE_UNDER}; color: {FOREGROUND}; border: 1px solid {BORDER_DEFAULT}; padding: {PANEL_PADDING}px; }}"
        )
```

#### 2. `github_panel.py`
Modify `__init__` layouts and styling:
```python
        self.setStyleSheet(
            f"QFrame {{ background: {SURFACE_UNDER}; color: {FOREGROUND_SECONDARY}; border: 1px solid {BORDER_DEFAULT}; }}"
        )
        v = QVBoxLayout(self)
        v.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)

        header = QLabel("GitHub Status")
        header.setStyleSheet(f"font-weight: 600; font-size: {TEXT_BASE}px; border: none;")
        v.addWidget(header)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet(
            f"QPushButton {{ background: {ELEVATED_PRIMARY}; border: 1px solid {BORDER_DEFAULT}; border-radius: {RADIUS_MD}px; padding: 4px; }}"
            f"QPushButton:hover {{ background: {ELEVATED_SECONDARY}; }}"
        )
        v.addWidget(self.refresh_btn)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {FOREGROUND_TERTIARY}; border: none;")
        v.addWidget(self.status_label)

        v.addWidget(QLabel("Pull Requests", styleSheet=f"font-weight: 600; margin-top: {PANEL_PADDING}px; border: none;"))
        self.pr_list = QListWidget()
        self.pr_list.setStyleSheet(f"border: none; background: {SURFACE_UNDER};")
        v.addWidget(self.pr_list, 1)

        v.addWidget(QLabel("Recent Actions", styleSheet=f"font-weight: 600; margin-top: {PANEL_PADDING}px; border: none;"))
        self.actions_list = QListWidget()
        self.actions_list.setStyleSheet(f"border: none; background: {SURFACE_UNDER};")
        v.addWidget(self.actions_list, 1)
```

Modify the direct item foreground styling in `_on_result`:
```python
            if status == "success":
                item.setForeground(COLOR_PRIMARY)
            elif status == "failure":
                item.setForeground(COLOR_DANGER)
```

#### 3. `log_view.py`
Modify `COLORS` and font initializers:
```python
    COLORS = {
        "cmd": WARNING,        # accent — the command header
        "out": FOREGROUND,     # stdout
        "err": DANGER,         # stderr
        "ok": PRIMARY,         # success exit
        "fail": DANGER,        # failure exit
        "muted": FOREGROUND_TERTIARY,
    }
```

```python
    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
        f = QFont("JetBrains Mono")
        f.setStyleHint(QFont.Monospace)
        f.setPointSize(TEXT_SM)
        self.setFont(f)
        self.setStyleSheet(
            f"QPlainTextEdit {{ background: {SURFACE_UNDER}; color: {FOREGROUND}; border: 1px solid {BORDER_DEFAULT}; }}"
        )
```

---

## 5. Verification Method
1. Create the `theme.py` file with the proposed contents.
2. Apply the proposed QSS and inline adaptations to the three view files.
3. Launch the cockpit application via:
   `python -m cockpit`
4. Confirm that:
   - The main window background matches the `#111516` palette.
   - Text boxes (Doc Panel, Log View, GitHub lists) use `#050606` for background.
   - Borders and border radius adapt smoothly without rendering anomalies.
   - The UI matches the Qt6 Fusion-based SysterTheme specifications.
