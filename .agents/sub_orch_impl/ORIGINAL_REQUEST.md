# Original User Request for Implementation Track

## 2026-06-17T14:34:00Z

You are the Implementation Sub-orchestrator. Your working directory is `/home/tension_atoi/Projects/Gnu.in/.agents/sub_orch_impl/`.
Your mission is to implement all three requirements for the `gnu.in-cockpit` project:
1. R1: GitHub REST API Authentication (using requests/PAT, removing `gh` CLI subprocess dependence, adding settings field).
2. R2: UI styling adaptation (adapt native Qt6 styling/colors from `SysterTheme.hpp` to cockpit).
3. R3: Local installation script (`install.sh` for private deployment, standard `.desktop` generation).

## Workflow
1. Run the Explorer -> Worker -> Reviewer -> Challenger loop to implement these features.
2. In Phase 1: once `TEST_READY.md` is published at the project root by the E2E Testing Track, run the E2E tests and fix any failing test cases. All Tier 1-4 tests must pass.
3. In Phase 2: run adversarial coverage hardening (Tier 5) to verify correctness and robustness.
4. Adhere to key constraints: No GNOME/GTK, native Qt6 only.

Please communicate all updates and results back to the Project Orchestrator (conversation ID: 93c5aade-0d72-478e-a46e-a3dc7c62b0c4).
