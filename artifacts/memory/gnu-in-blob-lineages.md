---
name: gnu-in-blob-lineages
description: "Three parallel GNU.IN \"blob\" engines and the decision to consolidate on blobin-core"
metadata: 
  node_type: memory
  type: project
  originSessionId: b3b32797-38ae-4ac4-8402-162d95119c88
---

Verified 2026-07-01. There are **three** parallel blob renderers, and the compositor kernel uses none of them for the blob shape:

1. `engine/blob.in` (`blobin-core`) — Rust-native 4.0 organic engine: lyon tessellation, superellipse/bloom, `raster.rs` CPU mirror of `blob.frag`, golden-parity harness (r7–r10 + rtx3070 hardware run). The asset worth keeping, but currently **orphaned** from the compositor. Authority copy is ahead of ZIP9 (ZIP9 is port-from seed).
2. `engine/blob-uniforms` — byte-for-byte port of the **QML** `blobmaterial.cpp` std140 UBO serializer (+ `polish.rs`). Feeds `blob.frag` GLSL; consumed **only by `blob-qml`**. Legacy QML tail — dies when the QML shell dies.
3. `gnuin-compose-core` blob node — the kernel renders the blob in its own `render.rs`; SDF tier via `blob-uniforms` is **specced (spec §5) but NOT wired**. compose-core references `blob.in` only for token codegen, not the shape engine.

**Decision (corrected "decision A"):** make `blobin-core` the blob-node primitive provider for `compose-core` (organic/SDF tier via a renderer-agnostic `Primitive::Custom` = mesh or raster patch). Retire `blob-uniforms` with the QML lane. Keep blobin-core standalone for the Gnosis mascot. NOT "evolve blobin-core into the whole kernel" — compose-core is the kernel.

**Closed 2026-07-01:** `gnuin-compose-core/src/render.rs` records abstract `DrawCmd`s, not pixels. The blob emits `DrawCmd::SdfBlob { rect, backs, fill, phase, amplitude, z }` — "SDF/membrane blob request with a static rounded-rect fallback." That's the renderer-agnostic seam already present (carries phase/amplitude like blobin-core state.rs). So compose-core is untouched; blobin-core plugs in at the **host paint step** (`SdfBlob → blobin_core::raster` into the tiny-skia Pixmap, rounded-rect fallback under pressure); blobin-core goldens become the blob parity gate. Decisions A+C land in one host function. No SDF shader / no blob-uniforms needed.

Related: [[gnu-in-renderer-stack]], [[gnu-in-layer-shell-host-decision]].
