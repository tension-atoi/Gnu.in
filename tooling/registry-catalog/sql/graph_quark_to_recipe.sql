SELECT
  parent.stable_id AS parent_stable,
  parent.version AS parent_version,
  parent.object_type AS parent_type,
  parent.slug AS parent_slug,
  rel.relation_type,
  child.stable_id AS child_stable,
  child.version AS child_version,
  child.object_type AS child_type,
  child.slug AS child_slug
FROM object_relations rel
JOIN registry_objects parent ON parent.id = rel.parent_id
JOIN registry_objects child ON child.id = rel.child_id
WHERE parent.object_type IN ('quark', 'atom', 'molecule')
  AND child.object_type IN ('atom', 'molecule', 'recipe')
ORDER BY parent.object_type, parent.stable_id, child.object_type, child.stable_id;
