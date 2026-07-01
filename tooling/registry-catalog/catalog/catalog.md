# RTTC Catalog (ZIP9-anchored)

Generated: 2026-07-01T03:43:08Z
Active criteria: active, candidate, canonical, validated
Recency cutoff: 2026-06-09 (last_activity >= this date, metadata-first unless --include-mtime-recent)
ZIP9 found: True
ZIP9 date: 2026-06-27

## Scope
- Total .rttc files: 30
- Active: 5
- Recent (last 21 days by default): 0
- Edits candidates (redesign + bugfix): 0

## Taxonomy

| kind | count |
|---|---:|
| atom | 1 |
| component | 10 |
| deprecated | 1 |
| molecule | 1 |
| motion | 14 |
| prototype | 2 |
| surface | 1 |

## Subcatalogs

- `components.motion`: 14 entries
- `components.motion.atoms`: 1 entries
- `components.motion.molecules`: 1 entries
- `components.root`: 4 entries
- `components.uikit`: 10 entries

## ZIP9-derived composition

- Motion atoms: 15
- Motion molecules: 12
- Context-menu molecule specs: 31
- Alignment ledger (Context):
  - Atoms keepable table rows: 24
  - Molecules keepable table rows: 16
  - Recipes keepable table rows: 8

### Motion composition (ZIP9) examples

| molecule_id | title | atom_refs |
|---|---|---|
| EmptySpaceStandard | EmptySpaceStandard | `A.04 (Mask reveal), A.02 (Scale), A.01 (Fade)` |
| EmptySpaceBranded | Gnu.In-Shell | `A.04 (Mask reveal), A.06 (Dither shift), A.01 (Fade)` |
| EmptySpaceRadial | EmptySpaceRadial | `A.02 (Scale), slice-stagger` |
| WidgetInline | Clock | `A.04 (Mask reveal), A.01 (Fade)` |
| WidgetCard | WidgetCard | `A.04 (Mask reveal), A.03 (Translate · Y-lift)` |
| WidgetPills | WidgetPills | `pill-stagger 8ms, A.12 (Magnetic snap)` |
| WindowStandard | WindowStandard | `A.04 (Mask reveal), A.01 (Fade)` |
| WindowTileDiagram | WindowTileDiagram | `A.04 (Mask reveal), tile-hover` |
| WindowCompact | WindowCompact | `A.04 (Mask reveal), A.12 (Magnetic snap)` |
| NestedCascade | NestedCascade | `A.04 (Mask reveal), connector-arc` |
| NestedDrill | NestedDrill | `A.03 (Translate · Y-lift), crumb-fade` |
| NestedMegaPanel | NestedMegaPanel | `A.04 (Mask reveal), column-stagger` |
| … | … | + 19 molécules restantes |

- Motion composition unresolved references: 22.
- Missing atom IDs in motion graph are mostly legacy/inline tokenized references from older exports.

## DB-like evolution (per component)

Projection of the RTTC scan into the registry DB vocabulary (`schema/registry_schema.sql`): stable_id, version, source_authority, parent, lifecycle status. Full table in `catalog/db_evolution.md`; structured data in `catalog/rttc_db_evolution.json` / `catalog/db_evolution.csv`.

- Components: 30
- Revision rows: 30
- Parent links resolved / unresolved: 10 / 20
- Multi-version components: 0
- promotion_state: candidate=4, canonical=1, deprecated=3, draft=22
- source_authority: -=6, runtime=4, spec-doc=20

## Catalogue snapshots

### Recent items
| relative | status | edit_scope | last_activity | activity_source | created | updated | kind | taxonomy |
|---|---|---|---|---|---|---|---|---|

### Filter snapshot
```
active_count=5
recent_count=0
bugfix_like_edits=0
redesign_edits=0
```
