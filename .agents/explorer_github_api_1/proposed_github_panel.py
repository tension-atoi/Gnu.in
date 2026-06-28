from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QFrame
)
from cockpit.github_client import GitHubClient

class GitHubWorker(QThread):
    result_ready = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, cwd: str, token: str | None = None) -> None:
        super().__init__()
        self.cwd = cwd
        self.token = token

    def run(self) -> None:
        try:
            prs = GitHubClient.get_pull_requests(self.cwd, token=self.token)
            runs = GitHubClient.get_recent_runs(self.cwd, token=self.token)
            self.result_ready.emit({"prs": prs, "runs": runs})
        except Exception as e:
            self.error_occurred.emit(str(e))

class GitHubPanel(QFrame):
    """A panel to show GitHub PRs and Actions."""

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

        self.worker = None

    def refresh(self, cwd: str, token: str | None = None) -> None:
        if not GitHubClient.is_installed():
            self.status_label.setText("requests is not installed or available.")
            return

        self.status_label.setText("Fetching...")
        self.refresh_btn.setEnabled(False)
        self.pr_list.clear()
        self.actions_list.clear()

        self.worker = GitHubWorker(cwd, token=token)
        self.worker.result_ready.connect(self._on_result)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.start()

    def _on_result(self, data: dict) -> None:
        self.status_label.setText("Updated")
        self.refresh_btn.setEnabled(True)

        prs = data.get("prs", [])
        if not prs:
            self.pr_list.addItem(QListWidgetItem("No open PRs"))
        for pr in prs:
            item = QListWidgetItem(f"#{pr['number']} {pr['title']} ({pr['author']['login']})")
            item.setToolTip(pr['url'])
            self.pr_list.addItem(item)

        runs = data.get("runs", [])
        if not runs:
            self.actions_list.addItem(QListWidgetItem("No recent runs"))
        for run in runs:
            status = run['conclusion'] if run['conclusion'] else run['status']
            item = QListWidgetItem(f"[{status.upper()}] {run['name']}")
            item.setToolTip(run['url'])
            if status == "success":
                item.setForeground(Qt.GlobalColor.green)
            elif status == "failure":
                item.setForeground(Qt.GlobalColor.red)
            self.actions_list.addItem(item)

    def _on_error(self, err: str) -> None:
        self.status_label.setText("Error fetching data")
        self.refresh_btn.setEnabled(True)
        self.pr_list.addItem(QListWidgetItem(err))
