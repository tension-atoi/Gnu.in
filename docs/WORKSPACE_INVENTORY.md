# GNU.IN Workspace Inventory

_Generated: 2026-06-16_

This document is a cross-repo snapshot of the GNU.IN workspace: what is done,
what is in progress, what is pending, and what has not been addressed.

---

## 1. Workspace Overview

The `~/Projects/Gnu.in/` folder is the org-level workspace for **gnu-in-labs**:
an experimental local-first desktop runtime on Hyprland + Quickshell. It is a
multi-repo project wired together by `gnu.in-os` as the integration authority.

**Current release train:** v0.12.0 / channel=beta  
**Latest promoted build:** `20260616-110125-824d3e1`

---

## 2. Repository Roster

### 2.1 `gnu.in-os` — OS Integration Workspace (source authority)

**Role:** Canonical build/release/engine repository. Owns release staging,
contracts, engine services, tooling, and the component lock.

**Recent commits:**
- `698d27a` chore(release): promote 20260616-110125-824d3e1
- `c67084a` chore(promote): auto-sync branch doc checkpoint
- `824d3e1` test(contract): assert engine re-exports shared config authority

**Sub-structure:**
- `engine/` — gnosis-engine (Rust), gnosis-sentinel, blob.in, gnuin-vector-core, hyprland-gnosis-plugin
- `contracts/` — runtime.toml, surfaces.toml, ipc/, gnomon/, state_authority.toml
- `agent_tasks/` — 16+ SPEC-*.json agent mission files (A01–B05, D02)
- `tools/` — build.sh, promote-latest.sh, verify.sh, status.sh, materialize-shell.sh, backup.sh, etc.
- `release/` — VERSION (0.12.0), CHANNEL (beta), LATEST-BUILD, GLOBAL-VERSION.json
- `docs/` — PROJECT_CHARTER, ROADMAP, AGENTIC_OPERATING_MODEL, CODEBASE_STANDARDS, SECURITY_AND_AUTOMATION_BOUNDARIES, VERSIONING_AND_RELEASES, and several audit/analysis docs

**Pinned components (components.lock.toml):**

| Component | Kind | Pinned rev |
|-----------|------|-----------|
| gnu.in-shell | product | 7273849... |
| gnu.in-gnosis-app | product | 9ac677d... |
| gnuin-hyprconf | service | 2abce25... |
| gnu.in-design-reference | reference | 18b8355... |
| hyprdynamicmonitors | optional-service | ce4292c0... |

**Status:** ✅ Active and healthy. Build/promote loop working.

---

### 2.2 `gnu.in-shell` — Quickshell/QML Desktop Shell

**Role:** Shell product surface. QML/Quickshell UI for taskbar, dock, overview,
panels, notifications, OSD, media controls, clipboard, wallpaper, sidebars,
launcher, etc.

**Branch:** `live/jj-overhaul-template`

**Recent commits:**
- `7273849` feat(surfaces): expose runtime authority state
- `d3f5f3d` feat(settings): canonicalize native page routing
- `6944eb0` feat(taskbar): refresh minimized app visibility

**Structure:**
- `services/` — MonitorService, InputManager, GnosisShellRuntime, ShellSettingsService, LauncherService…
- `components/` — UIKit, motion atoms, settings, dock, panel, overlay surfaces
- `tests/` — 40+ contract tests covering every major surface
- `tools/` — runtime helper scripts, component test runner, wallpaper tools

**Verification:**
```sh
tools/run-component-tests.sh
```

**Status:** ✅ Active. JJ overhaul template in place.

---

### 2.3 `gnu.in-gnosis-app` — Gnosis App Surface

**Role:** Tracking/overlay/voice/vision QML surface and shell-facing client
adapters. Materializes into shell via `tools/materialize-into-shell.sh`.

**Branch:** `live/ii-overhaul-template`

**Recent commits:**
- `9ac677d` refactor(surfaces): route gnosis app through surface router
- `ebb9cb7` fix(gnosis): promote runtime authority contracts
- `032d28e` Support compact JJ Gnosis status widget

**Key components:** GnosisApp.qml, GnosisStatusWidget.qml, GnosisTrackerOverlay.qml,
SemanticOverlay.qml, GuardianGate.qml, GnosisTracker native QML plugin.

**Status:** ✅ Active. Source boundary with gnu.in-shell clean.

---

### 2.4 `gnuin-hyprconf` — Rust Hyprland Settings Authority

**Role:** Rust crates for Hyprland config parsing, validation, live apply,
persistence, IPC. `hyprconfd` is the CLI/daemon. UI is handled by shell (QML).

**Branch:** `live/ii-overhaul-template`

**Recent commits:**
- `2abce25` fix(config): derive Default for CompatConfig
- `e2d99df` feat(settings): add JJ compat timing key
- `b6c2474` feat(settings): add JJ conflict killer policy keys

**Crates:** `hyprconf_core`, `hyprconf_ipc`, `hyprconfd`

**Verification:**
```sh
cargo test --workspace
```

**Status:** ✅ Active. Config writes to `~/.config/hypr/gnuin-shell.conf`.

---

### 2.5 `gnu.in-design-reference` — Design Tokens & Reference

**Role:** Canonical design assets, token source (blob.in/tokens.json,
colors_and_type.css), imported design boards, and provenance. Not for direct
runtime import; runtime-eligible assets are overlaid via materialize-shell.sh.

**Branch:** `codex/runtime-design-rewrite`

**Recent commits:**
- `18b8355` blob.in: defer rust default flip for early phases
- `5da4a7a` blob.in: embed R10 day status in review packets
- `0b70f06` blob.in: add R10 daily coverage view

**Key artifacts:** tokens.json, colors_and_type.css, fonts/Montreal, _ds_bundle.js,
blob.in/ (Rust shape engine), design_refs/, preview/ (brand-mascot, brand-states)

**Status:** ✅ Active. blob.in R10 phase in review. Rust default flip deferred.

---

### 2.6 `gnuin-alaelestia-component` — QML/C++ Component Library

**Role:** Reusable visual units (atoms, molecules, recipes) for GNU.IN UIs.
Not the shell runtime; staged into integration builds by `gnu.in-os`.

**Recent commits:**
- `732320d` feat: add right-click component inspection hook to CustomMouseArea
- `7e51156` feat: expose component inspection state layer hook
- `4d0d3ef` chore: bootstrap alaelestia component repo

**Atoms:** MaterialIcon, StyledRect, StyledText, StyledSwitch, StyledSlider,
StyledTextField, StyledScrollBar, Tooltip, StateLayer, CustomMouseArea

**Molecules:** IconButton, TextButton, ToggleButton, SwitchRow, Menu,
SectionHeader, PropertyRow, SplitButton, IconTextButton

**Recipes:** CollapsibleSection, ConnectionInfoSection

**Verification:**
```sh
tools/verify-alaelestia.sh
```

**Status:** ✅ Bootstrap complete. Component inspection hooks added.

---

### 2.7 `gnu.in-syster-app` — Native Coding App (syster.app)

**Role:** Native QtQuick/QML refactor of Codex Desktop coding app. No Electron,
no webview. Wired to Gnosis D-Bus backend.

**Recent commits:**
- `1b32776` fix: repair native QML shell so the app window actually loads
- `b0f8f7f` chore: add system-wide install script
- `166c9a0` feat: native syster.app refactor (Phases 0–4 complete)

**Build/verify:**
```sh
cmake -S syster-app -B syster-app/build -DCMAKE_BUILD_TYPE=Release
cmake --build syster-app/build -j4
syster-app/build/syster-app --self-test
syster-app/build/syster-app --bench-text
```

**Docs:** codex-frontend-study, openai-auth-boundary, pretext-native-integration,
syster-app-native-refactor, syster-app-tooling-ideas

**Status:** ✅ Phases 0–4 complete. Window loads. Self-test and bench passing.

---

### 2.8 `sigma-flutter` — GPUI Rust File Manager Rebuild

**Role:** Rebuild of the Sigma file manager using GPUI (Rust native). Full UX
and functional parity with original Flutter implementation. No GTK/GNOME deps.

**Recent commits:**
- `2441be9` Fix compile errors (GPUI Stateful/ClipboardItem/on_click)
- `3db89bb` Day6: HomeDashboard static render with live navigation
- `6742bcf` P2 Day5: Settings panel — Gnosis theme display, show-hidden toggle

**Architecture:** GPUI frontend → rust_lib_sigma_flutter backend (fs, search,
extensions, network mounts, Gnosis config). Separate gpui-frontend/ Rust crate.

**Milestones:** All 6 PLANNED (M1–M6 not yet COMPLETE).

**Agent state:** Parallel tracks active (implementation + E2E testing
sub-orchestrators). `.agents/BRIEFING.md` tracks sentinel state.

**Untracked files present:** `.agents/`, `CMakeLists.txt`, `src/`

**Status:** ⚠️ In progress. Active agent work. Compile errors being fixed.
No milestone marked complete yet.

---

### 2.9 `hyprdynamicmonitors` — Dynamic Monitor Profiles (external)

**Role:** Optional service for automatic monitor profile switching. External
upstream (fiffeek/hyprdynamicmonitors), pinned as optional-service in gnu.in-os.

**Recent commits:** Upstream bug fixes (panic fix for missing TUI profile).

**Status:** ✅ Pinned at ce4292c0. Adoption policy: optional delegated
display-profile authority; GNU.IN has no direct monitor writer.

---

### 2.10 `dot-github` — GitHub Org Profile

**Role:** `.github` repo powering the public gnu-in-labs organization page.
Contains profile/README.md, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, PR template.

**Recent commits:**
- `2f0c33e` docs: clarify public profile update guidelines
- `5300f3f` docs: refresh public organization profile
- `8f5b8b4` docs: add explicit agent/automation posture

**Status:** ✅ Healthy. Public profile up to date.

---

### 2.11 `tension-atoi` — Personal Public Profile

**Role:** Personal GitHub profile README + assets.

**Recent commits:** `159375e` docs: add public profile

**Status:** ✅ Minimal. Profile exists.

---

### 2.12 `gnu.in.lab` — Private Lab Repository

**Role:** Private staging area for lab/experimental work.

**Recent commits:** `26da150` Initialize private lab repository

**Status:** 🟡 Initialized only. Content minimal.

---

## 3. Roadmap Status (from gnu.in-os/docs/ROADMAP.md)

### Phase 0: Governance baseline — IN PROGRESS

| Item | Status |
|------|--------|
| Project charter | ✅ Done |
| Public AI/vibe-coding stance | ✅ Done |
| AGPL-3.0 root license | ✅ Done |
| CODEOWNERS baseline | ✅ Done |
| CI workflow tied to verify script | ✅ Done |
| Security workflow baseline | ✅ Done |
| Dependabot for package roots | ✅ Done |
| License policy for mixed AGPL/MIT components | ❌ Not done |
| Branch protection / rulesets requiring review | ❌ Not done |
| CI green confirmed on clean runner | ❌ Not confirmed |

### Phase 1: Source and CI hardening — NOT STARTED

Tasks: split status.sh source-only/runtime, Rust format checks, shell format
checks, per-manifest test matrix, CI docs-link validator, pin high-risk Actions.

### Phase 2: Security boundary documentation — NOT STARTED

Tasks: D-Bus methods by risk level, Gnomon/Sentinel socket schemas, shared-memory
layouts, command-generation policy, screenshot/audio behavior, privacy notes.

### Phase 3: Local release discipline — PARTIALLY DONE

Build tooling exists (`tools/build.sh`, `promote-latest.sh`, version-signature,
build-manifest). Missing: documented rollback flow, artifact checksum verify
command, private GitHub release channel wired.

### Phase 4: Architecture documentation — NOT STARTED

Tasks: ARCHITECTURE.md, surface→contracts mapping, service docs, Gnosis/Gnomon/
Sentinel documentation, Quickshell/Hyprland/D-Bus/IPC diagram.

### Phase 5: gnu6.live boundary — NOT STARTED

Define site repo, static artifact format, keep deploy manual, publish manifesto
and screenshots when available.

### Phase 6: External tester path — NOT STARTED

Document distro/hardware assumptions, install/uninstall paths, smoke tests,
log collection policy, known issues, feedback template.

---

## 4. Tooling Assessment

### Claude Desktop setup

| Item | Status |
|------|--------|
| `CLAUDE.md` at workspace root | ✅ Created today |
| `.claude/settings.local.json` at root | ✅ Exists (extensive permission allowlist) |
| Per-repo AGENTS.md contracts | ✅ Present in all major repos |

### Build / verification tooling

| Tool | Location | Status |
|------|----------|--------|
| `tools/build.sh` | gnu.in-os | ✅ Working |
| `tools/promote-latest.sh` | gnu.in-os | ✅ Working (human-gated) |
| `tools/verify.sh` | gnu.in-os | ✅ Working |
| `tools/status.sh` | gnu.in-os | ✅ Working (source+runtime mixed) |
| `tools/materialize-shell.sh` | gnu.in-os | ✅ Working |
| `tools/backup.sh` | gnu.in-os | ✅ Working |
| `tools/run-component-tests.sh` | gnu.in-shell | ✅ Working |
| `tools/verify-alaelestia.sh` | gnuin-alaelestia-component | ✅ Working |
| `cargo test --workspace` | gnuin-hyprconf | ✅ Working |
| `syster-app --self-test` | gnu.in-syster-app | ✅ Working |
| CI (`ci.yml`, `security.yml`, etc.) | gnu.in-os/.github | ⚠️ Exists, green on clean runner not confirmed |

### Missing / not addressed

- `tools/status.sh` source-only mode (needed for CI without graphical session)
- Rust formatting enforcement in CI (rustfmt check job)
- Shell formatting enforcement (shfmt/shellcheck in CI)
- Artifact checksum verification command
- Private GitHub release channel for Gnosis package manager
- Documented rollback flow (beyond `promote-latest.sh`)
- ARCHITECTURE.md
- D-Bus method risk inventory
- Gnomon/Sentinel socket schema documentation

---

## 5. Work Threads

_State verified against live git on 2026-06-16. A thread counts as **active** only
if it has an in-progress branch with recent commits; threads whose milestone is
reached and that have gone dormant are moved to **Closed** below._

### 5.1 Active

| Thread | Repo(s) | Branch | State | Last commit |
|--------|---------|--------|-------|-------------|
| Live overhaul template — JJ | gnu.in-shell | `live/jj-overhaul-template` | Active | 19h ago |
| Live overhaul template — II | gnu.in-gnosis-app, gnuin-hyprconf | `live/ii-overhaul-template` | Active | 42m ago |
| GPUI Sigma rebuild | sigma-flutter | `claude/visual-spec-continuation-lq0uci` | Active — agent tracks, 15 uncommitted files | 16m ago |
| blob.in R10 phase | gnu.in-design-reference | `codex/runtime-design-rewrite` | In review (paused) | 4d ago |

> The JJ and II efforts are the same "live overhaul template" program split by
> branch family; they are unified here as one program with two active legs.

### 5.2 Closed / completed

| Thread | Repo | Outcome | Closed because |
|--------|------|---------|----------------|
| syster.app native refactor | gnu.in-syster-app | Phases 0–4 complete; window loads, self-test + bench passing | Milestone reached; dormant 7d. Repo now sits on `live/ii-overhaul-template` — any further work folds into the II leg above. |
| Alaelestia component inspection | gnuin-alaelestia-component | Inspection hooks shipped to `main` | Feature merged; dormant 12d. No open follow-up. |

---

## 6. Not Addressed / Open Questions

1. **`sigma-flutter` untracked files** — `.agents/`, `CMakeLists.txt`, `src/` not committed. Needs triage.
2. **`gnu.in.lab`** — initialized only, purpose/content not defined beyond "private lab".
3. **`docs/` at workspace root** — empty before this inventory was created.
4. **`tools/` at workspace root** — contains only `superpowers/` dir (currently empty).
5. **`50-flatpak-appstream.rules`** at workspace root — orphan file, purpose/ownership unclear.
6. **`error.log`** at workspace root — removed after it was found to contain private account metadata. Future `*.log` files are ignored at the workspace root.
7. **`DP-1/`, `DP-2/`** — screenshot artifacts of display outputs, not in any repo. Audit artifacts only.
8. **`audits/`** — `settings-launcher-2026-06-07/` audit with screenshots. Not tracked in any repo.
9. **Gnosis engine public readiness** — listed as "in progress" on public profile but no external tester path defined yet.
10. **`gnu6.live` website** — mentioned in profile but no dedicated repo or deployment plan documented.
11. **License policy** — Phase 0 item still open; mixed AGPL/MIT component policy not finalized.
12. **Branch protection** — no rulesets requiring review or checks confirmed on main branches.

---

## 7. Immediate Recommendations

These are low-effort, high-value items to unblock Phase 0 completion:

1. **Commit or gitignore untracked files in `sigma-flutter`** — `.agents/`, `CMakeLists.txt`, `src/` are dirty and block clean state verification.
2. **Add `docs/LICENSE_POLICY.md`** to `gnu.in-os` (already listed in docs index but Phase 0 item open) — draft AGPL/MIT split policy.
3. **Split `tools/status.sh`** into source-only and runtime modes so CI can run without a graphical session.
4. **Enable branch protection** on `main` in core repos via GitHub settings.
5. **Triage orphan workspace files** — `50-flatpak-appstream.rules`, `DP-1/`, `DP-2/`, `audits/` — decide if any belong in a repo.
6. **Define `gnu.in.lab` scope** — what goes there vs. `gnu.in-os`.

---

_This inventory was produced by Claude (Cowork mode) on 2026-06-16 by reading
all repo documentation, AGENTS.md contracts, roadmap, git logs, and workspace
structure. It is a point-in-time snapshot, not a live dashboard._
