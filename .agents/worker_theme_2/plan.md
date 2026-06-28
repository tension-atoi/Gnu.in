# Verification and Adaptation Plan

## Steps:
1. Verify the current git status and check if any changes are proposed or if the codebase already matches the patch.
2. If the files are already fully matching the patch, run the unit/launch tests for the python cockpit app:
   `cd gnu.in-cockpit && uv run pytest tests/test_e2e_launch.py tests/test_github_api.py tests/test_github_api_stress.py`
3. Verify that the C++ Syster app still compiles:
   `cd gnu.in-syster-app/syster-app && cmake --build build`
4. Document findings and compile handoff report.
