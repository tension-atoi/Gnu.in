# GNU.IN session handoff — 2026-07-01

Reference snapshot of a working session. Everything below is committed and
green unless explicitly flagged. Files in this folder are copies for reference;
the live sources are under `tooling/` and `gnu.in-os/`.

---

## The arc, in one line

Started at "did you actually read ZIP9?" → ended with a shared Rust
`wlr-layer-shell` host that draws **live pixels**, with the OSD fully migrated
off its bespoke loop and validated on hardware.

## What was built (in order)

1. **RTTC catalog / DB-evolution view** — `tooling/registry-catalog`
   (`generate_catalog_views.py`). Honest date/provenance contract; projects the
   `.rttc.md` scan into the registry DB vocabulary. See `rttc-db-evolution.md`.
   *Debt found:* it indexes the **retiring QML shell**, and duplicates the real
   in-engine registry (`gnuin-asset-core`). Re-point or fold in.
2. **ZIP9 durable index** — `tooling/asset-index` (extract once + `build_index.py`).
   718 files catalogued; blob.in reconcile. See `zip9-asset-index.md`,
   `blob_in_reconcile.json`. **Verdict: ZIP9 is the port-from seed;
   `gnu.in-os/engine/blob.in` is the authority and is ahead.**
3. **Architecture reconciliation** — see `2026-07-01-layer-shell-host-and-blob-decision.md`
   and `memory/`. Established the real renderer stack, the three blob lineages,
   and the LayerShellHost extraction plan.
4. **Landed the WIP** — the ~235-file `feat/central-parity-surfaces` changeset,
   committed in **9 grouped commits** (see below). Release pointers deliberately
   **held** (they referenced a `-dirty` build).
5. **Built the shared host** — new crate `gnu.in-os/engine/gnuin-layer-host`, on
   branch `feat/layer-shell-host` (7 commits, see below).
6. **Cut osd over** — deleted its ~450-line bespoke sctk loop; `main.rs` 524→37.
   **Validated: 32 unit + 7 golden tests, and live on the compositor.**

## Branches (local, unpushed)

`feat/layer-shell-host` (this session's engine work), on top of the landed WIP:

```
4f98cb0 refactor(layer-host): state-based rasterizer (drop scene() from trait)
b735adb feat(layer-host): per-frame InputRegion (Full/Empty/Rects)
fdcd0de refactor(osd): cut over to LayerShellHost, delete bespoke loop
64339e6 feat(layer-host): multi-output retargetable surface + HostCommand
4d9e35a feat(layer-host): calloop event loop + external sources + timer
79d7918 feat(osd): map OsdState onto LayerShellHost via OsdSurface adapter
82bfb25 feat(layer-host): scaffold generic LayerShellHost<S> + ShellSurface trait
```

`feat/central-parity-surfaces` (the WIP landing, 9 grouped commits):

```
5219a1d docs(shell): central-parity specs, ledgers & render proofs
6328655 feat(engine): compose-core/host, shell-chrome & asset-core parity core
0423af6 feat(shell): central parity across native layer-shell surfaces
519f4d9 feat(settings): CENTRAL control-center parity (gpui)
0947570 chore(gnosis): sentinel telemetry + engine desktop theme
b23aae9 chore(tools): r7–r10 sign-off & review-packet tooling
ee76e47 test(os): retained-mode integration tests
ee7cfea chore(components): re-lock gnu.in-shell & gnosis-app pins
ad721f1 chore(state): xdg-desktop-portal config
```

## The renderer reality (verified, load-bearing)

Two lanes, forced by Wayland roles — **not** a choice to revisit:

- **xdg-shell app windows** → **GPUI** (Settings/Control Center, gnosis-app, file-manager).
- **wlr-layer-shell chrome** (bar, dock, osd, launcher, notifications, sidebars… ~20 crates)
  → **smithay-client-toolkit + calloop + tiny-skia (CPU)**. GPUI can't do layer-shell.
- **wgpu / iced / taffy / glyphon / accesskit = 0** (not adopted). Kernel =
  `gnuin-compose-core` (framework-free `Scene`); it exists to kill the **membrane**.

## The shared host — `gnuin-layer-host`

`ShellSurface` trait (pure, sandbox-testable; no Wayland/Pixmap):

```
type State;  type External: Send;
fn config(&self) -> SurfaceConfig
fn update(&self, &mut State, HostEvent) -> Redraw
fn on_external(&self, &mut State, External) -> Vec<HostCommand>   // IPC/watcher msgs
fn on_timer(&self, &mut State) -> Vec<HostCommand>                // if config.tick_interval
fn start<E: Fn(External)+Clone+Send>(&mut self, emit: E)          // spawn IO threads
fn input_region(&self, &State, Rect) -> InputRegion              // Full|Empty|Rects
```

`HostCommand::{ Redraw, ShowOn(Option<output>), Hide }`.
`SurfaceConfig`: layer, anchor, size, exclusive_zone, keyboard, `tick_interval`,
`lazy()` (on-demand surface), `click_through()`.

`LayerShellHost<S>::run(surface, state, raster)` where
`raster: FnMut(&State, Rect, &mut Pixmap)` (wayland-side; keeps the crate
decoupled from compose-host). Host owns: calloop loop, one retargetable
per-output layer surface, shm/pool draw, frame pacing, pointer, input regions.

## What's next

- **notification cutover (IN PROGRESS, task 20).** The host render contract was
  just generalized (state-based raster, commit 4f98cb0) precisely because
  notification renders from **state** via `render::paint_stack` (compose-host
  does NOT render notification content). Remaining: `NotificationSurface`
  (stack reducer + per-popup `HashMap<id,Instant>` deadlines + click hit-test via
  `layout(state)` + `input_region` = card rects), refactor `paint_stack` into a
  `paint_stack_into(&mut Pixmap,…)`, thin `main.rs`, delete the bespoke loop.
  Full shape is in `memory/gnu-in-layer-shell-host-decision.md`.
- **bar + dock** — always-visible (eager), interactive, external sources
  (battery/net/hypr). Their move onto `compose_core::Scene` + this host is what
  **structurally deletes the membrane** (single-owner `NodeId::Bar`).
- **blob** — consolidate on `blobin-core` as compose-core's `DrawCmd::SdfBlob`
  provider; retire `blob-uniforms` with the QML lane. See `memory/gnu-in-blob-lineages.md`.

## Operator to-dos

- Merge/rebase `feat/layer-shell-host` when satisfied.
- Regenerate a **clean (non-`dirty`) build** so the release tooling can un-hold
  `release/GLOBAL-VERSION.json`, `LATEST-BUILD`, `LATEST-VERSION-SIGNATURE`.
- Run engine crates from the **crate dir** (they're independent, no workspace):
  `cd engine/<crate> && cargo test --features wayland`.

## Gotchas banked

- Manual OSD IPC test: `printf '%s\n' '<json>'` — a bare `printf` with a literal
  `%` (e.g. `"60%"`) truncates the message.
- `ShellSurface` can't take a `Pixmap` (wayland-only dep) — that's why rendering
  is the injected wayland-side raster, not a trait method.
