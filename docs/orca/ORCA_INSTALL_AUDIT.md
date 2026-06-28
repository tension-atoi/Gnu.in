# Orca Installation Audit and Smart Profile

Generated: 2026-06-28, America/Toronto

Scope: local Orca runtime, user-level Orca profile, GNU.IN workspace shape, agent hooks, auth surfaces, automation surfaces, and reusable prompt/config templates. Secret values were not copied into this document.

## Executive Summary

Orca is installed and running correctly through the Linux `orca-ide` CLI at `~/.local/bin/orca-ide`. The runtime is reachable, graph state is ready, and the current workspace is registered in Orca.

The current registration is broad: `/home/tension_atoi/Projects/Gnu.in` is registered as a `folder`, not as a Git repo. That matches the local state: the root contains a `.git/` stub but is not a valid Git repository. The actual GNU.IN source authority lives in nested Git repos such as `gnu.in-os`, `gnu.in-shell`, `gnu.in-gnosis-app`, and related component repos.

The strongest integration already present is agent status reporting. Orca has hook scripts under `~/.orca/agent-hooks`, a hook endpoint under `~/.config/orca/agent-hooks`, and cross-agent skill symlinks for Orca CLI usage. The weakest areas are automation, source-control templates, browser profile separation, and trust-tiering of agent defaults.

## Current State

### Runtime

- CLI: `orca-ide`
- App: running
- Runtime: ready and reachable
- Graph: ready
- Registered repo count: 1
- Registered project count: 1
- Registered automations: 0
- Saved remote environments: 0
- Browser profiles: only `Default`

### Workspace Registration

Current Orca repo:

- Path: `/home/tension_atoi/Projects/Gnu.in`
- Display name: `Gnu.in`
- Kind: `folder`
- Setup hook policy: `run-by-default`
- Setup script: empty
- Archive script: empty

Current Orca workspace state:

- Main workspace: `Gnu.in`, status `in-progress`
- Additional workspace: `Codex`, status `in-progress`
- Current comment set during this audit: `audited Orca install; drafting smart profile`

### GNU.IN Subrepo Snapshot

All checked subrepos were clean at audit time.

| Repo | Actual branch | Short HEAD |
| --- | --- | --- |
| `gnu.in-os` | `docs/operator-cutover-runbook` | `e79f60e` |
| `gnu.in-shell` | `feat/osd-rust-slice` | `5b7fe27` |
| `gnu.in-gnosis-app` | `live/ii-overhaul-template` | `a46e7d0` |
| `gnuin-hyprconf` | `live/ii-overhaul-template` | `7468978` |
| `gnu.in-design-reference` | `main` | `dde1675` |
| `gnuin-alaelestia-component` | `docs/readme-refresh` | `115929e` |
| `gnu.in-syster-app` | `docs/syster-app-docs-sync` | `d17fc02` |
| `hyprdynamicmonitors` | detached | `ce4292c0` |
| `dot-github` | `docs/readme-refresh` | `7e679f2` |
| `tension-atoi` | `docs/readme-refresh` | `c8f77d2` |
| `gnu.in.lab` | `docs/readme-refresh` | `c0a41c9` |

This differs from parts of the root `CLAUDE.md` branch map, so a smart Orca profile should surface branch drift rather than assuming the doc is current.

## Integration Surfaces

### Agent Hooks

Present:

- `~/.orca/agent-hooks/codex-hook.sh`
- `~/.orca/agent-hooks/claude-hook.sh`
- `~/.orca/agent-hooks/command-code-hook.sh`
- Hook scripts for Copilot, Grok, Gemini, Aider-adjacent agents, Kimi, Devin, Cursor, Droid, OpenClaude, Antigravity.
- Hook endpoint file: `~/.config/orca/agent-hooks/endpoint.env`
- Last status file: `~/.config/orca/agent-hooks/last-status.json`

Hook behavior:

- Hooks post lifecycle/tool payloads to a local Orca loopback endpoint.
- They require `ORCA_AGENT_HOOK_PORT`, `ORCA_AGENT_HOOK_TOKEN`, and `ORCA_PANE_KEY`.
- They fail closed and exit `0` when not inside an Orca-managed pane.

Cross-agent skill symlinks:

- `~/.claude/skills/orca-cli`
- `~/.hermes/skills/orca-cli`
- `~/.vibe/skills/orca-cli`
- `~/.aider-desk/skills/orca-cli`
- `~/.kilocode/skills/orca-cli`

Also present in those agent skill directories:

- `computer-use`
- `orchestration`

### Agent CLI Availability

Installed and responding:

- `codex`: `0.141.0`
- `claude`: `2.1.195`
- `gemini`: `0.43.0-preview.0`
- `opencode`: `1.17.10`

Configured or partially integrated but currently not callable from PATH:

- `grok`
- `copilot`
- `aider`
- `cursor`
- `command-code`

Broken:

- `hermes` is on PATH, but its shim points to a missing venv interpreter.

### Browser Integration

Current state:

- One persistent browser session profile: `Default`
- Orca browser automation commands are available.
- Profile separation is not yet used.

Recommended:

- Create separate browser profiles for admin/authenticated control, GitHub review, and research.
- Keep risky/untrusted browsing away from the default authenticated profile.

### Computer Use

Linux computer-use provider is present:

- App listing: supported
- Window listing: supported
- Element-frame observation: supported
- Click/type/paste/scroll/drag/set-value actions: supported

Limitations:

- Accessibility permission: unsupported
- Screenshots: unsupported
- Hotkeys: unsupported
- Menus/dialog/dock/menubar surfaces: unsupported

Practical conclusion: for this host, prefer Orca browser automation, terminals, worktrees, and orchestration over desktop-wide automation.

## Auth and Security Surfaces

Sensitive Orca files exist and have good owner-only permissions:

- `~/.config/orca/orca-runtime.json`
- `~/.config/orca/orca-e2ee-keypair.json`
- `~/.config/orca/agent-hooks/endpoint.env`
- `~/.config/orca/codex-runtime-home/system-default-auth.json`
- `~/.config/orca/Cookies`
- `~/.config/orca/Local Storage`
- `~/.config/orca/daemon/daemon-v18.token`

Auth material observed by category:

- Orca runtime auth token: present
- Orca E2EE keypair: present
- Orca agent hook token: present
- Orca daemon token: present
- Orca Codex runtime auth JSON: present
- Browser cookies/storage: present
- GitHub CLI auth: three GitHub accounts configured; one active account
- Claude OAuth/plugin credential metadata: present outside Orca config
- Codex auth: present outside Orca config
- Hermes auth files: present, but Hermes executable is currently broken
- Orca remote environments: none
- Orca managed Codex accounts: none
- Orca managed Claude accounts: none

Security notes:

- `agentStatusHooksEnabled` is on.
- Telemetry is opted in.
- Agent defaults are globally high-trust: Codex uses bypass approvals/sandbox, Claude uses skip permissions, and many other agents default to yolo/auto-approve modes.
- Usage JSON files under `~/.config/orca` are world-readable by mode (`0644`). They appeared to be usage telemetry rather than credentials, but they can still reveal behavior and timing.
- Two SSH target entries point to the same remote host and port with different users. Keep this intentional, documented, and audited.

## Automation Surfaces

Currently unused:

- Orca scheduled automations: none
- Terminal quick commands: none
- Source-control AI custom templates: generic `{basePrompt}` only
- Repo setup/archive scripts: empty
- Sparse presets: none

Available and useful:

- `orca-ide automations create`
- `orca-ide worktree create --agent ...`
- `orca-ide orchestration ...`
- `orca-ide terminal create/send/read/wait`
- `orca-ide tab profile ...`
- `orca-ide linear ...`
- `orca-ide repo add`
- `orca-ide repo set-base-ref`

## Recommended Smart Profile

### 1. Register Component Repos Individually

Keep the parent folder workspace as the control room, but register each real component repo so Orca can track branches, diffs, base refs, worktrees, and source-control actions correctly.

Suggested commands:

```sh
orca-ide repo add --path /home/tension_atoi/Projects/Gnu.in/gnu.in-os --json
orca-ide repo add --path /home/tension_atoi/Projects/Gnu.in/gnu.in-shell --json
orca-ide repo add --path /home/tension_atoi/Projects/Gnu.in/gnu.in-gnosis-app --json
orca-ide repo add --path /home/tension_atoi/Projects/Gnu.in/gnuin-hyprconf --json
orca-ide repo add --path /home/tension_atoi/Projects/Gnu.in/gnu.in-design-reference --json
orca-ide repo add --path /home/tension_atoi/Projects/Gnu.in/gnuin-alaelestia-component --json
orca-ide repo add --path /home/tension_atoi/Projects/Gnu.in/gnu.in-syster-app --json
orca-ide repo add --path /home/tension_atoi/Projects/Gnu.in/dot-github --json
orca-ide repo add --path /home/tension_atoi/Projects/Gnu.in/tension-atoi --json
orca-ide repo add --path /home/tension_atoi/Projects/Gnu.in/gnu.in.lab --json
```

Then set default base refs:

```sh
orca-ide repo set-base-ref --repo path:/home/tension_atoi/Projects/Gnu.in/gnu.in-os --ref origin/main --json
orca-ide repo set-base-ref --repo path:/home/tension_atoi/Projects/Gnu.in/gnu.in-shell --ref origin/feat/osd-rust-slice --json
orca-ide repo set-base-ref --repo path:/home/tension_atoi/Projects/Gnu.in/gnu.in-gnosis-app --ref origin/live/ii-overhaul-template --json
orca-ide repo set-base-ref --repo path:/home/tension_atoi/Projects/Gnu.in/gnuin-hyprconf --ref origin/main --json
```

Review `gnuin-hyprconf` first: local branch is `live/ii-overhaul-template`, while the root docs say `main`.

### 2. Add Disabled Automations First

Create automations disabled, inspect the prompts and first run output, then enable selectively.

Daily control-room digest:

```sh
orca-ide automations create --name "GNU.IN daily control-room digest" --trigger weekdays --time 08:45 --provider codex --workspace active --reuse-session --disabled --prompt "Audit the GNU.IN control room. Report subrepo branch drift against CLAUDE.md, dirty trees, pending Orca worktrees, active terminals, failed background agents, and any live-promotion boundary risks. Do not modify files." --json
```

Auth and integration hygiene:

```sh
orca-ide automations create --name "GNU.IN auth and integration hygiene" --trigger weekly --day 0 --time 10:00 --provider codex --workspace active --reuse-session --disabled --prompt "Audit Orca and agent integration health. Check that Orca runtime is ready, hook endpoint exists, auth files remain 0600, stale hook configs are documented, Hermes is callable, browser profiles exist, and no scheduled automation is enabled without explicit review. Do not print token values." --json
```

Release boundary watcher:

```sh
orca-ide automations create --name "GNU.IN release boundary watcher" --trigger daily --time 17:30 --provider claude --workspace active --reuse-session --disabled --prompt "Read gnu.in-os/AGENTS.md and root CLAUDE.md. Summarize release, promotion, and live-target risks. Confirm no direct edits under ~/.local/share/gnuin-shell and no promote-latest run without explicit approval. Do not modify files." --json
```

### 3. Split Browser Profiles

Suggested profiles:

```sh
orca-ide tab profile create --label "GNU.IN Admin" --scope isolated --json
orca-ide tab profile create --label "GitHub Review" --scope isolated --json
orca-ide tab profile create --label "Research Scratch" --scope isolated --json
```

Use `GNU.IN Admin` only for trusted logged-in surfaces. Use `Research Scratch` for untrusted browsing and docs reconnaissance.

### 4. Replace Generic Source-Control AI Templates

Current source-control AI templates are all `{basePrompt}`. Recommended instruction overlays:

Commit message overlay:

```text
Use GNU.IN conventions. Mention component scope first. Preserve live-promotion boundaries. Do not imply deployment or promotion unless the diff actually changes release metadata or promotion scripts. Include test/verification evidence when available.
```

Pull request overlay:

```text
Create a reviewer-ready PR description for the touched GNU.IN component. Include purpose, files changed, verification commands and results, risk boundaries, and whether live promotion is explicitly out of scope. If the change touches gnu.in-os, mention component pinning and materialization impact.
```

Branch name overlay:

```text
Generate a short branch name with one of: docs/, fix/, feat/, chore/, audit/. Include the component name when useful. Avoid claiming release/promotion unless explicitly requested.
```

### 5. Add Trust Tiers for Agent Launches

Current defaults are fast but risky. Keep two mental profiles:

- Trusted local repair: current yolo/bypass defaults are acceptable only for known local source work with clean boundaries.
- Untrusted input/browser/auth work: use fresh worktrees, isolated browser profiles, no secret printing, no direct promotion, and manual review before mutating auth/config.

Do not globally lower friction further. The next useful improvement is adding named quick commands or launch prompts that make the trust tier explicit.

### 6. Repair or Remove Stale Integrations

Recommended cleanup:

- Fix Hermes shim or remove Hermes from active automation plans until the venv is restored.
- Either install the missing CLIs for Grok/Copilot/Aider/Cursor/Command-Code or mark their Orca hook configs as inactive inventory.
- Keep Codex and Claude as primary providers because both are installed and currently integrated.

### 7. Use Orca Comments as Status Memory

Recommended short comments:

- `audit: checking branches/auth/hooks`
- `docs: drafting smart Orca profile`
- `blocked: Hermes shim missing venv`
- `ready: disabled automations drafted`
- `review: branch map drift vs CLAUDE.md`

Use:

```sh
orca-ide worktree set --worktree active --comment "review: branch map drift vs CLAUDE.md" --json
```

## Priority Actions

1. Register nested component repos with Orca.
2. Create isolated browser profiles.
3. Fix the Hermes shim or remove it from planned automations.
4. Add disabled daily/weekly automations and run them manually once.
5. Customize source-control AI templates with GNU.IN boundaries.
6. Review global yolo/bypass agent defaults and keep them out of auth/browser/untrusted workflows.
7. Document the duplicate SSH remote target intent.

## Non-Negotiable Boundaries

- Do not edit `~/.local/share/gnuin-shell/` directly.
- Do not run `tools/promote-latest.sh` without explicit human approval.
- Do not copy secrets, OAuth tokens, cookies, or Orca runtime tokens into prompts, reports, commits, or automations.
- Do not enable scheduled automations that can mutate source or auth until their first dry run has been reviewed.
- Do not treat the root `Gnu.in` folder as a single Git repo; use nested component repos for source-control work.
