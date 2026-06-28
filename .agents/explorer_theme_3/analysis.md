# UI Styling Adaptation Analysis & Design

## Executive Summary
This document defines the unified styling adaptation for the `gnu.in-cockpit` application views to match the visual design system defined in `gnu.in-syster-app/syster-app/src/systertheme.hpp`. 

To achieve this, we map all 12 core colors and 10 layout/font metrics from `SysterTheme` to Qt6 Style Sheets (QSS) and coordinate view-level code changes. Inline stylesheets across the cockpit views are consolidated into a single centralized stylesheet, resolving style-leak issues and standardizing component behaviors.

---

## 1. Theme Reference (From `systertheme.hpp`)

### 1.1 Color Palette
The C++ theme defines the following colors (converted here to QSS hex values):

| SysterTheme Color | Hex Code | Purpose in Design |
| :--- | :--- | :--- |
| `surfaceUnder` | `#050606` | Deepest background layer for input views and text fields. |
| `mainSurface` | `#111516` | Main window, parent containers, and status bar background. |
| `elevatedPrimary` | `#171b1d` | Normal interactive widgets (buttons) and dropdown menu backgrounds. |
| `elevatedSecondary` | `#202628` | Hover/active states of widgets, scrollbar handles, and item selection. |
| `borderDefault` | `#31393b` | Default border for inputs, buttons, panels, and group boxes. |
| `borderHeavy` | `#465154` | Enhanced borders for hovered buttons, focused inputs, and headers. |
| `foreground` | `#eef4f1` | Main text color for readability and clarity. |
| `foregroundSecondary` | `#a6b3af` | Secondary label text, group box headers, and status messages. |
| `foregroundTertiary` | `#7f8d89` | Muted descriptions, disabled states, and placeholder text. |
| `primary` | `#62dba6` | Accent color (mint green) for success status, checkmarks, active focus, and ok logs. |
| `warning` | `#e8bc62` | Yellow-orange color for warnings and command executions. |
| `danger` | `#ff6f7f` | Red/pink color for errors, failures, and destructive actions. |

### 1.2 Layout & Font Metrics
The C++ theme defines the following metrics:

| Metric | Value | QSS Mapping | Purpose |
| :--- | :--- | :--- | :--- |
| `toolbarHeight` | `46` | `height: 46px;` | Height of main toolbar components. |
| `toolbarSmallHeight`| `36` | `height: 36px;` | Height of compact toolbars/buttons. |
| `textXs` | `11` | `font-size: 11px;` | Extra-small helper labels, status text, and tooltips. |
| `textSm` | `12` | `font-size: 12px;` | Default size for buttons, checkbox labels, and input fields. |
| `textBase` | `14` | `font-size: 14px;` | Standard headers, panel titles, and group box titles. |
| `textLg` | `16` | `font-size: 16px;` | Large section headers. |
| `radiusMd` | `6` | `border-radius: 6px;`| Corner radius for buttons, line edits, and combo boxes. |
| `radiusLg` | `8` | `border-radius: 8px;`| Corner radius for panels, list widgets, and group boxes. |
| `radiusXl` | `10` | `border-radius: 10px;`| Extra-large container styling. |
| `panelPadding` | `12` | `padding: 12px;` | Layout padding and container margins. |

---

## 2. Unified Qt6 Stylesheet (QSS)

This stylesheet is designed to be applied globally at the `QApplication` level or on the `QMainWindow` to ensure consistent dark-mode styling across all views:

```css
/* --- Base Application Structure --- */
QMainWindow {
    background-color: #111516; /* mainSurface */
    color: #eef4f1; /* foreground */
}

QWidget#centralWidget {
    background-color: #111516; /* mainSurface */
}

/* --- Splitter Handles --- */
QSplitter::handle {
    background-color: #31393b; /* borderDefault */
}
QSplitter::handle:horizontal {
    width: 4px;
}
QSplitter::handle:vertical {
    height: 4px;
}

/* --- Common Text Elements --- */
QLabel {
    color: #eef4f1; /* foreground */
    font-size: 12px; /* textSm */
}

QLabel#panelHeader {
    font-weight: 600;
    font-size: 14px; /* textBase */
    color: #eef4f1; /* foreground */
    border: none;
}

QLabel#subHeader {
    font-weight: 600;
    font-size: 12px; /* textSm */
    color: #a6b3af; /* foregroundSecondary */
    border: none;
}

/* --- Push Buttons --- */
QPushButton {
    background-color: #171b1d; /* elevatedPrimary */
    border: 1px solid #31393b; /* borderDefault */
    border-radius: 6px; /* radiusMd */
    color: #eef4f1; /* foreground */
    font-size: 12px; /* textSm */
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: #202628; /* elevatedSecondary */
    border-color: #465154; /* borderHeavy */
}

QPushButton:pressed {
    background-color: #050606; /* surfaceUnder */
}

QPushButton:disabled {
    background-color: #111516; /* mainSurface */
    color: #7f8d89; /* foregroundTertiary */
    border-color: #202628; /* elevatedSecondary */
}

/* Danger / Destructive Action Button (using dynamic property 'danger') */
QPushButton[danger="true"] {
    background-color: #3a1c1c; /* Dark red background for contrast */
    border: 1px solid #ff6f7f; /* danger */
    color: #ff6f7f; /* danger */
}

QPushButton[danger="true"]:hover {
    background-color: #4a2020;
    border-color: #ff6f7f;
}

QPushButton[danger="true"]:pressed {
    background-color: #2a1010;
}

/* Compact specific button overrides */
QPushButton#githubRefreshBtn {
    padding: 4px 10px;
}

/* --- Input Elements --- */
QLineEdit, QComboBox {
    background-color: #050606; /* surfaceUnder */
    border: 1px solid #31393b; /* borderDefault */
    border-radius: 6px; /* radiusMd */
    padding: 4px 8px;
    color: #eef4f1; /* foreground */
    font-size: 12px; /* textSm */
}

QLineEdit:focus, QComboBox:focus {
    border-color: #62dba6; /* primary */
}

QLineEdit::placeholder {
    color: #7f8d89; /* foregroundTertiary */
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 18px;
    border-left: 1px solid #31393b; /* borderDefault */
}

QComboBox QAbstractItemView {
    background-color: #171b1d; /* elevatedPrimary */
    border: 1px solid #31393b; /* borderDefault */
    color: #eef4f1; /* foreground */
    selection-background-color: #202628; /* elevatedSecondary */
    selection-color: #62dba6; /* primary */
}

/* --- CheckBoxes --- */
QCheckBox {
    color: #eef4f1; /* foreground */
    font-size: 12px; /* textSm */
    spacing: 6px;
}

/* --- Group Boxes --- */
QGroupBox {
    border: 1px solid #31393b; /* borderDefault */
    border-radius: 8px; /* radiusLg */
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 600;
    font-size: 12px; /* textSm */
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #a6b3af; /* foregroundSecondary */
}

/* --- Status Bar --- */
QStatusBar {
    background-color: #111516; /* mainSurface */
    color: #a6b3af; /* foregroundSecondary */
    border-top: 1px solid #31393b; /* borderDefault */
    font-size: 11px; /* textXs */
}

/* --- Scrollable Text Panels & List Views --- */
LogView, QTextBrowser {
    background-color: #050606; /* surfaceUnder */
    border: 1px solid #31393b; /* borderDefault */
    border-radius: 8px; /* radiusLg */
    color: #eef4f1; /* foreground */
    padding: 12px; /* panelPadding */
}

QListWidget {
    background-color: #050606; /* surfaceUnder */
    border: 1px solid #31393b; /* borderDefault */
    border-radius: 8px; /* radiusLg */
    color: #eef4f1; /* foreground */
    font-size: 12px; /* textSm */
}

QListWidget::item {
    padding: 6px 8px;
    border-bottom: 1px solid #171b1d; /* elevatedPrimary separator */
}

QListWidget::item:hover {
    background-color: #171b1d; /* elevatedPrimary */
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #202628; /* elevatedSecondary */
    color: #62dba6; /* primary */
    border-radius: 4px;
}

/* --- Scrollbars --- */
QScrollBar:vertical {
    background-color: #050606; /* surfaceUnder */
    width: 12px;
    margin: 0px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #202628; /* elevatedSecondary */
    min-height: 20px;
    border-radius: 4px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover {
    background-color: #31393b; /* borderDefault */
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: none;
    border: none;
}

QScrollBar:horizontal {
    background-color: #050606; /* surfaceUnder */
    height: 12px;
    margin: 0px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #202628; /* elevatedSecondary */
    min-width: 20px;
    border-radius: 4px;
    margin: 2px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #31393b; /* borderDefault */
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    background: none;
    border: none;
}
```

---

## 3. View-Specific Implementation Guide

To implement the unified stylesheet, code changes should be made to clean up inline styles and configure naming/properties correctly.

### 3.1 `gnu.in-cockpit/src/cockpit/views/main_window.py`

#### A. Centralize Stylesheet Application
* **What to change**: Replace the hardcoded CSS string in the `_apply_theme` method.
* **Why**: To apply the complete, unified QSS stylesheet.
* **Code Modification**:
  ```python
  # Before
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

  # After
  def _apply_theme(self) -> None:
      # centralized QSS style string matching SysterTheme
      style_qss = """
      [Insert Centralized Stylesheet QSS from Section 2]
      """
      self.setStyleSheet(style_qss)
  ```

#### B. Dynamic Property for Danger Buttons
* **What to change**: Replace the local button stylesheet overrides with a dynamic property.
* **Why**: Consolidates layout code and leaves all coloring to the QSS engine.
* **Code Modification**:
  ```python
  # Before (line 123)
  if action.danger:
      btn.setStyleSheet(
          "QPushButton{background:#3a1c1c;border:1px solid #E5484D;}"
          "QPushButton:hover{background:#4a2020;}"
      )

  # After
  if action.danger:
      btn.setProperty("danger", True)
  ```

#### C. Layout Margins and Widget ID Assignments
* **What to change**: Assign Object Names to key widgets so they are targeted explicitly by the stylesheet without leaking styles to sub-widgets, and update margins.
* **Code Modification**:
  ```python
  # Before (line 39)
  root = QWidget()
  self.setCentralWidget(root)
  outer = QVBoxLayout(root)
  
  # After
  root = QWidget()
  root.setObjectName("centralWidget")
  self.setCentralWidget(root)
  outer = QVBoxLayout(root)
  outer.setContentsMargins(12, 12, 12, 12) # panelPadding (12px)
  ```
  And for doc browser (line 167):
  ```python
  # Before
  header = QLabel("What does this do?")
  header.setStyleSheet("font-weight:600;")
  v.addWidget(header)
  self.doc = QTextBrowser()
  self.doc.setOpenExternalLinks(False)
  self.doc.setStyleSheet(
      "QTextBrowser{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;padding:10px;}"
  )
  
  # After
  header = QLabel("What does this do?")
  header.setObjectName("panelHeader")
  v.addWidget(header)
  self.doc = QTextBrowser()
  self.doc.setOpenExternalLinks(False)
  # Inline stylesheet removed completely (styled via global QSS)
  ```

---

### 3.2 `gnu.in-cockpit/src/cockpit/views/github_panel.py`

#### A. Consolidate Panel Styling and Margins
* **What to change**: Remove local stylesheets on the `GitHubPanel` instance and assign Object Names to the elements.
* **Why**: To prevent style leaks from `QFrame{...}` selectors affecting other child QFrame structures and to utilize standard padding (12px).
* **Code Modification**:
  ```python
  # Before (line 32)
  def __init__(self, parent=None) -> None:
      super().__init__(parent)
      self.setMinimumWidth(320)
      self.setStyleSheet(
          "QFrame{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;}"
      )
      v = QVBoxLayout(self)
      v.setContentsMargins(10, 10, 10, 10)

      header = QLabel("GitHub Status")
      header.setStyleSheet("font-weight:600; font-size: 14px; border:none;")
      v.addWidget(header)

      self.refresh_btn = QPushButton("Refresh")
      self.refresh_btn.setStyleSheet(
          "QPushButton{background:#1A2026;border:1px solid #2B3037;border-radius:6px;padding:4px;}"
          "QPushButton:hover{background:#222a32;}"
      )
      v.addWidget(self.refresh_btn)

      self.status_label = QLabel("Ready")
      self.status_label.setStyleSheet("color:#7C828A; border:none;")
      v.addWidget(self.status_label)

      v.addWidget(QLabel("Pull Requests", styleSheet="font-weight:600; margin-top:10px; border:none;"))
      self.pr_list = QListWidget()
      self.pr_list.setStyleSheet("border:none; background:#0F1115;")
      v.addWidget(self.pr_list, 1)

      v.addWidget(QLabel("Recent Actions", styleSheet="font-weight:600; margin-top:10px; border:none;"))
      self.actions_list = QListWidget()
      self.actions_list.setStyleSheet("border:none; background:#0F1115;")
      v.addWidget(self.actions_list, 1)

  # After
  def __init__(self, parent=None) -> None:
      super().__init__(parent)
      self.setObjectName("GitHubPanel")
      self.setMinimumWidth(320)
      # No inline stylesheet on QFrame to avoid style leak
      
      v = QVBoxLayout(self)
      v.setContentsMargins(12, 12, 12, 12) # panelPadding (12px)

      header = QLabel("GitHub Status")
      header.setObjectName("panelHeader")
      v.addWidget(header)

      self.refresh_btn = QPushButton("Refresh")
      self.refresh_btn.setObjectName("githubRefreshBtn") # Inline styles removed
      v.addWidget(self.refresh_btn)

      self.status_label = QLabel("Ready")
      self.status_label.setObjectName("githubStatusLabel") # Inline styles removed
      v.addWidget(self.status_label)

      pr_header = QLabel("Pull Requests")
      pr_header.setObjectName("subHeader")
      v.addWidget(pr_header)
      
      self.pr_list = QListWidget()
      self.pr_list.setObjectName("githubPrList") # Inline styles removed
      v.addWidget(self.pr_list, 1)

      actions_header = QLabel("Recent Actions")
      actions_header.setObjectName("subHeader")
      v.addWidget(actions_header)
      
      self.actions_list = QListWidget()
      self.actions_list.setObjectName("githubActionsList") # Inline styles removed
      v.addWidget(self.actions_list, 1)
  ```

#### B. Update Theme Colors for List Items
* **What to change**: Replace global green/red colors with the new theme colors in Python code.
* **Why**: Unifies the palette for action runs with the `primary` and `danger` hex codes.
* **Code Modification**:
  ```python
  # Before (line 115)
  if status == "success":
      item.setForeground(Qt.GlobalColor.green)
  elif status == "failure":
      item.setForeground(Qt.GlobalColor.red)

  # After
  from PySide6.QtGui import QColor
  
  if status == "success":
      item.setForeground(QColor("#62dba6")) # primary
  elif status == "failure":
      item.setForeground(QColor("#ff6f7f")) # danger
  ```

---

### 3.3 `gnu.in-cockpit/src/cockpit/views/log_view.py`

#### A. Consolidate LogView Stylesheet
* **What to change**: Remove the local stylesheet inside LogView.
* **Why**: Styled globally via LogView type selectors.
* **Code Modification**:
  ```python
  # Before (line 23)
  self.setStyleSheet(
      "QPlainTextEdit{background:#0F1115;color:#D7DCE2;border:1px solid #1A2026;}"
  )

  # After
  # Remove self.setStyleSheet call completely. The QSS is inherited from global QSS.
  ```

#### B. Update Log Color Mapping
* **What to change**: Update `COLORS` dictionary in `LogView` to match `systertheme.hpp`.
* **Why**: Replaces hardcoded console colors with the exact C++ theme colors.
* **Code Modification**:
  ```python
  # Before (line 7)
  COLORS = {
      "cmd": "#FF8E40",      # accent — the command header
      "out": "#D7DCE2",      # stdout
      "err": "#E5707A",      # stderr
      "ok": "#8DA982",       # success exit
      "fail": "#E5484D",     # failure exit
      "muted": "#7C828A",
  }

  # After
  COLORS = {
      "cmd": "#e8bc62",      # warning (#e8bc62) -> Orange-yellow accent
      "out": "#eef4f1",      # foreground (#eef4f1)
      "err": "#ff6f7f",      # danger (#ff6f7f)
      "ok": "#62dba6",       # primary (#62dba6) -> Mint green success
      "fail": "#ff6f7f",     # danger (#ff6f7f)
      "muted": "#7f8d89",    # foregroundTertiary (#7f8d89)
  }
  ```

---

## 4. Verification and Testing Reference

### 4.1 Automated Tests
Verify that these visual changes do not break the functional e2e and unit tests. The project includes tests that launch the GUI and mock GitHub calls.

Run the test suite using `pytest` within the project root virtualenv:
```bash
# Cockpit view tests
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit
.venv/bin/pytest tests/test_e2e_launch.py tests/test_github_api.py
```

### 4.2 Manual Visual Inspection
Launch the Cockpit GUI using the following command to manually verify colors, margins, border radii, and correct dark-mode styling:
```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit
.venv/bin/python -m cockpit
```

Verify the following:
1. **Background Contrast**: The main window and group boxes are at `#111516` (`mainSurface`), whereas log/doc text areas and the GitHub panel are darker at `#050606` (`surfaceUnder`).
2. **Interactive Elements**: Default buttons show `#171b1d` with `#31393b` borders and `#202628` hover backgrounds. Checkboxes and inputs have a 6px corner radius.
3. **Danger Actions**: Destructive buttons (e.g. "Clean/Rebuild", "Reset git hard") render with `#ff6f7f` border/text, and hover states remain legible.
4. **Log Colors**: Log output utilizes the new warning `#e8bc62` for commands and `#62dba6` / `#ff6f7f` for success and failure exits.
5. **No GNOME/GTK Warning**: Visual verification is completely standalone (Qt native style `Fusion` under X11/Wayland), fully complying with system constraints.
