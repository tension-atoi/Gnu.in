#!/usr/bin/env python3
"""Build an iteration-aware catalog snapshot from RTTC metadata + ZIP9 source.

This keeps runtime consumption clean:
- .rttc.md files are scanned as source inputs
- ZIP9 specs provide composition/count provenance and release window
- generated artifacts are versioned report files (JSON/CSV/Markdown)

The outputs are descriptive only (no runtime writes, no renderer DB reads).
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import yaml
except Exception:  # pragma: no cover - very defensive fallback
    yaml = None


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent.parent
DEFAULT_COMPONENTS_DIR = REPO_ROOT / "gnu.in-shell" / "components"
DEFAULT_DOCS_DIR = REPO_ROOT / "gnu.in-shell" / "docs"
ACTIVE_STATUSES = {"active", "validated", "candidate", "canonical"}


@dataclass
class CatalogItem:
    path: Path
    relative: str
    name: str
    status: str
    created_dt: Optional[datetime]
    updated_dt: Optional[datetime]
    created: str
    updated: str
    mtime: str
    subtype: str
    taxonomy: str
    kind: str
    tags: List[str]
    doc_id: str
    canonical: bool
    active: bool
    recent: bool
    edit_scope: str
    last_activity: Optional[str]
    last_activity_dt: Optional[datetime]
    last_activity_source: str
    source_ref: str
    chunk_version: int
    owner: str
    refs: List[str]
    provenance: Dict[str, Any]


@dataclass
class ZipMotionAtom:
    id: str
    title: str


@dataclass
class ZipMotionMolecule:
    id: str
    title: str
    moment: str
    atoms: List[str]


def _coerce_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)

    s = str(value).strip()
    if not s:
        return None

    s = s.replace("Z", "+00:00")
    fmts = (
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S%z",
    )
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _format_date(value: Optional[datetime]) -> str:
    if not value:
        return "-"
    return value.strftime("%Y-%m-%d")


def resolve_last_activity(
    created_dt: Optional[datetime],
    updated_dt: Optional[datetime],
    mtime_dt: Optional[datetime],
    *,
    allow_mtime_fallback: bool = False,
) -> Tuple[Optional[datetime], str]:
    """Prefer authored metadata over filesystem timestamps.

    Iterative design decisions should be based on explicit metadata (created/updated)
    to avoid noise from workspace extraction operations.
    """

    for value, source in ((updated_dt, "updated"), (created_dt, "created")):
        if value is not None:
            return value, source
    if allow_mtime_fallback and mtime_dt is not None:
        return mtime_dt, "mtime"
    return None, "missing"


def parse_frontmatter(lines: List[str]) -> Dict[str, Any]:
    if not lines or not lines[0].strip() == "---":
        return {}

    fm: List[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        fm.append(line)
    if not fm:
        return {}

    fm_text = "\n".join(fm)
    if yaml is not None:
        try:
            data = yaml.safe_load(fm_text)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    meta: Dict[str, Any] = {}
    current_key = None
    for line in fm:
        raw = line.rstrip("\n")
        if not raw.strip():
            continue
        if re.match(r"^\s{2,}\S", raw):
            if current_key is not None and isinstance(meta.get(current_key), list):
                meta[current_key].append(raw.strip())
            continue
        if ":" in raw:
            key, value = raw.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                items = []
                for part in value[1:-1].split(","):
                    part = part.strip().strip('"\'')
                    if part:
                        items.append(part)
                meta[key] = items
            else:
                meta[key] = value.strip().strip('"\'')
                current_key = key
            if value == "":
                meta[key] = []
                current_key = key
    return meta


def _clean_tags(raw_tags: Any) -> List[str]:
    if isinstance(raw_tags, list):
        return [str(t).strip() for t in raw_tags if str(t).strip()]
    if not raw_tags:
        return []
    return [part.strip() for part in str(raw_tags).strip().split(",") if part.strip()]


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"true", "1", "yes", "on"}


def _coerce_int(value: Any, default: int = 1) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _clean_refs(raw_refs: Any) -> List[str]:
    """Normalize frontmatter refs, stripping wiki-link brackets and quotes."""
    if isinstance(raw_refs, list):
        values = raw_refs
    elif raw_refs:
        values = [raw_refs]
    else:
        return []
    out: List[str] = []
    for ref in values:
        s = str(ref).strip().strip("\"'")
        if s.startswith("[[") and s.endswith("]]"):
            s = s[2:-2]
        s = s.strip()
        if s:
            out.append(s)
    return out


def _clean_provenance(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return {str(k): v for k, v in raw.items()}
    return {}


def classify_file(path: Path) -> str:
    rel = path.as_posix()
    if rel.startswith("components/motion/atoms/"):
        return "components.motion.atoms"
    if rel.startswith("components/motion/molecules/"):
        return "components.motion.molecules"
    if rel.startswith("components/motion/"):
        return "components.motion"
    if rel.startswith("components/uikit/"):
        return "components.uikit"
    if rel.startswith("components/services/"):
        return "components.services"
    if rel.startswith("components/"):
        return "components.root"
    return "components.legacy"


def classify_kind(item: Dict[str, str], taxonomy: str, stem: str) -> str:
    status = item.get("status", "draft")
    if taxonomy.endswith("motion.atoms"):
        return "atom"
    if taxonomy.endswith("motion.molecules"):
        return "molecule"
    if taxonomy.endswith("motion"):
        return "motion"
    if taxonomy.endswith("uikit"):
        # Most uikit entries are component-style primitives and are usually used as atoms.
        if stem in {"notifpill", "icon", "mascotmini", "systemchip", "gnuicon"}:
            return "atom"
        if status == "superseded":
            return "prototype"
        return "component"
    if taxonomy.endswith("services"):
        return "service"
    if status == "validated":
        return "surface"
    if status == "superseded":
        return "deprecated"
    return "component"


def infer_edit_scope(item: Dict[str, Any], status: str, tags: Sequence[str]) -> str:
    tags_lower = [t.lower() for t in tags]
    if "bugfix" in tags_lower or any("bug" in t for t in tags_lower):
        return "bugfix"
    if any("redesign" in t for t in tags_lower):
        return "redesign"
    if any(t in {"archive", "archived"} for t in tags_lower):
        return "archive"
    if status in {"active", "validated", "canonical", "candidate", "superseded"}:
        return "production"
    return "draft"


def canonical_source(meta: Dict[str, Any]) -> str:
    provenance = meta.get("provenance")
    if isinstance(provenance, dict):
        qml_target = provenance.get("qml_target_path")
        if qml_target:
            return str(qml_target)
    refs = meta.get("refs")
    if isinstance(refs, list) and refs:
        return str(refs[0]).strip()
    if isinstance(refs, str):
        return refs.strip()
    return ""


def scan_rttc_files(components_dir: Path) -> List[CatalogItem]:
    rows: List[CatalogItem] = []

    for path in sorted(components_dir.rglob("*.rttc.md")):
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        meta = parse_frontmatter(lines)

        status = (str(meta.get("status", "draft") or "draft")).strip().lower()
        created = str(meta.get("created") or "").strip()
        updated = str(meta.get("updated") or "").strip()

        created_dt = _coerce_datetime(created)
        updated_dt = _coerce_datetime(updated)
        stat = path.stat()
        mtime_dt = datetime.fromtimestamp(stat.st_mtime)
        mtime = _format_date(mtime_dt)

        last_dt, last_source = resolve_last_activity(
            created_dt=created_dt,
            updated_dt=updated_dt,
            mtime_dt=mtime_dt,
            allow_mtime_fallback=False,
        )

        rel = path.relative_to(components_dir.parent.parent)
        taxonomy = classify_file(path.relative_to(components_dir.parent))
        stem = path.stem.lower()

        tags = _clean_tags(meta.get("tags", []))
        source_ref = canonical_source(meta)
        chunk_version = _coerce_int(meta.get("chunk_version", 1), default=1)
        owner = str(meta.get("owner", "") or "").strip()
        refs = _clean_refs(meta.get("refs", []))
        provenance = _clean_provenance(meta.get("provenance"))

        item = CatalogItem(
            path=path,
            relative=str(rel),
            name=path.name,
            status=status,
            created_dt=created_dt,
            updated_dt=updated_dt,
            created=created_dt.strftime("%Y-%m-%d") if created_dt else "-",
            updated=updated_dt.strftime("%Y-%m-%d") if updated_dt else "-",
            mtime=mtime,
            subtype=str(meta.get("type", "research-note") or "research-note"),
            taxonomy=taxonomy,
            kind="",
            tags=tags,
            doc_id=str(meta.get("doc_id", "") or ""),
            canonical=_coerce_bool(meta.get("canonical", "false")),
            active=status in ACTIVE_STATUSES and status != "superseded",
            recent=False,
            edit_scope="draft",
            last_activity=_format_date(last_dt),
            last_activity_dt=last_dt,
            last_activity_source=last_source,
            source_ref=source_ref,
            chunk_version=chunk_version,
            owner=owner,
            refs=refs,
            provenance=provenance,
        )
        item.kind = classify_kind(meta, taxonomy, stem)
        item.edit_scope = infer_edit_scope(meta, status, tags)
        rows.append(item)

    return rows


def read_zip9_manifest(zip_path: Path) -> Dict[str, Any]:
    if not zip_path.exists():
        return {
            "found": False,
            "path": str(zip_path),
            "motion": {"atoms": 0, "molecules": 0},
            "molecules": {"molecules": 0},
        }

    def read_json(name: str) -> Optional[dict]:
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                raw = zf.read(name)
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return None

    def read_text(name: str) -> Optional[str]:
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                return zf.read(name).decode("utf-8", errors="ignore")
        except Exception:
            return None

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())

    manifest = read_json("ZIP_DROP_MANIFEST.json") or {}
    motion_json = read_json("port-data/motion.spec.json")
    molecule_json = read_json("port-data/molecule_specs.json")

    return {
        "found": True,
        "path": str(zip_path),
        "date": manifest.get("date", ""),
        "drop": manifest.get("drop", ""),
        "base_ref": manifest.get("baseline_ref", ""),
        "intent": manifest.get("intent", ""),
        "files": [f for f in manifest.get("files", []) if isinstance(f, str)],
        "motion": _read_motion_counts(motion_json),
        "molecules": _read_molecule_counts(molecule_json),
        "motion_spec_raw": motion_json or {},
        "molecule_specs_raw": molecule_json or {},
        "alignment_audit_excerpt": _read_motion_audit_excerpt(read_text("docs/zip-drop-audit-2026-06-25-merging-design-assets-2.md")),
        "zip_contents_count": len(names),
    }


def _read_motion_audit_excerpt(audit_text: Optional[str]) -> str:
    if not audit_text:
        return ""
    m = re.search(r"ZIP Drop Audit -.*?\n\n## Executive Decision", audit_text, re.S)
    if m:
        return "Exec decision present in ZIP_DROP_AUDIT"
    return ""


def _read_motion_counts(motion_json: Optional[dict]) -> Dict[str, Any]:
    result: Dict[str, Any] = {"atoms": 0, "molecules": 0, "imported_from": None}
    if not motion_json:
        return result
    result["atoms"] = len(motion_json.get("atoms", []))
    result["molecules"] = len(motion_json.get("molecules", []))
    if "version" in motion_json:
        result["version"] = motion_json["version"]
    if "imported_from" in motion_json:
        result["imported_from"] = motion_json["imported_from"]
    return result


def _read_molecule_counts(molecule_json: Optional[dict]) -> Dict[str, Any]:
    result: Dict[str, Any] = {"molecules": 0}
    if not molecule_json:
        return result
    result["molecules"] = len(molecule_json.get("molecules", []))
    return result


def parse_alignment_counts(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        return {}

    text = file_path.read_text(encoding="utf-8", errors="ignore")

    def count_rows(prefix: str) -> int:
        pattern = rf"^\|\s*{re.escape(prefix)}\.\d+[0-9A-Za-z_-]*\s*\|"
        return sum(1 for line in text.splitlines() if re.match(pattern, line))

    return {
        "atoms": count_rows("C"),
        "molecules": count_rows("CM"),
        "recipes": count_rows("R"),
    }


def build_motion_graph(motion_summary: Dict[str, Any]) -> Dict[str, Any]:
    atoms_raw = motion_summary.get("motion_spec_raw", {}) or {}
    molecules_raw = motion_summary.get("molecule_specs_raw", {}) or {}

    atoms: List[ZipMotionAtom] = []
    atom_index: Dict[str, ZipMotionAtom] = {}
    for row in atoms_raw.get("atoms", []) if isinstance(atoms_raw, dict) else []:
        row_id = str(row.get("id", "")).strip()
        row_title = str(row.get("title", "")).strip()
        if not row_id:
            continue
        atom = ZipMotionAtom(id=row_id, title=row_title)
        atoms.append(atom)
        atom_index[row_id] = atom

    def normalize_atom_ref(raw_ref: str) -> str:
        s = str(raw_ref).strip()
        m = re.search(r"A\.\d{2}", s)
        return m.group(0) if m else s

    def to_list(raw: Any) -> List[str]:
        if isinstance(raw, list):
            return [str(v).strip() for v in raw if str(v).strip()]
        if raw is None:
            return []
        if isinstance(raw, str):
            s = raw.strip()
            if not s:
                return []
            return [part.strip() for part in s.split(",") if part.strip()]
        return []

    molecule_specs = molecules_raw.get("molecules", []) if isinstance(molecules_raw, dict) else []
    molecule_graph = []
    unresolved: List[Tuple[str, str]] = []

    for row in molecule_specs:
        mol_id = str(row.get("id", "")).strip()
        mol_title = str(row.get("title", "")).strip() or str(row.get("name", "")).strip()
        if not mol_title:
            model = row.get("model")
            if isinstance(model, dict):
                header = model.get("header")
                if isinstance(header, dict):
                    mol_title = str(header.get("title", "")).strip()
        if not mol_title:
            mol_title = mol_id
        raw_atoms = row.get("atoms")
        if raw_atoms is None:
            raw_atoms = row.get("motion")
        atom_refs_raw = to_list(raw_atoms)
        atom_refs: List[str] = []
        atom_refs_display: List[str] = []
        for atom_ref in atom_refs_raw:
            atom_id = normalize_atom_ref(str(atom_ref))
            atom_label = atom_index.get(atom_id).title if atom_id in atom_index else ""
            atom_refs.append(atom_id)
            if atom_label:
                atom_refs_display.append(f"{atom_id} ({atom_label})")
            else:
                atom_refs_display.append(atom_id)
            if atom_id and atom_id not in atom_index:
                unresolved.append((mol_id, atom_id))
        molecule_graph.append(
            {
                "id": mol_id,
                "title": mol_title,
                "atoms": atom_refs,
                "atoms_display": ", ".join(atom_refs_display) if atom_refs_display else "(none)",
                "moment": str(row.get("moment", "")).strip(),
            }
        )

    families = Counter()
    if isinstance(molecules_raw, dict):
        for row in molecules_raw.get("molecules", []):
            fam = str(row.get("family", "unknown")).strip() or "unknown"
            families[fam] += 1

    styles = Counter()
    if isinstance(molecules_raw, dict):
        for row in molecules_raw.get("molecules", []):
            style = str(row.get("style", "unknown")).strip() or "unknown"
            styles[style] += 1

    return {
        "atoms_count": len(atoms),
        "molecules_count": len(molecule_graph),
        "molecules": molecule_graph,
        "moment_count": Counter(m.get("moment", "") for m in molecule_graph).most_common(),
        "unresolved_atom_refs": [
            {"molecule_id": mol, "atom_ref": atom}
            for mol, atom in unresolved
        ],
        "families": dict(families),
        "styles": dict(styles),
        "agentic_family_size": len([
            m
            for m in molecule_specs
            if isinstance(m, dict) and str(m.get("family", "")).strip().lower() == "agentic"
        ]),
    }


# --- DB-like evolution projection -------------------------------------------
# Projects the RTTC scan into the registry DB vocabulary defined in
# schema/registry_schema.sql (lifecycle statuses, source_authority enum,
# stable_id/version/parent). This is a descriptive projection: every field is
# read directly from frontmatter or derived by an explicit rule below. Nothing
# here writes to a live DB or fabricates lineage.

# RTTC frontmatter status -> registry lifecycle status
# (schema: draft, lab, candidate, canonical, deprecated, retired).
STATUS_TO_PROMOTION_STATE: Dict[str, str] = {
    "draft": "draft",
    "lab": "lab",
    "active": "candidate",
    "candidate": "candidate",
    "validated": "canonical",
    "canonical": "canonical",
    "superseded": "deprecated",
    "deprecated": "deprecated",
    "retired": "retired",
}

# source_authority enum from schema/registry_schema.sql.
SOURCE_AUTHORITY_ENUM = {"ZIP9/Central", "spec-doc", "screenshot", "runtime", "mixed"}

# RTTC kind -> registry object_type enum (quark, atom, molecule, recipe,
# engine, proof, fork). Only clean mappings are asserted; anything else is left
# unmapped (None) rather than forced into the enum.
KIND_TO_DB_OBJECT_TYPE: Dict[str, str] = {
    "atom": "atom",
    "molecule": "molecule",
    "motion": "molecule",
    "service": "engine",
}


def promotion_state_from_status(status: str) -> Tuple[str, bool]:
    """Map an RTTC status onto the registry lifecycle vocabulary.

    Returns (promotion_state, mapped); mapped is False when status is unknown
    and we fall back to 'draft'.
    """
    key = (status or "").strip().lower()
    if key in STATUS_TO_PROMOTION_STATE:
        return STATUS_TO_PROMOTION_STATE[key], True
    return "draft", False


def derive_db_object_type(kind: str) -> Optional[str]:
    return KIND_TO_DB_OBJECT_TYPE.get((kind or "").strip().lower())


def derive_source_authority(item: CatalogItem) -> Tuple[str, bool]:
    """Derive a registry source_authority value from provenance/refs.

    Provenance-first, conservative:
    - a design_source_path present            -> 'spec-doc'
    - provenance present, no design path, .qml refs -> 'runtime'
    - provenance present but ambiguous        -> 'mixed'
    - no provenance                           -> unresolved ('-')
    Returns (value, resolved).
    """
    prov = item.provenance or {}
    design_path = str(prov.get("design_source_path", "") or "").strip()
    has_qml = any(r.lower().endswith(".qml") for r in item.refs)
    if design_path:
        return "spec-doc", True
    if prov:
        if has_qml:
            return "runtime", True
        return "mixed", False
    return "-", False


def _slugify_stable(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return s or "unknown"


def _component_slug(item: CatalogItem) -> str:
    stem = Path(item.name).name
    if stem.endswith(".rttc.md"):
        stem = stem[: -len(".rttc.md")]
    return stem


def stable_id_for(item: CatalogItem) -> str:
    """Stable component identity: prefer doc_id, else taxonomy+stem.

    Same stem in different lanes (e.g. NotifPill in motion vs uikit) stays
    distinct because taxonomy is folded into the fallback id and doc_id is
    lane-specific.
    """
    if item.doc_id:
        return item.doc_id.strip()
    return _slugify_stable(f"{item.taxonomy}-{_component_slug(item)}")


def derive_parent(item: CatalogItem, stable_by_key: Dict[str, set]) -> Dict[str, Any]:
    """Resolve a parent stable_id from refs pointing to another RTTC doc.

    RTTC files do not encode explicit version chains, so parent_version is
    always unknown. We only claim a parent when a ref resolves to exactly one
    other scanned component; otherwise it is reported unresolved (never guessed).
    """
    self_id = stable_id_for(item)
    for ref in item.refs:
        base = Path(ref).name
        for suffix in (".rttc.md", ".rttc", ".md"):
            if base.endswith(suffix):
                base = base[: -len(suffix)]
                break
        key = base.strip().lower()
        candidates = stable_by_key.get(key, set()) - {self_id}
        if len(candidates) == 1:
            return {
                "parent_stable_id": next(iter(candidates)),
                "parent_version": None,
                "parent_ref": ref,
                "resolved": True,
            }
    return {"parent_stable_id": None, "parent_version": None, "parent_ref": "", "resolved": False}


def build_db_evolution(items: List[CatalogItem]) -> Dict[str, Any]:
    """Group RTTC items into per-component evolution rows in DB vocabulary."""
    stable_by_key: Dict[str, set] = defaultdict(set)
    for it in items:
        stable_by_key[_component_slug(it).strip().lower()].add(stable_id_for(it))

    grouped: Dict[str, List[CatalogItem]] = defaultdict(list)
    for it in items:
        grouped[stable_id_for(it)].append(it)

    components: List[Dict[str, Any]] = []
    promo_dist: Counter = Counter()
    authority_dist: Counter = Counter()
    parent_resolved = 0
    parent_unresolved = 0

    for stable_id, group in grouped.items():
        group_sorted = sorted(
            group,
            key=lambda x: (x.chunk_version, x.last_activity_dt or datetime.min, x.relative),
        )
        rows: List[Dict[str, Any]] = []
        for it in group_sorted:
            promotion_state, promo_mapped = promotion_state_from_status(it.status)
            source_authority, authority_resolved = derive_source_authority(it)
            parent = derive_parent(it, stable_by_key)
            prov = it.provenance or {}
            rows.append(
                {
                    "version": it.chunk_version,
                    "version_source": "frontmatter.chunk_version",
                    "kind": it.kind,
                    "db_object_type": derive_db_object_type(it.kind),
                    "status_rttc": it.status,
                    "promotion_state": promotion_state,
                    "promotion_state_source": "derived:status" if promo_mapped else "derived:status(fallback)",
                    "source_authority": source_authority,
                    "source_authority_resolved": authority_resolved,
                    "canonical_flag": it.canonical,
                    "parent_stable_id": parent["parent_stable_id"],
                    "parent_version": parent["parent_version"],
                    "parent_ref": parent["parent_ref"],
                    "parent_resolved": parent["resolved"],
                    "created": it.created,
                    "updated": it.updated,
                    "last_activity": it.last_activity or "-",
                    "last_activity_source": it.last_activity_source,
                    "owner": it.owner,
                    "design_source_path": str(prov.get("design_source_path", "") or ""),
                    "qml_target_path": str(prov.get("qml_target_path", "") or ""),
                    "generator": str(prov.get("generator", "") or ""),
                    "relative": it.relative,
                    "taxonomy": it.taxonomy,
                }
            )
            promo_dist[promotion_state] += 1
            authority_dist[source_authority] += 1
            if parent["resolved"]:
                parent_resolved += 1
            else:
                parent_unresolved += 1

        latest = rows[-1]
        components.append(
            {
                "stable_id": stable_id,
                "slug": _component_slug(group_sorted[-1]),
                "taxonomy": group_sorted[-1].taxonomy,
                "kind": group_sorted[-1].kind,
                "db_object_type": latest["db_object_type"],
                "versions_known": len(rows),
                "current_version": latest["version"],
                "current_promotion_state": latest["promotion_state"],
                "current_source_authority": latest["source_authority"],
                "parent_stable_id": latest["parent_stable_id"],
                "parent_resolved": latest["parent_resolved"],
                "created": group_sorted[0].created,
                "updated": latest["updated"],
                "last_activity": latest["last_activity"],
                "last_activity_source": latest["last_activity_source"],
                "rows": rows,
            }
        )

    components.sort(key=lambda c: (c["taxonomy"], c["kind"], c["stable_id"]))

    return {
        "columns": [
            "stable_id", "version", "db_object_type", "kind", "promotion_state",
            "source_authority", "parent_stable_id", "created", "updated",
            "last_activity", "last_activity_source",
        ],
        "contract": {
            "lifecycle": "schema/registry_schema.sql lifecycle_statuses",
            "source_authority_enum": sorted(SOURCE_AUTHORITY_ENUM),
            "dates": "metadata-first (updated>created), same as catalog snapshot",
            "note": "descriptive projection of the RTTC scan; no live DB writes; lineage not fabricated",
        },
        "summary": {
            "components": len(components),
            "revision_rows": sum(c["versions_known"] for c in components),
            "promotion_state_distribution": dict(sorted(promo_dist.items())),
            "source_authority_distribution": dict(sorted(authority_dist.items())),
            "parent_resolved": parent_resolved,
            "parent_unresolved": parent_unresolved,
            "multi_version_components": [
                c["stable_id"] for c in components if c["versions_known"] > 1
            ],
        },
        "components": components,
    }


def build_db_evolution_md(evolution: Dict[str, Any]) -> str:
    summary = evolution["summary"]
    lines = [
        "# RTTC Evolution (DB-like projection)",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "Descriptive projection of the RTTC scan into the registry DB vocabulary "
        "(`schema/registry_schema.sql`). Columns map to `registry_objects` "
        "(stable_id, version, source_authority, parent, lifecycle status). Values "
        "are read from frontmatter or derived by explicit rules; nothing is written "
        "to a live DB and no lineage is fabricated.",
        "",
        "## Contract",
        f"- Lifecycle vocab: {evolution['contract']['lifecycle']}",
        f"- source_authority enum: {', '.join(evolution['contract']['source_authority_enum'])}",
        f"- Dates: {evolution['contract']['dates']}",
        "- version = `frontmatter.chunk_version`; promotion_state = derived from `status`; "
        "parent resolved only from an unambiguous ref.",
        "",
        "## Summary",
        f"- Components: {summary['components']}",
        f"- Revision rows: {summary['revision_rows']}",
        f"- Parent links resolved: {summary['parent_resolved']} / unresolved: {summary['parent_unresolved']}",
        f"- Multi-version components: {len(summary['multi_version_components'])}",
        "",
        "### promotion_state distribution",
        "",
        "| promotion_state | count |",
        "|---|---:|",
    ]
    for state, count in summary["promotion_state_distribution"].items():
        lines.append(f"| {state} | {count} |")
    lines.append("")
    lines.append("### source_authority distribution")
    lines.append("")
    lines.append("| source_authority | count |")
    lines.append("|---|---:|")
    for authority, count in summary["source_authority_distribution"].items():
        lines.append(f"| {authority} | {count} |")
    lines.append("")
    lines.append("## Evolution per component (latest revision)")
    lines.append("")
    lines.append(
        "| stable_id | slug | kind | db_type | ver | promotion_state | source_authority | parent | created | updated | last_activity (src) |"
    )
    lines.append("|---|---|---|---|---:|---|---|---|---|---|---|")
    for comp in evolution["components"]:
        parent = comp["parent_stable_id"] or "-"
        db_type = comp["db_object_type"] or "-"
        lines.append(
            f"| {comp['stable_id']} | {comp['slug']} | {comp['kind']} | {db_type} | "
            f"{comp['current_version']} | {comp['current_promotion_state']} | "
            f"{comp['current_source_authority']} | {parent} | {comp['created']} | "
            f"{comp['updated']} | {comp['last_activity']} ({comp['last_activity_source']}) |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def write_db_evolution_files(out: Path, evolution: Dict[str, Any]) -> Dict[str, str]:
    out.mkdir(parents=True, exist_ok=True)
    written: Dict[str, str] = {}

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **evolution,
    }
    json_path = out / "rttc_db_evolution.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    written["json"] = str(json_path)

    md_path = out / "db_evolution.md"
    md_path.write_text(build_db_evolution_md(evolution), encoding="utf-8")
    written["md"] = str(md_path)

    csv_cols = [
        "stable_id", "slug", "taxonomy", "kind", "db_object_type", "version",
        "status_rttc", "promotion_state", "source_authority",
        "source_authority_resolved", "parent_stable_id", "parent_resolved",
        "created", "updated", "last_activity", "last_activity_source",
        "design_source_path", "qml_target_path",
    ]

    def esc(value: Any) -> str:
        s = "" if value is None else str(value)
        if any(ch in s for ch in (",", '"', "\n")):
            return '"' + s.replace('"', '""') + '"'
        return s

    csv_lines = [",".join(csv_cols)]
    for comp in evolution["components"]:
        for row in comp["rows"]:
            record = {
                "stable_id": comp["stable_id"],
                "slug": comp["slug"],
                "taxonomy": row["taxonomy"],
                "kind": row["kind"],
                "db_object_type": row["db_object_type"],
                "version": row["version"],
                "status_rttc": row["status_rttc"],
                "promotion_state": row["promotion_state"],
                "source_authority": row["source_authority"],
                "source_authority_resolved": row["source_authority_resolved"],
                "parent_stable_id": row["parent_stable_id"],
                "parent_resolved": row["parent_resolved"],
                "created": row["created"],
                "updated": row["updated"],
                "last_activity": row["last_activity"],
                "last_activity_source": row["last_activity_source"],
                "design_source_path": row["design_source_path"],
                "qml_target_path": row["qml_target_path"],
            }
            csv_lines.append(",".join(esc(record[c]) for c in csv_cols))
    csv_path = out / "db_evolution.csv"
    csv_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")
    written["csv"] = str(csv_path)

    return written


def as_record(item: CatalogItem) -> Dict[str, Any]:
    return {
        "path": item.relative,
        "name": item.name,
        "status": item.status,
        "status_source": "frontmatter.status",
        "created": item.created,
        "updated": item.updated,
        "mtime": item.mtime,
        "last_activity": item.last_activity,
        "last_activity_source": item.last_activity_source,
        "taxonomy": item.taxonomy,
        "kind": item.kind,
        "subtype": item.subtype,
        "doc_id": item.doc_id,
        "canonical": item.canonical,
        "active": item.active,
        "recent": item.recent,
        "edit_scope": item.edit_scope,
        "source_ref": item.source_ref,
        "tags": item.tags,
    }


def _group_by_subcatalog(items: Iterable[CatalogItem]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for i in items:
        out[i.taxonomy].append(as_record(i))
    for records in out.values():
        records.sort(key=lambda r: (r["kind"], r["status"], r["name"]))
    return dict(sorted(out.items(), key=lambda kv: kv[0]))


def is_recent(item: CatalogItem, cutoff: datetime, include_mtime_fallback: bool = False) -> bool:
    if item.last_activity_dt is not None:
        return item.last_activity_dt >= cutoff
    if include_mtime_fallback:
        mtime_dt = _coerce_datetime(item.mtime)
        return mtime_dt is not None and mtime_dt >= cutoff
    return False


def build_md_report(
    items: List[CatalogItem],
    active_cutoff: datetime,
    subcatalogs: Dict[str, List[Dict[str, Any]]],
    zip_summary: Dict[str, Any],
    motion_graph: Dict[str, Any],
    alignment_counts: Dict[str, Any],
    db_evolution: Dict[str, Any],
) -> str:
    total = len(items)
    active_items = [i for i in items if i.active]
    recent_items = [i for i in items if i.recent]
    edits = [i for i in items if i.edit_scope == "bugfix" or i.edit_scope == "redesign"]

    lines = [
        "# RTTC Catalog (ZIP9-anchored)",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"Active criteria: {', '.join(sorted(ACTIVE_STATUSES))}",
        f"Recency cutoff: {active_cutoff.date()} (last_activity >= this date, metadata-first unless --include-mtime-recent)",
        f"ZIP9 found: {zip_summary.get('found', False)}",
        f"ZIP9 date: {zip_summary.get('date', '-')}",
        "",
        "## Scope",
        f"- Total .rttc files: {total}",
        f"- Active: {len(active_items)}",
        f"- Recent (last 21 days by default): {len(recent_items)}",
        f"- Edits candidates (redesign + bugfix): {len(edits)}",
        "",
    ]

    kinds = Counter(i.kind for i in items)
    lines.append("## Taxonomy")
    lines.append("")
    lines.append("| kind | count |")
    lines.append("|---|---:|")
    for kind, count in sorted(kinds.items()):
        lines.append(f"| {kind} | {count} |")
    lines.append("")

    lines.append("## Subcatalogs")
    lines.append("")
    for taxonomy, records in subcatalogs.items():
        lines.append(f"- `{taxonomy}`: {len(records)} entries")
    lines.append("")

    lines.append("## ZIP9-derived composition")
    lines.append("")
    lines.append("- Motion atoms: " + str(zip_summary.get("motion", {}).get("atoms", 0)))
    lines.append("- Motion molecules: " + str(zip_summary.get("motion", {}).get("molecules", 0)))
    lines.append("- Context-menu molecule specs: " + str(zip_summary.get("molecules", {}).get("molecules", 0)))
    lines.append("- Alignment ledger (Context):")
    lines.append(f"  - Atoms keepable table rows: {alignment_counts.get('atoms', '-')}")
    lines.append(f"  - Molecules keepable table rows: {alignment_counts.get('molecules', '-')}")
    lines.append(f"  - Recipes keepable table rows: {alignment_counts.get('recipes', '-')}")
    lines.append("")

    if motion_graph.get("molecules"):
        lines.append("### Motion composition (ZIP9) examples")
        lines.append("")
        lines.append("| molecule_id | title | atom_refs |")
        lines.append("|---|---|---|")
        for mol in motion_graph["molecules"][:12]:
            atoms = mol.get("atoms_display", "(none)")
            lines.append(f"| {mol['id']} | {mol['title']} | `{atoms}` |")
        if len(motion_graph["molecules"]) > 12:
            lines.append(f"| … | … | + {len(motion_graph['molecules']) - 12} molécules restantes |")
        unresolved = len(motion_graph.get("unresolved_atom_refs", []))
        lines.append("")
        lines.append(f"- Motion composition unresolved references: {unresolved}.")
        if unresolved:
            lines.append("- Missing atom IDs in motion graph are mostly legacy/inline tokenized references from older exports.")
        lines.append("")

    lines.append("## DB-like evolution (per component)")
    lines.append("")
    ev_summary = db_evolution.get("summary", {})
    lines.append(
        "Projection of the RTTC scan into the registry DB vocabulary "
        "(`schema/registry_schema.sql`): stable_id, version, source_authority, "
        "parent, lifecycle status. Full table in `catalog/db_evolution.md`; "
        "structured data in `catalog/rttc_db_evolution.json` / `catalog/db_evolution.csv`."
    )
    lines.append("")
    lines.append(f"- Components: {ev_summary.get('components', 0)}")
    lines.append(f"- Revision rows: {ev_summary.get('revision_rows', 0)}")
    lines.append(
        f"- Parent links resolved / unresolved: "
        f"{ev_summary.get('parent_resolved', 0)} / {ev_summary.get('parent_unresolved', 0)}"
    )
    lines.append(
        f"- Multi-version components: {len(ev_summary.get('multi_version_components', []))}"
    )
    promo_dist = ev_summary.get("promotion_state_distribution", {})
    if promo_dist:
        lines.append(
            "- promotion_state: "
            + ", ".join(f"{state}={count}" for state, count in promo_dist.items())
        )
    authority_dist = ev_summary.get("source_authority_distribution", {})
    if authority_dist:
        lines.append(
            "- source_authority: "
            + ", ".join(f"{authority}={count}" for authority, count in authority_dist.items())
        )
    lines.append("")

    lines.append("## Catalogue snapshots")
    lines.append("")
    lines.append("### Recent items")
    lines.append("| relative | status | edit_scope | last_activity | activity_source | created | updated | kind | taxonomy |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for item in sorted(recent_items, key=lambda x: (x.last_activity or "", x.relative), reverse=True):
        lines.append(
            f"| {item.relative} | {item.status} | {item.edit_scope} | {item.last_activity or '-'} | {item.last_activity_source} | "
            f"{item.created} | {item.updated} | {item.kind} | {item.taxonomy} |"
        )
    lines.append("")

    if edits:
        lines.append("### Edits ciblées")
        lines.append("| relative | status | last_activity | activity_source | edit_scope | source_ref |")
        lines.append("|---|---|---|---|---|---|")
        for item in sorted(edits, key=lambda x: (x.last_activity or "", x.relative), reverse=True):
            source = item.source_ref.replace("|", "⧹|")
            lines.append(
                f"| {item.relative} | {item.status} | {item.last_activity or '-'} | {item.last_activity_source} | {item.edit_scope} | {source} |"
            )
        lines.append("")

    lines.append("### Filter snapshot")
    lines.append("" + "```")
    lines.append(f"active_count={len(active_items)}")
    lines.append(f"recent_count={len(recent_items)}")
    lines.append(f"bugfix_like_edits={len([i for i in edits if i.edit_scope == 'bugfix'])}")
    lines.append(f"redesign_edits={len([i for i in edits if i.edit_scope == 'redesign'])}")
    lines.append("```")

    return "\n".join(lines) + "\n"


def build_subcatalog_files(
    out: Path,
    subcatalogs: Dict[str, List[Dict[str, Any]]],
    items: List[CatalogItem],
    active_cutoff: datetime,
    zip_summary: Dict[str, Any],
) -> Dict[str, str]:
    out.mkdir(parents=True, exist_ok=True)
    written: Dict[str, str] = {}

    # Master snapshot
    snapshot = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "active_cutoff": active_cutoff.strftime("%Y-%m-%d"),
        "zip9_found": zip_summary.get("found", False),
        "counts": {
            "total": len(items),
            "active": len([i for i in items if i.active]),
            "recent": len([i for i in items if i.recent]),
        },
        "taxonomy": {taxonomy: len(records) for taxonomy, records in subcatalogs.items()},
        "kind": {k: len([i for i in items if i.kind == k]) for k in sorted(set(i.kind for i in items))},
        "items": [as_record(i) for i in sorted(items, key=lambda x: x.relative)],
        "subcatalogs": {
            t: f"subcatalog/{sanitize_catalog_name(t)}.json" for t in subcatalogs
        },
    }

    snapshot_path = out / "rttc_catalog_snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    written["snapshot"] = str(snapshot_path)

    active_recent = [
        as_record(i) for i in items
        if i.active and i.recent
    ]
    active_path = out / "rttc_active_recent.json"
    active_path.write_text(json.dumps(active_recent, indent=2, sort_keys=True), encoding="utf-8")
    written["active_recent"] = str(active_path)

    edits = [
        as_record(i) for i in items
        if i.edit_scope in {"bugfix", "redesign"}
    ]
    edits_path = out / "rttc_edits_focus.json"
    edits_path.write_text(json.dumps(edits, indent=2, sort_keys=True), encoding="utf-8")
    written["edits"] = str(edits_path)

    for taxonomy, records in subcatalogs.items():
        name = f"{sanitize_catalog_name(taxonomy)}.json"
        path = out / "subcatalog" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        records_with_context = {
            "taxonomy": taxonomy,
            "count": len(records),
            "generated_at": snapshot["generated_at"],
            "items": records,
        }
        path.write_text(json.dumps(records_with_context, indent=2, sort_keys=True), encoding="utf-8")
        written[taxonomy] = str(path)

    return written


def sanitize_catalog_name(name: str) -> str:
    return name.replace(".", "_").replace("/", "_")


def write_legacy_outputs(
    root_out: Path,
    items: List[CatalogItem],
    active_cutoff: datetime,
    include_mtime_recent: bool = False,
) -> None:
    # Keep backward-compatible outputs used by current tooling.
    active_recent = [i for i in items if i.active and is_recent(i, active_cutoff, include_mtime_recent)]

    recent_records = [
        {
            "path": str(i.path),
            "name": i.name,
            "relative": i.relative,
            "status": i.status,
            "subtype": i.subtype,
            "kind": i.kind,
            "taxonomy": i.taxonomy,
            "created": i.created,
            "updated": i.updated,
            "last_activity": i.last_activity,
            "mtime": i.mtime,
        }
        for i in active_recent
    ]

    (root_out / "active_rttc_recent.json").write_text(
        json.dumps(recent_records, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    root_csv = [
        "relative,name,status,subtype,kind,taxonomy,created,updated,last_activity,mtime,path"
    ]
    for i in active_recent:
        row = [
            i.relative,
            i.name,
            i.status,
            i.subtype,
            i.kind,
            i.taxonomy,
            i.created,
            i.updated,
            i.last_activity or "-",
            i.mtime,
            str(i.path),
        ]
        escaped = [
            f"\"{v.replace('"', '\\"')}\"" if "," in v or "\"" in v else v
            for v in row
        ]
        root_csv.append(",".join(escaped))
    (root_out / "active_rttc_recent.csv").write_text("\n".join(root_csv) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an iteration-aware catalog snapshot.")
    parser.add_argument(
        "--components-dir",
        default=str(DEFAULT_COMPONENTS_DIR),
        help="Path containing .rttc.md files (default: gnu.in-shell/components)",
    )
    parser.add_argument(
        "--zip9",
        default="/mnt/hdd/Téléchargements/Merging design assets and specs (9).zip",
        help="ZIP9 archive path",
    )
    parser.add_argument(
        "--alignment-doc",
        default=str(DEFAULT_DOCS_DIR / "context-menu-v31-alignment.md"),
        help="Alignment ledger path used for legacy status counts",
    )
    parser.add_argument(
        "--out",
        default=str((ROOT / "catalog")),
        help="Output directory for iteration-aware catalog artifacts",
    )
    parser.add_argument(
        "--recent-days",
        type=int,
        default=21,
        help="Recency threshold in days (based on last_activity)",
    )
    parser.add_argument(
        "--limit-recent",
        type=int,
        default=0,
        help="Optional hard cap of recent lines in Markdown (0 = no cap)",
    )
    parser.add_argument(
        "--include-mtime-recent",
        action="store_true",
        help="Fallback to file mtime when created/updated metadata is missing (for recency checks)",
    )
    args = parser.parse_args()

    components_dir = Path(args.components_dir).resolve()
    out = Path(args.out).resolve()
    root_out = ROOT
    out.mkdir(parents=True, exist_ok=True)

    active_cutoff = datetime.now() - timedelta(days=args.recent_days)
    items = scan_rttc_files(components_dir)

    for item in items:
        item.recent = is_recent(item, active_cutoff, args.include_mtime_recent)
        if not item.last_activity_dt and args.include_mtime_recent:
            mtime_dt = _coerce_datetime(item.mtime)
            if mtime_dt:
                item.last_activity = _format_date(mtime_dt)
                item.last_activity_source = "mtime"

    items = sorted(items, key=lambda x: (x.taxonomy, x.kind, x.relative))

    zip_summary = read_zip9_manifest(Path(args.zip9))
    alignment_counts = parse_alignment_counts(Path(args.alignment_doc))
    motion_graph = build_motion_graph(zip_summary)
    subcatalogs = _group_by_subcatalog(items)
    db_evolution = build_db_evolution(items)

    if args.limit_recent and args.limit_recent > 0:
        recent_limited = [i for i in items if i.recent][: args.limit_recent]
    else:
        recent_limited = [i for i in items if i.recent]

    # Markdown index and catalog payloads.
    md = build_md_report(
        items=items,
        active_cutoff=active_cutoff,
        subcatalogs=subcatalogs,
        zip_summary=zip_summary,
        motion_graph=motion_graph,
        alignment_counts=alignment_counts,
        db_evolution=db_evolution,
    )

    # Keep legacy names expected by current tooling.
    write_legacy_outputs(root_out, items, active_cutoff, include_mtime_recent=args.include_mtime_recent)

    write_catalog = build_subcatalog_files(out, subcatalogs, items, active_cutoff, zip_summary)
    md_path = out / "catalog.md"
    md_path.write_text(md, encoding="utf-8")

    write_evolution = write_db_evolution_files(out, db_evolution)

    # Backwards readme for the active recent list in the tooling folder.
    (root_out / "README-FRESH-ACTIVE-RTTC.md").write_text(
        _build_fresh_readme(
            items=items,
            cutoff=active_cutoff,
            recent=recent_limited,
            zip_summary=zip_summary,
            alignment_counts=alignment_counts,
        ),
        encoding="utf-8",
    )

    print(f"generated: {out}")
    print(f"wrote: {write_catalog.get('snapshot')}")
    print(f"wrote: {write_catalog.get('active_recent')}")
    print(f"wrote: {write_catalog.get('edits')}")
    print(f"wrote: {write_evolution.get('json')}")
    print(f"wrote: {write_evolution.get('md')}")
    print(f"wrote: {write_evolution.get('csv')}")


def _build_fresh_readme(
    items: List[CatalogItem],
    cutoff: datetime,
    recent: List[CatalogItem],
    zip_summary: Dict[str, Any],
    alignment_counts: Dict[str, Any],
) -> str:
    active_recent = [i for i in recent if i.active]
    return (
        "# RTTC actifs / récents\n\n"
        f"- Baseline ZIP9: {zip_summary.get('path', '-')}.\n"
        f"- Date ZIP9: {zip_summary.get('date', '-')}.\n"
        f"- Cutoff: {cutoff.date()} (last_activity >= this date, metadata-first).\n"
        f"- Total fichiers RTTC scannés: {len(items)}\n"
        f"- Total actifs récents: {len(active_recent)}\n"
        f"- Alignement context-menu (ledger): C:{alignment_counts.get('atoms', '-')}, CM:{alignment_counts.get('molecules', '-')}, R:{alignment_counts.get('recipes', '-')}.\n\n"
        "| Relative path | Status | Last activity | Activity source | Created | Updated | Kind | Taxonomy | Edit scope |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        + "\n".join(
            f"| {i.relative} | {i.status} | {i.last_activity or '-'} | {i.last_activity_source} | {i.created} | {i.updated} | {i.kind} | {i.taxonomy} | {i.edit_scope} |"
            for i in sorted(active_recent, key=lambda x: (x.last_activity or "", x.relative), reverse=True)
        )
    )


if __name__ == "__main__":
    main()
