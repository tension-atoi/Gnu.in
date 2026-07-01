# RTTC Evolution (DB-like projection)

Generated: 2026-07-01T03:43:08Z

Descriptive projection of the RTTC scan into the registry DB vocabulary (`schema/registry_schema.sql`). Columns map to `registry_objects` (stable_id, version, source_authority, parent, lifecycle status). Values are read from frontmatter or derived by explicit rules; nothing is written to a live DB and no lineage is fabricated.

## Contract
- Lifecycle vocab: schema/registry_schema.sql lifecycle_statuses
- source_authority enum: ZIP9/Central, mixed, runtime, screenshot, spec-doc
- Dates: metadata-first (updated>created), same as catalog snapshot
- version = `frontmatter.chunk_version`; promotion_state = derived from `status`; parent resolved only from an unambiguous ref.

## Summary
- Components: 30
- Revision rows: 30
- Parent links resolved: 10 / unresolved: 20
- Multi-version components: 0

### promotion_state distribution

| promotion_state | count |
|---|---:|
| candidate | 4 |
| canonical | 1 |
| deprecated | 3 |
| draft | 22 |

### source_authority distribution

| source_authority | count |
|---|---:|
| - | 6 |
| runtime | 4 |
| spec-doc | 20 |

## Evolution per component (latest revision)

| stable_id | slug | kind | db_type | ver | promotion_state | source_authority | parent | created | updated | last_activity (src) |
|---|---|---|---|---:|---|---|---|---|---|---|
| rttc-motion-bar-sweep | BarSweep | motion | molecule | 1 | draft | spec-doc | - | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-breach-frame | BreachFrame | motion | molecule | 1 | draft | spec-doc | - | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-check-tick | CheckTick | motion | molecule | 1 | draft | spec-doc | - | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-dots-march | DotsMarch | motion | molecule | 1 | draft | spec-doc | - | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-failsafe | Failsafe | motion | molecule | 1 | draft | spec-doc | - | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-lock-wake | LockWake | motion | molecule | 1 | draft | spec-doc | - | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-mascot | Mascot | motion | molecule | 1 | draft | spec-doc | rttc-uikit-mascot-mini | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-notif-pill | NotifPill | motion | molecule | 1 | draft | spec-doc | - | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-notif-stack | NotifStack | motion | molecule | 1 | draft | spec-doc | - | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-orbit-spinner | OrbitSpinner | motion | molecule | 1 | draft | spec-doc | - | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-prompt-cursor | PromptCursor | motion | molecule | 1 | draft | spec-doc | - | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-radio-pulse | RadioPulse | motion | molecule | 1 | draft | spec-doc | - | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-spec-sheet | MotionSpecSheet | motion | molecule | 1 | draft | spec-doc | rttc-motion-orbit-spinner | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-motion-toggle-switch | ToggleSwitch | motion | molecule | 1 | draft | spec-doc | - | 2026-05-16 | - | 2026-05-16 (created) |
| components-motion-atoms-readme | README | atom | atom | 1 | draft | - | - | - | - | - (missing) |
| components-motion-molecules-readme | README | molecule | molecule | 1 | draft | - | - | - | - | - (missing) |
| rttc-gnosis-app-2026-06-01 | GnosisApp | component | - | 1 | candidate | - | - | 2026-06-01 | 2026-06-02 | 2026-06-02 (updated) |
| rttc-gnosis-tracker-overlay-2026-06-01 | GnosisTrackerOverlay | component | - | 1 | candidate | - | - | 2026-06-01 | 2026-06-01 | 2026-06-01 (updated) |
| rttc-cmp-context-menu-host | ContextMenuHost | deprecated | - | 1 | deprecated | runtime | rttc-uikit-context-menu | 2026-05-16 | - | 2026-05-16 (created) |
| components-root-lockoverlay | LockOverlay | surface | - | 1 | canonical | - | - | 2026-05-16 | 2026-05-16 | 2026-05-16 (updated) |
| components-uikit-gnuicon | GnuIcon | component | - | 1 | candidate | - | - | 2026-05-16 | 2026-06-07 | 2026-06-07 (updated) |
| rttc-uikit-dock | Dock | component | - | 1 | draft | spec-doc | rttc-uikit-mascot-mini | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-uikit-mascot-mini | MascotMini | component | - | 1 | draft | spec-doc | rttc-motion-mascot | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-uikit-notif-pill | NotifPill | component | - | 1 | draft | spec-doc | rttc-motion-notif-pill | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-uikit-onboarding-card | OnboardingCard | component | - | 1 | draft | spec-doc | rttc-uikit-mascot-mini | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-uikit-system-chip | SystemChip | component | - | 1 | draft | runtime | rttc-uikit-mascot-mini | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-uikit-syster-tooltip | SysterToolTip | component | - | 2 | candidate | runtime | - | 2026-05-16 | 2026-06-07 | 2026-06-07 (updated) |
| rttc-uikit-toast | Toast | component | - | 1 | draft | runtime | - | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-uikit-context-menu | ContextMenu | prototype | - | 1 | deprecated | spec-doc | rttc-uikit-context-menu-archetypes | 2026-05-16 | - | 2026-05-16 (created) |
| rttc-uikit-context-menu-archetypes | ContextMenu.archetypes | prototype | - | 1 | deprecated | spec-doc | rttc-uikit-context-menu | 2026-05-16 | - | 2026-05-16 (created) |

