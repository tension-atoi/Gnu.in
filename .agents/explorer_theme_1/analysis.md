# UI Styling Adaptation Analysis & Design Proposal

This document presents the styling investigation for `gnu.in-cockpit` and details a unified Qt6 stylesheet design mapping the variables from `gnu.in-syster-app/syster-app/src/systertheme.hpp`.

## 1. Current Styling Analysis in gnu.in-cockpit

The cockpit frontend (`gnu.in-cockpit`) currently uses custom stylesheets specified directly inside views, creating inconsistent overrides and visual fragmentation.

- **`main_window.py`**:
  - Implements `_apply_theme` with basic background (`#15191E`), border (`#1A2026`, `#2B3037`), and button backgrounds (`#1A2026`).
  - Sets inline styling for danger actions (`#3a1c1c` background, `#E5484D` border).
  - Sets inline styling for the QTextBrowser documentation panel (`#0F1115` background, `#C7CDD4` foreground).
- **`github_panel.py`**:
  - Sets inline background on the main QFrame (`#0F1115`) and list widgets.
  - Styles headers and buttons manually.
  - Colors success list-items with `Qt.GlobalColor.green` and failure list-items with `Qt.GlobalColor.red`.
- **`log_view.py`**:
  - Hardcodes a dictionary of log role colors: `cmd` (`#FF8E40`), `out` (`#D7DCE2`), `err` (`#E5707A`), `ok` (`#8DA982`), `fail` (`#E5484D`), and `muted` (`#7C828A`).
  - Statically applies background `#0F1115` and border `#1A2026` via inline `setStyleSheet`.

---

## 2. Syster Theme Specification

The source of truth theme parameters from `systertheme.hpp` are:

### Colors
| Name | Hex Value | Intended Usage |
| :--- | :--- | :--- |
| `surfaceUnder` | `#050606` | Deepest background layer for recessed panels (input views, log consoles, list widgets). |
| `mainSurface` | `#111516` | Base surface color for windows and main container backdrops. |
| `elevatedPrimary` | `#171b1d` | Card structures, panels, group boxes, and default buttons. |
| `elevatedSecondary`| `#202628` | Hover or focus states for buttons and other interactive components. |
| `borderDefault` | `#31393b` | General-purpose subtle borders. |
| `borderHeavy` | `#465154` | Contrasting/active state borders and dividers. |
| `foreground` | `#eef4f1` | High-contrast main body text. |
| `foregroundSecondary`| `#a6b3af` | Mid-contrast text (subheadings, metadata, group box titles). |
| `foregroundTertiary` | `#7f8d89` | Muted annotations, placeholders, and disabled states. |
| `primary` | `#62dba6` | Accent color, highlights, success indicators, and main call-to-actions. |
| `warning` | `#e8bc62` | Warn/attention states. |
| `danger` | `#ff6f7f` | Errors, dangerous actions, and critical notifications. |

### Metrics
- **Font Sizes**: `textXs` (11 px), `textSm` (12 px), `textBase` (14 px), `textLg` (16 px)
- **Radii**: `radiusMd` (6 px), `radiusLg` (8 px), `radiusXl` (10 px)
- **Dimensions**: `toolbarHeight` (46 px), `toolbarSmallHeight` (36 px), `panelPadding` (12 px)

---

## 3. Unified Qt6 Stylesheet (QSS) Design

To ensure native styling alignment and visual harmony across all views, we design the following unified stylesheet to be set globally via `QMainWindow.setStyleSheet` in `main_window.py`.

```css
/* Base styling for Main Window and Widgets */
QMainWindow, QWidget {
    background-color: #111516; /* mainSurface */
    color: #eef4f1; /* foreground */
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 14px; /* textBase */
}

/* Config row inputs (QLineEdit, QComboBox) */
QLineEdit, QComboBox {
    background-color: #050606; /* surfaceUnder */
    color: #eef4f1; /* foreground */
    border: 1px solid #31393b; /* borderDefault */
    border-radius: 6px; /* radiusMd */
    padding: 4px 8px;
    font-size: 12px; /* textSm */
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #62dba6; /* primary */
}

/* Checkboxes */
QCheckBox {
    color: #a6b3af; /* foregroundSecondary */
    font-size: 12px; /* textSm */
    spacing: 6px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #31393b; /* borderDefault */
    border-radius: 4px;
    background-color: #050606; /* surfaceUnder */
}

QCheckBox::indicator:checked {
    background-color: #62dba6; /* primary */
    border-color: #62dba6;
}

/* Group Boxes (Commit Message & Action Panels) */
QGroupBox {
    border: 1px solid #31393b; /* borderDefault */
    border-radius: 8px; /* radiusLg */
    margin-top: 12px; /* panelPadding */
    padding-top: 12px; /* panelPadding */
    font-weight: 600;
    font-size: 12px; /* textSm */
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px; /* panelPadding */
    color: #a6b3af; /* foregroundSecondary */
    padding: 0 4px;
}

/* Buttons (QPushButtons) */
QPushButton {
    background-color: #171b1d; /* elevatedPrimary */
    color: #eef4f1; /* foreground */
    border: 1px solid #31393b; /* borderDefault */
    border-radius: 6px; /* radiusMd */
    padding: 6px 12px;
    font-size: 12px; /* textSm */
    font-weight: 500;
}

QPushButton:hover {
    background-color: #202628; /* elevatedSecondary */
    border-color: #465154; /* borderHeavy */
}

QPushButton:pressed {
    background-color: #111516; /* mainSurface */
}

QPushButton:disabled {
    color: #7f8d89; /* foregroundTertiary */
    border-color: #31393b; /* borderDefault */
    background-color: #111516; /* mainSurface */
}

/* Specific button styles (Danger) using QSS property selector */
QPushButton[danger="true"] {
    background-color: #2e1619; /* ~18% opacity of danger #ff6f7f on mainSurface */
    border: 1px solid #ff6f7f; /* danger */
    color: #ff6f7f; /* danger */
}

QPushButton[danger="true"]:hover {
    background-color: #3f1a1e;
    border-color: #ff6f7f;
}

/* Status Bar */
QStatusBar {
    color: #a6b3af; /* foregroundSecondary */
    font-size: 11px; /* textXs */
    background-color: #050606; /* surfaceUnder */
    border-top: 1px solid #31393b; /* borderDefault */
}

/* Log View & QTextBrowser panels */
QPlainTextEdit, QTextBrowser, QListWidget {
    background-color: #050606; /* surfaceUnder */
    color: #eef4f1; /* foreground */
    border: 1px solid #31393b; /* borderDefault */
    border-radius: 8px; /* radiusLg */
    padding: 12px; /* panelPadding */
}

QListWidget {
    border: none;
    padding: 0px;
}

QListWidget::item {
    color: #eef4f1; /* foreground */
    padding: 6px;
    border-radius: 4px;
}

QListWidget::item:hover {
    background-color: #171b1d; /* elevatedPrimary */
}

QListWidget::item:selected {
    background-color: #202628; /* elevatedSecondary */
    color: #62dba6; /* primary */
}
```

---

## 4. Specific Code Modifications Recommended

To successfully apply the unified style, the following changes are required in the cockpit files:

### A. `main_window.py`
1. Replace `_apply_theme()` body with the unified stylesheet above.
2. In `_build_action_panel()`, remove the inline styling for danger actions and replace it with a dynamic property:
   - Before:
     ```python
     if action.danger:
         btn.setStyleSheet(
             "QPushButton{background:#3a1c1c;border:1px solid #E5484D;}"
             "QPushButton:hover{background:#4a2020;}"
         )
     ```
   - After:
     ```python
     if action.danger:
         btn.setProperty("danger", True)
     ```
3. In `_build_doc_panel()`, remove the inline stylesheet definition on `self.doc`.

### B. `github_panel.py`
1. Remove the QFrame inline background stylesheet under `__init__`.
2. Remove the inline stylesheets from the PR and Actions list objects (`self.pr_list` and `self.actions_list`).
3. Set label elements to explicitly target `#eef4f1` (`foreground`) and `#a6b3af` (`foregroundSecondary`) where appropriate.
4. Import `QColor` from `PySide6.QtGui` and map list-item color states in `_on_result()`:
   - Before:
     ```python
     if status == "success":
         item.setForeground(Qt.GlobalColor.green)
     elif status == "failure":
         item.setForeground(Qt.GlobalColor.red)
     ```
   - After:
     ```python
     if status == "success":
         item.setForeground(QColor("#62dba6")) # primary
     elif status == "failure":
         item.setForeground(QColor("#ff6f7f")) # danger
     ```

### C. `log_view.py`
1. Remap the `COLORS` registry values to use Syster Theme hex values:
   - `cmd`: `#62dba6` (primary)
   - `out`: `#eef4f1` (foreground)
   - `err`: `#ff6f7f` (danger)
   - `ok`: `#62dba6` (primary/success)
   - `fail`: `#ff6f7f` (danger)
   - `muted`: `#7f8d89` (foregroundTertiary)
2. Remove the inline QPlainTextEdit style in `__init__` (letting it inherit background and border properties from the main window's stylesheet, while keeping custom padding or border-radius settings if necessary).

---

## 5. Verification Commands

### Cockpit Tests
Verify that python tests pass:
```bash
cd gnu.in-cockpit
uv run pytest tests/test_e2e_launch.py tests/test_github_api.py tests/test_github_api_stress.py
```

### Syster App Build
Verify that the C++ syster-app builds correctly:
```bash
cd gnu.in-syster-app/syster-app
cmake --build build
```
