# E2E Test Infra: gnu.in-cockpit

## Test Philosophy
- Opaque-box, requirement-driven. No dependency on implementation design where possible.
- Methodology: Category-Partition + BVA + Pairwise + Workload Testing.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 |
|---|---------|---------------------|:------:|:------:|:------:|
| 1 | GUI Launch | ORIGINAL_REQUEST §1 | 6      | 8      | 1      |
| 2 | GitHub REST Client | ORIGINAL_REQUEST §1 | 6      | 6      | 1      |
| 3 | Action Execution | ORIGINAL_REQUEST §1 | 6      | 9      | 1      |
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
- Tier 2: ≥5 per feature (where boundaries exist) (Total: 29 tests)
- Tier 3: pairwise coverage of major feature interactions (Total: 6 tests)
- Tier 4: ≥5 realistic application scenarios (Total: 6 tests)
- Total tests: 65 custom test cases implemented.
