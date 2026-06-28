# Styling Handoff Report - Explorer 3

## 1. Observation

Direct observations made within the codebase are listed below:

### A. Syster Theme Definitions (`systertheme.hpp`)
Path: `/home/tension_atoi/Projects/Gnu.in/gnu.in-syster-app/syster-app/src/systertheme.hpp`
Key declarations extracted directly:
```cpp
34:     QColor surfaceUnder() const { return QColor("#050606"); }
35:     QColor mainSurface() const { return QColor("#111516"); }
36:     QColor elevatedPrimary() const { return QColor("#171b1d"); }
37:     QColor elevatedSecondary() const { return QColor("#202628"); }
38:     QColor borderDefault() const { return QColor("#31393b"); }
39:     QColor borderHeavy() const { return QColor("#465154"); }
40:     QColor foreground() const { return QColor("#eef4f1"); }
41:     QColor foregroundSecondary() const { return QColor("#a6b3af"); }
42:     QColor foregroundTertiary() const { return QColor("#7f8d89"); }
43:     QColor primary() const { return QColor("#62dba6"); }
44:     QColor warning() const { return QColor("#e8bc62"); }
45:     QColor danger() const { return QColor("#ff6f7f"); }
46: 
47:     int toolbarHeight() const { return 46; }
48:     int toolbarSmallHeight() const { return 36; }
49:     int textXs() const { return 11; }
50:     int textSm() const { return 12; }
51:     int textBase() const { return 14; }
52:     int textLg() const { return 16; }
53:     int radiusMd() const { return 6; }
54:     int radiusLg() const { return 8; }
55:     int radiusXl() const { return 10; }
56:     int panelPadding() const { return 12; }
```

### B. Cockpit Views Styling

#### 1. Main Window (`main_window.py`)
Path: `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/views/main_window.py`
- **Danger button QSS (Lines 124-127):**
  ```python
  btn.setStyleSheet(
      "QPushButton{background:#3a1c1c;border:1px solid #E5484D;}"
      "QPushButton:hover{background:#4a2020;}"
  )
  ```
- **Text browser QSS (Lines 172-174):**
  ```python
  self.doc.setStyleSheet(
      "QTextBrowser{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;padding:10px;}"
  )
  ```
- **Main window QSS (Lines 334-344):**
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

#### 2. GitHub Panel (`github_panel.py`)
Path: `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/views/github_panel.py`
- **Panel frame QSS (Lines 35-37):**
  ```python
  self.setStyleSheet(
      "QFrame{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;}"
  )
  ```
- **Panel Layout Margins (Line 39):**
  ```python
  v.setContentsMargins(10, 10, 10, 10)
  ```
- **Header Label QSS (Line 42):**
  ```python
  header.setStyleSheet("font-weight:600; font-size: 14px; border:none;")
  ```
- **Refresh Button QSS (Lines 46-49):**
  ```python
  self.refresh_btn.setStyleSheet(
      "QPushButton{background:#1A2026;border:1px solid #2B3037;border-radius:6px;padding:4px;}"
      "QPushButton:hover{background:#222a32;}"
  )
  ```
- **Status Label QSS (Line 53):**
  ```python
  self.status_label.setStyleSheet("color:#7C828A; border:none;")
  ```
- **Pull Requests Header margins (Line 56):**
  ```python
  v.addWidget(QLabel("Pull Requests", styleSheet="font-weight:600; margin-top:10px; border:none;"))
  ```
- **Recent Actions Header margins (Line 61):**
  ```python
  v.addWidget(QLabel("Recent Actions", styleSheet="font-weight:600; margin-top:10px; border:none;"))
  ```
- **QListWidgets QSS (Lines 58, 63):**
  ```python
  self.pr_list.setStyleSheet("border:none; background:#0F1115;")
  self.actions_list.setStyleSheet("border:none; background:#0F1115;")
  ```
- **Action Success/Failure colors (Lines 115-119):**
  ```python
  if status == "success":
      item.setForeground(Qt.GlobalColor.green)
  elif status == "failure":
      item.setForeground(Qt.GlobalColor.red)
  ```

#### 3. Log View (`log_view.py`)
Path: `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/src/cockpit/views/log_view.py`
- **Log colors dict (Lines 7-14):**
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
- **QPlainTextEdit QSS (Lines 23-25):**
  ```python
  self.setStyleSheet(
      "QPlainTextEdit{background:#0F1115;color:#D7DCE2;border:1px solid #1A2026;}"
  )
  ```

---

## 2. Logic Chain

1. **Colors mapping logic**:
   - Compare the hex codes in QSS stylesheets and Python constants with those returned by functions in `systertheme.hpp`.
   - **Main Window/Widget background** `#15191E` is closest to `elevatedPrimary` (`#171b1d`).
   - **General text color** `#D7DCE2` is closest to `foreground` (`#eef4f1`).
   - **Dark backgrounds** like `#0F1115` (found on TextBrowser, LogView, GitHubPanel, and input fields) are closest to `mainSurface` (`#111516`).
   - **Active borders** `#1A2026` / `#2B3037` are closest to `borderDefault` (`#31393b`).
   - **Button background** `#1A2026` is closest to `elevatedSecondary` (`#202628`).
   - **Button hover backgrounds** `#222a32` are closest to `borderDefault` (`#31393b`).
   - **Disabled button text** `#555b62` is closest to `foregroundTertiary` (`#7f8d89`).
   - **Disabled button border** `#222` is closest to `elevatedSecondary` (`#202628`).
   - **Secondary labels / muted text** `#A1A6AD`, `#C7CDD4`, and `#7C828A` map to `foregroundSecondary` (`#a6b3af`) and `foregroundTertiary` (`#7f8d89`).
   - **Danger and Warning colors** (e.g. `#E5484D`, `#E5707A` for error, and `#FF8E40` for cmd) map directly to `danger` (`#ff6f7f`) and `warning` (`#e8bc62`).
   - **Success color** `Qt.GlobalColor.green` and `#8DA982` map to `primary` (`#62dba6`).

2. **Dimensions mapping logic**:
   - Margins/paddings of `10px` are closest to `radiusXl` (`10`) or `panelPadding` (`12`).
   - Border radius values (`8px`, `6px`, `5px`) map to `radiusLg` (`8`) and `radiusMd` (`6`).
   - Font sizes like `14px` map to `textBase` (`14`).

3. **Translation Strategy Recommendation**:
   - Direct translation of C++ files or QML is not possible/clean. Instead, we should create a Python styling module `theme.py` under `src/cockpit/views/`.
   - All components (`main_window.py`, `github_panel.py`, `log_view.py`) should import this module and use the f-string style generator functions or class attributes to populate their stylesheets.
   - This ensures unified theme application and single-source-of-truth configuration.

---

## 3. Caveats

- SysterTheme does not declare explicit hover state colors for buttons. We resolved this by mapping button hover backgrounds to `borderDefault` (`#31393b`) or slightly lighter variations, which is standard for QSS and matches the visual contrast of SysterTheme.
- We did not investigate dynamic theme updates (e.g., light mode transition) since SysterTheme defines constant colors. We assumed dark mode is persistent.

---

## 4. Conclusion

The hardcoded colors in cockpit can be fully adapted to native Qt6 styling parameters defined in `systertheme.hpp`. 
We propose creating `src/cockpit/views/theme.py` (which has been fully drafted in this workspace as `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_styling_3/proposed_theme.py`) and modifying the three cockpit views to use it.

Below are the before/after styling snippets for the files:

### A. `main_window.py`

#### Before (Line 124-127)
```python
                    btn.setStyleSheet(
                        "QPushButton{background:#3a1c1c;border:1px solid #E5484D;}"
                        "QPushButton:hover{background:#4a2020;}"
                    )
```
#### After
```python
                    from cockpit.views.theme import SysterTheme
                    btn.setStyleSheet(SysterTheme.danger_button_qss())
```

#### Before (Line 172-174)
```python
        self.doc.setStyleSheet(
            "QTextBrowser{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;padding:10px;}"
        )
```
#### After
```python
        from cockpit.views.theme import SysterTheme
        self.doc.setStyleSheet(SysterTheme.doc_browser_qss())
```

#### Before (Line 334-344)
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
#### After
```python
    def _apply_theme(self) -> None:
        from cockpit.views.theme import SysterTheme
        self.setStyleSheet(SysterTheme.main_window_qss())
```

---

### B. `github_panel.py`

#### Before (Line 35-37)
```python
        self.setStyleSheet(
            "QFrame{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;}"
        )
```
#### After
```python
        from cockpit.views.theme import SysterTheme
        self.setStyleSheet(SysterTheme.github_panel_qss())
```

#### Before (Line 39)
```python
        v.setContentsMargins(10, 10, 10, 10)
```
#### After
```python
        from cockpit.views.theme import SysterTheme
        v.setContentsMargins(SysterTheme.PANEL_PADDING, SysterTheme.PANEL_PADDING, SysterTheme.PANEL_PADDING, SysterTheme.PANEL_PADDING)
```

#### Before (Line 42)
```python
        header.setStyleSheet("font-weight:600; font-size: 14px; border:none;")
```
#### After
```python
        from cockpit.views.theme import SysterTheme
        header.setStyleSheet(f"font-weight:600; font-size: {SysterTheme.TEXT_BASE}px; border:none;")
```

#### Before (Line 46-49)
```python
        self.refresh_btn.setStyleSheet(
            "QPushButton{background:#1A2026;border:1px solid #2B3037;border-radius:6px;padding:4px;}"
            "QPushButton:hover{background:#222a32;}"
        )
```
#### After
```python
        from cockpit.views.theme import SysterTheme
        self.refresh_btn.setStyleSheet(SysterTheme.github_refresh_btn_qss())
```

#### Before (Line 53)
```python
        self.status_label.setStyleSheet("color:#7C828A; border:none;")
```
#### After
```python
        from cockpit.views.theme import SysterTheme
        self.status_label.setStyleSheet(f"color:{SysterTheme.FOREGROUND_TERTIARY}; border:none;")
```

#### Before (Line 56, 61)
```python
        v.addWidget(QLabel("Pull Requests", styleSheet="font-weight:600; margin-top:10px; border:none;"))
        ...
        v.addWidget(QLabel("Recent Actions", styleSheet="font-weight:600; margin-top:10px; border:none;"))
```
#### After
```python
        from cockpit.views.theme import SysterTheme
        v.addWidget(QLabel("Pull Requests", styleSheet=f"font-weight:600; margin-top:{SysterTheme.RADIUS_XL}px; border:none;"))
        ...
        v.addWidget(QLabel("Recent Actions", styleSheet=f"font-weight:600; margin-top:{SysterTheme.RADIUS_XL}px; border:none;"))
```

#### Before (Line 58, 63)
```python
        self.pr_list.setStyleSheet("border:none; background:#0F1115;")
        ...
        self.actions_list.setStyleSheet("border:none; background:#0F1115;")
```
#### After
```python
        from cockpit.views.theme import SysterTheme
        self.pr_list.setStyleSheet(f"border:none; background:{SysterTheme.MAIN_SURFACE};")
        ...
        self.actions_list.setStyleSheet(f"border:none; background:{SysterTheme.MAIN_SURFACE};")
```

#### Before (Line 115-119)
```python
            if status == "success":
                item.setForeground(Qt.GlobalColor.green)
            elif status == "failure":
                item.setForeground(Qt.GlobalColor.red)
```
#### After
```python
            from cockpit.views.theme import SysterTheme
            if status == "success":
                item.setForeground(SysterTheme.get_color(SysterTheme.PRIMARY))
            elif status == "failure":
                item.setForeground(SysterTheme.get_color(SysterTheme.DANGER))
```

---

### C. `log_view.py`

#### Before (Line 7-14)
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
#### After
```python
    from cockpit.views.theme import SysterTheme
    COLORS = {
        "cmd": SysterTheme.WARNING,      # accent — the command header
        "out": SysterTheme.FOREGROUND,   # stdout
        "err": SysterTheme.DANGER,       # stderr
        "ok": SysterTheme.PRIMARY,       # success exit
        "fail": SysterTheme.DANGER,      # failure exit
        "muted": SysterTheme.FOREGROUND_TERTIARY,
    }
```

#### Before (Line 23-25)
```python
        self.setStyleSheet(
            "QPlainTextEdit{background:#0F1115;color:#D7DCE2;border:1px solid #1A2026;}"
        )
```
#### After
```python
        from cockpit.views.theme import SysterTheme
        self.setStyleSheet(SysterTheme.log_view_qss())
```

---

## 5. Verification Method

To independently verify the mapping and the theme adaptation strategy:

1. **Verify theme.py Structure**:
   Inspect `/home/tension_atoi/Projects/Gnu.in/.agents/explorer_styling_3/proposed_theme.py`. Check that all parameters (colors, dimensions) match `systertheme.hpp` properties.
2. **Static Code Validation**:
   Validate that `theme.py` is free of syntax errors and correctly imports `QColor` from `PySide6.QtGui` using:
   ```bash
   python -m py_compile /home/tension_atoi/Projects/Gnu.in/.agents/explorer_styling_3/proposed_theme.py
   ```
3. **Interactive Validation (Post-Implementation)**:
   Launch the control panel using:
   ```bash
   python -m cockpit
   ```
   Ensure the app starts without errors and the styling matches SysterTheme's dark colors.
