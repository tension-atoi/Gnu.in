# Rust-Assisted Membrane Governor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and prove a Rust-assisted `membranePerfTier=auto|static|sdf` governor that keeps the Quickshell topbar static at idle, enables SDF only for eligible morphing surfaces, records live CPU/RSS evidence, and survives the OS verify/build/promote/status chain.

**Architecture:** QML owns rendering and per-frame visual state. `gnosis-sentinel` owns low-frequency CPU/RSS/pressure sampling and emits a `static|sdf` recommendation; the shell consumes that through a small QML singleton, not direct ad hoc calls from `MembraneHost`. `blob.in` Rust engine files from the new `Context.spec.zip` are inventoried as the renderer migration source of truth, but not folded into this governor patch.

**Tech Stack:** Quickshell/QML, QML singletons, `qs ipc`, Rust `gnosis-sentinel`, `sysinfo`, zbus D-Bus, Python SQLite runtime UI matrix, GNU.IN OS release scripts.

---

## Scope and Success Criteria

This plan covers the whole remaining membrane performance governor lane:

- Inventory the new motion/spec sources and identify the Rust blob engine files.
- Lock QML settings and IPC for `membranePerfTier=auto|static|sdf`.
- Add and consume Sentinel's low-frequency membrane recommendation.
- Gate `BlobGroup`/SDF in `MembraneHost` and render static topbar idle fallback.
- Add shell, Sentinel, OS, matrix, build, and live perf contracts.
- Run full verification, OS build, promotion, status, runtime matrix, and post-build analysis.

A run is accepted only when all of these are true:

- `gnu.in-shell/tools/run-component-tests.sh` passes.
- `gnu.in-os/tools/verify.sh` passes.
- `gnu.in-os/tools/build.sh` produces a release containing shell changes, design-system mirror, motion spec inventory, and compatibility assets.
- `gnu.in-os/tools/promote-latest.sh <build-id>` succeeds.
- `gnu.in-os/tools/status.sh --strict` returns `status: OK`.
- `gnu.in-os/tools/runtime-ui-matrix.sh refresh-live` records `quickshell-idle-cpu`.
- `gnu.in-os/tools/runtime-ui-matrix.sh verify-live` passes and fails if idle Quickshell CPU is above `15%` of one core after settle.
- Post-build SQLite/artifact analysis is written to `gnu.in-os/audit/membrane-perf-post-build.md`.

## File Structure

Create:

- `gnu.in-os/tools/inventory-motion-specs.py` — scans selected zip files and emits a reproducible JSON inventory under `audit/`.
- `gnu.in-os/tests/integration/test_motion_spec_inventory_contract.sh` — proves the inventory tool tracks `Context.spec.zip`, `Contextmenuv4.zip`, `GNU.IN Design System (3).zip`, and `sys_ter_source_rig_v5.zip` without versioning generated audit output.
- `gnu.in-os/tests/integration/test_membrane_perf_governor_contract.sh` — regex/source contract for Sentinel and runtime matrix governor behavior.
- `gnu.in-shell/services/SentinelMembranePerfService.qml` — QML singleton that polls Sentinel D-Bus at low frequency and exposes `recommendedTier`, CPU/RSS, pressure, and `effectiveTier(requestedTier, morphingSurfaceOpen)`.
- `gnu.in-shell/tests/test_sentinel_membrane_perf_contract.sh` — shell component contract for the new QML singleton and its `MembraneHost` usage.
- `gnu.in-os/audit/membrane-perf-post-build.md` — generated post-build analysis; do not commit if `audit/` is ignored.

Modify:

- `gnu.in-shell/qmldir` — register `SentinelMembranePerfService` as a singleton.
- `gnu.in-shell/services/ShellSettingsService.qml` — add or verify `membranePerfTier`, normalization, persistence, and setter.
- `gnu.in-shell/services/ShellIpc.qml` — add or verify shell-settings IPC getters/setters.
- `gnu.in-shell/components/MembraneHost.qml` — consume `SentinelMembranePerfService`, compute `morphingSurfaceOpen`, gate SDF, and keep static topbar fallback.
- `gnu.in-shell/tests/test_shell_settings_contract.sh` — lock settings and IPC contracts.
- `gnu.in-shell/tests/test_gnosis_membrane_contract.sh` — lock static fallback, SDF gating, and no-input exclusion assumptions.
- `gnu.in-os/engine/gnosis-sentinel/src/state.rs` — add or verify `QuickshellSnapshot` inside `HardwareSnapshot`.
- `gnu.in-os/engine/gnosis-sentinel/src/monitor.rs` — add or verify Quickshell CPU/RSS sampling and recommendation rules.
- `gnu.in-os/engine/gnosis-sentinel/src/main.rs` — add or verify D-Bus/socket exposure for membrane perf.
- `gnu.in-os/tools/runtime-ui-scan.py` — add or verify `quickshell-idle-cpu` probe and `verify-live` CPU threshold.

Do not modify in this plan:

- `blob.in` renderer C++/Rust plugin integration in the shell runtime. That is a separate renderer migration lane.
- Generated captures under `gnu.in-os/audit/visual/`.
- Generated SQLite/HTML/MD audit files except the explicit post-build analysis if the repo policy allows committing it.

---

### Task 1: Source Inventory Tool for Motion Spec and blob.in Rust

**Files:**

- Create: `gnu.in-os/tools/inventory-motion-specs.py`
- Create: `gnu.in-os/tests/integration/test_motion_spec_inventory_contract.sh`

- [ ] **Step 1: Write the failing inventory contract**

Create `gnu.in-os/tests/integration/test_motion_spec_inventory_contract.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOL="$ROOT/tools/inventory-motion-specs.py"

fail() {
  printf '[FAIL] %s\n' "$1" >&2
  exit 1
}

assert_file() {
  [ -f "$1" ] || fail "missing ${1#$ROOT/}"
}

assert_contains() {
  local file="$1"
  local pattern="$2"
  grep -qE "$pattern" "$file" || fail "${file#$ROOT/} missing pattern: $pattern"
}

assert_file "$TOOL"
assert_contains "$TOOL" 'Context\.spec\.zip'
assert_contains "$TOOL" 'Contextmenuv4\.zip'
assert_contains "$TOOL" 'GNU\.IN Design System \(3\)\.zip'
assert_contains "$TOOL" 'sys_ter_source_rig_v5\.zip'
assert_contains "$TOOL" 'blob\.in/blobin-core/src/engine\.rs'
assert_contains "$TOOL" 'motion\.spec\.v5\.json'
assert_contains "$TOOL" 'Motion-Spec-4\.0-Plan\.md'
assert_contains "$TOOL" 'audit/motion-spec-inventory\.json'
assert_contains "$TOOL" 'sha256'

python3 "$TOOL" --check --output "$ROOT/audit/motion-spec-inventory.contract.json" >/tmp/gnuin-motion-inventory.out
assert_contains /tmp/gnuin-motion-inventory.out 'motion spec inventory OK'
assert_contains "$ROOT/audit/motion-spec-inventory.contract.json" '"rust_file_count"'
assert_contains "$ROOT/audit/motion-spec-inventory.contract.json" '"canonical_motion_specs"'

printf '[OK] motion spec inventory contract holds\n'
```

- [ ] **Step 2: Run the failing inventory contract**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
bash tests/integration/test_motion_spec_inventory_contract.sh
```

Expected before implementation:

```text
[FAIL] missing tools/inventory-motion-specs.py
```

- [ ] **Step 3: Implement the inventory tool**

Create `gnu.in-os/tools/inventory-motion-specs.py`:

```python
#!/usr/bin/env python3
"""Inventory GNU.IN motion/spec zip sources without extracting them.

Generated output is audit evidence. It is reproducible and should not be treated
as runtime source code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "audit" / "motion-spec-inventory.json"
ZIP_PATHS = [
    Path("/home/tension_atoi/Downloads/Context.spec.zip"),
    Path("/home/tension_atoi/Downloads/Contextmenuv4.zip"),
    Path("/home/tension_atoi/Downloads/GNU.IN Design System (3).zip"),
    Path("/home/tension_atoi/Downloads/sys_ter_source_rig_v5.zip"),
]
CANONICAL_MARKERS = [
    "Motion-Spec-4.0-Plan.md",
    "uploads/motion.spec.v4.json",
    "uploads/motion.spec.v4.md",
    "sys_ter_source_rig_v5/docs/motion.spec.v5.json",
    "sys_ter_source_rig_v5/docs/motion.spec.v5.md",
    "blob.in/tokens.json",
    "blob.in/blobin-core/src/engine.rs",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inspect_zip(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "zip": str(path),
            "exists": False,
            "entry_count": 0,
            "rust_file_count": 0,
            "canonical_motion_specs": [],
            "blobin_rust_files": [],
            "sha256": "",
        }

    blobin_rust_files: list[str] = []
    canonical_specs: list[dict[str, object]] = []
    with ZipFile(path) as zf:
        names = sorted(zf.namelist())
        for name in names:
            if name.endswith(".rs") and name.startswith("blob.in/"):
                blobin_rust_files.append(name)
            if name in CANONICAL_MARKERS or "motion.spec" in name.lower() or name.endswith("Motion-Spec-4.0-Plan.md"):
                data = zf.read(name)
                canonical_specs.append({
                    "path": name,
                    "bytes": len(data),
                    "sha256": sha256_bytes(data),
                })

    return {
        "zip": str(path),
        "exists": True,
        "sha256": sha256_bytes(path.read_bytes()),
        "entry_count": len(names),
        "rust_file_count": len(blobin_rust_files),
        "canonical_motion_specs": canonical_specs,
        "blobin_rust_files": blobin_rust_files,
    }


def build_inventory() -> dict[str, object]:
    zips = [inspect_zip(path) for path in ZIP_PATHS]
    return {
        "schema": "gnu.in.motion-spec-inventory.v1",
        "source_rule": "Zips remain external design/reference inputs; runtime consumes generated/native artifacts only.",
        "zips": zips,
        "summary": {
            "zip_count": len(zips),
            "existing_zip_count": sum(1 for z in zips if z["exists"]),
            "rust_file_count": sum(int(z["rust_file_count"]) for z in zips),
            "canonical_motion_spec_count": sum(len(z["canonical_motion_specs"]) for z in zips),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    inventory = build_inventory()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")

    missing = [z["zip"] for z in inventory["zips"] if not z["exists"]]
    rust_count = int(inventory["summary"]["rust_file_count"])
    spec_count = int(inventory["summary"]["canonical_motion_spec_count"])
    if args.check:
        if missing:
            print("motion spec inventory missing zip(s): " + ", ".join(missing))
            return 1
        if rust_count < 17:
            print(f"motion spec inventory insufficient rust files: {rust_count}")
            return 1
        if spec_count < 4:
            print(f"motion spec inventory insufficient canonical specs: {spec_count}")
            return 1
    print(f"motion spec inventory OK: rust={rust_count} specs={spec_count} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Make the tool executable and run the contract**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
chmod +x tools/inventory-motion-specs.py
bash tests/integration/test_motion_spec_inventory_contract.sh
```

Expected:

```text
[OK] motion spec inventory contract holds
```

- [ ] **Step 5: Commit**

```bash
cd /home/tension_atoi/Projects/Gnu.in
git add gnu.in-os/tools/inventory-motion-specs.py gnu.in-os/tests/integration/test_motion_spec_inventory_contract.sh
git commit -m "Add motion spec inventory contract"
```

---

### Task 2: Sentinel Quickshell Snapshot and Membrane Recommendation

**Files:**

- Modify: `gnu.in-os/engine/gnosis-sentinel/src/state.rs`
- Modify: `gnu.in-os/engine/gnosis-sentinel/src/monitor.rs`
- Modify: `gnu.in-os/engine/gnosis-sentinel/src/main.rs`
- Create: `gnu.in-os/tests/integration/test_membrane_perf_governor_contract.sh`

- [ ] **Step 1: Write the failing OS contract**

Create `gnu.in-os/tests/integration/test_membrane_perf_governor_contract.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STATE="$ROOT/engine/gnosis-sentinel/src/state.rs"
MONITOR="$ROOT/engine/gnosis-sentinel/src/monitor.rs"
MAIN="$ROOT/engine/gnosis-sentinel/src/main.rs"
MATRIX="$ROOT/tools/runtime-ui-scan.py"

fail() {
  printf '[FAIL] %s\n' "$1" >&2
  exit 1
}

assert_contains() {
  local file="$1"
  local pattern="$2"
  grep -qE "$pattern" "$file" || fail "${file#$ROOT/} missing pattern: $pattern"
}

assert_not_contains() {
  local file="$1"
  local pattern="$2"
  if grep -qE "$pattern" "$file"; then
    fail "${file#$ROOT/} contains forbidden pattern: $pattern"
  fi
}

assert_contains "$STATE" 'struct QuickshellSnapshot'
assert_contains "$STATE" 'cpu_percent_one_core'
assert_contains "$STATE" 'membrane_perf_tier'
assert_contains "$STATE" 'pub quickshell: QuickshellSnapshot'

assert_contains "$MONITOR" 'QUICKSHELL_IDLE_CPU_THRESHOLD: f32 = 15\.0'
assert_contains "$MONITOR" 'fn is_quickshell_process'
assert_contains "$MONITOR" 'fn recommend_membrane_perf_tier'
assert_contains "$MONITOR" 'PressureLevel::Critical.*static|static.*PressureLevel::Critical'
assert_contains "$MONITOR" 'PressureLevel::Elevated.*static|static.*PressureLevel::Elevated'
assert_contains "$MONITOR" 'quickshell_cpu > QUICKSHELL_IDLE_CPU_THRESHOLD'
assert_contains "$MONITOR" 'recommend_membrane_perf_tier_uses_pressure_and_quickshell_cpu'
assert_not_contains "$MONITOR" 'per_frame|frame_uniform|shape_uniform|json.*uniform'

assert_contains "$MAIN" 'fn get_membrane_perf'
assert_contains "$MAIN" '"membrane_perf"'
assert_contains "$MAIN" 'hardware\.quickshell|"quickshell"'

assert_contains "$MATRIX" 'QUICKSHELL_IDLE_CPU_THRESHOLD = 15\.0'
assert_contains "$MATRIX" 'QUICKSHELL_IDLE_SETTLE_SECONDS = 20\.0'
assert_contains "$MATRIX" 'quickshell-idle-cpu'
assert_contains "$MATRIX" 'cpu_percent_one_core'
assert_contains "$MATRIX" 'quickshell idle CPU too high'

printf '[OK] membrane perf governor contract holds\n'
```

- [ ] **Step 2: Run the failing OS contract**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
bash tests/integration/test_membrane_perf_governor_contract.sh
```

Expected before implementation:

```text
[FAIL] engine/gnosis-sentinel/src/state.rs missing pattern: struct QuickshellSnapshot
```

- [ ] **Step 3: Implement `QuickshellSnapshot` in Sentinel state**

In `gnu.in-os/engine/gnosis-sentinel/src/state.rs`, add this struct before `HardwareSnapshot` and include it in `HardwareSnapshot`:

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuickshellSnapshot {
    pub cpu_percent_one_core: f32,
    pub rss_mb: u64,
    pub pids: Vec<u32>,
    pub membrane_perf_tier: String,
    pub reason: String,
}

impl Default for QuickshellSnapshot {
    fn default() -> Self {
        Self {
            cpu_percent_one_core: 0.0,
            rss_mb: 0,
            pids: Vec::new(),
            membrane_perf_tier: "static".to_string(),
            reason: "not-sampled".to_string(),
        }
    }
}
```

Then ensure `HardwareSnapshot` contains:

```rust
pub quickshell: QuickshellSnapshot,
```

- [ ] **Step 4: Implement Sentinel recommendation logic**

In `gnu.in-os/engine/gnosis-sentinel/src/monitor.rs`, import `QuickshellSnapshot`:

```rust
use crate::state::{HardwareSnapshot, PressureLevel, ProcessSnapshot, QuickshellSnapshot, SentinelState};
```

Add these helpers near `classify_pressure`:

```rust
const QUICKSHELL_IDLE_CPU_THRESHOLD: f32 = 15.0;

fn is_quickshell_process(name: &str, cmdline: &str) -> bool {
    name == "quickshell"
        || cmdline.contains("quickshell")
        || (name == "qs" && cmdline.contains("shell.qml"))
}

fn recommend_membrane_perf_tier(pressure: &PressureLevel, quickshell_cpu: f32) -> (String, String) {
    match pressure {
        PressureLevel::Critical => ("static".to_string(), "critical-pressure".to_string()),
        PressureLevel::Elevated => ("static".to_string(), "elevated-pressure".to_string()),
        PressureLevel::Normal if quickshell_cpu > QUICKSHELL_IDLE_CPU_THRESHOLD => (
            "static".to_string(),
            format!("quickshell-cpu>{:.1}", QUICKSHELL_IDLE_CPU_THRESHOLD),
        ),
        PressureLevel::Normal => ("sdf".to_string(), "healthy".to_string()),
    }
}
```

Inside `run_hardware_monitor`, before building `top_processes`, compute Quickshell metrics:

```rust
let mut quickshell_cpu = 0.0_f32;
let mut quickshell_rss_mb = 0_u64;
let mut quickshell_pids = Vec::new();
for p in &process_list {
    let name = p.name().to_string_lossy().to_string();
    let cmdline = p
        .cmd()
        .iter()
        .map(|part| part.to_string_lossy())
        .collect::<Vec<_>>()
        .join(" ");
    if is_quickshell_process(&name, &cmdline) {
        quickshell_cpu += p.cpu_usage();
        quickshell_rss_mb += p.memory() / 1024 / 1024;
        quickshell_pids.push(p.pid().as_u32());
    }
}
```

After pressure stabilization, add:

```rust
let (membrane_perf_tier, reason) = recommend_membrane_perf_tier(&pressure, quickshell_cpu);
```

Then build the snapshot with:

```rust
quickshell: QuickshellSnapshot {
    cpu_percent_one_core: quickshell_cpu,
    rss_mb: quickshell_rss_mb,
    pids: quickshell_pids,
    membrane_perf_tier,
    reason,
},
```

Add the unit test in `monitor.rs`:

```rust
#[test]
fn recommend_membrane_perf_tier_uses_pressure_and_quickshell_cpu() {
    assert_eq!(
        recommend_membrane_perf_tier(&PressureLevel::Normal, 4.0).0,
        "sdf"
    );
    assert_eq!(
        recommend_membrane_perf_tier(&PressureLevel::Normal, 46.0).0,
        "static"
    );
    assert_eq!(
        recommend_membrane_perf_tier(&PressureLevel::Elevated, 4.0).0,
        "static"
    );
    assert_eq!(
        recommend_membrane_perf_tier(&PressureLevel::Critical, 4.0).0,
        "static"
    );
}
```

- [ ] **Step 5: Expose Sentinel recommendation through D-Bus and socket**

In `gnu.in-os/engine/gnosis-sentinel/src/main.rs`, add `quickshell` to `get_status()` hardware JSON:

```rust
"quickshell": state.hardware.quickshell,
```

Add this D-Bus method after `get_ledger_head`:

```rust
fn get_membrane_perf(&self) -> String {
    let state = self.state.blocking_read();
    serde_json::json!({
        "tier": state.hardware.quickshell.membrane_perf_tier,
        "reason": state.hardware.quickshell.reason,
        "quickshell_cpu_percent_one_core": state.hardware.quickshell.cpu_percent_one_core,
        "quickshell_rss_mb": state.hardware.quickshell.rss_mb,
        "pressure": format!("{:?}", state.hardware.pressure),
    })
    .to_string()
}
```

Add this case to the Unix socket `match msg_type`:

```rust
"membrane_perf" => {
    let s = state.read().await;
    serde_json::json!({
        "type": "membrane_perf",
        "tier": s.hardware.quickshell.membrane_perf_tier,
        "reason": s.hardware.quickshell.reason,
        "quickshell_cpu_percent_one_core": s.hardware.quickshell.cpu_percent_one_core,
        "quickshell_rss_mb": s.hardware.quickshell.rss_mb,
        "pressure": format!("{:?}", s.hardware.pressure),
    })
}
```

- [ ] **Step 6: Run Sentinel unit tests and OS source contract**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os/engine/gnosis-sentinel
cargo test
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
bash tests/integration/test_membrane_perf_governor_contract.sh
```

Expected:

```text
test result: ok
[OK] membrane perf governor contract holds
```

- [ ] **Step 7: Commit**

```bash
cd /home/tension_atoi/Projects/Gnu.in
git add gnu.in-os/engine/gnosis-sentinel/src/state.rs gnu.in-os/engine/gnosis-sentinel/src/monitor.rs gnu.in-os/engine/gnosis-sentinel/src/main.rs gnu.in-os/tests/integration/test_membrane_perf_governor_contract.sh
git commit -m "Add Sentinel membrane performance governor"
```

---

### Task 3: Shell Settings and IPC Contract for `membranePerfTier`

**Files:**

- Modify: `gnu.in-shell/services/ShellSettingsService.qml`
- Modify: `gnu.in-shell/services/ShellIpc.qml`
- Modify: `gnu.in-shell/tests/test_shell_settings_contract.sh`

- [ ] **Step 1: Extend shell settings contract first**

In `gnu.in-shell/tests/test_shell_settings_contract.sh`, ensure these assertions exist near existing motion settings assertions:

```bash
assert_contains "$SETTINGS" 'readonly property string membranePerfTier: _normalizeMembranePerfTier\(settingsAdapter\.membranePerfTier\)'
assert_contains "$SETTINGS" 'function _normalizeMembranePerfTier'
assert_contains "$SETTINGS" 'property string membranePerfTier: "auto"'
assert_contains "$SETTINGS" 'function setMembranePerfTier'
assert_contains "$SETTINGS" 'shell\.membrane\.perf_tier'
assert_contains "$SETTINGS" 'static.*sdf.*auto|auto.*static.*sdf'
```

Also ensure these assertions exist near shell-settings IPC assertions:

```bash
assert_contains "$IPC" 'function getMembranePerfTier\(\) : string'
assert_contains "$IPC" 'function setMembranePerfTier\(tier: string\) : string'
assert_contains "$IPC" 'ShellSettingsService\.setMembranePerfTier\(tier\)'
```

- [ ] **Step 2: Run the failing shell settings contract**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-shell
bash tests/test_shell_settings_contract.sh
```

Expected before implementation:

```text
FAIL: services/ShellSettingsService.qml missing pattern: readonly property string membranePerfTier
```

- [ ] **Step 3: Implement settings normalization and persistence**

In `gnu.in-shell/services/ShellSettingsService.qml`, add near the existing motion properties:

```qml
// membranePerfTier : "auto" | "static" | "sdf" — gates the expensive
//   blob.in membrane. auto idles static and enables SDF only for morphing surfaces.
readonly property string membranePerfTier: _normalizeMembranePerfTier(settingsAdapter.membranePerfTier)
```

Add this helper near `_normalizePerfTier`:

```qml
function _normalizeMembranePerfTier(value) {
    return (value === "static" || value === "sdf") ? value : "auto"
}
```

Add this persisted adapter property next to `motionPerfTier`:

```qml
property string membranePerfTier: "auto"
```

Add this setter near `setMotionPerfTier`:

```qml
function setMembranePerfTier(tier) {
    const next = _normalizeMembranePerfTier(tier)
    if (settingsAdapter.membranePerfTier === next)
        return
    settingsAdapter.membranePerfTier = next
    _requestSet("shell.membrane.perf_tier", next)
}
```

- [ ] **Step 4: Implement IPC accessors**

In `gnu.in-shell/services/ShellIpc.qml`, inside the `IpcHandler` with `target: "shell-settings"`, add:

```qml
function getMembranePerfTier() : string {
    return ShellSettingsService.membranePerfTier
}

function setMembranePerfTier(tier: string) : string {
    ShellSettingsService.setMembranePerfTier(tier)
    return ShellSettingsService.membranePerfTier
}
```

- [ ] **Step 5: Run the shell settings contract**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-shell
bash tests/test_shell_settings_contract.sh
```

Expected:

```text
[OK] shell-v2 settings/topbar/dock contract holds
```

- [ ] **Step 6: Commit**

```bash
cd /home/tension_atoi/Projects/Gnu.in
git add gnu.in-shell/services/ShellSettingsService.qml gnu.in-shell/services/ShellIpc.qml gnu.in-shell/tests/test_shell_settings_contract.sh
git commit -m "Add shell membrane performance setting"
```

---

### Task 4: QML Sentinel Membrane Perf Service

**Files:**

- Create: `gnu.in-shell/services/SentinelMembranePerfService.qml`
- Modify: `gnu.in-shell/qmldir`
- Create: `gnu.in-shell/tests/test_sentinel_membrane_perf_contract.sh`

- [ ] **Step 1: Write the failing shell service contract**

Create `gnu.in-shell/tests/test_sentinel_membrane_perf_contract.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE="$ROOT/services/SentinelMembranePerfService.qml"
QMLDIR="$ROOT/qmldir"
MEMBRANE="$ROOT/components/MembraneHost.qml"

fail() {
  printf '[FAIL] %s\n' "$1" >&2
  exit 1
}

assert_file() {
  [ -f "$1" ] || fail "missing ${1#$ROOT/}"
}

assert_contains() {
  local file="$1"
  local pattern="$2"
  grep -qE "$pattern" "$file" || fail "${file#$ROOT/} missing pattern: $pattern"
}

assert_not_contains() {
  local file="$1"
  local pattern="$2"
  if grep -qE "$pattern" "$file"; then
    fail "${file#$ROOT/} contains forbidden pattern: $pattern"
  fi
}

assert_file "$SERVICE"
assert_contains "$QMLDIR" 'singleton SentinelMembranePerfService 1\.0 services/SentinelMembranePerfService\.qml'
assert_contains "$SERVICE" 'pragma Singleton'
assert_contains "$SERVICE" 'in\.gnu\.Gnosis\.Sentinel'
assert_contains "$SERVICE" 'GetMembranePerf'
assert_contains "$SERVICE" 'interval:[[:space:]]*5000'
assert_contains "$SERVICE" 'function effectiveTier\(requestedTier, morphingSurfaceOpen\)'
assert_contains "$SERVICE" 'recommendedTier'
assert_contains "$SERVICE" 'cpuPercentOneCore'
assert_contains "$SERVICE" 'rssMb'
assert_contains "$SERVICE" 'pressure'
assert_contains "$SERVICE" 'JSON\.parse'
assert_not_contains "$SERVICE" 'interval:[[:space:]]*[0-9]{1,3}([^0-9]|$)'
assert_not_contains "$SERVICE" 'onFrame|beforeRendering|beforeSynchronizing|NumberAnimation|Behavior on'

assert_contains "$MEMBRANE" 'SentinelMembranePerfService\.effectiveTier\(requestedMembranePerfTier, morphingSurfaceOpen\)'

printf '[OK] sentinel membrane perf QML contract holds\n'
```

- [ ] **Step 2: Run the failing service contract**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-shell
bash tests/test_sentinel_membrane_perf_contract.sh
```

Expected before implementation:

```text
[FAIL] missing services/SentinelMembranePerfService.qml
```

- [ ] **Step 3: Implement the QML singleton**

Create `gnu.in-shell/services/SentinelMembranePerfService.qml`:

```qml
pragma Singleton

import QtQuick
import Quickshell
import Quickshell.Io as QsIo

Item {
    id: root
    width: 0
    height: 0

    readonly property string busName: "in.gnu.Gnosis.Sentinel"
    readonly property string objectPath: "/in/gnu/Gnosis/Sentinel"
    readonly property string interfaceName: "in.gnu.Gnosis.Sentinel"

    property bool available: false
    property string recommendedTier: "static"
    property string reason: "not-sampled"
    property real cpuPercentOneCore: 0
    property int rssMb: 0
    property string pressure: "Unknown"
    property string lastPayload: ""
    property string lastError: ""
    property int revision: 0

    Timer {
        id: pollTimer
        interval: 5000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: root.refresh()
    }

    function refresh() {
        if (pollProcess.running)
            return
        pollProcess.command = [
            "gdbus", "call", "--session",
            "--dest", root.busName,
            "--object-path", root.objectPath,
            "--method", root.interfaceName + ".GetMembranePerf"
        ]
        pollProcess.running = true
    }

    function effectiveTier(requestedTier, morphingSurfaceOpen) {
        const requested = String(requestedTier || "auto")
        if (requested === "sdf")
            return "sdf"
        if (requested === "static")
            return "static"
        if (!root.available)
            return morphingSurfaceOpen ? "sdf" : "static"
        if (root.recommendedTier === "static")
            return "static"
        return morphingSurfaceOpen ? "sdf" : "static"
    }

    function _parseGdbusString(output) {
        const text = String(output || "").trim()
        const first = text.indexOf("'")
        const last = text.lastIndexOf("'")
        if (first >= 0 && last > first) {
            return text.substring(first + 1, last)
                .replace(/\\'/g, "'")
                .replace(/\\\\/g, "\\")
        }
        return text
    }

    function _applyPayload(payload) {
        lastPayload = payload
        const obj = JSON.parse(payload)
        const tier = String(obj.tier || "static")
        recommendedTier = tier === "sdf" ? "sdf" : "static"
        reason = String(obj.reason || "unknown")
        cpuPercentOneCore = Number(obj.quickshell_cpu_percent_one_core || 0)
        rssMb = Math.round(Number(obj.quickshell_rss_mb || 0))
        pressure = String(obj.pressure || "Unknown")
        available = true
        lastError = ""
        revision += 1
    }

    QsIo.Process {
        id: pollProcess
        running: false
        stdout: QsIo.StdioCollector {
            onStreamFinished: {
                try {
                    root._applyPayload(root._parseGdbusString(this.text))
                } catch (e) {
                    root.available = false
                    root.lastError = String(e)
                }
            }
        }
        stderr: QsIo.StdioCollector {
            onStreamFinished: {
                if (this.text.length > 0) {
                    root.available = false
                    root.lastError = this.text
                }
            }
        }
    }
}
```

- [ ] **Step 4: Register the singleton**

Add this line to `gnu.in-shell/qmldir`:

```text
singleton SentinelMembranePerfService 1.0 services/SentinelMembranePerfService.qml
```

- [ ] **Step 5: Run the service contract**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-shell
bash tests/test_sentinel_membrane_perf_contract.sh
```

Expected until `MembraneHost` is wired in Task 5:

```text
[FAIL] components/MembraneHost.qml missing pattern: SentinelMembranePerfService.effectiveTier
```

- [ ] **Step 6: Commit the standalone service only if the project accepts partial contracts**

If the team requires every commit to pass all component tests, skip this commit and commit Tasks 4 and 5 together. If partial commits are accepted, run:

```bash
cd /home/tension_atoi/Projects/Gnu.in
git add gnu.in-shell/services/SentinelMembranePerfService.qml gnu.in-shell/qmldir gnu.in-shell/tests/test_sentinel_membrane_perf_contract.sh
git commit -m "Add Sentinel membrane perf QML service"
```

---

### Task 5: MembraneHost Static/SDF Cutover

**Files:**

- Modify: `gnu.in-shell/components/MembraneHost.qml`
- Modify: `gnu.in-shell/tests/test_gnosis_membrane_contract.sh`
- Modify: `gnu.in-shell/tests/test_sentinel_membrane_perf_contract.sh`

- [ ] **Step 1: Extend membrane contract**

In `gnu.in-shell/tests/test_gnosis_membrane_contract.sh`, ensure these assertions exist near existing `MembraneHost` assertions:

```bash
assert_contains "$MEMBRANE" 'requestedMembranePerfTier:[[:space:]]*ShellSettingsService\.membranePerfTier'
assert_contains "$MEMBRANE" 'morphingSurfaceOpen:[[:space:]]*contextMenuMorphingOpen'
assert_contains "$MEMBRANE" 'effectiveMembranePerfTier:[[:space:]]*SentinelMembranePerfService\.effectiveTier\(requestedMembranePerfTier, morphingSurfaceOpen\)'
assert_contains "$MEMBRANE" 'sdfMembraneActive:[[:space:]]*effectiveMembranePerfTier === "sdf"'
assert_contains "$MEMBRANE" 'id:[[:space:]]*staticTaskbarSurface'
assert_contains "$MEMBRANE" 'visible:[[:space:]]*!root\.sdfMembraneActive'
assert_contains "$MEMBRANE" 'BlobGroup[[:space:]]*\{'
assert_contains "$MEMBRANE" 'visible:[[:space:]]*root\.sdfMembraneActive'
assert_contains "$MEMBRANE" 'visible:[[:space:]]*root\.sdfMembraneActive && ContextMenuService\.open'
assert_contains "$MEMBRANE" 'visible:[[:space:]]*root\.sdfMembraneActive && launcher\._shown'
assert_contains "$MEMBRANE" 'visible:[[:space:]]*root\.sdfMembraneActive && sm\._shown'
```

- [ ] **Step 2: Run failing membrane contracts**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-shell
bash tests/test_gnosis_membrane_contract.sh
bash tests/test_sentinel_membrane_perf_contract.sh
```

Expected before implementation:

```text
[FAIL] components/MembraneHost.qml missing pattern: SentinelMembranePerfService.effectiveTier
```

- [ ] **Step 3: Wire `MembraneHost` effective tier**

In `gnu.in-shell/components/MembraneHost.qml`, near the root properties, use this property block:

```qml
readonly property string requestedMembranePerfTier: ShellSettingsService.membranePerfTier
readonly property bool contextMenuMorphingOpen: ContextMenuService.open && (ContextMenuService.screenName === "" || ContextMenuService.screenName === root.targetScreen.name)
readonly property bool morphingSurfaceOpen: contextMenuMorphingOpen
    || launcher.openOnScreen || launcher._shown
    || settings.openOnScreen
    || sm.openOnScreen || sm._shown
    || gnosisApp.openOnScreen
    || !dock.isHidden
readonly property string effectiveMembranePerfTier: SentinelMembranePerfService.effectiveTier(requestedMembranePerfTier, morphingSurfaceOpen)
readonly property bool sdfMembraneActive: effectiveMembranePerfTier === "sdf"
```

- [ ] **Step 4: Add static topbar fallback**

In the membrane geometry item, before `BlobGroup`, add:

```qml
Rectangle {
    id: staticTaskbarSurface
    visible: !root.sdfMembraneActive
    x: taskbarNode.x
    y: taskbarNode.y
    width: taskbarNode.width
    height: taskbarNode.height
    radius: taskbarNode.radius
    color: GnuChrome.membraneSurface
    opacity: root.membraneMetrics.visibleOpacity
}
```

- [ ] **Step 5: Gate SDF nodes**

Set the `BlobGroup` and taskbar `BlobRect` visibility:

```qml
BlobGroup {
    id: blobGroup
    visible: root.sdfMembraneActive
    color: GnuChrome.membraneSurface
    smoothing: root.membraneMetrics.blobSmoothing
}
```

```qml
BlobRect {
    group: blobGroup
    visible: root.sdfMembraneActive
    x: taskbarNode.x
    y: taskbarNode.y
    implicitWidth: taskbarNode.width
    implicitHeight: taskbarNode.height
    radius: taskbarNode.radius
    smoothing: taskbarNode.smoothing
}
```

Gate dynamic blobs with these exact predicates:

```qml
visible: root.sdfMembraneActive && ContextMenuService.open && ContextMenuService.usesMembraneChrome && (ContextMenuService.screenName === "" || ContextMenuService.screenName === root.targetScreen.name)
```

```qml
visible: root.sdfMembraneActive && !dock.isHidden
```

```qml
visible: root.sdfMembraneActive && sm._shown
```

```qml
visible: root.sdfMembraneActive && launcher._shown
```

- [ ] **Step 6: Run shell membrane contracts**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-shell
bash tests/test_gnosis_membrane_contract.sh
bash tests/test_sentinel_membrane_perf_contract.sh
```

Expected:

```text
[OK] gnosis membrane contract holds
[OK] sentinel membrane perf QML contract holds
```

- [ ] **Step 7: Commit**

```bash
cd /home/tension_atoi/Projects/Gnu.in
git add gnu.in-shell/components/MembraneHost.qml gnu.in-shell/tests/test_gnosis_membrane_contract.sh gnu.in-shell/tests/test_sentinel_membrane_perf_contract.sh gnu.in-shell/services/SentinelMembranePerfService.qml gnu.in-shell/qmldir
git commit -m "Gate membrane SDF with Sentinel performance tier"
```

---

### Task 6: Runtime UI Matrix CPU/RSS Perf Gate

**Files:**

- Modify: `gnu.in-os/tools/runtime-ui-scan.py`
- Modify: `gnu.in-os/tests/integration/test_membrane_perf_governor_contract.sh`

- [ ] **Step 1: Extend matrix contract**

In `gnu.in-os/tests/integration/test_membrane_perf_governor_contract.sh`, ensure these assertions exist:

```bash
assert_contains "$MATRIX" 'QUICKSHELL_IDLE_CPU_THRESHOLD = 15\.0'
assert_contains "$MATRIX" 'QUICKSHELL_IDLE_SETTLE_SECONDS = 20\.0'
assert_contains "$MATRIX" 'QUICKSHELL_CPU_SAMPLE_SECONDS = 1\.0'
assert_contains "$MATRIX" 'def sample_quickshell_idle_cpu'
assert_contains "$MATRIX" 'quickshell-idle-cpu'
assert_contains "$MATRIX" 'cpu_percent_one_core'
assert_contains "$MATRIX" 'rss_mb'
assert_contains "$MATRIX" 'threshold_percent_one_core'
assert_contains "$MATRIX" 'quickshell idle CPU too high'
```

- [ ] **Step 2: Run failing matrix contract**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
bash tests/integration/test_membrane_perf_governor_contract.sh
```

Expected before implementation:

```text
[FAIL] tools/runtime-ui-scan.py missing pattern: quickshell-idle-cpu
```

- [ ] **Step 3: Add CPU/RSS sampler**

In `gnu.in-os/tools/runtime-ui-scan.py`, add after `insert_runtime_probe`:

```python
QUICKSHELL_IDLE_CPU_THRESHOLD = 15.0
QUICKSHELL_IDLE_SETTLE_SECONDS = 20.0
QUICKSHELL_CPU_SAMPLE_SECONDS = 1.0


def _proc_total_jiffies() -> int:
    fields = Path("/proc/stat").read_text().splitlines()[0].split()[1:]
    return sum(int(v) for v in fields)


def _proc_process_jiffies(pid: int) -> int:
    stat = Path(f"/proc/{pid}/stat").read_text()
    rparen = stat.rfind(")")
    fields = stat[rparen + 2:].split()
    return int(fields[11]) + int(fields[12])


def _proc_rss_kb(pid: int) -> int:
    status = Path(f"/proc/{pid}/status")
    if not status.exists():
        return 0
    for line in status.read_text().splitlines():
        if line.startswith("VmRSS:"):
            parts = line.split()
            return int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return 0


def _quickshell_pids() -> list[int]:
    candidates: set[int] = set()
    for args in (["pgrep", "-x", "quickshell"], ["pgrep", "-f", "(^|/)quickshell( |$)|qs .*shell\\.qml"]):
        try:
            out = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False).stdout
        except FileNotFoundError:
            continue
        for raw in out.split():
            if raw.isdigit():
                pid = int(raw)
                if pid != os.getpid() and Path(f"/proc/{pid}").exists():
                    candidates.add(pid)
    return sorted(candidates)


def sample_quickshell_idle_cpu(settle_seconds: float = QUICKSHELL_IDLE_SETTLE_SECONDS, sample_seconds: float = QUICKSHELL_CPU_SAMPLE_SECONDS) -> tuple[str, str]:
    if settle_seconds > 0:
        time.sleep(settle_seconds)
    pids = _quickshell_pids()
    if not pids:
        return ("probe-failed", "quickshell process not found")
    try:
        start_proc = sum(_proc_process_jiffies(pid) for pid in pids if Path(f"/proc/{pid}").exists())
        start_total = _proc_total_jiffies()
        time.sleep(max(0.1, sample_seconds))
        live = [pid for pid in pids if Path(f"/proc/{pid}").exists()]
        end_proc = sum(_proc_process_jiffies(pid) for pid in live)
        end_total = _proc_total_jiffies()
        rss_mb = sum(_proc_rss_kb(pid) for pid in live) / 1024.0
    except (OSError, ValueError) as exc:
        return ("probe-failed", f"quickshell cpu sample failed: {exc}")
    proc_delta = max(0, end_proc - start_proc)
    total_delta = max(1, end_total - start_total)
    cpu_count = max(1, os.cpu_count() or 1)
    cpu_one_core = (proc_delta / total_delta) * cpu_count * 100.0
    value = {
        "cpu_percent_one_core": round(cpu_one_core, 2),
        "rss_mb": round(rss_mb, 1),
        "pids": live,
        "settle_seconds": settle_seconds,
        "sample_seconds": sample_seconds,
        "threshold_percent_one_core": QUICKSHELL_IDLE_CPU_THRESHOLD,
    }
    return ("captured", json.dumps(value, sort_keys=True))
```

- [ ] **Step 4: Insert the probe during live capture**

Inside `capture_live`, after `gnu.in-os-status`, insert:

```python
cpu_status, cpu_value = sample_quickshell_idle_cpu()
insert_runtime_probe(con, "quickshell-idle-cpu", cpu_value, cpu_status, captured_at)
```

- [ ] **Step 5: Enforce threshold in `verify_live`**

In `verify_live`, include `quickshell-idle-cpu` in required probes and enforce JSON threshold:

```python
for probe_name in ("qs-ipc-ping", "grim", "gnu.in-os-status", "quickshell-idle-cpu"):
    probe = con.execute("SELECT evidence_status, probe_value FROM runtime_probes WHERE probe_name = ? ORDER BY captured_at DESC LIMIT 1", (probe_name,)).fetchone()
    if not probe:
        errors.append(f"missing probe: {probe_name}")
    elif probe["evidence_status"] != "captured":
        errors.append(f"probe not captured: {probe_name}={probe['evidence_status']}")
    elif probe_name == "quickshell-idle-cpu":
        try:
            cpu_value = json.loads(probe["probe_value"])
            cpu_percent = float(cpu_value.get("cpu_percent_one_core", 999.0))
        except (TypeError, ValueError, json.JSONDecodeError):
            errors.append("quickshell-idle-cpu probe value is not valid JSON")
        else:
            if cpu_percent > QUICKSHELL_IDLE_CPU_THRESHOLD:
                errors.append(f"quickshell idle CPU too high: {cpu_percent:.2f}% > {QUICKSHELL_IDLE_CPU_THRESHOLD:.2f}% one core")
```

- [ ] **Step 6: Run matrix contract**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
bash tests/integration/test_membrane_perf_governor_contract.sh
```

Expected:

```text
[OK] membrane perf governor contract holds
```

- [ ] **Step 7: Commit**

```bash
cd /home/tension_atoi/Projects/Gnu.in
git add gnu.in-os/tools/runtime-ui-scan.py gnu.in-os/tests/integration/test_membrane_perf_governor_contract.sh
git commit -m "Add runtime UI idle CPU perf gate"
```

---

### Task 7: Shell Component Test Pass

**Files:**

- No new files.
- Uses all shell files changed above.

- [ ] **Step 1: Run targeted shell contracts**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-shell
bash tests/test_shell_settings_contract.sh
bash tests/test_gnosis_membrane_contract.sh
bash tests/test_sentinel_membrane_perf_contract.sh
```

Expected:

```text
[OK] shell-v2 settings/topbar/dock contract holds
[OK] gnosis membrane contract holds
[OK] sentinel membrane perf QML contract holds
```

- [ ] **Step 2: Run all shell component tests**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-shell
bash tools/run-component-tests.sh
```

Expected:

```text
[OK]
```

If the script prints individual `[OK] ... contract holds` lines and exits `0`, that is acceptable.

- [ ] **Step 3: Commit test-only contract fixes if any were needed**

```bash
cd /home/tension_atoi/Projects/Gnu.in
git add gnu.in-shell/tests/test_shell_settings_contract.sh gnu.in-shell/tests/test_gnosis_membrane_contract.sh gnu.in-shell/tests/test_sentinel_membrane_perf_contract.sh
git commit -m "Tighten shell membrane performance contracts"
```

Skip this commit if there were no changes since Task 5.

---

### Task 8: OS Verification and Build

**Files:**

- No source files should be edited in this task.
- Generated: release/build output under `gnu.in-os/release/`.

- [ ] **Step 1: Run OS source verification**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
./tools/verify.sh
```

Expected:

```text
[OK]
```

If `verify.sh` prints a longer success line and exits `0`, that is acceptable.

- [ ] **Step 2: Build release artifact**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
./tools/build.sh
```

Expected:

```text
[OK]
```

If the script prints a build ID and exits `0`, capture it:

```bash
build_id="$(find release/builds -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort | tail -1)"
printf 'build_id=%s\n' "$build_id"
```

- [ ] **Step 3: Check artifact contains expected runtime files**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
build_id="$(find release/builds -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort | tail -1)"
artifact="release/builds/$build_id"
find "$artifact" -type f | grep -E 'ShellSettingsService\.qml|ShellIpc\.qml|MembraneHost\.qml|SentinelMembranePerfService\.qml|runtime-ui-scan\.py|design_system|motion\.spec|tokens\.json' >/tmp/gnuin-build-artifact-files.txt
cat /tmp/gnuin-build-artifact-files.txt
```

Expected: output includes at least these names:

```text
ShellSettingsService.qml
ShellIpc.qml
MembraneHost.qml
SentinelMembranePerfService.qml
design_system
```

- [ ] **Step 4: Commit OS metadata changes if build scripts updated generated pointers**

If build scripts changed tracked release metadata, run:

```bash
cd /home/tension_atoi/Projects/Gnu.in
git add gnu.in-os/release gnu.in-os/tools gnu.in-os/tests
git commit -m "Build membrane governor release artifact"
```

Skip this commit if only ignored build output changed.

---

### Task 9: Promotion and Strict Runtime Status

**Files:**

- No source files should be edited in this task.
- May update tracked release promotion pointers depending on repo policy.

- [ ] **Step 1: Promote latest build**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
build_id="$(find release/builds -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort | tail -1)"
./tools/promote-latest.sh "$build_id"
```

Expected:

```text
[OK]
```

If the script prints `promoted <build-id>` and exits `0`, that is acceptable.

- [ ] **Step 2: Run strict status**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
./tools/status.sh --strict
```

Expected:

```text
status: OK
```

- [ ] **Step 3: Commit promotion pointers if tracked**

Run only if `promote-latest.sh` changed tracked files:

```bash
cd /home/tension_atoi/Projects/Gnu.in
git add gnu.in-os/release gnu.in-os/runtime gnu.in-os/LATEST gnu.in-os/LATEST-*
git commit -m "Promote membrane governor build"
```

If some paths do not exist, remove only the nonexistent path from the `git add` command and keep the commit message unchanged.

---

### Task 10: Live Runtime Matrix and Perf Gate

**Files:**

- Generated: `gnu.in-os/audit/runtime-ui-matrix.sqlite`
- Generated: `gnu.in-os/audit/runtime-ui-matrix.md`
- Generated: `gnu.in-os/audit/runtime-ui-matrix.html`
- Generated: screenshots under `gnu.in-os/audit/visual/`

- [ ] **Step 1: Refresh live runtime matrix**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
./tools/runtime-ui-matrix.sh refresh-live
```

Expected:

```text
context-menu-brand
context-menu-list
context-menu-tray-audio
context-menu-workspace-card
context-menu-widget-card
quickshell-idle-cpu
```

The script may print more lines; it must exit `0`.

- [ ] **Step 2: Verify live runtime matrix**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
./tools/runtime-ui-matrix.sh verify-live
```

Expected:

```text
[OK] runtime UI matrix live visual contract holds
```

If this fails with `quickshell idle CPU too high`, do not waive it. Return to Task 5 and make idle `BlobGroup` gating stricter.

- [ ] **Step 3: Inspect CPU/RSS probe row**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
sqlite3 audit/runtime-ui-matrix.sqlite \
  "SELECT captured_at, evidence_status, probe_value FROM runtime_probes WHERE probe_name='quickshell-idle-cpu' ORDER BY captured_at DESC LIMIT 3;"
```

Expected: JSON containing these keys:

```json
{"cpu_percent_one_core":0,"rss_mb":0,"threshold_percent_one_core":15.0}
```

Actual values may differ; `cpu_percent_one_core` must be `<= 15.0` for the latest row.

---

### Task 11: Post-Build Analysis Report

**Files:**

- Create: `gnu.in-os/audit/membrane-perf-post-build.md`

- [ ] **Step 1: Generate post-build analysis inputs**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
build_id="$(find release/builds -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort | tail -1)"
status_output="$(./tools/status.sh --strict)"
cpu_probe="$(sqlite3 audit/runtime-ui-matrix.sqlite "SELECT probe_value FROM runtime_probes WHERE probe_name='quickshell-idle-cpu' ORDER BY captured_at DESC LIMIT 1;")"
scenario_rows="$(sqlite3 audit/runtime-ui-matrix.sqlite "SELECT surface_id || ':' || state_name || '=' || evidence_status FROM visual_states WHERE surface_id='context-menus' ORDER BY captured_at DESC LIMIT 8;")"
artifact_files="$(find "release/builds/$build_id" -type f | grep -E 'ShellSettingsService\.qml|ShellIpc\.qml|MembraneHost\.qml|SentinelMembranePerfService\.qml|design_system|tokens\.json|motion\.spec' | sed "s#release/builds/$build_id/##" | sort | head -80)"
printf '%s\n' "$status_output" > /tmp/gnuin-status-strict.txt
printf '%s\n' "$cpu_probe" > /tmp/gnuin-cpu-probe.json
printf '%s\n' "$scenario_rows" > /tmp/gnuin-scenarios.txt
printf '%s\n' "$artifact_files" > /tmp/gnuin-artifact-files.txt
```

Expected:

```text
/tmp/gnuin-status-strict.txt exists
/tmp/gnuin-cpu-probe.json exists
/tmp/gnuin-scenarios.txt exists
/tmp/gnuin-artifact-files.txt exists
```

- [ ] **Step 2: Write the analysis report**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
build_id="$(find release/builds -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort | tail -1)"
cat > audit/membrane-perf-post-build.md <<REPORT
# Membrane Performance Governor Post-Build Analysis

- Build ID: \`$build_id\`
- Date: \`$(date --iso-8601=seconds)\`

## Strict Status

\`\`\`text
$(cat /tmp/gnuin-status-strict.txt)
\`\`\`

## Latest Quickshell Idle CPU Probe

\`\`\`json
$(cat /tmp/gnuin-cpu-probe.json)
\`\`\`

## Latest Context Menu Visual Rows

\`\`\`text
$(cat /tmp/gnuin-scenarios.txt)
\`\`\`

## Release Artifact Evidence

\`\`\`text
$(cat /tmp/gnuin-artifact-files.txt)
\`\`\`

## Decision

The build is acceptable only if strict status is OK, live matrix verification passed, and the latest \`quickshell-idle-cpu\` JSON reports \`cpu_percent_one_core <= 15.0\`.
REPORT
cat audit/membrane-perf-post-build.md
```

Expected: report includes `Build ID`, `Strict Status`, `Latest Quickshell Idle CPU Probe`, `Latest Context Menu Visual Rows`, and `Release Artifact Evidence`.

- [ ] **Step 3: Commit report if audit reports are tracked**

Run only if `audit/*.md` is tracked in this repo:

```bash
cd /home/tension_atoi/Projects/Gnu.in
git add gnu.in-os/audit/membrane-perf-post-build.md
git commit -m "Document membrane governor post-build analysis"
```

Skip this commit if `audit/` generated reports are ignored by policy.

---

### Task 12: Final Full-Chain Verification Summary

**Files:**

- No source files should be edited.

- [ ] **Step 1: Run final command chain**

Run:

```bash
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-shell
bash tools/run-component-tests.sh

cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
bash tests/integration/test_motion_spec_inventory_contract.sh
bash tests/integration/test_membrane_perf_governor_contract.sh
./tools/verify.sh
./tools/status.sh --strict
./tools/runtime-ui-matrix.sh verify-live
```

Expected:

```text
[OK] shell component tests pass
[OK] motion spec inventory contract holds
[OK] membrane perf governor contract holds
status: OK
[OK] runtime UI matrix live visual contract holds
```

Exact shell test wording may vary; every command must exit `0`.

- [ ] **Step 2: Produce final operator summary**

Use this format in the final response:

```markdown
Implemented and proved the Rust-assisted membrane governor.

Evidence:
- Shell component tests: PASS
- Motion spec inventory contract: PASS
- Membrane perf governor contract: PASS
- OS verify: PASS
- Build ID: <build-id>
- Promotion: PASS
- Strict status: OK
- Runtime matrix live: PASS
- Latest Quickshell idle CPU: <cpu>% of one core, RSS <rss> MiB
- Post-build analysis: gnu.in-os/audit/membrane-perf-post-build.md

Notes:
- QML still owns rendering and frame state.
- Sentinel only emits low-frequency performance recommendation.
- blob.in Rust renderer migration remains a separate lane.
```

- [ ] **Step 3: Push only if requested**

If the user explicitly requests GitHub push, run:

```bash
cd /home/tension_atoi/Projects/Gnu.in
git status --short
git push
```

Expected:

```text
Everything up-to-date
```

or a normal push summary. If `git status --short` shows unrelated user changes, stop and ask how to proceed before pushing.

---

## Self-Review

Spec coverage:

- `membranePerfTier=auto|static|sdf`: Tasks 3, 4, 5.
- Rust governor in Sentinel: Task 2.
- QML remains renderer, no per-frame D-Bus: Tasks 4 and 5 contracts.
- Static topbar idle fallback: Task 5.
- SDF only for morphing surfaces: Task 5.
- Idle CPU live gate below 15% after 20s settle: Tasks 6 and 10.
- SQLite history for CPU/RSS: Task 6.
- Inventory of new motion spec and Rust files: Task 1.
- Shell tests: Task 7.
- OS verify/build/promote/status: Tasks 8 and 9.
- Post-build analysis: Task 11.
- Do not merge blob.in renderer migration into governor work: stated in architecture and file boundaries.

Placeholder scan:

- No `TBD` placeholders.
- No “write tests for above” without code.
- No undefined function names in snippets: every introduced function is shown in the task that introduces it.

Type consistency:

- QML setting name is consistently `membranePerfTier`.
- Sentinel JSON field is consistently `membrane_perf_tier` internally and exposed as `tier` for shell consumption.
- Runtime matrix probe is consistently `quickshell-idle-cpu`.
- CPU field is consistently `cpu_percent_one_core` / `cpuPercentOneCore` depending on JSON vs QML property naming.
