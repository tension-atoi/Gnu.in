# Registry Catalog (data process only)

This is an isolated data tool for a canonical registry.
It is purpose-built to avoid the "copy/paste snippets folder" failure mode.

## What this gives you

- Typed central registry in SQLite (`schema/registry_schema.sql`)
- strict lifecycle and anti-pollution controls
- fork lineages
- promotion audits with explicit checks and reviewer metadata
- frozen export package for renderer consumption

Runtime reads remain clean: only exported artifacts, never raw DB.

## Lifecycle

`draft -> lab -> candidate -> canonical -> deprecated -> retired`

A renderer can only consume:

- `candidate` in test environments
- `canonical` only in production exports

## Promotion gates (default)

- `candidate`: `geometry + tokens + states + behavior + renderers + proof`
- `canonical`: same gate set as `candidate`
- `--reviewer` is required for `candidate` and `canonical`
- duplicate `slug/type` in (`candidate`, `canonical`) is blocked unless
  `--allow-duplicate` is used

## Quick start

```bash
cd /home/tension_atoi/Projects/Gnu.in/tooling/registry-catalog
python3 scripts/registry_tool.py --db ../registry-catalog.db init
```

You can also bootstrap a complete test catalog:

```bash
python3 scripts/seed_demo.py --db /tmp/registry-catalog.db --proof-root /tmp/registry-proof
```

### View DB quickly

```bash
./scripts/view_registry.sh /tmp/registry-catalog-demo-enriched.db
```

Or for interactive SQL:

```bash
sqlite3 /tmp/registry-catalog-demo-enriched.db
```

### Add canonical-ready quark example

```bash
python3 scripts/registry_tool.py --db ../registry-catalog.db add-object \
  --type quark \
  --slug color/neutral-100 \
  --name neutral_100 \
  --source-authority ZIP9/Central \
  --status draft \
  --geometry '{"radius":{"s":1,"m":2}}' \
  --tokens '{"name":"neutral-100","hex":"#f5f5f5","alpha":1.0}' \
  --states '{"hover":false,"pressed":false,"focus":false,"disabled":false,"active":false}' \
  --behaviors '{"timers":{},"input":"mouse","animation":"linear","telemetry":true}' \
  --renderers '["RustRenderer","GPUI","simulator","QML","web-preview"]'
```

### Attach proof

```bash
python3 scripts/registry_tool.py --db ../registry-catalog.db add-proof \
  --object-id <OBJECT_ID> \
  --version 1 \
  --renderer RustRenderer \
  --screenshot /tmp/proof-neutral-100.png \
  --hash sha256:... \
  --diff-hash sha256:... \
  --diff-payload '{}' \
  --behavior-payload '{}' \
  --telemetry-payload '{}'
```

### Promote

```bash
python3 scripts/registry_tool.py --db ../registry-catalog.db promote \
  --object-id <OBJECT_ID> \
  --to-status canonical \
  --strict \
  --requested-by design-lead \
  --reviewer qa-agent \
  --reason "Stable geometry + tokens + states + behavior + renderer support + proof"
```

`--strict` enforces:
- presence of `geometry`, `tokens`, `states`, `behavior`, `renderers`, `proof`
- full state keys: `hover`, `pressed`, `focus`, `disabled`, `active`
- full behavior keys: `timers`, `input`, `animation`, `telemetry`
- `source_authority` in one of `ZIP9/Central`, `spec-doc`, `screenshot`, `runtime`, `mixed`

### Enriched seed dataset

`seed_demo.py` now generates a richer canonical starter set:

- 7 quarks (`color`, `radius`, `spacing`, `font`, `easing`, `shadow`, etc.)
- 7 atoms (`button`, `icon`, `badge`, `track`, `glyph`, `surface`)
- 5 molecules (`notification`, `menu`, `control-row`, `control-group`)
- 4 recipes (`surface/osd-control`, `surface/control-bar`, `menu/top-strip`, `surface/panelized`)
- 5 engines (`RustRenderer`, `GPUI`, `simulator`, `QML`, `web-preview`)

It also populates object tags, relations, proofs, then promotes atoms/molecules/recipes to `canonical`.

```bash
python3 scripts/seed_demo.py --db /tmp/registry-catalog.db --proof-root /tmp/registry-proof
```

### Audit SQL

Run built-in checks and object graph introspection:

```bash
sqlite3 /tmp/registry-catalog.db < sql/quality_audit.sql
```

### Fork and iterate

```bash
python3 scripts/registry_tool.py --db ../registry-catalog.db fork \
  --object-id <STABLE_OR_OBJECT_ID> \
  --reason "Refine hover response on notification surface" \
  --state lab \
  --delta '{"animation":"spring"}' \
  --proof-before proof-before-id \
  --proof-after proof-after-id \
  --decision "Candidate once visual diff and interaction diff pass"
```

### Inspect lineage

```bash
python3 scripts/registry_tool.py --db ../registry-catalog.db inspect \
  --object-id <STABLE_OR_OBJECT_ID> \
  --json
```

### Export frozen package

```bash
python3 scripts/registry_tool.py --db ../registry-catalog.db export \
  --out /tmp/registry-artifacts \
  --environment test
```

`environment test` exports `canonical` + `candidate`.
`environment production` exports only `canonical`.

The package contains:

- `registry.json`
- `tokens.rs`
- `recipes/*.json`
- `proof-manifest.json`
- `registry-manifest.json`
- `docs/catalog.md`

## Data model

- `registry_objects`: canonical object rows with stable id + version + contracts
- `status_history`: full status change history
- `lifecycle_transitions`: transition matrix constraints
- `object_relations`: graph links (`quark -> atom -> molecule -> recipe`)
- `proofs`: evidence (screenshot + hashes + behavior + telemetry)
- `fork_attempts`: experimental lineage (`component_id`, `parent_version`, `reason`, `delta`, `proof_*`, `decision`)
- `promotion_attempts` + `promotion_checks`: mandatory structured reviews
- `renderers` / `registry_object_renderers`: renderer compatibility matrix

## Files

- `schema/registry_schema.sql`: full schema and constraints
- `scripts/registry_tool.py`: data-only CLI + promotion/export pipeline
- `sql/graph_quark_to_recipe.sql`: canonical object graph extractor
- `sql/status_matrix.sql`: status matrix by object type
