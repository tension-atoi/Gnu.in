-- Canonical registry quality and promotion readiness checks

SELECT
  'duplicate_slug_status' AS check_name,
  object_type,
  slug,
  status,
  COUNT(*) AS count
FROM registry_objects
WHERE status IN ('candidate', 'canonical')
GROUP BY object_type, slug, status
HAVING COUNT(*) > 1
ORDER BY object_type, slug;

SELECT
  'missing_geometric_contract' AS check_name,
  id,
  stable_id,
  version,
  object_type,
  slug,
  status
FROM registry_objects
WHERE geometry_contract IN ('{}', '[]', '""')
  AND status IN ('candidate', 'canonical');

SELECT
  'missing_tokens_contract' AS check_name,
  id,
  stable_id,
  version,
  object_type,
  slug,
  status
FROM registry_objects
WHERE tokens_contract IN ('{}', '[]', '""')
  AND status IN ('candidate', 'canonical');

SELECT
  'no_renderers' AS check_name,
  ro.id,
  ro.stable_id,
  ro.version,
  ro.object_type,
  ro.slug,
  ro.status
FROM registry_objects ro
WHERE ro.status IN ('candidate', 'canonical')
  AND NOT EXISTS (
    SELECT 1
    FROM registry_object_renderers ror
    WHERE ror.object_id = ro.id
  );

SELECT
  'no_proof' AS check_name,
  ro.id,
  ro.stable_id,
  ro.version,
  ro.object_type,
  ro.slug,
  ro.status
FROM registry_objects ro
WHERE ro.status IN ('candidate', 'canonical')
  AND NOT EXISTS (
    SELECT 1
    FROM proofs p
    WHERE p.object_id = ro.id
      AND p.object_version = ro.version
  );

SELECT
  'object_graph_depth' AS check_name,
  parent.object_type AS parent_type,
  parent.slug AS parent_slug,
  child.object_type AS child_type,
  child.slug AS child_slug,
  rel.relation_type
FROM object_relations rel
JOIN registry_objects parent ON parent.id = rel.parent_id
JOIN registry_objects child ON child.id = rel.child_id
WHERE parent.status IN ('candidate', 'canonical')
  AND child.status IN ('candidate', 'canonical')
ORDER BY parent.slug, child.slug;
