#!/usr/bin/env python3
"""Durable asset index for the ZIP9 design/PoC drop.

Why this exists
---------------
ZIP9 ("Merging design assets and specs (9).zip") is a 718-file, ~48 MB drop.
Re-reading it every session to answer "what is in here / what maps to what /
what still needs porting" is exactly the limited-memory fight we want to end.

This tool extracts the archive **once** into a persistent, gitignored working
tree and emits small JSON indexes that later sessions (and other tooling) can
query instead of re-scanning the archive.

Authority model (verified 2026-06-30/07-01)
-------------------------------------------
- ZIP9 is the *port-from* seed: design PoCs (.jsx), a legacy Qt/QML render PoC,
  motion/behavior specs, screenshots.
- `gnu.in-os/engine/blob.in` (in the live tree) is the *authority*: it is ahead
  of ZIP9's blob.in, carries the Rust/GPUI-native lane (gen/gnu_theme.gpui.rs)
  and hardware-golden parity work, and has already shed the QML surface.
- Therefore the index tags ZIP9 assets by role and, for blob.in, reconciles
  ZIP9 against the authority tree rather than treating ZIP9 as source of truth.

Outputs (tooling/asset-index/index/)
- zip9_files.json        one record per extracted file
- summary.json           rollups by category / role / extension
- blob_in_reconcile.json ZIP9 blob.in copies vs authority engine/blob.in
- INDEX.md               human-readable summary

Usage
  python3 build_index.py --extract     # (re)extract the archive, then index
  python3 build_index.py               # index the already-extracted tree
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
ASSET_INDEX_DIR = SCRIPTS_DIR.parent
REPO_ROOT = ASSET_INDEX_DIR.parent.parent
EXTRACT_DIR = ASSET_INDEX_DIR / "extract" / "zip9"
INDEX_DIR = ASSET_INDEX_DIR / "index"
AUTHORITY_BLOBIN = REPO_ROOT / "gnu.in-os" / "engine" / "blob.in"
DEFAULT_ZIP = Path("/mnt/hdd/Téléchargements/Merging design assets and specs (9).zip")

# Skip build artefacts when hashing/reconciling source trees.
SKIP_MARKERS = ("target/", "build/", ".fingerprint", ".git/", "__pycache__/")

TEXT_EXTS = {
    ".rs", ".jsx", ".js", ".ts", ".tsx", ".qml", ".cpp", ".h", ".hpp", ".c",
    ".css", ".html", ".md", ".json", ".toml", ".sh", ".frag", ".vert", ".dart",
    ".txt", ".yaml", ".yml", ".svg",
}

# Extension -> role in the port pipeline.
ROLE_BY_EXT: Dict[str, str] = {
    ".jsx": "design-poc",
    ".tsx": "design-poc",
    ".rs": "rust-engine",
    ".qml": "legacy-render-poc",
    ".cpp": "legacy-render-poc",
    ".h": "legacy-render-poc",
    ".hpp": "legacy-render-poc",
    ".frag": "legacy-render-poc",
    ".vert": "legacy-render-poc",
    ".dart": "legacy-gen",
    ".png": "render-evidence",
    ".svg": "asset-vector",
    ".woff": "asset-font",
    ".json": "spec-data",
    ".toml": "build-config",
    ".md": "doc",
    ".html": "prototype-html",
    ".css": "style",
    ".js": "script",
    ".sh": "tooling",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def keep_source(rel: str) -> bool:
    return not any(marker in rel for marker in SKIP_MARKERS)


def extract_archive(zip_path: Path, dest: Path) -> int:
    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            zf.extract(info, dest)
            count += 1
    return count


def top_category(rel: str) -> str:
    """Coarse bucket by leading path segment(s)."""
    parts = rel.split("/")
    head = parts[0]
    if head == "uploads" and len(parts) > 1:
        sub = parts[1]
        if "blob.in" in rel:
            return "blob-in"
        mapping = {
            "Context.Spec": "context-spec",
            "GNU.IN Design System": "design-system",
            "Gnosis App": "gnosis-app",
            "Gnosis App (1)": "gnosis-app",
        }
        return mapping.get(sub, f"uploads/{sub}")
    if head == "screenshots":
        return "screenshots"
    if head == "port-data":
        return "port-data"
    if head.startswith("gnu-in-shell-docs"):
        return "docs-drop"
    if head == "audit-handoff":
        return "audit"
    if head.endswith(".dc.html") or head.endswith(".md") or head.endswith(".json"):
        return "root-doc"
    return head or "(root)"


def component_hint(rel: str) -> str:
    stem = Path(rel).stem
    for suffix in (".rttc", ".spec", ".archetypes", ".dc"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    return stem


@dataclass
class FileRecord:
    path: str
    ext: str
    size: int
    sha256: str
    category: str
    role: str
    component_hint: str
    loc: Optional[int]


def count_loc(path: Path, ext: str) -> Optional[int]:
    if ext not in TEXT_EXTS:
        return None
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return None


def build_file_index(extract_dir: Path) -> List[FileRecord]:
    records: List[FileRecord] = []
    for root, _, files in os.walk(extract_dir):
        for name in files:
            abs_path = Path(root) / name
            rel = abs_path.relative_to(extract_dir).as_posix()
            ext = abs_path.suffix.lower() or "(noext)"
            try:
                size = abs_path.stat().st_size
            except OSError:
                continue
            records.append(
                FileRecord(
                    path=rel,
                    ext=ext,
                    size=size,
                    sha256=sha256_file(abs_path),
                    category=top_category(rel),
                    role=ROLE_BY_EXT.get(ext, "other"),
                    component_hint=component_hint(rel),
                    loc=count_loc(abs_path, ext),
                )
            )
    records.sort(key=lambda r: r.path)
    return records


def build_summary(records: List[FileRecord]) -> Dict[str, object]:
    by_cat: Counter = Counter()
    by_role: Counter = Counter()
    by_ext: Counter = Counter()
    bytes_by_cat: Counter = Counter()
    loc_by_role: Counter = Counter()
    for r in records:
        by_cat[r.category] += 1
        by_role[r.role] += 1
        by_ext[r.ext] += 1
        bytes_by_cat[r.category] += r.size
        if r.loc:
            loc_by_role[r.role] += r.loc
    return {
        "total_files": len(records),
        "total_bytes": sum(r.size for r in records),
        "by_category": dict(by_cat.most_common()),
        "bytes_by_category": dict(bytes_by_cat.most_common()),
        "by_role": dict(by_role.most_common()),
        "loc_by_role": dict(loc_by_role.most_common()),
        "by_extension": dict(by_ext.most_common()),
    }


def _hash_tree(root: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not root.exists():
        return out
    for dpath, _, files in os.walk(root):
        for name in files:
            abs_path = Path(dpath) / name
            rel = abs_path.relative_to(root).as_posix()
            if keep_source(rel):
                try:
                    out[rel] = sha256_file(abs_path)
                except OSError:
                    pass
    return out


def _hash_zip_subtree(extract_dir: Path, sub: str) -> Dict[str, str]:
    root = extract_dir / sub
    return _hash_tree(root)


def reconcile_blob_in(extract_dir: Path, authority: Path) -> Dict[str, object]:
    copies = {
        "context_spec": "uploads/Context.Spec/blob.in",
        "design_system": "uploads/GNU.IN Design System/blob.in",
    }
    auth = _hash_tree(authority)

    def diff(zmap: Dict[str, str]) -> Dict[str, object]:
        zk, ak = set(zmap), set(auth)
        common = zk & ak
        differ = sorted(r for r in common if zmap[r] != auth[r])
        return {
            "zip_source_files": len(zmap),
            "authority_source_files": len(ak),
            "identical": sorted(r for r in common if zmap[r] == auth[r]),
            "differ": differ,
            "only_in_zip": sorted(zk - ak),
            "only_in_authority": sorted(ak - zk),
        }

    results = {}
    for label, sub in copies.items():
        zmap = _hash_zip_subtree(extract_dir, sub)
        results[label] = diff(zmap)

    ref = results["context_spec"]
    verdict = (
        "authority_ahead"
        if len(ref["only_in_authority"]) > len(ref["only_in_zip"])
        else "zip_ahead_or_equal"
    )
    return {
        "authority_path": str(authority.relative_to(REPO_ROOT)),
        "verdict": verdict,
        "note": (
            "ZIP9 is the port-from seed; authority engine/blob.in is ahead. "
            "only_in_zip is expected to be legacy QML/Qt/Dart PoC; "
            "only_in_authority is the forward Rust/GPUI + parity work."
        ),
        "copies": results,
    }


def write_index_md(summary: Dict[str, object], reconcile: Dict[str, object]) -> str:
    lines = [
        "# ZIP9 Asset Index",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "Durable index of the ZIP9 design/PoC drop. Query `index/*.json` instead "
        "of re-reading the 718-file archive. Authority = `gnu.in-os/engine/blob.in` "
        "(ahead of ZIP9); ZIP9 = port-from seed.",
        "",
        f"- Total files: {summary['total_files']}",
        f"- Total size: {int(summary['total_bytes']) / 1_000_000:.1f} MB",
        "",
        "## By category",
        "",
        "| category | files |",
        "|---|---:|",
    ]
    for cat, count in summary["by_category"].items():
        lines.append(f"| {cat} | {count} |")
    lines += ["", "## By role (port pipeline)", "", "| role | files | LoC |", "|---|---:|---:|"]
    loc_by_role = summary["loc_by_role"]
    for role, count in summary["by_role"].items():
        lines.append(f"| {role} | {count} | {loc_by_role.get(role, '')} |")
    ctx = reconcile["copies"]["context_spec"]
    lines += [
        "",
        "## blob.in reconcile (ZIP9 vs authority)",
        "",
        f"- Verdict: **{reconcile['verdict']}**",
        f"- Identical: {len(ctx['identical'])} | Differ: {len(ctx['differ'])} | "
        f"Only in ZIP9: {len(ctx['only_in_zip'])} | Only in authority: {len(ctx['only_in_authority'])}",
        f"- Only-in-ZIP9 (legacy PoC): {', '.join(ctx['only_in_zip']) or '-'}",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the durable ZIP9 asset index.")
    parser.add_argument("--zip", default=str(DEFAULT_ZIP), help="ZIP9 archive path")
    parser.add_argument("--extract", action="store_true", help="(re)extract before indexing")
    args = parser.parse_args()

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    if args.extract:
        zip_path = Path(args.zip)
        if not zip_path.exists():
            raise SystemExit(f"archive not found: {zip_path}")
        n = extract_archive(zip_path, EXTRACT_DIR)
        print(f"extracted {n} files -> {EXTRACT_DIR}")

    if not EXTRACT_DIR.exists():
        raise SystemExit(f"no extracted tree at {EXTRACT_DIR}; run with --extract first")

    records = build_file_index(EXTRACT_DIR)
    summary = build_summary(records)
    reconcile = reconcile_blob_in(EXTRACT_DIR, AUTHORITY_BLOBIN)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (INDEX_DIR / "zip9_files.json").write_text(
        json.dumps(
            {"generated_at": generated_at, "count": len(records), "files": [asdict(r) for r in records]},
            indent=2,
        ),
        encoding="utf-8",
    )
    (INDEX_DIR / "summary.json").write_text(
        json.dumps({"generated_at": generated_at, **summary}, indent=2),
        encoding="utf-8",
    )
    (INDEX_DIR / "blob_in_reconcile.json").write_text(
        json.dumps({"generated_at": generated_at, **reconcile}, indent=2),
        encoding="utf-8",
    )
    (INDEX_DIR / "INDEX.md").write_text(write_index_md(summary, reconcile), encoding="utf-8")

    print(f"indexed {len(records)} files")
    print(f"wrote: {INDEX_DIR / 'zip9_files.json'}")
    print(f"wrote: {INDEX_DIR / 'summary.json'}")
    print(f"wrote: {INDEX_DIR / 'blob_in_reconcile.json'}")
    print(f"wrote: {INDEX_DIR / 'INDEX.md'}")
    print(f"blob.in verdict: {reconcile['verdict']}")


if __name__ == "__main__":
    main()
