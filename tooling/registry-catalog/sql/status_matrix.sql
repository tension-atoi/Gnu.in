SELECT
  object_type,
  status,
  COUNT(*) AS object_count
FROM registry_objects
GROUP BY object_type, status
ORDER BY object_type, status;
