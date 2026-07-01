PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS lifecycle_statuses (
  status TEXT PRIMARY KEY CHECK(status IN ('draft', 'lab', 'candidate', 'canonical', 'deprecated', 'retired'))
);

INSERT INTO lifecycle_statuses(status)
VALUES ('draft'), ('lab'), ('candidate'), ('canonical'), ('deprecated'), ('retired')
ON CONFLICT(status) DO NOTHING;

CREATE TABLE IF NOT EXISTS lifecycle_transitions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_status TEXT NOT NULL REFERENCES lifecycle_statuses(status),
  to_status TEXT NOT NULL REFERENCES lifecycle_statuses(status),
  description TEXT NOT NULL,
  UNIQUE(from_status, to_status)
);

INSERT INTO lifecycle_transitions(from_status, to_status, description)
VALUES
  ('draft', 'lab', 'Work in progress in authoring zone'),
  ('lab', 'candidate', 'Ready for targeted review and test'),
  ('candidate', 'canonical', 'Approved for production runtime consumption'),
  ('candidate', 'deprecated', 'Rejected from promotion candidate path'),
  ('canonical', 'deprecated', 'Superseded or behavior risk detected'),
  ('deprecated', 'retired', 'Fully retired and blocked for runtime use'),
  ('canonical', 'retired', 'Hard retirement from canonical use'),
  ('retired', 'draft', 'Re-open only via explicit new revision')
ON CONFLICT(from_status, to_status) DO NOTHING;

CREATE TABLE IF NOT EXISTS object_types (
  object_type TEXT PRIMARY KEY
);

INSERT INTO object_types(object_type)
VALUES ('quark'), ('atom'), ('molecule'), ('recipe'), ('engine'), ('proof'), ('fork')
ON CONFLICT(object_type) DO NOTHING;

CREATE TABLE IF NOT EXISTS source_authorities (
  source_authority TEXT PRIMARY KEY,
  description TEXT DEFAULT ''
);

INSERT INTO source_authorities(source_authority, description)
VALUES
  ('ZIP9/Central', 'Primary design source authority'),
  ('spec-doc', 'Design/specification source document'),
  ('screenshot', 'Derived from rendered screenshot evidence'),
  ('runtime', 'Derived from existing runtime behavior'),
  ('mixed', 'Multi-origin composite')
ON CONFLICT(source_authority) DO NOTHING;

CREATE TABLE IF NOT EXISTS check_types (
  check_type TEXT PRIMARY KEY
);

INSERT INTO check_types(check_type)
VALUES
  ('geometry'),
  ('tokens'),
  ('states'),
  ('behavior'),
  ('renderers'),
  ('renderer_support'),
  ('source_authority'),
  ('proof')
ON CONFLICT(check_type) DO NOTHING;

CREATE TABLE IF NOT EXISTS registry_objects (
  id TEXT PRIMARY KEY,
  stable_id TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  object_type TEXT NOT NULL REFERENCES object_types(object_type),
  slug TEXT NOT NULL,
  display_name TEXT NOT NULL,
  source_authority TEXT NOT NULL REFERENCES source_authorities(source_authority),
  schema_version TEXT NOT NULL DEFAULT '1.0.0',
  status TEXT NOT NULL DEFAULT 'draft' REFERENCES lifecycle_statuses(status),
  geometry_contract TEXT NOT NULL DEFAULT '{}',
  tokens_contract TEXT NOT NULL DEFAULT '{}',
  state_contract TEXT NOT NULL DEFAULT '{}',
  behavior_contract TEXT NOT NULL DEFAULT '{}',
  telemetry_contract TEXT NOT NULL DEFAULT '{}',
  constraints_contract TEXT NOT NULL DEFAULT '{}',
  payload JSON NOT NULL DEFAULT '{}',
  authority_notes TEXT DEFAULT '',
  parent_stable_id TEXT DEFAULT NULL,
  parent_version INTEGER DEFAULT NULL,
  created_by TEXT DEFAULT 'unknown',
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(stable_id, version),
  CHECK (version > 0),
  CHECK (json_valid(geometry_contract)),
  CHECK (json_valid(tokens_contract)),
  CHECK (json_valid(state_contract)),
  CHECK (json_valid(behavior_contract)),
  CHECK (json_valid(telemetry_contract)),
  CHECK (json_valid(constraints_contract)),
  CHECK (json_valid(payload))
);

CREATE INDEX IF NOT EXISTS idx_registry_objects_type_status
ON registry_objects(object_type, status);

CREATE INDEX IF NOT EXISTS idx_registry_objects_stable
ON registry_objects(stable_id, version);

CREATE TABLE IF NOT EXISTS status_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  object_id TEXT NOT NULL REFERENCES registry_objects(id) ON DELETE CASCADE,
  from_status TEXT NOT NULL REFERENCES lifecycle_statuses(status),
  to_status TEXT NOT NULL REFERENCES lifecycle_statuses(status),
  reason TEXT DEFAULT '',
  decided_by TEXT DEFAULT 'unknown',
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS renderers (
  renderer_name TEXT PRIMARY KEY,
  engine_layer TEXT NOT NULL,
  supports_simulation INTEGER NOT NULL DEFAULT 0,
  supports_raster INTEGER NOT NULL DEFAULT 0,
  notes TEXT DEFAULT ''
);

INSERT INTO renderers(renderer_name, engine_layer, supports_simulation, supports_raster, notes)
VALUES
  ('RustRenderer', 'native', 0, 1, 'Rust native renderer lane'),
  ('GPUI', 'native', 0, 1, 'GPUI native lane'),
  ('simulator', 'tooling', 1, 0, 'Offline behavior simulator'),
  ('QML', 'qml', 1, 1, 'Legacy QML surface lane'),
  ('web-preview', 'web', 1, 1, 'Preview in browser/web harness')
ON CONFLICT(renderer_name) DO NOTHING;

CREATE TABLE IF NOT EXISTS registry_object_renderers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  object_id TEXT NOT NULL REFERENCES registry_objects(id) ON DELETE CASCADE,
  renderer_name TEXT NOT NULL REFERENCES renderers(renderer_name),
  support_tier TEXT NOT NULL DEFAULT 'pilot' CHECK(support_tier IN ('pilot', 'supported', 'deprecated')),
  support_notes TEXT DEFAULT '',
  UNIQUE(object_id, renderer_name)
);

CREATE TABLE IF NOT EXISTS object_relations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  parent_id TEXT NOT NULL REFERENCES registry_objects(id) ON DELETE CASCADE,
  child_id TEXT NOT NULL REFERENCES registry_objects(id) ON DELETE CASCADE,
  relation_type TEXT NOT NULL DEFAULT 'uses',
  rationale TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(parent_id, child_id, relation_type)
);

CREATE TABLE IF NOT EXISTS object_tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  object_id TEXT NOT NULL REFERENCES registry_objects(id) ON DELETE CASCADE,
  tag TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(object_id, tag)
);

CREATE TABLE IF NOT EXISTS proofs (
  id TEXT PRIMARY KEY,
  object_id TEXT NOT NULL REFERENCES registry_objects(id) ON DELETE CASCADE,
  object_version INTEGER NOT NULL,
  renderer_name TEXT NOT NULL REFERENCES renderers(renderer_name),
  evidence_type TEXT NOT NULL DEFAULT 'full',
  screenshot_path TEXT NOT NULL,
  screenshot_hash TEXT NOT NULL,
  pixel_diff_hash TEXT DEFAULT '',
  pixel_diff_payload TEXT DEFAULT '{}',
  behavior_payload TEXT DEFAULT '{}',
  telemetry_payload TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  created_by TEXT DEFAULT 'unknown',
  CHECK (json_valid(pixel_diff_payload)),
  CHECK (json_valid(behavior_payload)),
  CHECK (json_valid(telemetry_payload)),
  UNIQUE(object_id, object_version, renderer_name, evidence_type)
);

CREATE TABLE IF NOT EXISTS fork_attempts (
  id TEXT PRIMARY KEY,
  component_id TEXT NOT NULL REFERENCES registry_objects(id) ON DELETE CASCADE,
  parent_version INTEGER NOT NULL,
  reason TEXT NOT NULL,
  delta_payload TEXT NOT NULL DEFAULT '{}',
  fork_state TEXT NOT NULL DEFAULT 'lab' CHECK(fork_state IN ('lab','candidate','canonical','deprecated','retired')),
  proof_before_id TEXT DEFAULT NULL REFERENCES proofs(id),
  proof_after_id TEXT DEFAULT NULL REFERENCES proofs(id),
  decision TEXT DEFAULT '',
  created_by TEXT DEFAULT 'unknown',
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  CHECK (json_valid(delta_payload))
);

CREATE TABLE IF NOT EXISTS promotion_attempts (
  id TEXT PRIMARY KEY,
  object_id TEXT NOT NULL REFERENCES registry_objects(id) ON DELETE CASCADE,
  from_status TEXT NOT NULL REFERENCES lifecycle_statuses(status),
  to_status TEXT NOT NULL REFERENCES lifecycle_statuses(status),
  requested_by TEXT NOT NULL,
  reviewer TEXT DEFAULT 'pending',
  decision TEXT DEFAULT 'pending' CHECK(decision IN ('pending','approved','rejected')),
  rationale TEXT DEFAULT '',
  geometry_ok INTEGER NOT NULL DEFAULT 0,
  tokens_ok INTEGER NOT NULL DEFAULT 0,
  states_ok INTEGER NOT NULL DEFAULT 0,
  behavior_ok INTEGER NOT NULL DEFAULT 0,
  renderers_ok INTEGER NOT NULL DEFAULT 0,
  proof_ok INTEGER NOT NULL DEFAULT 0,
  proofs_json TEXT DEFAULT '[]',
  requested_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  reviewed_at TEXT DEFAULT NULL,
  source_authority TEXT NOT NULL,
  CHECK (json_valid(proofs_json))
);

CREATE TABLE IF NOT EXISTS promotion_checks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  promotion_id TEXT NOT NULL REFERENCES promotion_attempts(id) ON DELETE CASCADE,
  check_type TEXT NOT NULL REFERENCES check_types(check_type),
  result INTEGER NOT NULL DEFAULT 0 CHECK(result IN (0,1)),
  details TEXT DEFAULT '',
  checked_by TEXT DEFAULT 'unknown',
  checked_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(promotion_id, check_type)
);

CREATE VIEW IF NOT EXISTS v_runtime_consumable AS
SELECT
  ro.id,
  ro.stable_id,
  ro.version,
  ro.object_type,
  ro.slug,
  ro.display_name,
  ro.status,
  ro.source_authority,
  ro.geometry_contract,
  ro.tokens_contract,
  ro.state_contract,
  ro.behavior_contract,
  ro.telemetry_contract,
  ro.payload
FROM registry_objects ro
WHERE ro.status IN ('canonical','candidate');

CREATE VIEW IF NOT EXISTS v_registry_quality AS
SELECT
  ro.id,
  ro.stable_id,
  ro.version,
  ro.object_type,
  ro.slug,
  ro.status,
  ro.source_authority,
  (ro.geometry_contract NOT IN ('{}','[]','""')) AS has_geometry,
  (ro.tokens_contract NOT IN ('{}','[]','""')) AS has_tokens,
  (ro.state_contract NOT IN ('{}','[]','""')) AS has_states,
  (ro.behavior_contract NOT IN ('{}','[]','""')) AS has_behavior,
  (
    SELECT 1
    FROM registry_object_renderers ror
    WHERE ror.object_id = ro.id
    LIMIT 1
  ) IS NOT NULL AS has_renderers,
  (
    SELECT 1
    FROM proofs p
    WHERE p.object_id = ro.id
      AND p.object_version = ro.version
    LIMIT 1
  ) IS NOT NULL AS has_proof,
  (
    json_object(
      'geometry', ro.geometry_contract,
      'tokens', ro.tokens_contract,
      'states', ro.state_contract,
      'behavior', ro.behavior_contract
    )
  ) AS contracts
FROM registry_objects ro;

CREATE VIEW IF NOT EXISTS v_candidate_ready AS
SELECT
  id,
  stable_id,
  version,
  object_type,
  slug,
  status,
  source_authority
FROM v_registry_quality
WHERE status = 'candidate';

CREATE TRIGGER IF NOT EXISTS trg_update_timestamp
AFTER UPDATE ON registry_objects
FOR EACH ROW
BEGIN
  UPDATE registry_objects
  SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_status_transition_guard
BEFORE UPDATE OF status ON registry_objects
BEGIN
  SELECT
    CASE
      WHEN NEW.status = OLD.status THEN
        RAISE(IGNORE)
      WHEN NOT EXISTS (
        SELECT 1
        FROM lifecycle_transitions t
        WHERE t.from_status = OLD.status
          AND t.to_status = NEW.status
      ) THEN
        RAISE(ABORT, 'invalid lifecycle transition')
    END;
END;
