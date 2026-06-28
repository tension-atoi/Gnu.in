# BRIEFING — 2026-06-17T10:35:30-04:00

## Mission
Implement GitHub native PAT authentication, adapt native Qt6 styles from SysterTheme, and build a local installer for gnu.in-cockpit.

## 🔒 My Identity
- Archetype: self
- Roles: orchestrator, user_liaison, human_reporter, successor
- Working directory: /home/tension_atoi/Projects/Gnu.in/.agents/sub_orch_impl/
- Original parent: Project Orchestrator
- Original parent conversation ID: 93c5aade-0d72-478e-a46e-a3dc7c62b0c4

## 🔒 My Workflow
- **Pattern**: Project
- **Scope document**: /home/tension_atoi/Projects/Gnu.in/.agents/sub_orch_impl/SCOPE.md
1. **Decompose**: We decompose the implementation into five core steps:
   - Milestone 1: GitHub native REST API authentication integration (R1)
   - Milestone 2: UI styling adaptation from SysterTheme (R2)
   - Milestone 3: Local installation script and .desktop file setup (R3)
   - Milestone 4: Phase 1 E2E tests passing (Tiers 1-4)
   - Milestone 5: Phase 2 adversarial coverage hardening (Tier 5)
2. **Dispatch & Execute**:
   - **Direct (iteration loop)**: We run Explorer -> Worker -> Reviewer -> Challenger loop for each milestone directly.
3. **On failure** (in this order):
   - Retry: nudge stuck agent or re-send task
   - Replace: spawn fresh agent with partial progress
   - Skip: proceed without (only if non-critical)
   - Redistribute: split stuck agent's remaining work
   - Redesign: re-partition decomposition
   - Escalate: report to parent (sub-orchestrators only, last resort)
4. **Succession**: Self-succeed at 16 spawns, write handoff.md, spawn successor.
- **Work items**:
  1. R1 GitHub REST API [pending]
  2. R2 UI Styling [pending]
  3. R3 Installation script [pending]
  4. E2E Test Suite verification [pending]
  5. Adversarial coverage hardening [pending]
- **Current phase**: 1
- **Current focus**: Planning and Initial Exploration

## 🔒 Key Constraints
- NO GNOME OR GTK. Use Qt6 Native only.
- Never reuse a subagent after it has delivered its handoff — always spawn fresh

## Current Parent
- Conversation ID: 93c5aade-0d72-478e-a46e-a3dc7c62b0c4
- Updated: 2026-06-17T10:35:30-04:00

## Key Decisions Made
- Use requests library for REST API queries to fetch PRs and recent runs.
- Extract styling parameters from systertheme.hpp and implement stylesheet classes or styling functions for cockpit views.
- Create local installation script using standard user paths (~/.local/bin, ~/.local/share/applications).

## Team Roster
| Agent | Type | Work Item | Status | Conv ID |
|-------|------|-----------|--------|---------|
| sub_orch_m1 | self | R1 GitHub API Integration | completed | 38894c54-eef8-45e6-a5e2-cf2203765329 |
| sub_orch_m2 | self | R2 UI Styling Adaptation | in-progress | c9276cb5-9529-4a13-812b-7e363a0d77d3 |

## Succession Status
- Succession required: no
- Spawn count: 2 / 16
- Pending subagents: [c9276cb5-9529-4a13-812b-7e363a0d77d3]
- Predecessor: none
- Successor: not yet spawned

## Active Timers
- Heartbeat cron: 10e16449-35f8-42f3-a388-2a59a246b984/task-47
- Safety timer: none
- On succession: kill all timers before spawning successor
- On context truncation: run manage_task(Action="list") — re-create if missing

## Artifact Index
- /home/tension_atoi/Projects/Gnu.in/.agents/sub_orch_impl/SCOPE.md — Implementation scope and milestone details
- /home/tension_atoi/Projects/Gnu.in/.agents/sub_orch_impl/progress.md — Step-by-step progress checklist
