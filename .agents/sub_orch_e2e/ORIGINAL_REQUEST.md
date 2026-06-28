# Original User Request for E2E Testing Track

## 2026-06-17T14:34:00Z

You are the E2E Testing Orchestrator. Your working directory is `/home/tension_atoi/Projects/Gnu.in/.agents/sub_orch_e2e/`.
Your mission is to design and implement a comprehensive, requirement-driven, opaque-box E2E test suite for the `gnu.in-cockpit` Qt6 project, following the Project Pattern's Dual Track: E2E Testing Track.

## Requirements
1. Design and write test cases across 4 tiers:
   - Tier 1: Feature Coverage (verify cockpit launch, github REST client, and installation script).
   - Tier 2: Boundary/Edge cases (invalid/missing PAT, missing workspace directories, invalid repo config, install overrides).
   - Tier 3: Cross-feature combinations (verifying refresh after installation, UI update when repo config changes).
   - Tier 4: Real-world scenarios (mocking full user workflow: configure workspace/repo -> set PAT -> fetch PRs/runs -> verify installation).
2. The verification channel must be opaque-box, not relying on internal python module imports if possible (except for unit tests like `test_github_api.py` which can mock requests/PAT).
3. The test suite must run using standard tools (e.g. `pytest` or a simple test runner).
4. Publish `TEST_READY.md` and `TEST_INFRA.md` at the project root `/home/tension_atoi/Projects/Gnu.in/` (via a worker) once all tests are created and documented.
5. Adhere to key constraints: No GNOME/GTK, native Qt6 only.

Please communicate all updates and results back to the Project Orchestrator (conversation ID: 93c5aade-0d72-478e-a46e-a3dc7c62b0c4).

## 2026-06-17T14:34:18Z

Resume work at /home/tension_atoi/Projects/Gnu.in/.agents/sub_orch_e2e/. Read ORIGINAL_REQUEST.md for your mission.
Your parent is 93c5aade-0d72-478e-a46e-a3dc7c62b0c4 — use this ID for all escalation, status reporting, and completion reports (send_message).
Initialize your BRIEFING.md (archetype: self) and progress.md, start a heartbeat cron, plan your milestones, and delegate the work.
