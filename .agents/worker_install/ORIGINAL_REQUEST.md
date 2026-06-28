## 2026-06-17T19:22:30Z
You are a worker subagent named worker_install.
Your working directory is /home/tension_atoi/Projects/Gnu.in/.agents/worker_install/.
Your mission is to implement and verify the local installation script and desktop configuration (Milestone 3).

Specifically:
1. Create the installation script at gnu.in-cockpit/install.sh. Use the code from /home/tension_atoi/Projects/Gnu.in/.agents/explorer_install/proposed_install.sh verbatim, which is a fully designed bash script parsing --prefix, checking Python version >= 3.10, verifying permissions, creating the virtual environment under share/gnuin-cockpit/venv, installing gnuin-cockpit, deploying the executable wrapper under bin/gnuin-cockpit, and configuring the .desktop entry with Wayland and Kvantum environment overrides.
2. Make the script executable: chmod +x gnu.in-cockpit/install.sh
3. Verify your implementation by running the installer E2E tests:
   cd gnu.in-cockpit && .venv/bin/pytest tests/test_e2e_install.py
   Ensure all tests pass.
4. Document the exact steps, modifications, and test results in handoff.md under /home/tension_atoi/Projects/Gnu.in/.agents/worker_install/handoff.md.

MANDATORY INTEGRITY WARNING: DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
