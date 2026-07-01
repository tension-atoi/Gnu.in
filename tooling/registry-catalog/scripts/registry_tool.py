#!/usr/bin/env python3
"""
registry_tool.py

Data-process tool for a strict visual registry:
- SQLite typed catalog
- lifecycle gates
- forks with lineage
- proof attachment
- export of frozen artifacts for renderers
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "registry_schema.sql"
REQUIRED_STATE_KEYS = {"hover", "pressed", "focus", "disabled", "active"}
REQUIRED_BEHAVIOR_KEYS = {"timers", "input", "animation", "telemetry"}

PROMOTION_REQUIRED_CHECKS = {
    "candidate": ["geometry", "tokens", "states", "behavior", "renderers", "source_authority", "proof"],
    "canonical": ["geometry", "tokens", "states", "behavior", "renderers", "source_authority", "proof"],
}
PROMOTION_CHECK_ALIASES: Dict[str, str] = {
    "states": "states_strict",
    "behavior": "behavior_strict",
    "source_authority": "source_authority_strict",
}


def connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def load_schema(con: sqlite3.Connection) -> None:
    con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def parse_json(raw: str) -> str:
    payload = json.loads(raw)
    # normalize and store compact json
    return json.dumps(payload, sort_keys=True)


def parse_json_object(raw: str) -> Dict[str, Any]:
    payload = json.loads(raw or "{}")
    if not isinstance(payload, dict):
        raise ValueError(f"invalid contract payload, expected object: {raw}")
    return payload


def ensure_required_keys(payload: Dict[str, Any], required: set[str]) -> bool:
    return required.issubset(payload.keys())


def normalize_slug(slug: str) -> str:
    slug = slug.strip().lower()
    return re.sub(r"[^a-z0-9._-]+", "-", slug)


def resolve_object(con: sqlite3.Connection, object_key: str) -> sqlite3.Row:
    # Accept either object revision id, or stable_id.
    row = con.execute(
        "SELECT * FROM registry_objects WHERE id = ?",
        (object_key,),
    ).fetchone()
    if row is not None:
        return row
    row = con.execute(
        """
        SELECT * FROM registry_objects
        WHERE stable_id = ?
        ORDER BY version DESC
        LIMIT 1
        """,
        (object_key,),
    ).fetchone()
    if row is None:
        raise SystemExit(f"object not found: {object_key}")
    return row


def next_version_for_stable(con: sqlite3.Connection, stable_id: str) -> int:
    row = con.execute(
        "SELECT COALESCE(MAX(version), 0) + 1 AS next_v FROM registry_objects WHERE stable_id = ?",
        (stable_id,),
    ).fetchone()
    return int(row["next_v"]) if row else 1


def do_init(args: argparse.Namespace) -> None:
    db_path = Path(args.db).resolve()
    con = connect(db_path)
    load_schema(con)
    con.commit()
    print(f"initialized sqlite registry at {db_path}")


def do_status(con: sqlite3.Connection) -> None:
    rows = con.execute(
        "SELECT status, COUNT(*) AS n FROM registry_objects GROUP BY status ORDER BY n DESC;"
    ).fetchall()
    print("lifecycle distribution:")
    for r in rows:
        print(f"- {r['status']:10s}: {r['n']}")


def do_add_object(args: argparse.Namespace) -> None:
    con = connect(Path(args.db))
    con.row_factory = sqlite3.Row
    con.execute("BEGIN")
    geometry = parse_json(args.geometry or "{}")
    tokens = parse_json(args.tokens or "{}")
    states = parse_json(args.states or "{}")
    behaviors = parse_json(args.behaviors or "{}")
    telemetry = parse_json(args.telemetry or "{}")
    constraints = parse_json(args.constraints or "{}")
    renderers = parse_json(args.renderers or "[]")
    payload = parse_json(args.payload or "{}")

    stable_id = args.stable_id or str(uuid.uuid4())
    version = args.version or next_version_for_stable(con, stable_id)
    object_id = str(uuid.uuid4())
    parent_stable_id = args.parent_stable_id
    parent_version = args.parent_version
    status = args.status or "draft"

    con.execute(
        """
        INSERT INTO registry_objects (
          id, stable_id, version, object_type, slug, display_name, source_authority,
          schema_version, status, geometry_contract, tokens_contract, state_contract,
          behavior_contract, telemetry_contract, constraints_contract, payload,
          parent_stable_id, parent_version, created_by, authority_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            object_id,
            stable_id,
            version,
            args.type,
            normalize_slug(args.slug),
            args.name,
            args.source_authority,
            args.schema_version,
            status,
            geometry,
            tokens,
            states,
            behaviors,
            telemetry,
            constraints,
            payload,
            parent_stable_id,
            parent_version,
            args.created_by,
            args.authority_notes or "",
        ),
    )
    for r in json.loads(renderers):
        if isinstance(r, dict):
            renderer_name = str(r.get("name", "")).strip()
        else:
            renderer_name = str(r).strip()
        if not renderer_name:
            raise SystemExit("invalid renderer entry in --renderers")
        con.execute(
            """
            INSERT INTO registry_object_renderers (object_id, renderer_name, support_tier, support_notes)
            VALUES (?, ?, ?, ?)
            """,
            (object_id, renderer_name, "pilot", ""),
        )
    con.commit()
    print(f"created: id={object_id} stable_id={stable_id} version={version}")


def do_link_relation(args: argparse.Namespace) -> None:
    con = connect(Path(args.db))
    parent = resolve_object(con, args.parent)
    child = resolve_object(con, args.child)
    con.execute(
        """
        INSERT INTO object_relations (parent_id, child_id, relation_type, rationale)
        VALUES (?, ?, ?, ?)
        """,
        (parent["id"], child["id"], args.relation, args.rationale or ""),
    )
    con.commit()
    print(f"relation: {parent['id']} -[{args.relation}]-> {child['id']}")


def gather_proof_checks(con: sqlite3.Connection, object_row: sqlite3.Row, object_version: int) -> Dict[str, bool]:
    checks = {
        "geometry": object_row["geometry_contract"] not in ("{}", "[]", '""'),
        "tokens": object_row["tokens_contract"] not in ("{}", "[]", '""'),
        "states": object_row["state_contract"] not in ("{}", "[]", '""'),
        "behavior": object_row["behavior_contract"] not in ("{}", "[]", '""'),
        "source_authority": object_row["source_authority"] is not None and object_row["source_authority"] != "",
        "source_authority_strict": object_row["source_authority"] in {"ZIP9/Central", "spec-doc", "screenshot", "runtime", "mixed"},
    }
    try:
        checks["states_strict"] = ensure_required_keys(parse_json_object(object_row["state_contract"]), REQUIRED_STATE_KEYS)
    except ValueError:
        checks["states_strict"] = False
    try:
        checks["behavior_strict"] = ensure_required_keys(parse_json_object(object_row["behavior_contract"]), REQUIRED_BEHAVIOR_KEYS)
    except ValueError:
        checks["behavior_strict"] = False
    checks["renderers"] = con.execute(
        "SELECT 1 FROM registry_object_renderers WHERE object_id = ? LIMIT 1",
        (object_row["id"],),
    ).fetchone() is not None
    checks["proof"] = con.execute(
        """
        SELECT 1
        FROM proofs
        WHERE object_id = ? AND object_version = ? LIMIT 1
        """,
        (object_row["id"], object_version),
    ).fetchone() is not None
    return checks


def required_checks_for(target_status: str) -> List[str]:
    if target_status in {"candidate", "canonical"}:
        return PROMOTION_REQUIRED_CHECKS[target_status][:]
    return []


def find_duplicate_candidates(
    con: sqlite3.Connection,
    object_row: sqlite3.Row,
    target_status: str,
) -> List[sqlite3.Row]:
    if target_status not in ("candidate", "canonical"):
        return []
    return con.execute(
        """
        SELECT id, stable_id, version, source_authority
        FROM registry_objects
        WHERE object_type = ?
          AND slug = ?
          AND status IN ('candidate', 'canonical')
          AND id != ?
          AND stable_id != ?
        ORDER BY updated_at DESC
        """,
        (
            object_row["object_type"],
            object_row["slug"],
            object_row["id"],
            object_row["stable_id"],
        ),
    ).fetchall()


def write_manifest(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def do_promote(args: argparse.Namespace) -> None:
    con = connect(Path(args.db))
    obj = resolve_object(con, args.object_id)

    if args.to_status not in {"draft", "lab", "candidate", "canonical", "deprecated", "retired"}:
        raise SystemExit(f"invalid target status: {args.to_status}")

    checks = gather_proof_checks(con, obj, obj["version"])
    required = required_checks_for(args.to_status)
    requested = set(args.check or required)
    if args.check:
        missing = [c for c in requested if c not in required]
        if missing:
            raise SystemExit(f"unsupported checks: {', '.join(sorted(missing))}")
        required = sorted(requested)

    required = list(dict.fromkeys(required))
    if args.strict and args.to_status in {"candidate", "canonical"}:
        required = [PROMOTION_CHECK_ALIASES.get(item, item) for item in required]
    required = list(dict.fromkeys(required))
    passed = all(checks.get(c, False) for c in required)
    if args.force and args.force.lower() in {"1", "true", "yes", "on", "y"}:
        passed = True

    duplicates = find_duplicate_candidates(con, obj, args.to_status)
    if duplicates and not args.allow_duplicate:
        duplicate_ids = ", ".join([x["stable_id"] for x in duplicates])
        raise SystemExit(f"promotion blocked: duplicate component signature for slug '{obj['slug']}' (found {duplicate_ids}). use --allow-duplicate to bypass")

    if args.to_status in {"candidate", "canonical"} and (args.reviewer is None or args.reviewer == "pending"):
        raise SystemExit("promotion to candidate/canonical requires --reviewer")

    decision = "approved" if passed else "rejected"
    if args.reviewer is None:
        args.reviewer = "pending"
    source_authority = args.source_authority or obj["source_authority"]

    prom_id = str(uuid.uuid4())
    con.execute(
        """
        INSERT INTO promotion_attempts (
          id, object_id, from_status, to_status, requested_by, reviewer, decision,
          rationale, geometry_ok, tokens_ok, states_ok, behavior_ok, renderers_ok,
          proof_ok, proofs_json, source_authority
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            prom_id,
            obj["id"],
            obj["status"],
            args.to_status,
            args.requested_by,
            args.reviewer,
            decision,
            args.reason or "",
            1 if checks["geometry"] else 0,
            1 if checks["tokens"] else 0,
            1 if checks["states"] else 0,
            1 if checks["behavior"] else 0,
            1 if checks["renderers"] else 0,
            1 if checks["proof"] else 0,
            json.dumps([]),
            source_authority,
        ),
    )

    for check_name in required:
        if check_name == "states_strict":
            status_check = checks.get("states_strict", False)
            check_type = "states"
        elif check_name == "behavior_strict":
            status_check = checks.get("behavior_strict", False)
            check_type = "behavior"
        elif check_name == "source_authority_strict":
            status_check = checks.get("source_authority_strict", False)
            check_type = "source_authority"
        else:
            status_check = checks[check_name]
            check_type = check_name
        if check_type == "renderers":
            check_type = "renderer_support"
        con.execute(
            "INSERT INTO promotion_checks (promotion_id, check_type, result, details, checked_by) VALUES (?, ?, ?, ?, ?)",
            (prom_id, check_type, 1 if status_check else 0, "auto", args.requested_by),
        )

    if decision == "approved":
        con.execute(
            "UPDATE registry_objects SET status = ? WHERE id = ?",
            (args.to_status, obj["id"]),
        )
        con.execute(
            "INSERT INTO status_history (object_id, from_status, to_status, reason, decided_by) VALUES (?, ?, ?, ?, ?)",
            (obj["id"], obj["status"], args.to_status, args.reason or "", args.requested_by),
        )
    else:
        con.execute(
            "INSERT INTO status_history (object_id, from_status, to_status, reason, decided_by) VALUES (?, ?, ?, ?, ?)",
            (obj["id"], obj["status"], obj["status"], args.reason or "checks failed", args.requested_by),
        )

    con.commit()
    print(
        f"promotion={prom_id} object={obj['id']} {obj['status']} -> {args.to_status} decision={decision}"
    )
    if decision == "rejected":
        raise SystemExit("promotion rejected by checks")


def do_inspect(args: argparse.Namespace) -> None:
    con = connect(Path(args.db))
    obj = resolve_object(con, args.object_id)
    stable_versions = con.execute(
        "SELECT * FROM registry_objects WHERE stable_id = ? ORDER BY version",
        (obj["stable_id"],),
    ).fetchall()
    versions = []
    for row in stable_versions:
        versions.append(dict(row))

    relations_in = con.execute(
        """
        SELECT parent_id, relation_type, rationale
        FROM object_relations
        WHERE child_id = ?
        """,
        (obj["id"],),
    ).fetchall()

    relations_out = con.execute(
        """
        SELECT child_id, relation_type, rationale
        FROM object_relations
        WHERE parent_id = ?
        """,
        (obj["id"],),
    ).fetchall()

    renderers = con.execute(
        "SELECT renderer_name, support_tier, support_notes FROM registry_object_renderers WHERE object_id = ?",
        (obj["id"],),
    ).fetchall()

    proofs = con.execute(
        "SELECT * FROM proofs WHERE object_id = ? ORDER BY created_at DESC",
        (obj["id"],),
    ).fetchall()

    forks = con.execute(
        """
        SELECT * FROM fork_attempts
        WHERE component_id = ? OR component_id IN (
          SELECT id FROM registry_objects WHERE stable_id = ?
        )
        ORDER BY created_at DESC
        """,
        (obj["id"], obj["stable_id"]),
    ).fetchall()

    history = con.execute(
        "SELECT from_status, to_status, reason, decided_by, created_at FROM status_history WHERE object_id = ? ORDER BY created_at",
        (obj["id"],),
    ).fetchall()

    payload = {
        "target": dict(obj),
        "versions": versions,
        "relations_in": [dict(r) for r in relations_in],
        "relations_out": [dict(r) for r in relations_out],
        "renderers": [dict(r) for r in renderers],
        "proofs": [dict(r) for r in proofs],
        "forks": [dict(r) for r in forks],
        "status_history": [dict(r) for r in history],
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"inspect target: {obj['id']} ({obj['stable_id']} v{obj['version']})")
        print(f"type/status: {obj['object_type']} / {obj['status']}")
        print(f"stable lineage versions: {len(versions)}")
        print(f"renderers: {len(renderers)}")
        print(f"proofs: {len(proofs)}")
        print(f"fork entries: {len(forks)}")
        print(f"incoming relations: {len(relations_in)} outgoing relations: {len(relations_out)}")


def do_fork(args: argparse.Namespace) -> None:
    con = connect(Path(args.db))
    parent = resolve_object(con, args.object_id)
    new_id = str(uuid.uuid4())
    new_version = next_version_for_stable(con, parent["stable_id"])

    fork_reason = args.reason or "iteration"
    delta = parse_json(args.delta or "{}")
    decision = args.decision or ""
    status = args.state or "lab"

    con.execute("BEGIN")
    con.execute(
        """
        INSERT INTO registry_objects (
          id, stable_id, version, object_type, slug, display_name, source_authority,
          schema_version, status, geometry_contract, tokens_contract, state_contract,
          behavior_contract, telemetry_contract, constraints_contract, payload,
          parent_stable_id, parent_version, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            new_id,
            parent["stable_id"],
            new_version,
            parent["object_type"],
            parent["slug"],
            f"{parent['display_name']} (fork)",
            parent["source_authority"],
            parent["schema_version"],
            status,
            parent["geometry_contract"],
            parent["tokens_contract"],
            parent["state_contract"],
            parent["behavior_contract"],
            parent["telemetry_contract"],
            parent["constraints_contract"],
            parent["payload"],
            parent["stable_id"],
            parent["version"],
            args.created_by,
        ),
    )
    for row in con.execute(
        "SELECT renderer_name, support_tier, support_notes FROM registry_object_renderers WHERE object_id = ?",
        (parent["id"],),
    ):
        con.execute(
            "INSERT INTO registry_object_renderers (object_id, renderer_name, support_tier, support_notes) VALUES (?, ?, ?, ?)",
            (new_id, row["renderer_name"], row["support_tier"], row["support_notes"]),
        )
    con.execute(
        """
        INSERT INTO fork_attempts (
          id, component_id, parent_version, reason, delta_payload, fork_state, proof_before_id, proof_after_id, decision, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            new_id,
            parent["version"],
            fork_reason,
            delta,
            status,
            args.proof_before or None,
            args.proof_after or None,
            decision,
            args.created_by,
        ),
    )
    con.execute(
        "INSERT INTO status_history (object_id, from_status, to_status, reason, decided_by) VALUES (?, ?, ?, ?, ?)",
        (new_id, status, status, "fork", args.created_by),
    )
    con.commit()
    print(f"forked: parent={parent['id']} -> new={new_id} version={new_version}")


def do_add_proof(args: argparse.Namespace) -> None:
    con = connect(Path(args.db))
    obj = resolve_object(con, args.object_id)
    object_version = args.version or obj["version"]
    con.execute(
        """
        INSERT INTO proofs (
          id, object_id, object_version, renderer_name, evidence_type,
          screenshot_path, screenshot_hash, pixel_diff_hash, pixel_diff_payload,
          behavior_payload, telemetry_payload, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            obj["id"],
            object_version,
            args.renderer,
            args.evidence_type,
            args.screenshot,
            args.hash,
            args.diff_hash or "",
            parse_json(args.diff_payload or "{}"),
            parse_json(args.behavior_payload or "{}"),
            parse_json(args.telemetry_payload or "{}"),
            args.created_by,
        ),
    )
    con.commit()
    print(
        f"proof attached: object={obj['id']} version={object_version} renderer={args.renderer}"
    )


def ensure_artifacts_root(out: Path) -> None:
    (out / "recipes").mkdir(parents=True, exist_ok=True)
    (out / "docs").mkdir(parents=True, exist_ok=True)
    (out / "proofs").mkdir(parents=True, exist_ok=True)


def normalize_file_base(slug: str) -> str:
    return normalize_slug(slug).replace("/", "-")


def token_sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def export_tokens_rs(records: Iterable[sqlite3.Row], out: Path) -> None:
    lines: List[str] = [
        "// AUTOGENERATED - do not edit",
        "use std::collections::BTreeMap;",
        "",
        "pub fn token_registry() -> BTreeMap<&'static str, &'static str> {",
        "    let mut map = BTreeMap::new();",
    ]
    for row in records:
        const_name = re.sub(r"[^A-Za-z0-9_]", "_", row["slug"].upper())
        lines.append(f'    map.insert("{const_name}", r#"{row["tokens_contract"]}"#);')
    lines.extend(["    map", "}", ""])
    text = "\n".join(lines) + "\n"
    out.write_text(text, encoding="utf-8")
    print(f"wrote tokens.rs ({token_sha(text.encode('utf-8'))})")


def do_export(args: argparse.Namespace) -> None:
    out = Path(args.out).resolve()
    ensure_artifacts_root(out)
    con = connect(Path(args.db))
    if args.environment == "test":
        allowed = ("canonical", "candidate")
    else:
        allowed = ("canonical",)

    placeholders = ",".join(["?"] * len(allowed))
    objects = con.execute(
        f"""
        SELECT * FROM registry_objects
        WHERE status IN ({placeholders})
        ORDER BY stable_id, version
        """,
        allowed,
    ).fetchall()

    registry = []
    for row in objects:
        renderers = [
            r["renderer_name"] for r in con.execute(
                "SELECT renderer_name FROM registry_object_renderers WHERE object_id = ?",
                (row["id"],),
            ).fetchall()
        ]
        item = dict(row)
        item["renderers"] = renderers
        item["artifact_id"] = row["id"]
        registry.append(item)

    proof_rows = con.execute(
        f"""
        SELECT p.*
        FROM proofs p
        JOIN registry_objects ro ON ro.id = p.object_id
        WHERE ro.status IN ({",".join(["?"] * len(allowed))})
        ORDER BY p.created_at DESC
        """,
        allowed,
    ).fetchall()
    proofs = [dict(r) for r in proof_rows]

    registry_path = out / "registry.json"
    proof_path = out / "proof-manifest.json"
    token_path = out / "tokens.rs"
    proof_dir = out / "proofs"
    token_quarks = [r for r in objects if r["object_type"] == "quark"]
    recipes = [r for r in objects if r["object_type"] == "recipe"]

    write_json(registry_path, registry)
    export_tokens_rs(token_quarks, token_path)

    for row in recipes:
        ext = ".ron" if args.recipe_format == "ron" else ".json"
        path = out / "recipes" / f"{normalize_file_base(row['slug'])}{ext}"
        if args.recipe_format == "ron":
            path.write_text(python_dict_to_ron(dict(row)), encoding="utf-8")
        else:
            write_json(path, dict(row))
        print(f"wrote recipe: {path}")

    copied_proofs = []
    for row in proofs:
        src = Path(row["screenshot_path"])
        if src.exists():
            target = proof_dir / src.name
            target.write_bytes(src.read_bytes())
            copied_proofs.append({"source": str(src), "target": str(target.relative_to(out))})

    write_json(proof_path, {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "environment": args.environment,
        "count": len(proofs),
        "proofs": proofs,
    })

    doc_lines = [
        "# Registry export",
        "",
        f"Generated for environment: {args.environment}",
        f"Total consumable objects: {len(objects)}",
        f"Quarks: {len([r for r in objects if r['object_type'] == 'quark'])}",
        f"Atoms: {len([r for r in objects if r['object_type'] == 'atom'])}",
        f"Molecules: {len([r for r in objects if r['object_type'] == 'molecule'])}",
        f"Recipes: {len([r for r in objects if r['object_type'] == 'recipe'])}",
        "",
        "## Exports",
        "- registry.json",
        "- tokens.rs",
        "- recipes/*.json",
        "- proof-manifest.json",
        "- registry-manifest.json",
        "",
        "## Status policy",
        "- production: canonical only",
        "- test: canonical + candidate",
    ]
    (out / "docs" / "catalog.md").write_text("\n".join(doc_lines) + "\n", encoding="utf-8")

    def sha256_file(path: Path) -> str:
        return token_sha(path.read_bytes())

    def as_manifest_entry(path: Path) -> dict:
        return {"path": str(path.relative_to(out)), "sha256": sha256_file(path)}

    manifest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "package_version": args.package_version,
        "environment": args.environment,
        "allowed_statuses": allowed,
        "counts_by_status": {s: 0 for s in ("canonical", "candidate", "deprecated", "retired", "lab", "draft")},
        "files": [
            as_manifest_entry(registry_path),
            as_manifest_entry(token_path),
            as_manifest_entry(proof_path),
        ],
        "proof_copies": copied_proofs,
    }
    for status in ("canonical", "candidate", "deprecated", "retired", "lab", "draft"):
        manifest["counts_by_status"][status] = len([o for o in objects if o["status"] == status])
    recipe_glob = "*.ron" if args.recipe_format == "ron" else "*.json"
    for recipe_file in sorted((out / "recipes").glob(recipe_glob)):
        manifest["files"].append(as_manifest_entry(recipe_file))
    for proof_file in sorted((out / "docs").glob("*.md")):
        manifest["files"].append(as_manifest_entry(proof_file))
    for copied in copied_proofs:
        manifest["files"].append({"path": copied["target"], "sha256": sha256_file(proof_dir / Path(copied["target"]).name)})

    manifest["file_count"] = len(manifest["files"])
    write_manifest(out / "registry-manifest.json", manifest)
    print(f"export complete: {out}")


def python_dict_to_ron(payload: Dict[str, Any], indent: int = 0) -> str:
    pad = "  " * indent
    if isinstance(payload, dict):
        body = []
        for key, value in payload.items():
            body.append(f'{pad}  {key}: {python_dict_to_ron(value, indent + 1)}')
        inner = ",\n".join(body)
        return "{" + (f"\n{inner}\n{pad}" if inner else "") + "}"
    if isinstance(payload, list):
        if not payload:
            return "[]"
        items = [python_dict_to_ron(v, indent + 1) for v in payload]
        return "[" + ", ".join(items) + "]"
    if isinstance(payload, str):
        return json.dumps(payload)
    if isinstance(payload, bool):
        return "true" if payload else "false"
    if payload is None:
        return "None"
    return str(payload)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Strict canonical registry tool")
    p.add_argument("--db", default=str((ROOT.parent / "registry-catalog.db").resolve()))

    sub = p.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize sqlite database")
    init.set_defaults(func=do_init)

    st = sub.add_parser("status", help="show status distribution")
    st.set_defaults(func=lambda args: do_status(connect(Path(args.db))))

    add = sub.add_parser("add-object", help="create one registry object revision")
    add.add_argument("--type", required=True, choices=["quark", "atom", "molecule", "recipe", "engine", "proof", "fork"])
    add.add_argument("--slug", required=True)
    add.add_argument("--name", required=True)
    add.add_argument(
        "--source-authority",
        required=True,
        choices=["ZIP9/Central", "spec-doc", "screenshot", "runtime", "mixed"],
    )
    add.add_argument("--schema-version", default="1.0.0")
    add.add_argument("--status", default="draft")
    add.add_argument("--stable-id")
    add.add_argument("--version", type=int)
    add.add_argument("--parent-stable-id")
    add.add_argument("--parent-version", type=int)
    add.add_argument("--geometry", default="{}")
    add.add_argument("--tokens", default="{}")
    add.add_argument("--states", default="{}")
    add.add_argument("--behaviors", default="{}")
    add.add_argument("--telemetry", default="{}")
    add.add_argument("--constraints", default="{}")
    add.add_argument("--payload", default="{}")
    add.add_argument("--renderers", default="[]")
    add.add_argument("--created-by", default="agent")
    add.add_argument("--authority-notes", default="")
    add.set_defaults(func=do_add_object)

    addp = sub.add_parser("add-proof", help="attach proof artifact to an object version")
    addp.add_argument("--object-id", required=True)
    addp.add_argument("--version", type=int)
    addp.add_argument("--renderer", required=True)
    addp.add_argument("--evidence-type", default="full")
    addp.add_argument("--screenshot", required=True)
    addp.add_argument("--hash", required=True)
    addp.add_argument("--diff-hash")
    addp.add_argument("--diff-payload", default="{}")
    addp.add_argument("--behavior-payload", default="{}")
    addp.add_argument("--telemetry-payload", default="{}")
    addp.add_argument("--created-by", default="agent")
    addp.set_defaults(func=do_add_proof)

    rel = sub.add_parser("link-relation", help="link parent->child graph edges")
    rel.add_argument("--parent", required=True)
    rel.add_argument("--child", required=True)
    rel.add_argument("--relation", required=True, default="uses")
    rel.add_argument("--rationale")
    rel.set_defaults(func=do_link_relation)

    fork = sub.add_parser("fork", help="fork a revision into a new lab/candidate variant")
    fork.add_argument("--object-id", required=True)
    fork.add_argument("--reason", required=True)
    fork.add_argument("--delta", default="{}")
    fork.add_argument("--state", default="lab", choices=["lab", "candidate"])
    fork.add_argument("--proof-before")
    fork.add_argument("--proof-after")
    fork.add_argument("--decision", default="")
    fork.add_argument("--created-by", default="agent")
    fork.set_defaults(func=do_fork)

    prom = sub.add_parser("promote", help="run promotion checks and set status")
    prom.add_argument("--object-id", required=True)
    prom.add_argument("--to-status", required=True, choices=["draft", "lab", "candidate", "canonical", "deprecated", "retired"])
    prom.add_argument("--requested-by", required=True)
    prom.add_argument(
        "--source-authority",
        default=None,
        choices=["ZIP9/Central", "spec-doc", "screenshot", "runtime", "mixed"],
    )
    prom.add_argument("--reviewer", default="pending")
    prom.add_argument("--reason", default="")
    prom.add_argument("--check", action="append", choices=["geometry", "tokens", "states", "behavior", "renderers", "proof", "source_authority"])
    prom.add_argument("--strict", action="store_true", default=True, help="enforce strict protocol checks (state/behavior required keys)")
    prom.add_argument("--force")
    prom.add_argument("--allow-duplicate", action="store_true", help="allow same slug/type duplicate on candidate/canonical promotion")
    prom.set_defaults(func=do_promote)

    exp = sub.add_parser("export", help="export renderable artifacts")
    exp.add_argument("--environment", required=True, choices=["test", "production"])
    exp.add_argument("--out", required=True)
    exp.add_argument("--recipe-format", choices=["json", "ron"], default="json")
    exp.add_argument("--package-version", default=datetime.now(timezone.utc).strftime("%Y%m%d.%H%M%S"))
    exp.set_defaults(func=do_export)

    ins = sub.add_parser("inspect", help="inspect object lineage, relations, proofs, forks")
    ins.add_argument("--object-id", required=True, help="object id or stable_id")
    ins.add_argument("--json", action="store_true", help="emit full JSON payload")
    ins.set_defaults(func=do_inspect)
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
