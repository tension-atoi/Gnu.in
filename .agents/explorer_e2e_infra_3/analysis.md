# gnu.in-cockpit E2E Test Cases and Scenarios

This document contains a comprehensive design of E2E test cases and scenarios across Tiers 1-4 for the **gnu.in-cockpit** project. It specifies test cases, setup steps, inputs, and expected outcomes for each.

## Feature Enumeration
The gnu.in-cockpit project comprises the following primary features:
1. **GUI Launch**: Starts the PySide6 application, initializes native Qt6 styling (Fusion style), verifies Wayland environment compatibility, reads saved configuration, and renders UI components (Action Buttons, LogView, Docs Browser, GitHubPanel).
2. **GitHub Status (REST Client)**: Integrates with GitHub REST API using a Personal Access Token (PAT) / `GITHUB_TOKEN` to retrieve Pull Requests and recent Action Runs, populating list widgets in the sidebar.
3. **Action Execution**: Leverages `QProcess` to run shell actions (Checks, Session, Release, Git, Build/Deploy) asynchronously inside a resolved repository directory, streaming stdout/stderr line-by-line into a color-coded log pane.
4. **Installation Script**: A packaging and setup bash script (`install.sh`) that validates python version, creates an isolated virtual environment, installs dependencies, builds the application, and deploys the `.desktop` launcher and system icons.

---

## Tier 1: Feature Coverage
Verify basic functionality under ideal conditions. (24 test cases)

### Feature A: GUI Launch

#### Test case T1-A1: Basic GUI Launch
- **Description**: Verifies that the cockpit application initializes and launches the main window without throwing errors.
- **Setup steps**: Set environment variable `QT_QPA_PLATFORM=offscreen` (for headless testing) and run python launcher.
- **Input**: Run command `python3 -m cockpit` (or `gnuin-cockpit` executable).
- **Expected outcome**: Application initializes, returns exit status indicating running event loop, and window object is instantiated.

#### Test case T1-A2: App Title and Layout Size Validation
- **Description**: Verifies that the window title matches "GNU.IN Pipeline Cockpit" and default sizes are set correctly.
- **Setup steps**: Initialize `QApplication` and instantiate `Cockpit` window in headless mode.
- **Input**: Inspect `windowTitle()` and `width()`, `height()`.
- **Expected outcome**: Title matches exactly "GNU.IN Pipeline Cockpit". Width is $\ge 1360$ and height is $\ge 740$ (default `1600x800` in refactored window).

#### Test case T1-A3: Stylesheet Style Enforcement (Fusion Style)
- **Description**: Verifies that PySide6 application style is explicitly set to Fusion.
- **Setup steps**: Launch application in headless mode.
- **Input**: Query `QApplication.style().objectName()`.
- **Expected outcome**: Returns `"fusion"` (case-insensitive). Style sheet is successfully applied and does not trigger errors.

#### Test case T1-A4: Load Configuration from QSettings
- **Description**: Verifies that last workspace path, repo name, and author settings are retrieved from QSettings.
- **Setup steps**: Write mock values to QSettings key `gnu-in-labs/pipeline-cockpit`: `workspace="/tmp/mock-ws"`, `repo="gnu.in-shell"`, `gnosis_author=True`. Launch app.
- **Input**: Inspect `ws_edit.text()`, `repo_combo.currentText()`, and `author_cb.isChecked()`.
- **Expected outcome**: Fields display `/tmp/mock-ws`, `"gnu.in-shell"`, and checked state, respectively.

#### Test case T1-A5: Action Button Generation and Categorization
- **Description**: Verifies that all 14 actions from the `ACTIONS` list are correctly rendered in their respective group boxes.
- **Setup steps**: Launch application.
- **Input**: Find child widgets of type `QGroupBox` and check button text inside them.
- **Expected outcome**: Group boxes for "Checks", "Session", "Release", "Git", and "Build / Deploy" exist and contain corresponding action buttons (e.g., "Status (strict)", "Stage all + commit").

#### Test case T1-A6: Right Pane Markdown Loading
- **Description**: Verifies that the right documentation pane loads `INTRO_DOC` on startup.
- **Setup steps**: Launch application.
- **Input**: Query the text of the `doc` (QTextBrowser) widget.
- **Expected outcome**: Widget contains markdown-rendered text matching `INTRO_DOC` (e.g., "# GNU.IN Pipeline Cockpit").

---

### Feature B: GitHub Status (REST Client)

#### Test case T1-B1: PAT Token Detection from Env
- **Description**: Verifies that the GitHub client successfully detects the PAT token from `GITHUB_TOKEN` env variable.
- **Setup steps**: Set `GITHUB_TOKEN="ghp_mocktoken123"` in terminal environment. Run client token validation.
- **Input**: Execute `GitHubClient._get_token()`.
- **Expected outcome**: Returns `"ghp_mocktoken123"`.

#### Test case T1-B2: Fetch Pull Requests (REST API Success)
- **Description**: Verifies that the client fetches open PRs from the REST API and parse JSON correctly under a mock environment.
- **Setup steps**: Run local mock HTTP server that simulates GitHub API endpoint `/repos/gnu-in-labs/gnu.in-shell/pulls` returning a standard list of 2 PRs. Configure client to target mock server.
- **Input**: Call `GitHubClient.get_pull_requests(cwd)`.
- **Expected outcome**: Returns a list of dicts containing keys `number`, `title`, `state`, `author`, `url`.

#### Test case T1-B3: Fetch Recent Action Runs (REST API Success)
- **Description**: Verifies that the client fetches recent action runs from `/repos/gnu-in-labs/gnu.in-shell/actions/runs`.
- **Setup steps**: Mock server simulates endpoint returning 3 action runs (2 success, 1 failure).
- **Input**: Call `GitHubClient.get_recent_runs(cwd, limit=5)`.
- **Expected outcome**: Returns a list of runs containing `databaseId`, `name`, `status`, `conclusion`, `url`.

#### Test case T1-B4: Populate Pull Requests List Widget
- **Description**: Verifies that PR data retrieved is correctly rendered in `pr_list`.
- **Setup steps**: Trigger a mock result ready signal with a PR: `{"number": 42, "title": "Add theme", "author": {"login": "dev1"}, "url": "http://github.com/..."}`.
- **Input**: Query items in `github_panel.pr_list`.
- **Expected outcome**: Widget has an item containing `"#42 Add theme (dev1)"`, and its tooltip is set to the URL.

#### Test case T1-B5: Populate Actions List Widget and Color Coding
- **Description**: Verifies that runs data are rendered in `actions_list` with appropriate colors (green for success, red for failure).
- **Setup steps**: Trigger a mock result ready signal with two runs: one successful, one failed.
- **Input**: Inspect `github_panel.actions_list` items.
- **Expected outcome**: Item 1 contains `"[SUCCESS] Build"`, text color is green. Item 2 contains `"[FAILURE] Lint"`, text color is red.

#### Test case T1-B6: Manual Refresh Button Action
- **Description**: Verifies that clicking "Refresh" in GitHubPanel disables the button and spawns the worker thread.
- **Setup steps**: Set valid workspace path. Click the "Refresh" button.
- **Input**: Intercept click signal on `github_panel.refresh_btn`.
- **Expected outcome**: Button becomes disabled, status label shows "Fetching...", and `GitHubWorker` thread is started.

---

### Feature C: Action Execution

#### Test case T1-C1: Execute Read-Only Script Action
- **Description**: Verifies that running a read-only script (e.g. `Status (strict)`) launches a QProcess.
- **Setup steps**: Ensure mock workspace exists. Click the "Status (strict)" button.
- **Input**: Trigger button click.
- **Expected outcome**: QProcess launches `tools/status.sh --strict` under bash `-lc`. UI enters busy state (buttons disabled).

#### Test case T1-C2: Dynamic Git Commit Command Resolution
- **Description**: Verifies that commit action resolves dynamically to include the user's message.
- **Setup steps**: Enter `"Initial refactor"` in the commit message text field. Click "Stage all + commit".
- **Input**: Inspect resolved command in `_resolve_cmd()`.
- **Expected outcome**: Returns `git add -A && git commit -m "Initial refactor"` (with prefix if Author checkbox is checked).

#### Test case T1-C3: Danger Action Confirmation Gate (Cancel)
- **Description**: Verifies that danger actions prompt the user and can be cancelled.
- **Setup steps**: Click "Promote latest" button. Mock QMessageBox response to return `QMessageBox.No`.
- **Input**: Trigger button click.
- **Expected outcome**: Confirmation box shows warning. Clicking No cancels execution; log prints `• Promote latest cancelled.` and no process is launched.

#### Test case T1-C4: Danger Action Confirmation Gate (Proceed)
- **Description**: Verifies that danger actions launch the QProcess after user confirmation.
- **Setup steps**: Click "Promote latest" button. Mock QMessageBox response to return `QMessageBox.Yes`.
- **Input**: Trigger button click.
- **Expected outcome**: Confirmation box shows warning. Clicking Yes executes command `tools/promote-latest.sh` via QProcess.

#### Test case T1-C5: Real-time Live Log Streaming
- **Description**: Verifies stdout from QProcess is captured line-by-line and color-coded.
- **Setup steps**: Launch action that prints 3 lines of output spaced 100ms apart.
- **Input**: Read standard output stream.
- **Expected outcome**: Lines are written to `LogView` in real-time before process exits. Log format displays commands in orange and stdout in light gray.

#### Test case T1-C6: Successful Action Exit Handling
- **Description**: Verifies that QProcess finished handler cleans up correctly on success.
- **Setup steps**: Execute short-running successful command (e.g. `echo "hello"`).
- **Input**: Wait for process exit.
- **Expected outcome**: Logs `✓ exit 0`, status bar updates to `Done (exit 0)`, busy state cleared (buttons enabled), and GitHub status is refreshed.

---

### Feature D: Installation Script

#### Test case T1-D1: Basic Installation Execution
- **Description**: Verifies that running `install.sh` under normal user environment completes successfully.
- **Setup steps**: Create temporary target directory.
- **Input**: Run `./install.sh --prefix /tmp/test-install`.
- **Expected outcome**: Script returns exit code 0. Virtual environment and desktop files are generated.

#### Test case T1-D2: Python Version Check Validation
- **Description**: Verifies that the installer confirms python version meets requirement ($\ge 3.10$).
- **Setup steps**: Run installer in environment with python 3.11 available.
- **Input**: Execute `./install.sh`.
- **Expected outcome**: Installer succeeds and prints that python version check passed.

#### Test case T1-D3: Virtual Environment (venv) Creation
- **Description**: Verifies that the installer creates a dedicated python virtual environment.
- **Setup steps**: Run `./install.sh --prefix /tmp/test-install`.
- **Input**: Check files in `/tmp/test-install/share/gnuin-cockpit/venv`.
- **Expected outcome**: Directory exists and contains virtualenv structure (e.g., `bin/pip`, `bin/python`).

#### Test case T1-D4: Dependency Installation (PySide6)
- **Description**: Verifies PySide6 is installed in the generated venv.
- **Setup steps**: Run install script.
- **Input**: Run `/tmp/test-install/share/gnuin-cockpit/venv/bin/python -c "import PySide6"`.
- **Expected outcome**: Python import executes successfully with no ImportError.

#### Test case T1-D5: Desktop File Deployment
- **Description**: Verifies that `.desktop` launcher is copied and paths are adjusted to match prefix.
- **Setup steps**: Run `./install.sh --prefix /tmp/test-install`.
- **Input**: Read `/tmp/test-install/share/applications/gnuin-cockpit.desktop`.
- **Expected outcome**: File exists. The `Exec` key points to the correct executable wrapper: `Exec=/tmp/test-install/bin/gnuin-cockpit`.

#### Test case T1-D6: Desktop Icon Deployment
- **Description**: Verifies that icons are deployed to host system directories.
- **Setup steps**: Run `./install.sh --prefix /tmp/test-install`.
- **Input**: Check existence of icon file at `/tmp/test-install/share/icons/hicolor/scalable/apps/gnuin-cockpit.svg`.
- **Expected outcome**: Icon file is successfully installed.

---

## Tier 2: Boundary/Edge Cases
Verify application stability under abnormal or failure conditions. (24 test cases)

### Feature A: GUI Launch Boundaries

#### Test case T2-A1: Launch without Display (DISPLAY and WAYLAND_DISPLAY Unset)
- **Description**: Verifies app behavior when started in a headless/bare TTY environment with no X11/Wayland variables.
- **Setup steps**: Unset `DISPLAY`, `WAYLAND_DISPLAY`, and `QT_QPA_PLATFORM`. Run application.
- **Input**: Run `python3 -m cockpit`.
- **Expected outcome**: PySide6 exits with standard Qt platform error (exit code 1 or similar) rather than hanging or leaving orphan processes.

#### Test case T2-A2: Launch in Headless Mode using offscreen
- **Description**: Verifies app launches successfully and exits gracefully when `QT_QPA_PLATFORM` is explicitly set to `offscreen`.
- **Setup steps**: Set `QT_QPA_PLATFORM=offscreen`. Run application.
- **Input**: Run `python3 -m cockpit`.
- **Expected outcome**: Application starts main window in memory, is able to close cleanly, exits 0.

#### Test case T2-A3: Multiple Concurrent App Instances
- **Description**: Verifies that multiple instances of cockpit can launch concurrently without lock conflicts.
- **Setup steps**: Launch one instance of cockpit, then start a second instance.
- **Input**: Run two instances of `python3 -m cockpit`.
- **Expected outcome**: Both instances run independently; QSettings write operations do not corrupt settings.

#### Test case T2-A4: Corrupted QSettings INI File
- **Description**: Verifies application behavior when QSettings configuration file is malformed or corrupted.
- **Setup steps**: Write random binary data into QSettings file path (`~/.config/gnu-in-labs/pipeline-cockpit.conf`). Launch application.
- **Input**: Start cockpit.
- **Expected outcome**: Application ignores corrupted settings, boots successfully, and falls back to `DEFAULT_WORKSPACE` and default values.

#### Test case T2-A5: Invalid Command Line Arguments
- **Description**: Verifies that cockpit handles unknown command line arguments gracefully.
- **Setup steps**: Pass random parameters to launcher.
- **Input**: Run `python3 -m cockpit --unknown-argument -xyz`.
- **Expected outcome**: Application ignores arguments or displays help message and runs/exits cleanly.

#### Test case T2-A6: High-DPI Scaling Constraints
- **Description**: Verifies layout stays readable when running in high device-pixel-ratio.
- **Setup steps**: Set environment variable `QT_SCALE_FACTOR=2` and launch application.
- **Input**: Start cockpit.
- **Expected outcome**: Layout components remain scaled proportionally, widgets do not clip or overlap, and text remains readable in Fusion style.

---

### Feature B: GitHub Status Boundaries

#### Test case T2-B1: Missing PAT/Token Configuration
- **Description**: Verifies behavior when no PAT token is set in environment or config.
- **Setup steps**: Ensure `GITHUB_TOKEN` is unset. Trigger refresh.
- **Input**: Click "Refresh".
- **Expected outcome**: Status label displays error message "No GitHub PAT configured" and logs it to panel.

#### Test case T2-B2: Invalid PAT (401 Unauthorized)
- **Description**: Verifies error handling when PAT token is revoked or incorrect.
- **Setup steps**: Set `GITHUB_TOKEN="ghp_invalidtoken123"`. Trigger refresh.
- **Input**: Intercept GET request to GitHub API and mock a 401 Unauthorized status.
- **Expected outcome**: Worker thread raises error, status label updates to "Error fetching data", list widgets display "401 Unauthorized: Invalid Personal Access Token".

#### Test case T2-B3: Rate Limit Exceeded (403 Forbidden)
- **Description**: Verifies graceful handling when the GitHub API rate limit is reached.
- **Setup steps**: Configure mock server to return HTTP 403 with `x-ratelimit-remaining: 0`.
- **Input**: Trigger refresh.
- **Expected outcome**: Status label shows error; list widget displays "Rate limit exceeded. Try again later."

#### Test case T2-B4: Network Offline/Disconnect Timeout
- **Description**: Verifies behavior when internet connection is lost or DNS lookup fails.
- **Setup steps**: Configure mock server to drop connection or block port.
- **Input**: Trigger refresh.
- **Expected outcome**: Request times out (e.g., after 5 seconds); worker catches exception, updates status to "Error fetching data", and logs connection timeout error without freezing GUI.

#### Test case T2-B5: Empty GitHub Repository (0 PRs / 0 Runs)
- **Description**: Verifies UI display when repository contains no open PRs or action history.
- **Setup steps**: Configure mock server to return empty JSON lists `[]` for pulls and runs.
- **Input**: Trigger refresh.
- **Expected outcome**: UI lists show single items "No open PRs" and "No recent runs" rather than displaying empty widgets or crashing.

#### Test case T2-B6: Malformed JSON Response
- **Description**: Verifies resilience when GitHub API returns garbled/malformed data.
- **Setup steps**: Configure mock server to return corrupted non-JSON plain text.
- **Input**: Trigger refresh.
- **Expected outcome**: JSON decode error is caught; status displays "Error fetching data" and PR list displays "Failed to parse API response".

---

### Feature C: Action Execution Boundaries

#### Test case T2-C1: Workspace Directory Missing
- **Description**: Verifies behavior when the workspace path configured in QLineEdit does not exist.
- **Setup steps**: Set workspace path to `/tmp/nonexistent-directory-xyz`. Click "Git status".
- **Input**: Trigger button click.
- **Expected outcome**: QProcess does not launch. LogView appends red error line: `✗ working dir not found: /tmp/nonexistent-directory-xyz`.

#### Test case T2-C2: Workspace Repository lacks Git (.git folder missing)
- **Description**: Verifies handling when repository folder exists but is not a Git repo.
- **Setup steps**: Create directory `/tmp/fake-repo` without initializing git. Set workspace to `/tmp/` and Repo to `fake-repo`. Click "Git status".
- **Input**: Trigger button click.
- **Expected outcome**: QProcess runs `git status ...` in `/tmp/fake-repo`. Exit code is non-zero, and error log prints standard git error: `fatal: not a git repository`.

#### Test case T2-C3: Read-Only Workspace Directory Permissions
- **Description**: Verifies behavior when trying to run git commit in workspace with read-only permissions.
- **Setup steps**: Create mock git repository and change ownership/permissions to read-only (`chmod 555`). Enter commit message and click commit.
- **Input**: Trigger commit.
- **Expected outcome**: Command fails; log records git permission error and exits non-zero. Cockpit recovers and UI is re-enabled.

#### Test case T2-C4: Stop Action (Killing Hung Process)
- **Description**: Verifies that clicking "Stop" kills a long-running/hung process immediately.
- **Setup steps**: Execute action `sleep 100` (by configuring it in ACTIONS or simulating). Wait 1 second.
- **Input**: Click the "Stop" button.
- **Expected outcome**: LogView appends `• stopping…`. QProcess is killed. Status bar updates to `Failed (exit -1)` (or platform exit code for killed process), and buttons are re-enabled.

#### Test case T2-C5: Exit Application during Action Execution
- **Description**: Verifies that closing the window kills any running QProcess child cleanly.
- **Setup steps**: Run long-running action `sleep 100`. Close the cockpit window.
- **Input**: Trigger `closeEvent`.
- **Expected outcome**: The application window closes, running subprocess is terminated immediately via `proc.kill()`, and python process exits.

#### Test case T2-C6: Non-Zero Exit Code with Empty Stderr
- **Description**: Verifies exit handler behaves correctly when a process fails but emits no standard error.
- **Setup steps**: Execute command `sh -c "exit 5"`.
- **Input**: Wait for process exit.
- **Expected outcome**: LogView prints `✗ exit 5`. Status shows `Failed (exit 5)`. No crash occurs.

---

### Feature D: Installation Script Boundaries

#### Test case T2-D1: Custom Installation Prefix Overrides
- **Description**: Verifies that `install.sh` accepts and respects custom `--prefix` path.
- **Setup steps**: Run installer with `--prefix /tmp/custom-prefix`.
- **Input**: Check install path.
- **Expected outcome**: Binary wrapper is created under `/tmp/custom-prefix/bin/gnuin-cockpit`.

#### Test case T2-D2: Insufficient Write Permissions to Prefix Path
- **Description**: Verifies that installer exits with error when path is write-protected (e.g. `/usr/bin` without sudo).
- **Setup steps**: Run installer with `--prefix /usr` as a non-root user.
- **Input**: Execute `./install.sh`.
- **Expected outcome**: Script checks write permissions, fails early, logs `Permission denied`, and exits with non-zero code.

#### Test case T2-D3: Missing Python 3 Dependency on Host
- **Description**: Verifies installer behavior when python3 executable is missing.
- **Setup steps**: Hide python3 from `PATH` by overriding env.
- **Input**: Execute `./install.sh`.
- **Expected outcome**: Installer outputs `python3 is required but was not found` and exits non-zero.

#### Test case T2-D4: Python Version Unsupported (< 3.10)
- **Description**: Verifies installer fails when python version on host is obsolete (e.g. 3.9).
- **Setup steps**: Configure mock `python3` command in test environment to return `Python 3.9.2` on version check.
- **Input**: Execute `./install.sh`.
- **Expected outcome**: Installer outputs error stating python version must be $\ge 3.10$, and exits non-zero.

#### Test case T2-D5: Mid-Execution Interrupt Cleanup
- **Description**: Verifies that killing the install script mid-run doesn't leave locked states.
- **Setup steps**: Run `./install.sh`, send `SIGINT` (Ctrl+C) while pip is installing.
- **Input**: Check directory. Re-run `./install.sh`.
- **Expected outcome**: Re-running the script cleans up/overwrites previous partial virtual environment successfully.

#### Test case T2-D6: Pre-existing Read-Only Desktop Launcher
- **Description**: Verifies that installer overrides existing file or displays clean skip/override error.
- **Setup steps**: Create read-only mock desktop entry in target folder.
- **Input**: Execute install script.
- **Expected outcome**: Installer handles override (or requests sudo/permissions), or prints warning.

---

## Tier 3: Cross-Feature Combinations
Verify behavior when multiple features interact. (6 test cases)

#### Test case T3-1: Post-install Launcher Verification
- **Description**: Verifies that the installer's output wrapper correctly launches the GUI with Wayland environments.
- **Setup steps**: Run `./install.sh --prefix /tmp/ti`.
- **Input**: Run launcher `/tmp/ti/bin/gnuin-cockpit` in headless mode.
- **Expected outcome**: Launcher initializes virtualenv python path, reads variables from `.desktop` file context (e.g., `QT_QPA_PLATFORM=wayland`), and launches the cockpit MainWindow successfully.

#### Test case T3-2: Config Modification during Action Execution
- **Description**: Verifies that workspace/repository dropdowns cannot disrupt a running command.
- **Setup steps**: Start long running action `tools/sync-release-cascade.sh`. Change repository dropdown value in GUI.
- **Input**: Change Repo combo-box selection.
- **Expected outcome**: Repository dropdown and workspace line edit are disabled or ignored while action runs, preventing execution directory mismatch.

#### Test case T3-3: Action Completion Auto-Refreshes GitHub Panel
- **Description**: Verifies that successful git push/commit triggers refresh of PRs/Runs list.
- **Setup steps**: Execute the "Push" action button (confirm Yes). Wait for exit 0.
- **Input**: Observe finished hook.
- **Expected outcome**: On exit 0 of Git Push, `_refresh_github()` is automatically invoked, updating the PRs and Actions lists.

#### Test case T3-4: Missing PAT on start, then setting PAT and refreshing
- **Description**: Verifies that configuring the token post-launch enables GitHub panel loading.
- **Setup steps**: Start cockpit with no token. Panel displays error. Set `GITHUB_TOKEN` environment variable or write to configuration file.
- **Input**: Click "Refresh".
- **Expected outcome**: Status updates from error to "Fetching..." and then lists PRs successfully.

#### Test case T3-5: Workspace Path change Updates GitHub Panel CWD
- **Description**: Verifies that selecting another repository updates the working directory passed to GitHub REST client.
- **Setup steps**: Open cockpit. Change Repo selection from `gnu.in-os` to `gnu.in-shell`.
- **Input**: Trigger combo-box index change.
- **Expected outcome**: GitHubPanel receives index change event, cancels any active worker thread, and starts new query using the path `/home/tension_atoi/Projects/Gnu.in/gnu.in-shell`.

#### Test case T3-6: Log View Buffer Overflow during Large Action Output
- **Description**: Verifies that executing a verbose command (printing thousands of lines) streams output smoothly and updates GitHub status without memory leaks or freezing GUI.
- **Setup steps**: Execute action that prints 8000 lines of output.
- **Input**: Wait for completion.
- **Expected outcome**: LogView caps logs at `10000` blocks, scrolling remains smooth, and finished callback is reached.

---

## Tier 4: Real-World Scenarios
Verify end-to-end user journeys and developer workflows. (6 test cases)

#### Scenario T4-1: Standard Developer Onboarding
- **Description**: Simulates a new developer installing the cockpit, launching it, configuring access, and executing initial checks.
- **Step-by-step**:
  1. Developer runs `./install.sh --prefix ~/.local` to set up environment.
  2. Launches application via `gnuin-cockpit`.
  3. Checks workspace path (`~/Projects/Gnu.in`).
  4. Sets `GITHUB_TOKEN` in the environment.
  5. Clicks "Refresh" on the GitHub Status panel to load pull requests.
  6. Executes `Status (strict)` to verify system state.
- **Expected Outcome**: Installation succeeds, app launches with Fusion style on Wayland, fetches PRs, runs the status script, and logs output successfully.

#### Scenario T4-2: Release Gatekeeper Workflow
- **Description**: Simulates the exact steps to build and promote a version release on the live desktop.
- **Step-by-step**:
  1. Gatekeeper selects `gnu.in-os` repository.
  2. Runs `Relock components` to pin revisions.
  3. Runs `Sync version manifest` to write `GLOBAL-VERSION.json`.
  4. Runs `Sync release cascade` to assemble and token-sync.
  5. Verifies verify source check is green.
  6. Clicks `Promote latest` (confirms Yes).
- **Expected Outcome**: All release scripts are executed sequentially inside the correct directory. Each exits 0, and the live desktop is promoted.

#### Scenario T4-3: Agent-Assisted Development Commit Cycle
- **Description**: Simulates using the cockpit to commit and push changes prepared by an agent.
- **Step-by-step**:
  1. Agent prepares files in `gnu.in-shell`.
  2. User opens cockpit, ticks "Commit as Gnosis.Agent" checkbox.
  3. Types commit message `"fix(taskbar): resolve clipping on workspace label"`.
  4. Clicks "Stage all + commit".
  5. Clicks "Pull (ff-only)".
  6. Clicks "Push" (confirms Yes).
- **Expected Outcome**: Git commit environment variables (`GIT_AUTHOR_NAME="Gnosis.Agent"`, etc.) are injected into QProcess, committing authorship cleanly. Git pushes successfully, and the GitHub status panel updates with new runs.

#### Scenario T4-4: GUI Recovery from Missing Dependency
- **Description**: Simulates app recovery and fallback when environment lacks standard CLI dependencies.
- **Step-by-step**:
  1. Host lacks `gh` CLI tool.
  2. User runs `install.sh` which installs `PySide6`.
  3. User launches application.
  4. GitHub Panel uses native python requests/REST client (with valid token).
  5. Action buttons run standard git shell actions.
- **Expected Outcome**: GitHub panel loads PR list and runs without CLI dependency. Git commands execute normally.

#### Scenario T4-5: Hotfix Deployment under Network Instability
- **Description**: Simulates managing a hotfix when network is dropping.
- **Step-by-step**:
  1. User starts cockpit and edits `gnu.in-os`.
  2. Clicks `Status (strict)` (runs locally, exits 0).
  3. Network drops. User clicks "Push" (git push fails, exits non-zero, log prints host error).
  4. GitHub panel shows connection error.
  5. Network restores. User clicks "Refresh" on GitHub panel (fetches successfully).
  6. User clicks "Push" (exits 0).
- **Expected Outcome**: Cockpit doesn't crash during network loss, displays clear feedback, and recovers immediately once network connection is re-established.

#### Scenario T4-6: Clean Uninstall and Re-installation
- **Description**: Simulates clean removal of cockpit config/binaries followed by installation in custom path.
- **Step-by-step**:
  1. User deletes desktop files, target directory and settings files.
  2. Runs `./install.sh --prefix ~/myapps`.
  3. Launches cockpit via `~/myapps/bin/gnuin-cockpit`.
  4. Changes workspace line edit to custom path.
  5. Closes application.
  6. Launches cockpit again.
- **Expected Outcome**: App installs and runs cleanly in new path. Custom workspace path is preserved in QSettings on second launch.
