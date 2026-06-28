from PySide6.QtGui import QColor

class SysterTheme:
    # Colors
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

    # Dimensions
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

    @classmethod
    def get_color(cls, hex_color: str) -> QColor:
        return QColor(hex_color)

    @classmethod
    def main_window_qss(cls) -> str:
        return (
            f"QMainWindow, QWidget {{ background: {cls.ELEVATED_PRIMARY}; color: {cls.FOREGROUND}; }}"
            f"QGroupBox {{ border: 1px solid {cls.BORDER_DEFAULT}; border-radius: {cls.RADIUS_LG}px; margin-top: {cls.RADIUS_LG}px; padding-top: {cls.RADIUS_LG}px; }}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left: {cls.RADIUS_XL}px; color: {cls.FOREGROUND_SECONDARY}; }}"
            f"QPushButton {{ background: {cls.ELEVATED_SECONDARY}; border: 1px solid {cls.BORDER_DEFAULT}; border-radius: {cls.RADIUS_MD}px; padding: {cls.RADIUS_MD}px; }}"
            f"QPushButton:hover {{ background: {cls.BORDER_DEFAULT}; }}"
            f"QPushButton:disabled {{ color: {cls.FOREGROUND_TERTIARY}; border-color: {cls.ELEVATED_SECONDARY}; }}"
            f"QLineEdit, QComboBox {{ background: {cls.SURFACE_UNDER}; border: 1px solid {cls.BORDER_DEFAULT}; border-radius: 5px; padding: 4px; }}"
            f"QStatusBar {{ color: {cls.FOREGROUND_SECONDARY}; }}"
        )

    @classmethod
    def danger_button_qss(cls) -> str:
        # background: #3a1c1c is a dark red based on danger
        return (
            f"QPushButton {{ background: #3a1c1c; border: 1px solid {cls.DANGER}; }}"
            f"QPushButton:hover {{ background: #4a2020; }}"
        )

    @classmethod
    def doc_browser_qss(cls) -> str:
        return (
            f"QTextBrowser {{ background: {cls.MAIN_SURFACE}; color: {cls.FOREGROUND_SECONDARY}; border: 1px solid {cls.BORDER_DEFAULT}; padding: {cls.RADIUS_XL}px; }}"
        )

    @classmethod
    def github_panel_qss(cls) -> str:
        return (
            f"QFrame {{ background: {cls.MAIN_SURFACE}; color: {cls.FOREGROUND_SECONDARY}; border: 1px solid {cls.BORDER_DEFAULT}; }}"
        )

    @classmethod
    def github_refresh_btn_qss(cls) -> str:
        return (
            f"QPushButton {{ background: {cls.ELEVATED_SECONDARY}; border: 1px solid {cls.BORDER_DEFAULT}; border-radius: {cls.RADIUS_MD}px; padding: 4px; }}"
            f"QPushButton:hover {{ background: {cls.BORDER_DEFAULT}; }}"
        )

    @classmethod
    def log_view_qss(cls) -> str:
        return (
            f"QPlainTextEdit {{ background: {cls.MAIN_SURFACE}; color: {cls.FOREGROUND}; border: 1px solid {cls.BORDER_DEFAULT}; }}"
        )
