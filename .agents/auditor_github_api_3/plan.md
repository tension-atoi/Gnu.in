# Forensic Audit Plan — GitHub API Integration

To independently verify the integrity and correct implementation of the GitHub API integration in the `gnu.in-cockpit` project, the following steps will be executed:

## 1. Static Analysis & Code Inspections
- [ ] Inspect `src/cockpit/github_client.py` for hardcoded payloads, expected test values, or mock responses.
- [ ] Inspect `src/cockpit/views/github_panel.py` and `src/cockpit/views/main_window.py` for any facade patterns, mock fallbacks or dummy data return conditions.
- [ ] Search the entire codebase for pre-populated mock logs or verification results.
- [ ] Check if imports of `requests` and custom parsing verify correctness of authentic requests (no dummy delegates).

## 2. Dynamic & Test Verification
- [ ] Run the suite of unit tests using Python's unittest module to ensure all tests pass cleanly.
  - Command: `python3 -m unittest discover -s tests -p "test_*.py"`
- [ ] Run the empirical git remote URL parsing script to ensure it handles all variations (e.g. dots, attacker subdomains, ssh paths).
  - Command: `python3 tests/verify_empirical_git.py`

## 3. Forensic Check Execution & Verdict Formulation
- [ ] Evaluate the behavior against Development Mode rules.
- [ ] Generate the final forensic audit handoff report (`handoff.md`).
