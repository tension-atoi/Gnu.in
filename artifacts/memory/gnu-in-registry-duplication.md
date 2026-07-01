---
name: gnu-in-registry-duplication
description: gnuin-asset-core is the real in-engine registry; my tooling/ duplicates it
metadata: 
  node_type: memory
  type: reference
  originSessionId: b3b32797-38ae-4ac4-8402-162d95119c88
---

`gnu.in-os/engine/gnuin-asset-core` is the real component/asset registry: UI-free, **SQLite** durable index, provenance + policy in typed Rust, and it `include_str!`s `blob.in/tokens.json` as the token SSOT.

My session tooling partly reinvented it and should be **folded in, not maintained in parallel**:
- `tooling/registry-catalog/` — SQLite `registry_schema.sql` (lifecycle/promotion/source_authority/parent + proofs/golden) + `generate_catalog_views.py` (scans `gnu.in-shell/**/*.rttc.md`). Problem: the `.rttc` inputs point at the **retiring QML shell** (`qml_target_path`), i.e. it catalogs the graveyard. The schema/mechanism is good; re-point inputs at the `gnuin-*` Rust crates or merge into gnuin-asset-core.
- `tooling/asset-index/` — durable index of ZIP9 (extract + `build_index.py` → `index/*.json` + blob.in reconcile). Keep as the ZIP9 provenance/port-from index; ZIP9 is seed, `engine/blob.in` is authority.

Goal per the user: registry should be **runtime-emitted** (each host/widget self-declares identity+lifecycle+source_authority+parent), not scraped — solves the "re-derive from N files" pain at the architecture level. Related: [[gnu-in-renderer-stack]].
