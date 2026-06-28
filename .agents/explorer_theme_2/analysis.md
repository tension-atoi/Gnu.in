# Theme Analysis and Stylesheet Design

## Summary
The goal of this analysis is to unify the visual theme of the `gnu.in-cockpit` Python application with the system-wide styling properties defined in the `gnu.in-syster-app` C++ design system. Currently, the cockpit views use hardcoded styling values, creating a visual disconnect. 

By designing a unified Qt6 stylesheet and dynamic theme parser, the cockpit application will automatically adapt to changes in the master design system (`syster-app/src/systertheme.hpp`) while maintaining robust standalone fallbacks.

---

## 1. Master Design System (`systertheme.hpp`) Properties
The C++ theme configuration defines the following colors and metrics:

### Colors
| Property | Value | Description |
|---|---|---|
| `surfaceUnder` | `#050606` | Background color behind panels/layouts |
| `mainSurface` | `#111516` | Base color for main panels and containers |
| `elevatedPrimary` | `#171b1d` | Color for primary interactive controls / inputs |
| `elevatedSecondary` | `#202628` | Hover state background / selection highlight |
| `borderDefault` | `#31393b` | Default border lines |
| `borderHeavy` | `#465154` | Hovered / active state border line |
| `foreground` | `#eef4f1` | Primary text |
| `foregroundSecondary` | `#a6b3af` | Secondary/subtle text |
| `foregroundTertiary` | `#7f8d89` | Muted/placeholder/disabled text |
| `primary` | `#62dba6` | Accent color (brand teal-green, positive states) |
| `warning` | `#e8bc62` | Alert/warning color |
| `danger` | `#ff6f7f` | Error/danger state color |

### Metrics
*   `toolbarHeight`: `46px`
*   `toolbarSmallHeight`: `36px`
*   `textXs`: `11px`
*   `textSm`: `12px`
*   `textBase`: `14px`
*   `textLg`: `16px`
*   `radiusMd`: `6px`
*   `radiusLg`: `8px`
*   `radiusXl`: `10px`
*   `panelPadding`: `12px`

---

## 2. Recommended Changes

### A. Introduce `theme.py`
A new file `gnu.in-cockpit/src/cockpit/views/theme.py` should be introduced to dynamically load the C++ theme variables at runtime. This maintains a single source of truth across repositories.
*Refer to the full implementation in `.agents/explorer_theme_2/proposed_theme.py`.*

Key features:
1.  **Regex Parser**: Reads `systertheme.hpp` on startup using safe regular expressions.
2.  **Fallback Defaults**: Restores exact design values if the C++ repository is missing or unreadable.
3.  **Dynamic Stylesheet**: Generates a unified QSS template with exact variable mapping.

### B. Adjustments to `main_window.py`
To align with the unified stylesheet and avoid visual overrides:
1.  **Import & Initialize Theme Manager**:
    ```python
    from cockpit.views.theme import CockpitTheme
    # In Cockpit.__init__:
    self.theme = CockpitTheme()
    ```
2.  **Define Targetable Object Names**:
    *   Set `root.setObjectName("centralWidget")`
    *   In `_build_action_panel`, set `panel.setObjectName("action_panel")`
    *   In `_build_log_panel`, set `panel.setObjectName("log_panel")`
    *   In `_build_doc_panel`, set `panel.setObjectName("doc_panel")`
3.  **Remove Inline Styles for Action Buttons**:
    Instead of setting hardcoded styles on danger buttons:
    ```python
    # Before
    if action.danger:
        btn.setStyleSheet("QPushButton{background:#3a1c1c;border:1px solid #E5484D;}QPushButton:hover{background:#4a2020;}")
        
    # After
    if action.danger:
        btn.setProperty("danger", True)
    ```
4.  **Simplify `_apply_theme()`**:
    ```python
    def _apply_theme(self) -> None:
        self.setStyleSheet(self.theme.get_stylesheet())
    ```

### C. Adjustments to `github_panel.py`
1.  **Remove Widget-Level Stylesheets**:
    Remove hardcoded `self.setStyleSheet(...)` and `self.refresh_btn.setStyleSheet(...)` calls.
2.  **Assign Properties for Stylesheet Targetting**:
    *   `header.setProperty("class", "header")`
    *   `self.status_label.setObjectName("status_label")`
    *   For the group title labels:
        ```python
        pr_header = QLabel("Pull Requests")
        pr_header.setProperty("listHeader", True)
        ```
3.  **Update Item Foreground Colors**:
    Avoid using hardcoded system-native `Qt.GlobalColor.green` and `Qt.GlobalColor.red`, which might clash with the dark palette:
    ```python
    # Before
    if status == "success":
        item.setForeground(Qt.GlobalColor.green)
    elif status == "failure":
        item.setForeground(Qt.GlobalColor.red)
        
    # After (resolving color strings from CockpitTheme)
    from PySide6.QtGui import QColor
    if status == "success":
        item.setForeground(QColor(self.theme.primary))
    elif status == "failure":
        item.setForeground(QColor(self.theme.danger))
    ```

### D. Adjustments to `log_view.py`
1.  **Remove Widget-Level Stylesheet**:
    Remove `self.setStyleSheet("QPlainTextEdit{...}")` inside `LogView.__init__`.
2.  **Map Colors Dictionary**:
    ```python
    # Before
    COLORS = {
        "cmd": "#FF8E40",
        "out": "#D7DCE2",
        "err": "#E5707A",
        "ok": "#8DA982",
        "fail": "#E5484D",
        "muted": "#7C828A",
    }
    
    # After (referencing CockpitTheme)
    # We can pass the theme instance into LogView constructor or reference a global theme instance.
    COLORS = {
        "cmd": theme.primary,              # Accented command line
        "out": theme.foreground,           # Standard stdout
        "err": theme.danger,               # Stderr
        "ok": theme.primary,               # Exit 0
        "fail": theme.danger,              # Non-zero exit
        "muted": theme.foregroundTertiary, # Helper context details
    }
    ```

---

## 3. Verification Method

### Test Executions
To verify that the application imports and GUI structure changes do not break behavior, execute the following commands in `gnu.in-cockpit`:

1.  **Launch and GUI Lifecycle E2E Tests**:
    ```bash
    uv run pytest tests/test_e2e_launch.py
    ```
2.  **GitHub API and Business Logic Integration Tests**:
    ```bash
    uv run pytest tests/test_github_api.py
    uv run pytest tests/test_github_api_stress.py
    ```
3.  **Standalone CLI & Git Helper Verification**:
    ```bash
    uv run python tests/verify_empirical_git.py
    ```
