# LayerShellHost extraction + blob-engine decision

> Status: analysis / decision memo · 2026-07-01 · posture Level 1 (no source changed)
> Scope: (1) extract the shared `wlr-layer-shell` host that every `gnuin-*` chrome
> surface currently re-implements; (2) decide which of the three parallel "blob"
> lineages the compositor kernel adopts.
> Basis: read of `gnuin-compose-core`, `gnuin-compose-host`, `gnuin-shell-chrome`,
> `gnuin-asset-core`, `blob-uniforms`, and the `gnuin-bar/dock/osd/launcher/notification`
> surfaces, plus `docs/COMPOSITION_ENGINE_SPEC.md`. Dep facts verified by grep over
> `Cargo.toml` + `src`.

---

## Part 1 — Shared `LayerShellHost` (verdict: GO)

### 1.1 The finding

The runtime kernel already exists: `gnuin-compose-core` (framework-free `Scene` +
`tokens` + `motion` + `layout` + `render`, unit-tested) is the reactive compositor
core, and its design purpose per `COMPOSITION_ENGINE_SPEC.md` is to **kill the
membrane** (single-owner `NodeId::Bar` = tech-debt #5; engine-assigned geometry =
the "panneau noir" race #4; engine-owned z/input).

What is **not** shared is the Wayland host loop. Measured:

| surface | own `delegate_*!` set | `LayerShellHandler` impls | shm/Pixmap draw files |
|---|---|---|---|
| gnuin-bar | compositor·layer·output·pointer·registry·seat·shm | 1 | 3 |
| gnuin-dock | compositor·layer·output·pointer·registry·seat·shm | 1 | 3 |
| gnuin-osd | compositor·layer·output·registry·shm | 1 | 2 |
| gnuin-launcher | + `delegate_keyboard!` | 1 | 2 |
| gnuin-notification | compositor·layer·output·pointer·registry·seat·shm | 1 | 2 |

Five+ surfaces each re-implement the same ~500–1000-line sctk loop. The canonical,
best-developed version lives in `gnuin-compose-host/src/main.rs` (the `App` struct +
handlers), but **only in the binary** — `gnuin-compose-host/src/lib.rs` exposes
render helpers (`paint_scene`, `scene_builder`, `motion_driver`) and **no host**.
So the good loop cannot be imported; it is copy-adapted per surface. This is the
root duplication, and it is exactly the extraction `gnuin-shell-chrome`'s own doc
deferred "until dock/launcher provide a third consumer that justifies it" — a bar
that is now cleared (dock, osd, launcher, notification all exist).

Per-surface variation is small and structured: which input delegates are needed
(osd is non-interactive; launcher needs keyboard), anchors / exclusive-zone /
keyboard-interactivity, and the `Scene` the surface builds. Everything else —
registry, output, shm `SlotPool`, `LayerSurface` lifecycle, `configure`, frame-
callback pacing, `Pixmap` draw+swap — is identical boilerplate.

### 1.2 The blocker named by `gnuin-shell-chrome`, and its resolution

Two obstacles were cited for deferring the shared host:

1. **Two paint strategies** — "bar paints BGRA directly; compose-host rasterizes a
   tiny-skia `Pixmap` then swaps." Resolution: standardize on the **Pixmap →
   `Argb8888`** path (compose-host's), because it is the one already coupled to
   `compose_core::render(Scene)`. Bar's direct-BGRA is the older bespoke path and
   is retired by the migration, not preserved.
2. **`sctk delegate_*!` macros bind to the concrete host type.** Resolution: make
   the host **generic** and invoke each `delegate_*!` once on that generic type.
   The macros accept a generic `LayerShellHost<S>`; the per-surface behaviour is a
   trait `S`, so there is exactly one set of delegate invocations in the tree.

### 1.3 Proposed surface

New crate (or a `host` module promoted into `gnuin-shell-chrome`): a generic host
plus a per-surface trait. The host owns all Wayland side-effects; the surface owns
config, scene, and input reduction — the Elm loop, with `compose-core` already
providing the `Scene`/reducer/motion halves.

```rust
/// Per-surface behaviour. One impl per chrome surface (bar, dock, osd, …).
pub trait ShellSurface: 'static {
    type State;
    type Msg;

    /// Static layer-shell configuration (namespace, anchor, exclusive zone,
    /// keyboard interactivity, desired size policy).
    fn config(&self) -> SurfaceConfig;

    /// Build the immutable scene for the current state (delegates to compose-core
    /// scene builders). The host rasterizes it; the surface never touches pixels.
    fn scene(&self, state: &Self::State, screen: Rect) -> gnuin_compose_core::Scene;

    /// Fold an input/system event into messages (pure; unit-testable, no sctk).
    fn update(&self, state: &mut Self::State, ev: HostEvent) -> Vec<Self::Msg>;

    /// Optional: react to messages with host effects (redraw is implicit).
    fn effect(&self, _state: &mut Self::State, _msg: Self::Msg) -> Vec<Effect> { vec![] }
}

/// Owns registry/seat/output/shm/pool/LayerSurface/frame-clock/draw. Generic so
/// the sctk delegate macros are declared exactly once, here.
pub struct LayerShellHost<S: ShellSurface> {
    // registry_state, seat_state, output_state, shm, pool, compositor,
    // layer_shell, layer, surface_configured, pointer, keyboard, size, motion
    // timing, frame_index/current_fps … (lifted from compose-host `App`)
    surface: S,
    state: S::State,
}

impl<S: ShellSurface> LayerShellHost<S> {
    pub fn new(surface: S, state: S::State) -> Self { /* … */ }
    pub fn run(self) -> anyhow::Result<()> { /* calloop loop */ }
    fn draw(&mut self) { /* Pixmap::new → paint_scene(compose_core::render(scene)) → Argb8888 swap */ }
}

// One place, generic over S — resolves the delegate-macro-binds-to-concrete blocker:
delegate_compositor!(@<S: ShellSurface> LayerShellHost<S>);
delegate_layer!(@<S: ShellSurface> LayerShellHost<S>);
delegate_output!(@<S: ShellSurface> LayerShellHost<S>);
delegate_seat!(@<S: ShellSurface> LayerShellHost<S>);
delegate_pointer!(@<S: ShellSurface> LayerShellHost<S>);
delegate_keyboard!(@<S: ShellSurface> LayerShellHost<S>);
delegate_shm!(@<S: ShellSurface> LayerShellHost<S>);
delegate_registry!(@<S: ShellSurface> LayerShellHost<S>);
```

Non-interactive surfaces (osd) simply produce no messages from pointer/keyboard;
the host always registers the delegates and the trait's `update` ignores what it
doesn't care about — the delegate set stays uniform (one declaration site).

`gnuin-compose-host`'s existing `App` (menu overlay + QML IPC + `MotionDriver`)
becomes the **first implementor** of `ShellSurface`, validating the trait against
the most complex surface before touching the simpler ones.

### 1.4 Migration order (strangler; safe on a dirty tree)

0. Land/branch the current WIP first (219 uncommitted entries on
   `feat/central-parity-surfaces` — do not start on top of it).
1. Extract `LayerShellHost<S>` + `ShellSurface` (lift from compose-host `App`).
2. Re-express compose-host's menu overlay as `impl ShellSurface` (proves the trait).
3. Port **osd** (simplest: no pointer/seat) → delete its bespoke loop.
4. Port **notification**, then **bar + dock** — with bar/dock fully on
   `compose_core::Scene`, single-ownership is a kernel invariant and the **membrane
   is deleted**, not patched (resolves defects #3/#4/#5 structurally).
5. Port **launcher** (keyboard).
6. Fold `tooling/registry-catalog` into `gnuin-asset-core` (the real SQLite
   registry); the port ledger becomes runtime-emitted, not scraped.

---

## Part 2 — Blob-engine decision

### 2.1 There are three parallel blob lineages, and the kernel uses none of them

| lineage | what it is | feeds | dep'd by | lane |
|---|---|---|---|---|
| `engine/blob.in` (`blobin-core`) | Rust-native 4.0 organic engine: lyon tessellation, superellipse/bloom, `raster.rs` CPU mirror of `blob.frag`, golden parity | (its own Qt shim, now dead) | nothing in the shell | **orphan / mascot?** |
| `engine/blob-uniforms` | **byte-for-byte port of the QML** `blobmaterial.cpp` std140 UBO serializer (`+ polish.rs` port of `updatePolish`) | `blob.frag` (GLSL) | `blob-qml` only | **legacy QML tail** |
| `gnuin-compose-core` blob node | the compositor kernel renders the blob as an engine-owned node in its own `render.rs` (4239 LoC); SDF tier via `blob-uniforms` is **specced (§5) but not wired** | — | the shipping surfaces | **shipping kernel** |

Verified: `gnuin-compose-core` references `blob.in` **only** for the token codegen
(`include!("../../blob.in/gen/gnu_theme.rs")`), not the shape engine. Nothing in
the compositor or the surfaces depends on `blobin-core` or `blob-uniforms`. So the
kernel's live blob rendering is compose-core's own `render.rs`, and both "blob
engines" sit outside it.

### 2.2 Reading

- `blob-uniforms` exists to keep a **QML/C++ GPU material** byte-identical during
  the port. Its only consumer is `blob-qml`. When the QML shell dies (the whole
  point of this arc), its consumer dies with it. **`blob-uniforms` is legacy tail,
  not the future** — do not build the kernel's blob on it.
- `blobin-core` is the Rust-native engine with the golden-parity harness — the
  asset worth keeping — but it is currently orphaned from the compositor.
- `compose-core` is where the blob must actually render, and today it does so
  itself.

### 2.3 Recommendation (decision A, corrected)

Not "evolve blobin-core into the whole kernel" (compose-core is the kernel).
Instead: **make `blobin-core` the blob-node primitive provider for
`compose-core`** — the organic/SDF tier of the engine-owned blob node — via a
renderer-agnostic `Primitive::Custom` that hands compose-core either a tessellated
mesh or a rasterized `Pixmap` patch (blobin-core already has both: `tessellate.rs`
and `raster.rs`). Retire `blob-uniforms` with the QML lane. Keep `blobin-core`'s
standalone use for the Gnosis mascot.

Net: one blob engine (`blobin-core`) feeding two consumers (compose-core chrome
node + Gnosis mascot), the golden harness preserved as the parity gate, and the
QML-parity port (`blob-uniforms` + `blob.frag` GLSL) retired rather than carried.

### 2.4 The seam already exists (question closed, 2026-07-01)

Read of `gnuin-compose-core/src/render.rs`: compose-core does **not** rasterize —
it records abstract `DrawCmd`s. The blob node emits a first-class

```rust
DrawCmd::SdfBlob { id, kind, rect, backs, fill, phase, amplitude, z }
//   "SDF/membrane blob request with a static rounded-rect fallback available
//    to pressure-constrained hosts."
```

That **is** the renderer-agnostic `Primitive::Custom` seam decision C asked for —
it already exists, and it carries `phase`/`amplitude` (the same wobble drivers as
`blobin-core::state.rs`). So:

- compose-core is **untouched** — it already abstracts the blob correctly and
  derives its rect via `layout::blob_rect` (engine-owned, kills the panneau-noir race).
- The blob realization lives entirely in the **host paint step**: interpret
  `DrawCmd::SdfBlob` → today, the static rounded-rect fallback (tiny-skia); upgraded,
  **`blobin-core::raster.rs`** rasterizes the organic superellipse+bloom into the
  Pixmap patch for `rect`, driven by `phase`/`amplitude`. No SDF shader, no
  `blob-uniforms`, no compose-core change.
- `blobin-core`'s existing golden PNGs become the host's blob-render parity gate.

So decisions A + C **land together in one function** inside `LayerShellHost`:
`match DrawCmd::SdfBlob → blobin_core::raster(rect, fill, phase, amplitude)`, with
the rounded-rect fallback under frame-budget pressure. `blob-uniforms` + `blob.frag`
GLSL retire with the QML lane, uncarried.

---

## Consolidated debt map (what collapses into these two moves)

- ~20× duplicated sctk host loop → one `LayerShellHost<S>`.
- The membrane (#3/#4/#5) → deleted as a byproduct of bar/dock on `compose_core::Scene`.
- Two/three blob engines → one (`blobin-core`), QML material port retired.
- `tooling/registry-catalog` (my earlier work) → folded into `gnuin-asset-core`.
- Token SSOT → already correct (`tokens.json → blobin-gen → gen/gnu_theme.rs →
  compose-core`); leave it.

## Risks / honesty

- The generic-over-`S` delegate pattern is standard sctk but must be proven against
  the menu host (most complex) first; if a handler genuinely needs concrete-type
  state, that surfaces immediately in step 2.
- Dirty WIP branch is the top process risk — land it before extracting.
- Blob question is **closed** (§2.4): the `DrawCmd::SdfBlob` seam already exists;
  blobin-core plugs in at the host paint step with a rounded-rect fallback. No
  open reads remain for either decision.

## Verdict

GO on both. Extract `LayerShellHost` (the deferral condition is met and the
duplication is measured), and consolidate the blob lineages onto `blobin-core` as
compose-core's primitive provider while retiring the QML-material port. Start with
step 2 (menu host as first `ShellSurface` impl) once the WIP lands.
