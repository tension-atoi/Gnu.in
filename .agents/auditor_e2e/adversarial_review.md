# Adversarial Review — gnu.in-cockpit

## Challenge Summary

**Overall risk assessment**: MEDIUM

The application operates as a desktop UI tool that coordinates git commands, scripts, and release processes. Since it uses `QProcess` executing via `bash -lc` to perform operations, any inputs entering commands must be heavily scrutinized.

---

## Challenges

### [Medium] Challenge 1: Shell Command Injection in Commit Message

- **Assumption challenged**: The commit message entered in `self.msg_edit` is sufficiently sanitized using `.replace('"', '\\"')` before shell execution.
- **Attack scenario**:
  The application constructs the commit command as:
  ```python
  return f'git add -A && {prefix}git commit -m "{quoted}"'
  ```
  And executes it with:
  ```python
  self.proc.start("bash", ["-lc", cmd])
  ```
  If a user (or a malicious sub-agent/script providing inputs) enters a message containing command substitutions or backticks, such as:
  `fix(ui): resolve clipping $(touch /tmp/injected_payload)`
  The `replace` function turns it into:
  `fix(ui): resolve clipping $(touch /tmp/injected_payload)`
  Since it remains wrapped in double quotes (`"`), `bash` will evaluate the `$()` statement during execution of `bash -lc`, running the command `touch /tmp/injected_payload`.
- **Blast radius**: Arbitrary code execution under the privileges of the running user. This is a vulnerability if the user copies untrusted commit messages or is automated by a compromised sub-agent.
- **Mitigation**: Use direct process execution with argument lists rather than compiling commands into a shell command line (`bash -lc`). E.g., run `git` directly as the executable with `["commit", "-m", msg]` as arguments.

### [Low] Challenge 2: Network Interruption on Git Push

- **Assumption challenged**: Process commands (specifically `git push` or `finish-release.sh`) fail safely and cleanly during network loss.
- **Attack scenario**: If a push begins and connection is lost midway, git might leave a locked state or half-updated remote references.
- **Blast radius**: Desynchronization between local and remote status.
- **Mitigation**: The GUI displays the non-zero exit code and error trace from stderr. This is correctly handled behaviorwise.

---

## Stress Test Results

- **Command Injection Scenario** → Commit message containing `$(touch /tmp/injected)` → Process executes and creates `/tmp/injected` → Actual: Command substitution is executed by bash → **FAIL** (potential vulnerability)
- **Non-existent workspace** → ws_edit points to non-existent directory → Application aborts execution safely logging warning → **PASS**
- **Headless launch** → Run application without DISPLAY or WAYLAND_DISPLAY → Fails with standard QPA error instead of spawning zombie process → **PASS**

---

## Unchallenged Areas

- **Theme parsing and styling compatibility** — Checked only offscreen. Standard native Qt styling (Fusion) appears robust, but physical visual overlapping under multiple high-DPI setups was not visually audited on screen.
