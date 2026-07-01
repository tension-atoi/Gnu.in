#!/usr/bin/env bash
set -euo pipefail

DB_PATH="${1:-/tmp/registry-catalog-demo-enriched.db}"

if [[ ! -f "$DB_PATH" ]]; then
  echo "Database not found: $DB_PATH" >&2
  echo "Usage: $0 <path-to-db>" >&2
  exit 1
fi

if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "sqlite3 is required but not installed." >&2
  exit 1
fi

printf "Using DB: %s\n" "$DB_PATH"
echo "=== Object counts by type/status ==="
sqlite3 "$DB_PATH" <<'SQL'
.headers on
.mode column
.width 18 10 6
SELECT object_type, status, COUNT(*) AS n
FROM registry_objects
GROUP BY object_type, status
ORDER BY object_type, status;
SQL

echo
echo "=== All objects (stable_id, type, slug, name, status) ==="
sqlite3 "$DB_PATH" <<'SQL'
.headers on
.mode column
.width 38 12 36 32 10 14
SELECT
  stable_id,
  object_type,
  slug,
  display_name,
  status,
  source_authority
FROM registry_objects
ORDER BY object_type, slug;
SQL

echo
echo "=== Candidate/Canonical objects requiring attention ==="
sqlite3 "$DB_PATH" <<'SQL'
.headers on
.mode column
.width 38 12 36 10 12
SELECT
  stable_id,
  object_type,
  slug,
  status,
  updated_at
FROM registry_objects
WHERE status IN ('candidate', 'canonical')
ORDER BY object_type, updated_at DESC
LIMIT 200;
SQL
