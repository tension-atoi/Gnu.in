#!/usr/bin/env python3
"""
Seed a rich canonical registry dataset for a first-live verification pass.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List
from uuid import uuid4
import sqlite3

from registry_tool import connect, do_promote, load_schema, parse_json

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "registry_schema.sql"


def ensure_db(con: sqlite3.Connection) -> None:
    con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def insert_object(
    con: sqlite3.Connection,
    *,
    object_type: str,
    slug: str,
    name: str,
    source_authority: str,
    status: str,
    geometry: str,
    tokens: str,
    states: str,
    behaviors: str,
    renderers: List[str],
    stable_id: str | None = None,
    constraints: str | None = None,
    payload: str | None = None,
) -> str:
    object_id = str(uuid4())
    stable_id = stable_id or str(uuid4())
    con.execute(
        """
        INSERT INTO registry_objects (
          id, stable_id, version, object_type, slug, display_name, source_authority,
          schema_version, status, geometry_contract, tokens_contract, state_contract,
          behavior_contract, telemetry_contract, constraints_contract, payload
        ) VALUES (?, ?, 1, ?, ?, ?, ?, '1.0.0', ?, ?, ?, ?, ?, '{}', ?, '{}')
        """,
        (
            object_id,
            stable_id,
            object_type,
            slug,
            name,
            source_authority,
            status,
            parse_json(geometry),
            parse_json(tokens),
            parse_json(states),
            parse_json(behaviors),
            constraints or "{}",
        ),
    )
    for renderer in renderers:
        con.execute(
            """
            INSERT OR IGNORE INTO registry_object_renderers (
              object_id,
              renderer_name,
              support_tier,
              support_notes
            ) VALUES (?, ?, 'supported', '')
            """,
            (object_id, renderer),
        )
    if payload:
        con.execute(
            "UPDATE registry_objects SET payload = ? WHERE id = ?",
            (parse_json(payload), object_id),
        )
    return object_id


def insert_tags(con: sqlite3.Connection, object_id: str, tags: List[str]) -> None:
    for tag in tags:
        con.execute(
            "INSERT OR IGNORE INTO object_tags (object_id, tag) VALUES (?, ?)",
            (object_id, tag),
        )


def insert_proof(
    con: sqlite3.Connection,
    object_id: str,
    object_version: int,
    screenshot: Path,
    renderer: str,
    created_by: str,
    evidence_type: str = "full",
) -> str:
    proof_id = str(uuid4())
    screenshot.parent.mkdir(parents=True, exist_ok=True)
    if not screenshot.exists():
        screenshot.write_text(f"seed proof placeholder for {object_id}", encoding="utf-8")
    con.execute(
        """
        INSERT OR REPLACE INTO proofs (
          id, object_id, object_version, renderer_name, evidence_type,
          screenshot_path, screenshot_hash, pixel_diff_hash, pixel_diff_payload,
          behavior_payload, telemetry_payload, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, '', '{}', '{}', '{}', ?)
        """,
        (
            proof_id,
            object_id,
            object_version,
            renderer,
            evidence_type,
            str(screenshot),
            sha256_file(screenshot),
            created_by,
        ),
    )
    return proof_id


def insert_relation(con: sqlite3.Connection, parent_id: str, child_id: str, relation_type: str = "uses", rationale: str = "") -> None:
    con.execute(
        """
        INSERT OR IGNORE INTO object_relations (parent_id, child_id, relation_type, rationale)
        VALUES (?, ?, ?, ?)
        """,
        (parent_id, child_id, relation_type, rationale),
    )


def promote_to(con: sqlite3.Connection, db_path: Path, object_id: str, target: str) -> None:
    args = SimpleNamespace(
        object_id=object_id,
        db=str(db_path),
        to_status=target,
        requested_by="seed-demo",
        source_authority=None,
        reviewer="seed-demo",
        reason=f"seed pipeline bootstrap -> {target}",
        check=None,
        force="1",
        allow_duplicate=True,
        strict=True,
    )
    do_promote(args)


def do_seed(args: argparse.Namespace) -> None:
    db_path = Path(args.db).resolve()
    con = connect(db_path)
    ensure_db(con)

    proof_root = Path(args.proof_root).resolve()
    proof_root.mkdir(parents=True, exist_ok=True)

    # -------- Quarks --------
    quark_rows: Dict[str, str] = {}
    quarks = [
        ("color/neutral-100", "neutral_100", '{"r":245,"g":245,"b":245,"alpha":1}', '{"hex":"#f5f5f5","name":"neutral-100"}'),
        ("color/neutral-900", "neutral_900", '{"r":17,"g":24,"b":39,"alpha":1}', '{"hex":"#111827","name":"neutral-900"}'),
        ("radius/small", "radius_small", '{"radius":{"s":2,"m":4}}', '{"value":4,"unit":"px","scale":"small"}'),
        ("spacing/compact", "spacing_compact", '{"horizontal":8,"vertical":6,"unit":"px"}', '{"value":8,"unit":"px","scale":"compact"}'),
        ("easing/standard", "easing_standard", '{"curve":"cubic-bezier","x1":0.22,"y1":1,"x2":0.36,"y2":1}', '{"curve":"ease-out","curve_id":"standard"}'),
        ("font/primary-body", "font_primary_body", '{"size":14,"weight":"400","leading":1.4}', '{"family":"Inter","size":14,"weight":400}'),
        ("shadow/surface-soft", "shadow_soft", '{"x":0,"y":1,"blur":2,"color":"#00000022"}', '{"radius":4,"spread":0,"opacity":0.14}'),
    ]

    for slug, name, geometry, tokens in quarks:
        obj = insert_object(
            con,
            object_type="quark",
            slug=slug,
            name=name,
            source_authority="ZIP9/Central",
            status="canonical",
            geometry=geometry,
            tokens=tokens,
            states='{"hover":false,"pressed":false,"focus":false,"disabled":false,"active":false}',
            behaviors='{"timers":{"default":16},"input":"state-only","animation":"none","telemetry":true}',
            renderers=["RustRenderer", "GPUI", "web-preview"],
            constraints='{}',
            payload='{}',
        )
        quark_rows[slug] = obj

    # -------- Atoms --------
    atom_rows: Dict[str, str] = {}
    atoms = [
        ("button/primary", "button_primary", '{"radius":{"s":4},"padding":{"x":12,"y":7},"min-height":32}', '{"font":"Inter","font-size":14,"fg":"#ffffff","bg":"#111827","radius":"radius-small"}'),
        ("button/secondary", "button_secondary", '{"radius":{"s":4},"padding":{"x":12,"y":7},"min-height":32}', '{"font":"Inter","font-size":14,"fg":"#111827","bg":"#f5f5f5","radius":"radius-small"}'),
        ("icon/close", "icon_close", '{"size":16,"stroke":1.5}', '{"glyph":"x","size":16,"alpha":1}'),
        ("badge/info", "badge_info", '{"radius":999,"padding":{"x":8,"y":2}}', '{"label":"info","bg":"#1d4ed8","fg":"#ffffff"}'),
        ("track/volume", "track_volume", '{"height":6,"radius":999}', '{"track":"#E5E7EB","fill":"#111827"}'),
        ("glyph/arrow-right", "glyph_arrow_right", '{"size":12}', '{"unicode":"U+2192","size":12,"weight":"medium"}'),
        ("surface/panel", "surface_panel", '{"radius":6,"padding":10}', '{"bg":"#ffffff","border":"#e5e7eb"}'),
    ]

    for slug, name, geometry, tokens in atoms:
        obj = insert_object(
            con,
            object_type="atom",
            slug=slug,
            name=name,
            source_authority="ZIP9/Central",
            status="draft",
            geometry=geometry,
            tokens=tokens,
            states='{"hover":false,"pressed":false,"focus":false,"disabled":false,"active":false}',
            behaviors='{"timers":{"default":120,"hover":16},"input":"mouse","animation":"ease-out","telemetry":true}',
            renderers=["RustRenderer", "GPUI", "web-preview", "simulator"],
            constraints='{}',
            payload='{}',
        )
        atom_rows[slug] = obj
        insert_tags(con, obj, ["interaction", "surface", slug.split("/")[0]])

    # -------- Molecules --------
    molecule_rows: Dict[str, str] = {}
    molecules = [
        ("notification/osd", "notification_row", '{"layout":"hbox","gap":8,"radius":10}', '{"bg":"surface-dark","icon":"icon:info","badge":"info"}'),
        ("notification/stack", "notification_stack", '{"layout":"vbox","gap":10}', '{"spacing":"compact","edge":"top"}'),
        ("menu/item", "menu_item", '{"layout":"hbox","gap":8}', '{"padding":"compact","height":28,"leading":"tight"}'),
        ("control-row", "control_row", '{"layout":"hstack","gap":6,"align":"center"}', '{"density":"compact"}'),
        ("control-group", "control_group", '{"layout":"vbox","gap":12}', '{"bg":"surface-soft","padding":"compact"}'),
    ]

    for slug, name, geometry, tokens in molecules:
        obj = insert_object(
            con,
            object_type="molecule",
            slug=slug,
            name=name,
            source_authority="ZIP9/Central",
            status="draft",
            geometry=geometry,
            tokens=tokens,
            states='{"hover":false,"pressed":false,"focus":false,"disabled":false,"active":false}',
            behaviors='{"timers":{"default":16,"dismiss":180},"input":"mouse-pointer","animation":"ease-in-out","telemetry":true}',
            renderers=["RustRenderer", "GPUI", "web-preview"],
            constraints='{}',
            payload='{}',
        )
        molecule_rows[slug] = obj

    # -------- Recipes --------
    recipe_rows: Dict[str, str] = {}
    recipes = [
        ("surface/osd-control", "osd_control_surface", '{"layout":"stack","spacing":8,"max-width":420}', '{"atoms":["button/primary","glyph/arrow-right","badge/info"],"molecules":["notification/osd","control-row"]}'),
        ("surface/control-bar", "control_bar_surface", '{"layout":"row","spacing":10}', '{"atoms":["button/primary","button/secondary","track/volume"],"molecules":["control-row"]}'),
        ("menu/top-strip", "top_menu_strip", '{"layout":"row","spacing":12}', '{"atoms":["menu/item","icon/close","glyph/arrow-right"],"molecules":["menu/item"]}'),
        ("surface/panelized", "panelized_surface", '{"layout":"vbox","spacing":12}', '{"atoms":["surface/panel","badge/info"],"molecules":["control-group","notification/stack"]}'),
    ]

    for slug, name, geometry, tokens in recipes:
        obj = insert_object(
            con,
            object_type="recipe",
            slug=slug,
            name=name,
            source_authority="ZIP9/Central",
            status="draft",
            geometry=geometry,
            tokens=tokens,
            states='{"hover":false,"pressed":false,"focus":false,"disabled":false,"active":false}',
            behaviors='{"timers":{"default":16,"reveal":24},"input":"mouse","animation":"ease-in-out","telemetry":true}',
            renderers=["RustRenderer", "GPUI", "web-preview", "simulator"],
            constraints='{}',
            payload='{}',
        )
        recipe_rows[slug] = obj

    # -------- Engines --------
    engines: Dict[str, str] = {}
    engine_specs = [
        (
            "engine/rust-native",
            "RustRenderer",
            "runtime",
            '{"layer":"runtime","renderer":"RustRenderer"}',
            '{"runtime":"rust","backend":"native"}',
            ["RustRenderer"],
        ),
        (
            "engine/gpui",
            "GPUI",
            "runtime",
            '{"layer":"native","renderer":"GPUI"}',
            '{"runtime":"gpui","backend":"native"}',
            ["GPUI"],
        ),
        (
            "engine/simulator",
            "simulator",
            "runtime",
            '{"layer":"tooling","renderer":"simulator"}',
            '{"mode":"sim","backend":"tooling"}',
            ["simulator"],
        ),
        (
            "engine/qml",
            "QML",
            "runtime",
            '{"layer":"qml","renderer":"QML"}',
            '{"engine":"qml","backend":"qml"}',
            ["QML"],
        ),
        (
            "engine/web-preview",
            "web-preview",
            "runtime",
            '{"layer":"web","renderer":"web-preview"}',
            '{"engine":"web-preview","backend":"web"}',
            ["web-preview"],
        ),
    ]

    for slug, name, auth, geometry, tokens, renderers in engine_specs:
        engines[slug] = insert_object(
            con,
            object_type="engine",
            slug=slug,
            name=name,
            source_authority=auth,
            status="canonical",
            geometry=geometry,
            tokens=tokens,
            states='{"hover":false,"pressed":false,"focus":false,"disabled":false,"active":false}',
            behaviors='{"timers":{"default":16},"input":"any","animation":"none","telemetry":true}',
            renderers=renderers,
            constraints='{}',
            payload='{}',
        )

    # ---------- Relations ----------
    insert_relation(con, atom_rows["button/primary"], quark_rows["color/neutral-900"])
    insert_relation(con, atom_rows["button/primary"], quark_rows["radius/small"])
    insert_relation(con, atom_rows["button/primary"], quark_rows["spacing/compact"])
    insert_relation(con, atom_rows["button/secondary"], quark_rows["color/neutral-100"])
    insert_relation(con, atom_rows["badge/info"], quark_rows["color/neutral-900"])
    insert_relation(con, atom_rows["surface/panel"], quark_rows["shadow/surface-soft"])
    insert_relation(con, atom_rows["track/volume"], quark_rows["easing/standard"])

    insert_relation(con, molecule_rows["notification/osd"], atom_rows["button/primary"])
    insert_relation(con, molecule_rows["notification/osd"], atom_rows["icon/close"])
    insert_relation(con, molecule_rows["menu/item"], atom_rows["glyph/arrow-right"])
    insert_relation(con, molecule_rows["control-row"], atom_rows["surface/panel"])
    insert_relation(con, molecule_rows["control-group"], molecule_rows["control-row"])
    insert_relation(con, molecule_rows["notification/stack"], molecule_rows["notification/osd"])

    insert_relation(con, recipe_rows["surface/osd-control"], molecule_rows["notification/osd"])
    insert_relation(con, recipe_rows["surface/osd-control"], molecule_rows["control-row"])
    insert_relation(con, recipe_rows["surface/control-bar"], atom_rows["button/secondary"])
    insert_relation(con, recipe_rows["menu/top-strip"], molecule_rows["menu/item"])
    insert_relation(con, recipe_rows["menu/top-strip"], atom_rows["icon/close"])
    insert_relation(con, recipe_rows["surface/panelized"], molecule_rows["notification/stack"])
    insert_relation(con, recipe_rows["surface/panelized"], atom_rows["surface/panel"])

    # ---------- Proofs ----------
    proof_renderer = {
        "engine/rust-native": "RustRenderer",
        "engine/gpui": "GPUI",
        "engine/simulator": "simulator",
        "engine/qml": "QML",
        "engine/web-preview": "web-preview",
    }

    for slug, obj in {
        **atom_rows,
        **quark_rows,
        **molecule_rows,
        **recipe_rows,
        **engines,
    }.items():
        insert_proof(
            con,
            obj,
            1,
            proof_root / f"{slug.replace('/', '_')}.txt",
            renderer=proof_renderer.get(slug, "GPUI"),
            created_by="seed-demo",
        )

    con.commit()

    # ---------- Promotion funnel ----------
    for obj in list(atom_rows.values()) + list(molecule_rows.values()) + list(recipe_rows.values()):
        promote_to(con, db_path, obj, "lab")
        promote_to(con, db_path, obj, "candidate")
        promote_to(con, db_path, obj, "canonical")

    # Quarks already canonical in seed, as immutable design primitives.
    # Engines canonical.
    print(f"seeded enriched registry at {db_path}")
    print(f"quarks={len(quark_rows)} atoms={len(atom_rows)} molecules={len(molecule_rows)} recipes={len(recipe_rows)} engines={len(engines)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed a rich demo registry dataset")
    parser.add_argument("--db", default=str((ROOT.parent / "registry-catalog.db").resolve()))
    parser.add_argument("--proof-root", default=str((ROOT / "artifacts" / "seed-proofs").resolve()))
    args = parser.parse_args()
    do_seed(args)


if __name__ == "__main__":
    main()
