## 2026-06-17T14:56:30Z

Publish the TEST_READY.md and TEST_INFRA.md files to the project root directory /home/tension_atoi/Projects/Gnu.in/ and verify the test suite execution.

Instructions:
1. Write the file /home/tension_atoi/Projects/Gnu.in/TEST_INFRA.md with the following contents:
---
# E2E Test Infra: gnu.in-cockpit

## Test Philosophy
- Opaque-box, requirement-driven. No dependency on implementation design where possible.
- Methodology: Category-Partition + BVA + Pairwise + Workload Testing.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 |
|---|---------|---------------------|:------:|:------:|:------:|
| 1 | GUI Launch | ORIGINAL_REQUEST §1 | 6      | 8      | 1      |
| 2 | GitHub REST Client | ORIGINAL_REQUEST §1 | 6      | 6      | 1      |
| 3 | Action Execution | ORIGINAL_REQUEST §1 | 6      | 7      | 1      |
| 4 | Installation Script | ORIGINAL_REQUEST §1 | 6      | 6      | 1      |

## Test Architecture
- Test runner: pytest using pytest-qt under `uv run pytest` from the `gnu.in-cockpit/` directory.
- Test case format: PySide6 test window driving using qtbot fixture and selective QProcess or requests monkeypatching.
- Headless execution setup using environment overrides in conftest.py:
  - PYTEST_QT_API=pyside6
  - QT_QPA_PLATFORM=offscreen
  - QT_QPA_PLATFORMTHEME=""

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Developer Onboarding | GUI Launch + GitHub Status + Action Execution + Install | High |
| 2 | Coherence Release Gate | GUI Launch + Action Execution (checks & release sync) | Medium |
| 3 | Git Repository Branch Work | GUI Launch + Action Execution (commit message & push) | Medium |
| 4 | GitHub Workflow Monitoring | GUI Launch + GitHub Status (PR list & runs lists) | Medium |
| 5 | Environment Failure Fallback | GUI Launch + Action Execution (missing folders/remotes) | High |
| 6 | Broken Authentication Recovery | GUI Launch + GitHub Status (invalid PAT -> update token -> refresh) | High |

## Coverage Thresholds
- Tier 1: ≥5 per feature (Total: 24 tests)
- Tier 2: ≥5 per feature (where boundaries exist) (Total: 27 tests)
- Tier 3: pairwise coverage of major feature interactions (Total: 6 tests)
- Tier 4: ≥5 realistic application scenarios (Total: 6 tests)
- Total tests: 63 custom test cases implemented.
---

2. Write the file /home/tension_atoi/Projects/Gnu.in/TEST_READY.md with the following contents:
---
# E2E Test Suite Ready

## Test Runner
- Command: `uv run pytest` (or `pytest`)
- Location: `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/`
- Expected: all tests pass with exit code 0 (and install-script tests gracefully skipped if install.sh does not exist).

## Coverage Summary
| Tier | Count | Description |
|------|------:|-------------|
| 1. Feature Coverage | 24 | Verify basic happy paths for all 4 features |
| 2. Boundary & Corner | 27 | Verify failure robustness (missing display, invalid PAT, wrong workspace) |
| 3. Cross-Feature | 6 | Verify feature interactions (refresh after install, config updates UI) |
| 4. Real-World Application | 6 | Verify full developer workflows |
| **Total** | **63** | **New test cases implemented** |

## Feature Checklist
| Feature | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---------|:------:|:------:|:------:|:------:|
| GUI Launch | 6 | 8 | ✓ | ✓ |
| GitHub REST Client | 6 | 6 | ✓ | ✓ |
| Action Execution | 6 | 7 | ✓ | ✓ |
| Installation Script | 6 | 6 | ✓ | ✓ |
---

3. Run `uv run pytest` inside `/home/tension_atoi/Projects/Gnu.in/gnu.in-cockpit/` to verify the tests run successfully and all pass (excluding those skipped for install.sh).
4. Create a handoff report at /home/tension_atoi/Projects/Gnu.in/.agents/worker_doc_publisher/handoff.md documenting the verification command and results.
