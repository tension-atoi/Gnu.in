#!/usr/bin/env python3
"""GNU.IN Pipeline Cockpit — a fast local Qt6 control panel.

A single-file PySide6 GUI that drives the GNU.IN multi-repo release pipeline with
buttons and a live streaming log. Each action is a shell command run through
QProcess (async — the UI never freezes), with stdout/stderr streamed line-by-line
into a colour-coded log pane.

Design notes
------------
- Actions are *data-driven* (the ACTIONS list): add or edit a button by editing
  one entry — label, group, command, working dir, and whether it needs a confirm
  or the commit-message field.
- Destructive steps (push, finish-release, promote) require an explicit confirm.
  `promote-latest` is the project's non-negotiable human-approval gate.
- One command runs at a time; run buttons disable while busy, Stop kills it.
- The workspace root + selected repo resolve each command's cwd, so the same
  git buttons work across every repo in the workspace.

Run
---
    pip install pyside6          # once
    python3 tooling/gnuin_cockpit.py
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

# Run self-contained: skip the xdg-desktop-portal theme probe (it errors when no
# portal is running, e.g. a bare TTY session) and use Qt's built-in Fusion style.
# Our stylesheet sets every colour anyway, so the desktop theme is irrelevant.
os.environ.setdefault("QT_QPA_PLATFORMTHEME", "")

try:
    from PySide6.QtCore import QEvent, QProcess, QSettings, Qt
    from PySide6.QtGui import QFont, QTextCursor
    from PySide6.QtWidgets import (
        QApplication,
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
        QPlainTextEdit,
        QPushButton,
        QSplitter,
        QTextBrowser,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    sys.stderr.write(
        "PySide6 is not installed.\n  pip install pyside6\nthen re-run: "
        "python3 tooling/gnuin_cockpit.py\n"
    )
    sys.exit(1)


# ── Configuration ──────────────────────────────────────────────────────────

DEFAULT_WORKSPACE = str(Path.home() / "Projects" / "Gnu.in")

# Repos in the workspace (CLAUDE.md repository map). The git actions run against
# the selected one; the OS-scoped script actions always target gnu.in-os.
REPOS = [
    "gnu.in-os",
    "gnu.in-shell",
    "gnu.in-gnosis-app",
    "gnuin-hyprconf",
    "gnu.in-design-reference",
    "gnuin-alaelestia-component",
    "gnu.in-syster-app",
]

# cwd kinds: "os" → <workspace>/gnu.in-os, "repo" → <workspace>/<selected repo>,
# "workspace" → the workspace root.
OS_REPO = "gnu.in-os"


@dataclass(frozen=True)
class Action:
    label: str
    group: str
    cmd: str
    cwd_kind: str = "os"  # "os" | "repo" | "workspace"
    danger: bool = False
    confirm: str | None = None
    needs_msg: bool = False
    tip: str = ""


# The pipeline, as data. Edit here to add/retune buttons.
ACTIONS: list[Action] = [
    # ── Checks (safe, read-only) ──
    Action("Status (strict)", "Checks", "tools/status.sh --strict", tip="Tree state"),
    Action("Verify (source)", "Checks", "tools/verify.sh", tip="Source-only verification"),
    Action(
        "Coherence gate",
        "Checks",
        "tools/check-release-coherence.sh",
        tip="All release drift checks",
    ),
    Action(
        "Git status",
        "Checks",
        "git status --short --branch",
        cwd_kind="repo",
        tip="Selected repo working tree",
    ),
    Action(
        "Git log (10)",
        "Checks",
        "git log --oneline -10",
        cwd_kind="repo",
        tip="Recent commits",
    ),
    # ── Session ──
    Action(
        "Activate session (portal)",
        "Session",
        "GNUIN_WAYLAND_WAIT_TIMEOUT=6 bash state/hyprland/scripts/activate_gnuin_graphical_session.sh",
        tip="Bring up graphical-session.target + xdg-desktop-portal (fixes inactive-graphical-session)",
    ),
    Action(
        "Session status",
        "Session",
        "systemctl --user is-active graphical-session.target xdg-desktop-portal.service || true; "
        "echo '— portal —'; "
        "systemctl --user show xdg-desktop-portal.service -p ActiveState -p Result --no-pager",
        tip="Is the graphical session + portal up?",
    ),
    # ── Release rail ──
    Action(
        "Relock components",
        "Release",
        "tools/bump-lock.sh --branch main",
        tip="Pin component revs on main (canonical branch)",
    ),
    Action(
        "Sync version manifest",
        "Release",
        "python3 tools/update-global-version-manifest.py --write",
        tip="GLOBAL-VERSION.json ← lock",
    ),
    Action(
        "Sync release cascade",
        "Release",
        "tools/sync-release-cascade.sh",
        tip="regen → mirror → materialize",
    ),
    Action("Materialize shell", "Release", "tools/materialize-shell.sh", tip="Stage shell from pins"),
    # ── Git ──
    Action(
        "Stage all + commit",
        "Git",
        "",  # built dynamically (needs the message)
        cwd_kind="repo",
        needs_msg=True,
        tip="git add -A && git commit",
    ),
    Action(
        "Pull (ff-only)",
        "Git",
        "git pull --ff-only",
        cwd_kind="repo",
        tip="Fast-forward only",
    ),
    Action(
        "Push",
        "Git",
        "git push",
        cwd_kind="repo",
        danger=True,
        confirm="Push the selected repo to its remote?",
        tip="Publish commits",
    ),
    # ── Build / Deploy (guarded) ──
    Action(
        "Finish release",
        "Build / Deploy",
        "tools/finish-release.sh",
        danger=True,
        confirm="Run finish-release.sh? This pushes every pinned component.",
        tip="Push all pinned components",
    ),
    Action(
        "Promote latest",
        "Build / Deploy",
        "tools/promote-latest.sh",
        danger=True,
        confirm=(
            "PROMOTE to the live session?\n\n"
            "This is the project's human-approval gate — it mutates the live "
            "runtime. Continue only if you intend to deploy."
        ),
        tip="⚠ Live deploy — human-approval gate",
    ),
]

GROUP_ORDER = ["Checks", "Session", "Release", "Git", "Build / Deploy"]


# Per-action "stories" rendered in the right panel on hover. Written for someone
# who does NOT know git: each explains what happens, why it matters, and when to
# press it — and, for the shipping steps, the what/where/when of a deployment.
INTRO_DOC = """\
# GNU.IN Pipeline Cockpit

**Hover any button on the left** — this panel tells its story: *what* it does,
*why* it matters, and *when* to press it.

## The big picture

Shipping GNU.IN is like moving a parcel through a chain of workshops. The code
lives in several **repos** (workshops). To get a change from your editor onto the
running desktop, the parcel passes, in order, through:

1. **Checks** — inspect the parcel. Is the workshop tidy? Does everything still
   fit together? (Safe — reads only, changes nothing.)
2. **Release** — seal the parcel: write down exactly which version of each part
   goes in the box, and lay out the assembled kit.
3. **Git** — record the change in the logbook (*commit*) and ship the box to the
   shared warehouse (*push*) so it's backed up and others can see it.
4. **Build / Deploy** — open the box on the real machine and put the new desktop
   into service (*promote*). This is the only step that touches what you see live.

Green ✓ means a step succeeded; red ✗ means it stopped and the log explains why.
Nothing here changes your live desktop **until** you reach *Promote latest* — the
steps before it are all reversible.
"""

DOCS: dict[str, str] = {
    # ── Checks ──
    "Status (strict)": """\
# Status (strict)

**What.** Takes the pulse of the whole system: which version is checked out, what
files changed, whether the background services are alive, and whether the running
desktop matches the source.

**Why.** It's your dashboard. Before and after any real change you want to know
"is everything where I expect it?" *Strict* means it fails loudly on the smallest
discrepancy (an unexpected changed file, a service down) instead of glossing over
it.

**When.** First thing, and any time something feels off. A red result here is a
*stop and look* — read the lines above it; usually one says exactly what's wrong
(e.g. a file left modified, or a service not running).

It changes **nothing** — it only reports.
""",
    "Verify (source)": """\
# Verify (source)

**What.** Runs the full source self-check: all the component test suites and the
contracts that encode the project's rules (the "this must always be true"
assertions baked into the code).

**Why.** This is the safety net that proves a change didn't quietly break a rule.
The contracts are the project's memory — they catch regressions a human would
miss. If verify is green, the source is internally consistent.

**When.** After editing anything, and always before committing or shipping. Treat
a green verify as the entry ticket to the Git and Deploy steps.

It builds and tests in a scratch area; it does **not** touch your live desktop.
""",
    "Coherence gate": """\
# Coherence gate

**What.** Checks that all the version numbers and "which revision of each part"
records agree with each other across every repo — the lockfile, the version
manifest, the design tokens, the branch docs.

**Why.** In a multi-part project it's easy for the records to drift: the box says
"part A v2" but the shelf holds v3. That mismatch causes confusing, hard-to-trace
bugs. This gate makes drift impossible to ship — it fails until the records line
up again.

**When.** After *Relock* or *Sync* steps, and before *Finish release*. It's the
referee that confirms the paperwork matches the parts.

Read-only: it reports agreement or disagreement, fixing nothing itself.
""",
    "Git status": """\
# Git status

**What.** Shows, for the selected repo, which branch you're on and which files
have been changed but not yet recorded.

**Why.** Git is the logbook of every change. Before you "record" anything you want
to see exactly what's pending — like reviewing a receipt before signing. The
`[ahead N]` note means you have N recorded changes not yet shipped to the shared
warehouse.

**When.** Any time, especially before *Stage all + commit* (to see what you're
about to record) and before *Push* (to see what you're about to ship).

Completely safe — it only looks.
""",
    "Git log (10)": """\
# Git log (last 10)

**What.** Lists the ten most recent entries in the selected repo's logbook — each
a short line: a code and a one-sentence summary of a recorded change.

**Why.** It's the recent history: what happened, in what order. The code on each
line is that change's permanent address, so any past state can always be found
again. Reading it tells the story of how the project got to "now".

**When.** To get your bearings, to confirm your last commit landed, or to find the
address of an earlier change.

Read-only.
""",
    # ── Session ──
    "Activate session (portal)": """\
# Activate session (portal)

**What.** Tells the system "a graphical desktop is now running" and starts the
**portal** — the helper that lets apps open file pickers, pick screenshots, read
your light/dark theme, and so on.

**Why.** Hyprland can be drawing your windows while the system's *session
bookkeeping* never got switched on. That happens when the desktop was started the
"quick" way instead of through the managed launcher. The symptom: apps print
errors about `org.freedesktop.portal`, file dialogs misbehave, theming looks off,
and `Status (strict)` says **inactive-graphical-session**.

**What it does, plainly.** It waits for the screen to be ready, copies the
session's details to the background manager, then switches on the "graphical
session" and the portal. It's safe to press repeatedly — if everything is already
on, it changes nothing.

**When.** Press it once after logging in if *Session status* shows the portal is
down, or any time apps complain about the portal. It only affects this login
session; it does not deploy or change code.
""",
    "Session status": """\
# Session status

**What.** Reports whether the "graphical session" and the **portal** are
currently running.

**Why.** It's the quick health check behind the portal warnings. `active` on both
lines means apps can open file pickers and read your theme normally. Anything else
(`inactive`, `failed`) explains those `org.freedesktop.portal` messages and means
you should press **Activate session (portal)**.

**When.** Any time you see portal errors, or right after *Activate session* to
confirm it worked. Read-only — it only looks.
""",
    # ── Release ──
    "Relock components": """\
# Relock components

**What.** Writes down the exact current revision of every component repo into the
shared lockfile — pinned to the canonical **main** line.

**Why.** The project is assembled from several parts that each move on their own.
The lockfile is the bill of materials: "this release uses *exactly* these
revisions." Without it, two people (or two machines) could assemble subtly
different desktops. Pinning to **main** keeps everyone on the one official line
rather than a personal side-branch.

**When.** After a component has advanced and you want the assembled product to
pick up its new revision. Always follow it with *Sync version manifest* and the
*Coherence gate* so the paperwork stays consistent.

It edits records (the lockfile), not the live desktop — and it's reversible until
committed.
""",
    "Sync version manifest": """\
# Sync version manifest

**What.** Re-writes the global version manifest so the per-component revisions it
lists match the lockfile exactly.

**Why.** The manifest is a second copy of "which revision of each part" used
elsewhere in the build. After a relock it can fall out of step with the lockfile;
this re-aligns them. If you skip it, the *Coherence gate* will (correctly) refuse
to pass.

**When.** Immediately after *Relock components*, every time.

Edits a record file only; reversible until committed.
""",
    "Sync release cascade": """\
# Sync release cascade

**What.** Runs the chained refresh: regenerate the design tokens, copy them into
the places that consume them, and re-assemble the staged desktop — one command end
to end.

**Why.** Some parts are *generated* from others (for example, colours and sizes
flow from one source of truth out to several consumers). Doing those steps by hand
in the wrong order is how drift creeps in. The cascade does them in the correct
order, every time.

**When.** After changing design tokens or component pins, when you want the staged
build to reflect everything consistently.

Works in the staging area; your live desktop is untouched.
""",
    "Materialize shell": """\
# Materialize shell

**What.** Assembles the desktop shell into the staging area from the exact
revisions named in the lockfile — copying the right files into place.

**Why.** You never hand-copy files between repos (that's how mismatches happen).
This is the official assembler: given the bill of materials, it lays out the kit
ready to verify or build. It guarantees what you test is what the lockfile
describes.

**When.** Before verifying or building, or whenever you want the staged shell to
reflect the current pins.

Writes into the staging area only — not the live desktop.
""",
    # ── Git ──
    "Stage all + commit": """\
# Stage all + commit

**What.** Records every pending change in the selected repo as one entry in the
logbook, with the message you type in the box above.

**Why.** A *commit* is a permanent, named snapshot — a save point you can always
return to. The message is the story for your future self: *what* changed and
*why*. Good messages turn the logbook into a readable history instead of a pile of
mystery saves.

**When.** Once a change is complete and *Verify* is green. Write a clear message
first. Tick **"Commit as Gnosis.Agent"** if this change was prepared by the agent,
so the authorship is honest.

This records locally only — it does **not** ship anywhere yet. Nothing is public
until you *Push*.
""",
    "Pull (ff-only)": """\
# Pull (fast-forward only)

**What.** Brings the selected repo up to date with the shared warehouse, but only
if it can do so cleanly by simply moving forward (no tangled merge).

**Why.** Others (or another machine) may have shipped changes. Pulling keeps you
in sync. "Fast-forward only" is the safe setting: if histories have diverged it
*stops* rather than creating a messy automatic merge — telling you to sort it out
deliberately.

**When.** Before starting new work, and before *Push*, to make sure you're
building on the latest.

Updates your local copy; safe — it refuses anything risky.
""",
    "Push": """\
# Push  ⚠ publishes

**What.** Ships your recorded commits from the selected repo up to the shared
warehouse (the remote).

**Why.** Until you push, your commits live only on this machine. Pushing backs
them up and makes them visible to everyone and every other machine — this is the
moment a change becomes *shared reality*. **What** travels: your local commits.
**Where**: the repo's remote. **When**: now, on your click.

**When to press.** After committing and a green *Verify*, when you're confident the
change is ready to be seen by others.

Asks for confirmation first. It does not change the live desktop — but it *is*
public and not as trivially undone, so it's treated as a careful step.
""",
    # ── Build / Deploy ──
    "Finish release": """\
# Finish release  ⚠ publishes every part

**What.** Pushes *all* the pinned component repos for this release to their
remotes, so the whole bill of materials is published together, not just one part.

**Why.** A release is only reproducible if every part it names is actually
available in the shared warehouse. This step ships them as a set, so anyone (or any
machine) can later rebuild this exact release. **What**: every pinned component.
**Where**: each component's remote. **When**: when you're cutting the release.

**When to press.** After the *Coherence gate* is green and you've decided this is
the release. It's the "make it official and complete" button.

Asks for confirmation. Publishes widely — do it deliberately.
""",
    "Promote latest": """\
# Promote latest  ⚠ LIVE DEPLOY — human-approval gate

**What.** Takes the freshly built desktop and puts it **into service on the real,
running machine** — replacing what's live now.

**Why.** Everything before this was rehearsal in safe areas. This is opening night:
**what** is deployed — the latest built desktop; **where** — your live session;
**when** — the instant you confirm. After this, what you see and use changes.

**When to press.** Only when checks and the build are green *and* you intend to run
the new desktop right now. This is the project's deliberate **human-approval
gate** — it is never automated, by design, because it is the one step that can
disrupt a working machine.

Strong confirmation required. If unsure, run the *Checks* again first; promotion
can wait, a broken live session cannot.
""",
}


# ── Log pane ───────────────────────────────────────────────────────────────

class LogView(QPlainTextEdit):
    """Read-only, monospace, dark log with simple colour roles."""

    COLORS = {
        "cmd": "#FF8E40",      # accent — the command header
        "out": "#D7DCE2",      # stdout
        "err": "#E5707A",      # stderr
        "ok": "#8DA982",       # success exit
        "fail": "#E5484D",     # failure exit
        "muted": "#7C828A",
    }

    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
        f = QFont("JetBrains Mono")
        f.setStyleHint(QFont.Monospace)
        f.setPointSize(10)
        self.setFont(f)
        self.setStyleSheet(
            "QPlainTextEdit{background:#0F1115;color:#D7DCE2;border:1px solid #1A2026;}"
        )
        self.setMaximumBlockCount(10000)

    def append(self, text: str, role: str = "out") -> None:
        color = self.COLORS.get(role, self.COLORS["out"])
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        safe = (
            text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        cursor.insertHtml(f'<span style="color:{color};white-space:pre-wrap;">{safe}</span>')
        cursor.insertBlock()
        self.setTextCursor(cursor)
        self.ensureCursorVisible()


# ── Main window ────────────────────────────────────────────────────────────

class Cockpit(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GNU.IN Pipeline Cockpit")
        self.resize(1360, 740)
        self.settings = QSettings("gnu-in-labs", "pipeline-cockpit")

        self.proc: QProcess | None = None
        self.run_buttons: list[QPushButton] = []
        self.btn_docs: dict[QPushButton, str] = {}

        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)

        outer.addLayout(self._build_config_row())
        body = QSplitter(Qt.Horizontal)
        body.addWidget(self._build_action_panel())
        body.addWidget(self._build_log_panel())
        body.addWidget(self._build_doc_panel())
        body.setStretchFactor(0, 0)
        body.setStretchFactor(1, 1)
        body.setStretchFactor(2, 0)
        body.setSizes([320, 620, 420])
        outer.addWidget(body)

        self.status = self.statusBar()
        self.status.showMessage("Ready")
        self._apply_theme()

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
        row.addWidget(self.repo_combo)

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
            "QTextBrowser{background:#0F1115;color:#C7CDD4;border:1px solid #1A2026;"
            "padding:10px;}"
        )
        self.doc.setMarkdown(INTRO_DOC)
        v.addWidget(self.doc, 1)
        return panel

    def eventFilter(self, obj, event):  # noqa: N802 (Qt override)
        # Hover a run button → show its story in the right panel. The text stays
        # on screen after the cursor leaves so it can be read/scrolled.
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
        # Qt's own dialog (not the portal file-chooser) so it works with no
        # xdg-desktop-portal running.
        d = QFileDialog.getExistingDirectory(
            self,
            "Workspace root",
            self.ws_edit.text(),
            QFileDialog.Option.DontUseNativeDialog,
        )
        if d:
            self.ws_edit.setText(d)

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
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
            )
            if resp != QMessageBox.Yes:
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
        self.proc.setProcessChannelMode(QProcess.SeparateChannels)
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


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("GNU.IN Pipeline Cockpit")
    app.setStyle("Fusion")  # self-contained, theme-independent
    base = QFont("sans-serif", 10)  # concrete family ⇒ no empty-description warning
    app.setFont(base)
    win = Cockpit()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
