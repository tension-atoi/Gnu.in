## 2026-06-17T19:21:04Z
You are an explorer subagent named explorer_install.
Your working directory is /home/tension_atoi/Projects/Gnu.in/.agents/explorer_install/.
Your task is to analyze and design the installation script install.sh and the .desktop entry for the cockpit application.

Specifically, investigate:
1. The project codebase structure for gnu.in-cockpit.
2. How the application is launched (e.g. entry points, virtualenv location, python commands).
3. The expected paths for user-local installations (e.g. executable entry points in ~/.local/bin, desktop entries in ~/.local/share/applications, application icons, and application files).
4. The contents of the E2E test files (specifically tests/test_e2e_install.py or similar) to see what assertions are made about the installer, where it expects files to be installed, what variables or CLI flags it tests, and the exact names/paths expected.
5. Create a detailed implementation plan, detailing the structure of install.sh and the .desktop file configuration. Propose a clear design that ensures the application can be run directly from ~/.local/bin and launched via the desktop environment, without violating any user rules (specifically NO GNOME OR GTK dependencies, Qt6 native native environment).
Write your findings in /home/tension_atoi/Projects/Gnu.in/.agents/explorer_install/handoff.md.
