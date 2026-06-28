# GNU.IN Launcher + Settings Audit

Date: 2026-06-07
Mode: combined UX + accessibility screenshot audit
Destination: local folder

## Audit Scope

Flow audited:

1. Open the GNU.IN app launcher.
2. Search for `settings`.
3. Launch the visible `Settings` result.
4. Open the canonical GNU.IN settings surface via `gnuin-cli settings`.
5. Inspect the Displays settings page for screen-manager configuration readiness.

Capture note: Browser and Chrome cannot inspect native Quickshell/Wayland shell overlays. Screenshots were captured from the live user session with `grim`. Each accepted screenshot was saved locally and inspected before use. `00-current-state.png` is diagnostic only; the numbered screenshots below are the audit evidence.

## Screenshots

1. `01-launcher-empty.png` - launcher opened with no query.
2. `02-launcher-settings-search.png` - launcher search for `settings`.
3. `03-launcher-settings-result-wrong-app.png` - selecting the visible `Settings` result opened a non-GNU.IN authentication window.
4. `04-settings-displays-canonical.png` - canonical GNU.IN settings opened through `gnuin-cli settings`, showing Displays.

## Step List

1. Launcher empty state - poor health.
   The launcher opens, but the default ranking is dominated by generic apps and recent chips. It does not clearly separate shell actions from ordinary app entries.

2. Search `settings` - poor health.
   The right target appears as a generic `Settings` row with the subtitle `Hyprland configuration`, but it is mixed among Terminal, Files, Web, Reload Shell, Android Studio, and third-party apps. The product intent is ambiguous.

3. Activate `Settings` from launcher - critical health.
   The visible `Settings` result did not open the GNU.IN settings app. It opened an `Authentication Required` window from another app/context. This is the highest-risk finding because the launcher advertises a settings route but lands somewhere else.

4. Open canonical settings with `gnuin-cli settings` - mixed health.
   The actual GNU.IN Settings surface opens and the Displays page is visible, but this path is not discoverable from the launcher. The UI reads more like a diagnostic panel than a full display manager.

5. Configure Displays - poor health.
   Displays shows live monitor state, wallpaper paths, workspace count, and raw monitor directives. It does not yet provide user-facing controls for mode, position, scale, transform, mirror, bit depth, VRR, HDR, enable/disable, preview, apply, rollback, or error recovery.

## Strengths

- The settings surface exists inside the GNU.IN shell instead of reviving the retired external settings app.
- The Displays page is connected to live monitor data and shows all three detected outputs.
- Monitor health is visible as `ACTIVE`, and raw directives are exposed for debugging.
- The settings IA has recognizable sections: Appearance, Shell, Input, Displays, Services, Gnosis, Developer.
- The launcher supports typed search, recent chips, keyboard hints, and result grouping.

## UX Risks

1. Launcher route mismatch.
   Evidence: `02-launcher-settings-search.png` and `03-launcher-settings-result-wrong-app.png`.
   Searching for settings shows a plausible GNU.IN result, but activating it opens the wrong destination. This breaks trust in the launcher as a command surface.

2. System actions and apps are not separated.
   Evidence: `01-launcher-empty.png`.
   Terminal, Files, Web, Settings, Reload Shell, Android Studio, Antigravity, and AnythingLLM all live in one flat list. A user cannot tell which rows are shell commands, system actions, apps, or external tools.

3. Settings entry labeling is too generic.
   Evidence: `02-launcher-settings-search.png`.
   `Settings` is not specific enough in a desktop with app settings, browser settings, Codex settings, Hyprland settings, and GNU.IN settings. The launcher needs `GNU.IN Settings` or `Display Settings` as a first-class command.

4. Displays is diagnostic, not configurational.
   Evidence: `04-settings-displays-canonical.png`.
   The page exposes state but not the expected task controls for a display manager. Users can see raw monitor lines but cannot safely build or apply display topology from the UI.

5. Background context leaks into core flows.
   Evidence: all accepted captures.
   Launcher and settings appear over unrelated app windows. That can be acceptable for shell overlays, but here it creates visual noise and weakens focus for high-risk settings changes.

6. The Gnosis status undermines confidence.
   Evidence: top bar in screenshots.
   `Gnosis offline / backend unavailable` is visible while using GNU.IN settings. If settings can still function, the UI should distinguish "assistant offline" from "settings backend unavailable".

## Accessibility Risks

1. Keyboard path is not proven.
   The launcher hints at keyboard controls, but screenshots alone do not prove focus order, active focus visibility, or whether Settings can be opened reliably from keyboard. The wrong destination from step 3 suggests keyboard and pointer activation may share the same broken route.

2. Small, low-contrast metadata.
   In the Displays page, raw monitor directives and secondary labels are small and muted. Users with low vision may not be able to read the exact mode, position, transform, or VRR state.

3. Color and icon chips carry too much meaning.
   `ST`, `DP`, `AP`, and status colors are compact but cryptic. The page needs visible text labels and accessible names for screen readers.

4. Action affordances are unclear.
   `ACTIVE` appears inside button-like controls but is not interactive. The `LIVE` button refreshes a snapshot, not live applying. These labels can mislead keyboard and screen-reader users.

5. Error recovery is absent from the screenshots.
   There is no visible rollback, confirmation, preview, or "restore previous layout" control for display changes. That is an accessibility and safety issue because display misconfiguration can make the system unusable.

## Opportunity Areas

1. Make launcher actions typed, named, and authoritative.
   Add a `GNU.IN Settings` shell action and a `Display Settings` shell action. Rank them above app search results for `settings`, `display`, `monitor`, `screen`, and `hyprland`.

2. Add direct page routing.
   Provide commands such as:
   - `gnuin-cli settings`
   - `gnuin-cli settings displays`
   - `gnuin-cli raw settings openPage displays`

3. Make Displays a real workbench.
   Each monitor should have controls for resolution/mode, refresh, position, scale, rotation/transform, mirror, bit depth, VRR, HDR, enable/disable, and workspace anchoring. Use `hyprconfd monitor-set` and `workspace-set` behind the UI.

4. Add preview/apply/persist/rollback.
   Before applying a display change, show the generated directive, the affected outputs, and a timed rollback prompt.

5. Separate status from configuration.
   Keep live diagnostics, but do not make raw directives the main UI. Diagnostics can be an expandable "Advanced" section.

6. Improve focus and privacy treatment.
   Settings should visually own the task. Use a stronger scrim or workspace isolation when editing displays, especially because broken display changes are high-risk.

## Recommendations

P0 - Fix launcher destination.
The `Settings` result must launch GNU.IN Settings, not an unrelated authentication window. Until that is fixed, the launcher cannot be trusted for settings access.

P0 - Rename and split settings entries.
Use `GNU.IN Settings` for the shell settings app, `Display Settings` for the displays page, and reserve generic `Settings` for external apps only if clearly labeled.

P1 - Add direct Displays routing.
Make `gnuin-cli settings displays` and launcher `Display Settings` open the Displays page directly. This removes the current hidden dependency on last active page or manual nav.

P1 - Turn Displays into a guided display manager.
Replace the raw snapshot-first layout with monitor cards, controls, a topology canvas or ordered position controls, preview, apply, persist, and rollback.

P1 - Clarify backend status.
Separate `Gnosis offline` from display/settings backend state. If `hyprconfd` is healthy, the settings UI should say that clearly.

P2 - Improve readability and interaction labels.
Increase contrast and size for monitor directives, replace cryptic two-letter chips with labeled icons, and avoid button styling for non-interactive statuses.

## Evidence Limits

- Screenshots cannot prove screen-reader output, keyboard focus order, hit target size, or WCAG compliance.
- Native Wayland overlays could not be captured with Browser or Chrome; `grim` was used instead.
- The audit did not mutate monitor settings. It did not test `hyprconfd monitor-set` from the UI because the UI does not expose those controls yet.
- The right monitor contained unrelated app windows behind GNU.IN overlays; findings account for that visual context but do not inspect those apps.
