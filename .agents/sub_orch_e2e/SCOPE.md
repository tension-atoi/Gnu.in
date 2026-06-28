# Scope: E2E Testing Track

## Architecture
- Pytest-based E2E test suite under `gnu.in-cockpit/tests/` running using a virtual framebuffer or headless mode.
- Mocks for GitHub API: local environment mocking or a mock server/requests-mock to intercept API calls for the REST client, and subprocess wrapper intercepting for the `gh` CLI.
- Launch validation: tests launching the QMainWindow using PySide6's QApplication or subprocess execution, ensuring Fusion style and Wayland settings are respected.
- Installation validation: tests executing `install.sh` in an isolated temp environment (custom `HOME`) and verifying the created launcher, `.desktop` file, icons, and binary paths.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Test Infra & Mocks | Setup pytest environment, virtual display/headless config, and GitHub mock framework. | None | PLANNED |
| 2 | Tier 1: Feature Coverage | Implement cockpit launch tests, GitHub basic tests, and install script execution tests. | M1 | PLANNED |
| 3 | Tier 2: Boundary Cases | Implement tests for invalid PAT, missing workspace, invalid repo config, and install overrides. | M2 | PLANNED |
| 4 | Tier 3: Cross-Feature | Implement tests for refresh after installation and UI updates on repo changes. | M3 | PLANNED |
| 5 | Tier 4: Real-World Workflow | Mock full user workflow: config workspace -> set PAT -> fetch PRs/runs -> verify installation. | M4 | PLANNED |
| 6 | Publish & Sign-off | Generate TEST_INFRA.md and TEST_READY.md, run final checks, and sign off. | M5 | PLANNED |

## Interface Contracts
- Test command: `pytest gnu.in-cockpit/tests/` must be executable.
- head-less execution compatibility (use `pytest-qt` or similar virtual frame / XVFB / Qt offscreen platform `QT_QPA_PLATFORM=offscreen`).
- No internal python imports for E2E tests where possible, exercising cockpit via command line and GUI event loops.
