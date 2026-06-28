from pathlib import Path

from PySide6.QtCore import QEvent, QProcess, QSettings, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from cockpit.models.action import Action, ACTIONS, DEFAULT_WORKSPACE, DOCS, GROUP_ORDER, INTRO_DOC, OS_REPO, REPOS
from cockpit.views.log_view import LogView
from cockpit.views.github_panel import GitHubPanel


class Cockpit(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GNU.IN Pipeline Cockpit")
        self.resize(1600, 800)
        self.settings = QSettings("gnu-in-labs", "pipeline-cockpit")

        self.proc: QProcess | None = None
        self.run_buttons: list[QPushButton] = []
        self.btn_docs: dict[QPushButton, str] = {}

        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)

        outer.addLayout(self._build_config_row())
        body = QSplitter(Qt.Orientation.Horizontal)
        body.addWidget(self._build_action_panel())
        body.addWidget(self._build_log_panel())
        body.addWidget(self._build_doc_panel())
        
        self.github_panel = GitHubPanel()
        self.github_panel.refresh_btn.clicked.connect(self._refresh_github)
        body.addWidget(self.github_panel)

        body.setStretchFactor(0, 0)
        body.setStretchFactor(1, 1)
        body.setStretchFactor(2, 0)
        body.setStretchFactor(3, 0)
        body.setSizes([320, 600, 380, 300])
        outer.addWidget(body)

        self.status = self.statusBar()
        self.status.showMessage("Ready")
        self._apply_theme()

        # Initial GitHub refresh
        self._refresh_github()

    # ── config row ──
    def _build_config_row(self) -> QHBoxLayout:
        row = QHBoxLayout()

        row.addWidget(QLabel("Workspace:"))
        self.ws_edit = QLineEdit(self.settings.value("workspace", DEFAULT_WORKSPACE))
        row.addWidget(self.ws_edit, 1)
        browse = QPushButton("…")
        browse.setFixedWidth(32)
        browse.clicked.connect(self._browse)
        row.addWidget(browse)

        row.addWidget(QLabel("Repo:"))
        self.repo_combo = QComboBox()
        self.repo_combo.addItems(REPOS)
        saved = self.settings.value("repo", OS_REPO)
        if saved in REPOS:
            self.repo_combo.setCurrentText(saved)
        self.repo_combo.currentTextChanged.connect(self._refresh_github)
        row.addWidget(self.repo_combo)

        row.addWidget(QLabel("GitHub PAT:"))
        self.pat_edit = QLineEdit()
        self.pat_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pat_edit.setPlaceholderText("ghp_...")
        self.pat_edit.setText(self.settings.value("github_pat", ""))
        self.pat_edit.textChanged.connect(self._refresh_github)
        row.addWidget(self.pat_edit)

        self.author_cb = QCheckBox("Commit as Gnosis.Agent")
        self.author_cb.setChecked(bool(self.settings.value("gnosis_author", False, type=bool)))
        self.author_cb.setToolTip("Set GIT_AUTHOR/COMMITTER to Gnosis.Agent for commits")
        row.addWidget(self.author_cb)
        return row

    def _build_action_panel(self) -> QWidget:
        panel = QWidget()
        panel.setMinimumWidth(300)
        v = QVBoxLayout(panel)
        v.setContentsMargins(0, 0, 0, 0)

        self.msg_edit = QLineEdit()
        self.msg_edit.setPlaceholderText("commit message…")
        msg_box = QGroupBox("Commit message")
        ml = QVBoxLayout(msg_box)
        ml.addWidget(self.msg_edit)
        v.addWidget(msg_box)

        for group in GROUP_ORDER:
            box = QGroupBox(group)
            grid = QGridLayout(box)
            grid.setSpacing(6)
            col = 0
            rowi = 0
            for action in [a for a in ACTIONS if a.group == group]:
                btn = QPushButton(action.label)
                btn.setToolTip(action.tip or action.cmd)
                if action.danger:
                    btn.setStyleSheet(
                        "QPushButton{background:#3a1c1c;border:1px solid #E5484D;}"
                        "QPushButton:hover{background:#4a2020;}"
                    )
                btn.clicked.connect(lambda _=False, a=action: self.run(a))
                btn.installEventFilter(self)
                self.btn_docs[btn] = DOCS.get(action.label, INTRO_DOC)
                grid.addWidget(btn, rowi, col)
                self.run_buttons.append(btn)
                col += 1
                if col == 2:
                    col = 0
                    rowi += 1
            v.addWidget(box)

        ctrl = QHBoxLayout()
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop)
        clear_btn = QPushButton("Clear log")
        clear_btn.clicked.connect(lambda: self.log.clear())
        ctrl.addWidget(self.stop_btn)
        ctrl.addWidget(clear_btn)
        v.addLayout(ctrl)
        v.addStretch(1)
        return panel

    def _build_log_panel(self) -> QWidget:
        panel = QFrame()
        v = QVBoxLayout(panel)
        v.setContentsMargins(0, 0, 0, 0)
        header = QLabel("Feedback log")
        header.setStyleSheet("font-weight:600;")
        v.addWidget(header)
        self.log = LogView()
        v.addWidget(self.log, 1)
        return panel

    def _build_doc_panel(self) -> QWidget:
        panel = QFrame()
        panel.setMinimumWidth(320)
        v = QVBoxLayout(panel)
        v.setContentsMargins(0, 0, 0, 0)
        header = QLabel("What does this do?")
        header.setStyleSheet("font-weight:600;")
        v.addWidget(header)
        self.doc = QTextBrowser()
        self.doc.setOpenExternalLinks(False)
        self.doc.setStyleSheet(
            "QTextBrowser{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;padding:10px;}"
        )
        self.doc.setMarkdown(INTRO_DOC)
        v.addWidget(self.doc, 1)
        return panel

    def eventFilter(self, obj, event):  # noqa: N802 (Qt override)
        if event.type() == QEvent.Type.Enter and obj in self.btn_docs:
            self.doc.setMarkdown(self.btn_docs[obj])
        return super().eventFilter(obj, event)

    # ── paths ──
    def _workspace(self) -> Path:
        return Path(self.ws_edit.text().strip() or DEFAULT_WORKSPACE)

    def _cwd_for(self, kind: str) -> Path:
        ws = self._workspace()
        if kind == "os":
            return ws / OS_REPO
        if kind == "repo":
            return ws / self.repo_combo.currentText()
        return ws

    def _browse(self) -> None:
        d = QFileDialog.getExistingDirectory(
            self,
            "Workspace root",
            self.ws_edit.text(),
            QFileDialog.Option.DontUseNativeDialog,
        )
        if d:
            self.ws_edit.setText(d)
            self._refresh_github()

    def _refresh_github(self) -> None:
        cwd = str(self._cwd_for("repo"))
        token = self.pat_edit.text().strip()
        self.github_panel.refresh(cwd, token)

    # ── running ──
    def _resolve_cmd(self, action: Action) -> str | None:
        if action.needs_msg:
            msg = self.msg_edit.text().strip()
            if not msg:
                QMessageBox.warning(self, "Commit", "Enter a commit message first.")
                return None
            quoted = msg.replace('"', '\\"')
            prefix = ""
            if self.author_cb.isChecked():
                prefix = (
                    'GIT_AUTHOR_NAME="Gnosis.Agent" '
                    'GIT_AUTHOR_EMAIL="gnosis.agent@gnu-in-labs.dev" '
                    'GIT_COMMITTER_NAME="Gnosis.Agent" '
                    'GIT_COMMITTER_EMAIL="gnosis.agent@gnu-in-labs.dev" '
                )
            return f'git add -A && {prefix}git commit -m "{quoted}"'
        return action.cmd

    def run(self, action: Action) -> None:
        if self.proc is not None:
            QMessageBox.information(self, "Busy", "A command is already running.")
            return

        if action.confirm:
            resp = QMessageBox.question(
                self, action.label, action.confirm,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No,
            )
            if resp != QMessageBox.StandardButton.Yes:
                self.log.append(f"• {action.label} cancelled.", "muted")
                return

        cmd = self._resolve_cmd(action)
        if cmd is None:
            return

        cwd = self._cwd_for(action.cwd_kind)
        if not cwd.is_dir():
            self.log.append(f"✗ working dir not found: {cwd}", "fail")
            return

        self._persist()
        self.log.append(f"$ {cmd}", "cmd")
        self.log.append(f"  ↳ {cwd}", "muted")

        self.proc = QProcess(self)
        self.proc.setWorkingDirectory(str(cwd))
        self.proc.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.proc.readyReadStandardOutput.connect(self._read_out)
        self.proc.readyReadStandardError.connect(self._read_err)
        self.proc.finished.connect(self._finished)
        self.proc.errorOccurred.connect(self._proc_error)

        self._set_busy(True)
        self.status.showMessage(f"Running: {action.label}")
        self.proc.start("bash", ["-lc", cmd])

    def _read_out(self) -> None:
        if self.proc:
            data = bytes(self.proc.readAllStandardOutput()).decode("utf-8", "replace")
            for line in data.splitlines():
                self.log.append(line, "out")

    def _read_err(self) -> None:
        if self.proc:
            data = bytes(self.proc.readAllStandardError()).decode("utf-8", "replace")
            for line in data.splitlines():
                self.log.append(line, "err")

    def _finished(self, code: int, _status) -> None:
        if code == 0:
            self.log.append(f"✓ exit 0", "ok")
            self.status.showMessage("Done (exit 0)")
        else:
            self.log.append(f"✗ exit {code}", "fail")
            self.status.showMessage(f"Failed (exit {code})")
        self.log.append("", "muted")
        self.proc = None
        self._set_busy(False)
        self._refresh_github() # Auto-refresh github status after commands (e.g. push)

    def _proc_error(self, _err) -> None:
        if self.proc:
            self.log.append(f"✗ process error: {self.proc.errorString()}", "fail")

    def _stop(self) -> None:
        if self.proc:
            self.log.append("• stopping…", "muted")
            self.proc.kill()

    def _set_busy(self, busy: bool) -> None:
        for b in self.run_buttons:
            b.setEnabled(not busy)
        self.stop_btn.setEnabled(busy)

    def _persist(self) -> None:
        self.settings.setValue("workspace", self.ws_edit.text())
        self.settings.setValue("repo", self.repo_combo.currentText())
        self.settings.setValue("gnosis_author", self.author_cb.isChecked())
        self.settings.setValue("github_pat", self.pat_edit.text())

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self._persist()
        if self.proc:
            self.proc.kill()
        super().closeEvent(event)

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
