import re
from pathlib import Path

class CockpitTheme:
    """
    Unified theme properties mapping to systertheme.hpp.
    Parses the C++ header at runtime if available to maintain a single source of truth,
    with robust fallback values.
    """
    def __init__(self, hpp_path: Path | None = None) -> None:
        # Fallback values mirroring systertheme.hpp
        self.surfaceUnder = "#050606"
        self.mainSurface = "#111516"
        self.elevatedPrimary = "#171b1d"
        self.elevatedSecondary = "#202628"
        self.borderDefault = "#31393b"
        self.borderHeavy = "#465154"
        self.foreground = "#eef4f1"
        self.foregroundSecondary = "#a6b3af"
        self.foregroundTertiary = "#7f8d89"
        self.primary = "#62dba6"
        self.warning = "#e8bc62"
        self.danger = "#ff6f7f"

        self.toolbarHeight = 46
        self.toolbarSmallHeight = 36
        self.textXs = 11
        self.textSm = 12
        self.textBase = 14
        self.textLg = 16
        self.radiusMd = 6
        self.radiusLg = 8
        self.radiusXl = 10
        self.panelPadding = 12

        if hpp_path is None:
            # Resolve relative workspace path from cockpit/src/cockpit/views/theme.py
            try:
                current_dir = Path(__file__).resolve().parent
                workspace_root = current_dir.parents[3]
                hpp_path = workspace_root / "gnu.in-syster-app" / "syster-app" / "src" / "systertheme.hpp"
            except Exception:
                pass

        if hpp_path and hpp_path.exists():
            self.load_from_hpp(hpp_path)

    def load_from_hpp(self, path: Path) -> None:
        try:
            content = path.read_text(encoding="utf-8")
            
            # Match QColor return statements: QColor name() const { return QColor("#xxxxxx"); }
            color_matches = re.findall(
                r"QColor\s+(\w+)\s*\(\s*\)\s*const\s*\{\s*return\s*QColor\s*\(\s*\"([^\"]+)\"\s*\)\s*;\s*\}",
                content
            )
            for name, value in color_matches:
                if hasattr(self, name):
                    setattr(self, name, value)

            # Match int return statements: int name() const { return val; }
            int_matches = re.findall(
                r"int\s+(\w+)\s*\(\s*\)\s*const\s*\{\s*return\s*(\d+)\s*;\s*\}",
                content
            )
            for name, value in int_matches:
                if hasattr(self, name):
                    setattr(self, name, int(value))
        except Exception:
            # Fall back silently to default values on any parsing error
            pass

    def get_stylesheet(self) -> str:
        return f"""
        QMainWindow, QWidget#centralWidget {{
            background-color: {self.surfaceUnder};
            color: {self.foreground};
            font-size: {self.textBase}px;
        }}

        QWidget#action_panel {{
            background-color: {self.mainSurface};
        }}

        QFrame#log_panel, QFrame#doc_panel, GitHubPanel {{
            background-color: {self.mainSurface};
            border: 1px solid {self.borderDefault};
            border-radius: {self.radiusLg}px;
        }}

        QGroupBox {{
            background-color: {self.mainSurface};
            border: 1px solid {self.borderDefault};
            border-radius: {self.radiusLg}px;
            margin-top: {self.panelPadding}px;
            padding-top: {self.panelPadding}px;
            font-size: {self.textSm}px;
            font-weight: bold;
            color: {self.foregroundSecondary};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            color: {self.foregroundSecondary};
        }}

        QPlainTextEdit, QTextBrowser {{
            background-color: {self.elevatedPrimary};
            border: 1px solid {self.borderDefault};
            border-radius: {self.radiusMd}px;
            color: {self.foreground};
            padding: {self.panelPadding}px;
            font-family: "JetBrains Mono", monospace;
            font-size: {self.textSm}px;
        }}

        QListWidget {{
            background-color: {self.elevatedPrimary};
            border: 1px solid {self.borderDefault};
            border-radius: {self.radiusMd}px;
            color: {self.foreground};
            padding: 6px;
        }}

        QListWidget::item {{
            padding: 6px;
            border-radius: 4px;
            color: {self.foreground};
        }}

        QListWidget::item:hover {{
            background-color: {self.elevatedSecondary};
        }}

        QListWidget::item:selected {{
            background-color: {self.elevatedSecondary};
            color: {self.primary};
        }}

        QLineEdit, QComboBox {{
            background-color: {self.elevatedPrimary};
            border: 1px solid {self.borderDefault};
            border-radius: {self.radiusMd}px;
            padding: 4px 8px;
            color: {self.foreground};
            font-size: {self.textSm}px;
        }}

        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {self.primary};
        }}

        QComboBox QAbstractItemView {{
            background-color: {self.elevatedPrimary};
            border: 1px solid {self.borderDefault};
            selection-background-color: {self.elevatedSecondary};
            selection-color: {self.foreground};
            color: {self.foregroundSecondary};
        }}

        QCheckBox {{
            color: {self.foreground};
            font-size: {self.textSm}px;
            spacing: 6px;
        }}

        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {self.borderDefault};
            border-radius: 4px;
            background-color: {self.elevatedPrimary};
        }}

        QCheckBox::indicator:hover {{
            border-color: {self.borderHeavy};
            background-color: {self.elevatedSecondary};
        }}

        QCheckBox::indicator:checked {{
            background-color: {self.primary};
            border-color: {self.primary};
            image: url(data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="%23111516" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>);
        }}

        QPushButton {{
            background-color: {self.elevatedPrimary};
            border: 1px solid {self.borderDefault};
            border-radius: {self.radiusMd}px;
            color: {self.foreground};
            padding: 6px 12px;
            font-size: {self.textSm}px;
        }}

        QPushButton:hover {{
            background-color: {self.elevatedSecondary};
            border-color: {self.borderHeavy};
        }}

        QPushButton:pressed {{
            background-color: {self.mainSurface};
        }}

        QPushButton:disabled {{
            color: {self.foregroundTertiary};
            border-color: {self.borderDefault};
            background-color: {self.mainSurface};
        }}

        QPushButton[danger="true"] {{
            background-color: #331619;
            border: 1px solid {self.danger};
            color: {self.danger};
        }}

        QPushButton[danger="true"]:hover {{
            background-color: #441a1f;
            border-color: {self.danger};
        }}

        QPushButton[danger="true"]:pressed {{
            background-color: #220f11;
        }}

        QSplitter::handle {{
            background-color: {self.borderDefault};
        }}

        QSplitter::handle:horizontal {{
            width: 4px;
        }}

        QSplitter::handle:vertical {{
            height: 4px;
        }}

        QStatusBar {{
            background-color: {self.surfaceUnder};
            border-top: 1px solid {self.borderDefault};
            color: {self.foregroundSecondary};
            font-size: {self.textXs}px;
        }}

        QStatusBar::item {{
            border: none;
        }}

        /* GitHub Panel Custom Styling Overrides */
        GitHubPanel QLabel {{
            border: none;
            background: transparent;
        }}

        GitHubPanel QLabel[class="header"] {{
            font-weight: 600;
            font-size: {self.textBase}px;
            color: {self.foreground};
        }}

        GitHubPanel QLabel#status_label {{
            color: {self.foregroundTertiary};
        }}

        GitHubPanel QLabel[listHeader="true"] {{
            font-weight: 600;
            margin-top: 10px;
        }}

        GitHubPanel QListWidget {{
            border: none;
            background-color: transparent;
        }}
        """
