# Handoff Report: UI Styling Adaptation (Explorer 1)

This report details the findings and exact mapping of native Qt6 styling parameters from `systertheme.hpp` to the views in `gnu.in-cockpit`: `main_window.py`, `github_panel.py`, and `log_view.py`.

---

## 1. Observation

### Theme Configuration Source
In `/home/tension_atoi/Projects/Gnu.in/gnu.in-syster-app/syster-app/src/systertheme.hpp`:
* Colors:
  ```cpp
  QColor surfaceUnder() const { return QColor("#050606"); }
  QColor mainSurface() const { return QColor("#111516"); }
  QColor elevatedPrimary() const { return QColor("#171b1d"); }
  QColor elevatedSecondary() const { return QColor("#202628"); }
  QColor borderDefault() const { return QColor("#31393b"); }
  QColor borderHeavy() const { return QColor("#465154"); }
  QColor foreground() const { return QColor("#eef4f1"); }
  QColor foregroundSecondary() const { return QColor("#a6b3af"); }
  QColor foregroundTertiary() const { return QColor("#7f8d89"); }
  QColor primary() const { return QColor("#62dba6"); }
  QColor warning() const { return QColor("#e8bc62"); }
  QColor danger() const { return QColor("#ff6f7f"); }
  ```
* Sizing/Dimensions:
  ```cpp
  int toolbarHeight() const { return 46; }
  int toolbarSmallHeight() const { return 36; }
  int textXs() const { return 11; }
  int textSm() const { return 12; }
  int textBase() const { return 14; }
  int textLg() const { return 16; }
  int radiusMd() const { return 6; }
  int radiusLg() const { return 8; }
  int radiusXl() const { return 10; }
  int panelPadding() const { return 12; }
  ```

---

### Hardcoded Styles in Cockpit Views

#### File 1: `src/cockpit/views/main_window.py`
* Hardcoded style sheet (lines 334–344):
  ```python
  def _apply_theme(self) -> None:
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
* Danger button styles (lines 123–127):
  ```python
  if action.danger:
      btn.setStyleSheet(
          "QPushButton{background:#3a1c1c;border:1px solid #E5484D;}"
          "QPushButton:hover{background:#4a2020;}"
      )
  ```
* Documentation browser stylesheet (lines 172–174):
  ```python
  self.doc.setStyleSheet(
      "QTextBrowser{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;padding:10px;}"
  )
  ```
* Hardcoded font-weight styles for section headers (lines 156 and 168):
  ```python
  header.setStyleSheet("font-weight:600;")
  ```

---

#### File 2: `src/cockpit/views/github_panel.py`
* Main container style sheet (lines 35–37):
  ```python
  self.setStyleSheet(
      "QFrame{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;}"
  )
  ```
* Layout margins (line 39):
  ```python
  v.setContentsMargins(10, 10, 10, 10)
  ```
* Header styling (line 42):
  ```python
  header.setStyleSheet("font-weight:600; font-size: 14px; border:none;")
  ```
* Refresh button styling (lines 46–49):
  ```python
  self.refresh_btn.setStyleSheet(
      "QPushButton{background:#1A2026;border:1px solid #2B3037;border-radius:6px;padding:4px;}"
      "QPushButton:hover{background:#222a32;}"
  )
  ```
* Status label styling (line 53):
  ```python
  self.status_label.setStyleSheet("color:#7C828A; border:none;")
  ```
* Section label styling (lines 56 and 61):
  ```python
  v.addWidget(QLabel("Pull Requests", styleSheet="font-weight:600; margin-top:10px; border:none;"))
  v.addWidget(QLabel("Recent Actions", styleSheet="font-weight:600; margin-top:10px; border:none;"))
  ```
* List widget backgrounds (lines 58 and 63):
  ```python
  self.pr_list.setStyleSheet("border:none; background:#0F1115;")
  self.actions_list.setStyleSheet("border:none; background:#0F1115;")
  ```
* Action item success/failure text colors (lines 115–119):
  ```python
  if status == "success":
      item.setForeground(Qt.GlobalColor.green)
  elif status == "failure":
      item.setForeground(Qt.GlobalColor.red)
  ```

---

#### File 3: `src/cockpit/views/log_view.py`
* Monospace Font setup (lines 19–21) and stylesheet (lines 23–25):
  ```python
  f = QFont("JetBrains Mono")
  f.setStyleHint(QFont.Monospace)
  f.setPointSize(10)
  self.setFont(f)
  self.setStyleSheet(
      "QPlainTextEdit{background:#0F1115;color:#D7DCE2;border:1px solid #1A2026;}"
  )
  ```
* Inline text colors roles (lines 7–14):
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

---

## 2. Logic Chain

The objective is to replace the hardcoded values with native variables defined in `systertheme.hpp`. By comparing the semantics and values of the hardcoded properties with the variables in `systertheme.hpp`, we map each element systematically:

1. **Top-Level Surfaces**: 
   * `main_window.py` uses `#15191E` as the default window background. In the theme, this corresponds directly to `mainSurface` (`#111516`).
   * The text colors `#D7DCE2` and `#C7CDD4` correspond to the theme's high-contrast `foreground` (`#eef4f1`).

2. **Sunken/Underlay Panels**: 
   * Side panels, text browsers, and inputs use `#0F1115` to indicate depth. In the theme, this corresponds to `surfaceUnder` (`#050606`).

3. **Interactive Components**:
   * Hover backgrounds (`#222a32`) transition buttons to a lighter shade, which maps to `elevatedSecondary` (`#202628`).
   * Button background (`#1A2026`) maps to `elevatedPrimary` (`#171b1d`).
   * Button border (`#2B3037`) maps to `borderDefault` (`#31393b`).

4. **Borders**:
   * Most views use `#1A2026` for panel borders. In `SysterTheme`, this translates to `borderDefault` (`#31393b`).

5. **Muted Text / Secondary Labels**:
   * Labels like group titles, status text, and log-muted styles use `#A1A6AD` or `#7C828A`. These translate to `foregroundSecondary` (`#a6b3af`) and `foregroundTertiary` (`#7f8d89`) respectively.

6. **Accent / Status Indicators**:
   * Danger buttons use a `#E5484D` border, which maps directly to the theme's `danger` color (`#ff6f7f`).
   * The stdout log statuses (ok/fail/err/cmd) map directly to `primary`, `danger`, and `warning` respectively.
   * `github_panel.py` uses hardcoded `Qt.GlobalColor.green` and `Qt.GlobalColor.red`. These should map to `primary` (`#62dba6`) and `danger` (`#ff6f7f`) for aesthetic cohesion.

7. **Dimensions**:
   * Group boxes use `border-radius: 8px` which matches `radiusLg` (`8`).
   * Buttons and inputs use `border-radius: 6px` or `5px`, which maps to `radiusMd` (`6`).
   * Panel content margins in `github_panel.py` are `10px`, which maps to `panelPadding` (`12`).
   * Log view point size `10` is closest to `textXs` (`11`) or `textSm` (`12`). Standardizing on `textSm` (12px) or `textXs` (11px) aligns it with the rest of the application.

---

## 3. Caveats

* **Disabled/Danger Colors**: `SysterTheme` does not define a separate dark danger background (`#3a1c1c` / `#4a2020`) or a disabled text color (`#555b62`). We suggest defining these inline or as constants relative to the primary theme colors (e.g. keeping them hardcoded locally or mapping them to transparent/darkened variants if desired, though storing them as explicit secondary keys in Python's theme configuration is cleanest).
* **Font-Weights**: Standard font-weights like `font-weight:600` are structural and do not have mapping variables in `systertheme.hpp`, so they should remain hardcoded.
* **Layout Splits**: The QSplitter initial stretch factors and sizes (`[320, 600, 380, 300]`) are specific to the screen real estate of the window layout, and do not belong in the color/font theme.

---

## 4. Conclusion

The adaptation should be performed using a shared theme module to keep view files clean and easily configurable. Below is the proposed mapping schema and implementation code.

### Proposed Code: `src/cockpit/views/theme.py`
Create a new file `src/cockpit/views/theme.py` to act as the single source of truth for UI constants:

```python
# src/cockpit/views/theme.py
"""
Theme configuration for cockpit views.
Extracted and mapped from systertheme.hpp.
"""

from PySide6.QtGui import QColor

# ── Colors (Hex values) ──
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

# ── Dimension Metrics ──
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

# ── View-Specific Custom Variants (Not in systertheme.hpp but required) ──
DANGER_BTN_BG = "#3a1c1c"
DANGER_BTN_BG_HOVER = "#4a2020"

def get_main_stylesheet() -> str:
    """Generates the global stylesheet for the Main Window."""
    return f"""
    QMainWindow, QWidget {{
        background: {MAIN_SURFACE};
        color: {FOREGROUND};
    }}
    QGroupBox {{
        border: 1px solid {BORDER_DEFAULT};
        border-radius: {RADIUS_LG}px;
        margin-top: 8px;
        padding-top: 8px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        color: {FOREGROUND_SECONDARY};
    }}
    QPushButton {{
        background: {ELEVATED_PRIMARY};
        border: 1px solid {BORDER_DEFAULT};
        border-radius: {RADIUS_MD}px;
        padding: 6px;
    }}
    QPushButton:hover {{
        background: {ELEVATED_SECONDARY};
    }}
    QPushButton:disabled {{
        color: {FOREGROUND_TERTIARY};
        border-color: {SURFACE_UNDER};
    }}
    QLineEdit, QComboBox {{
        background: {SURFACE_UNDER};
        border: 1px solid {BORDER_DEFAULT};
        border-radius: {RADIUS_MD}px;
        padding: 4px;
    }}
    QStatusBar {{
        color: {FOREGROUND_SECONDARY};
    }}
    """
```

---

### Mapped View Integrations

Below are the changes required in each file to adopt the `theme` module:

#### 1. Integration for `src/cockpit/views/main_window.py`
```python
from cockpit.views import theme

# Inside _build_action_panel for danger buttons:
if action.danger:
    btn.setStyleSheet(
        f"QPushButton{{background:{theme.DANGER_BTN_BG};border:1px solid {theme.DANGER};}}"
        f"QPushButton:hover{{background:{theme.DANGER_BTN_BG_HOVER};}}"
    )

# Inside _build_doc_panel:
self.doc.setStyleSheet(
    f"QTextBrowser{{background:{theme.SURFACE_UNDER};color:{theme.FOREGROUND};"
    f"border:1px solid {theme.BORDER_DEFAULT};padding:{theme.PANEL_PADDING}px;}}"
)

# Replace _apply_theme with:
def _apply_theme(self) -> None:
    self.setStyleSheet(theme.get_main_stylesheet())
```

#### 2. Integration for `src/cockpit/views/github_panel.py`
```python
from PySide6.QtGui import QColor
from cockpit.views import theme

# Inside __init__:
self.setStyleSheet(
    f"QFrame{{background:{theme.SURFACE_UNDER};color:{theme.FOREGROUND};border:1px solid {theme.BORDER_DEFAULT};}}"
)
v.setContentsMargins(theme.PANEL_PADDING, theme.PANEL_PADDING, theme.PANEL_PADDING, theme.PANEL_PADDING)

header.setStyleSheet(f"font-weight:600; font-size: {theme.TEXT_BASE}px; border:none;")

self.refresh_btn.setStyleSheet(
    f"QPushButton{{background:{theme.ELEVATED_PRIMARY};border:1px solid {theme.BORDER_DEFAULT};"
    f"border-radius:{theme.RADIUS_MD}px;padding:4px;}}"
    f"QPushButton:hover{{background:{theme.ELEVATED_SECONDARY};}}"
)

self.status_label.setStyleSheet(f"color:{theme.FOREGROUND_TERTIARY}; border:none;")

# In labels additions:
v.addWidget(QLabel("Pull Requests", styleSheet=f"font-weight:600; margin-top:{theme.PANEL_PADDING}px; border:none;"))
self.pr_list.setStyleSheet(f"border:none; background:{theme.SURFACE_UNDER};")

v.addWidget(QLabel("Recent Actions", styleSheet=f"font-weight:600; margin-top:{theme.PANEL_PADDING}px; border:none;"))
self.actions_list.setStyleSheet(f"border:none; background:{theme.SURFACE_UNDER};")

# Inside _on_result:
if status == "success":
    item.setForeground(QColor(theme.PRIMARY))
elif status == "failure":
    item.setForeground(QColor(theme.DANGER))
```

#### 3. Integration for `src/cockpit/views/log_view.py`
```python
from cockpit.views import theme

# Replace COLORS:
COLORS = {
    "cmd": theme.WARNING,
    "out": theme.FOREGROUND,
    "err": theme.DANGER,
    "ok": theme.PRIMARY,
    "fail": theme.DANGER,
    "muted": theme.FOREGROUND_TERTIARY,
}

# Inside __init__:
f.setPointSize(theme.TEXT_SM) # 12px or theme.TEXT_XS (11px)
self.setStyleSheet(
    f"QPlainTextEdit{{background:{theme.SURFACE_UNDER};color:{theme.FOREGROUND};border:1px solid {theme.BORDER_DEFAULT};}}"
)
```

---

## 5. Verification Method

To verify these changes after implementation:

1. **Static Analysis/Verification**:
   Check if the theme constants file compiles and can be imported:
   ```bash
   python -c "import cockpit.views.theme; print(cockpit.views.theme.SURFACE_UNDER)"
   ```
2. **Visual Inspection**:
   Run the cockpit app and verify colors look correct without rendering anomalies:
   ```bash
   python -m cockpit
   ```
3. **Automated Unit Tests**:
   Run the test suite to ensure that nothing has broken layout loading:
   ```bash
   pytest gnu.in-cockpit/tests/
   ```
