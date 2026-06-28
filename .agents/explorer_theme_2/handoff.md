# Handoff Report — Explorer 2 (Milestone 2)

## 1. Observation
- Master Theme definitions reside in `gnu.in-syster-app/syster-app/src/systertheme.hpp` (Lines 34-56):
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
- Current styling in `gnu.in-cockpit/src/cockpit/views/main_window.py` (Lines 334-344) uses hardcoded color hex values and sizes:
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
- Inline style rules override theme settings in `gnu.in-cockpit/src/cockpit/views/github_panel.py` (e.g., Lines 35-37, 46-49, 53, 58, 63):
  ```python
  self.setStyleSheet("QFrame{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;}")
  self.refresh_btn.setStyleSheet("QPushButton{background:#1A2026;...}")
  ```
- Inline styling in `gnu.in-cockpit/src/cockpit/views/log_view.py` (Lines 23-25):
  ```python
  self.setStyleSheet("QPlainTextEdit{background:#0F1115;color:#D7DCE2;border:1px solid #1A2026;}")
  ```
- Mono-styled log elements colors in `gnu.in-cockpit/src/cockpit/views/log_view.py` (Lines 7-14):
  ```python
  COLORS = {
      "cmd": "#FF8E40",
      "out": "#D7DCE2",
      "err": "#E5707A",
      "ok": "#8DA982",
      "fail": "#E5484D",
      "muted": "#7C828A",
  }
  ```
- Python tests execution command `uv run pytest tests/test_e2e_launch.py` completed successfully:
  ```
  collected 12 items
  tests/test_e2e_launch.py ............
  ============================== 12 passed in 1.18s ==============================
  ```

## 2. Logic Chain
1. To ensure consistent visual identity, `gnu.in-cockpit` must align with the colors and dimensions specified in `systertheme.hpp` (Observation 1).
2. The current cockpit views hardcode styling values that differ from the master design system (Observations 2, 3, 4).
3. Directly styling base `QWidget` classes globally overrides components unexpectedly, so container widgets must be targetable by specific Object Names or subclasses (Observation 2).
4. Rather than manually copying hex values that could drift, a Python theme manager (`theme.py`) should dynamically parse `systertheme.hpp` via regular expressions at runtime, defaulting to static fallback variables when needed (Observation 1).
5. Dynamic properties (e.g., `setProperty("danger", True)`) in QSS are more maintainable than python-embedded stylesheet injections (Observation 2).

## 3. Caveats
- This investigation assumes that the relative path between the `gnu.in-cockpit` and `gnu.in-syster-app` repositories remains stable. The parser handles this by silently using static defaults if the C++ header file cannot be found or read.
- We did not implement or test the code changes since this is a read-only investigation.

## 4. Conclusion
We recommend creating a Python theme manager `theme.py` (see `proposed_theme.py`) that parses `systertheme.hpp` dynamically on startup and generates a unified Qt6 stylesheet. All views in cockpit (`main_window.py`, `github_panel.py`, `log_view.py`) should be refactored to clear inline styles, assign targetable object names/properties, and let the application-wide stylesheet drive styling.

## 5. Verification Method
Verify that cockpit is stable after integrating the stylesheet by running:
```bash
uv run pytest tests/test_e2e_launch.py
uv run pytest tests/test_github_api.py
uv run pytest tests/test_github_api_stress.py
uv run python tests/verify_empirical_git.py
```
Check that the stylesheet parses correctly without raising PySide6 errors during application startup.
