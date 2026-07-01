---
name: gnu-in-renderer-stack
description: "GNU.IN shell renderer/host reality — verified dep facts, single-renderer is precluded"
metadata: 
  node_type: memory
  type: project
  originSessionId: b3b32797-38ae-4ac4-8402-162d95119c88
---

Verified 2026-07-01 by grep over `gnu.in-os/engine/**/Cargo.toml` + src. This is the shipping reality, not the aspiration.

- **Two renderer lanes, forced by Wayland roles** (not a choice to revisit): GPUI (Zed) speaks only `xdg-shell` → used for app windows (Settings/Control Center, gnosis-app, findin file-manager). `wlr-layer-shell` chrome cannot use GPUI, so all chrome uses **smithay-client-toolkit + calloop + tiny-skia (CPU raster)**.
- Dep counts: tiny-skia ~20 crates, smithay-client-toolkit/calloop ~21, gpui 4, zbus 5. **wgpu / iced / taffy / glyphon / cosmic-text / accesskit = 0** (not adopted). So a proposal built on wgpu+Iced diverges from the tree; adopting either now adds a THIRD lane. "Single renderer" is precluded by the GPUI-layer-shell constraint.
- **Kernel** = `gnuin-compose-core` (framework-free `Scene`+tokens+motion+layout+render, unit-tested), governed by `docs/COMPOSITION_ENGINE_SPEC.md`, built to kill the membrane (single-owner NodeId::Bar #5, engine-assigned geometry #4, engine-owned z/input). Host = `gnuin-compose-host` (sctk/tiny-skia Scene→pixels).
- **Duplication debt**: the good sctk host loop lives only in `gnuin-compose-host/src/main.rs` (binary, not lib), so bar/dock/osd/launcher/notification each re-implement the full loop (own `delegate_*!` + `LayerShellHandler` + shm/Pixmap draw). Extraction into a generic `LayerShellHost<S>` is the fix — see [[gnu-in-layer-shell-host-decision]].
- Token SSOT is already correct: `blob.in/tokens.json → blobin-gen → gen/gnu_theme.rs → compose-core`. Leave it.

Related: [[gnu-in-blob-lineages]], [[gnu-in-registry-duplication]].
