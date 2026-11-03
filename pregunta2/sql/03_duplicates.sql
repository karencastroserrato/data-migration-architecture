-- Registros duplicados en los campos: policy_id y policy_number tanto en legacy como en target

SELECT 'legacy_policies' AS table_name, 'policy_id' AS duplicated_field, policy_id AS value, COUNT(*) AS occurrences
FROM legacy_policies
GROUP BY policy_id
HAVING COUNT(*) > 1
UNION ALL
SELECT 'target_policies' AS table_name, 'policy_id' AS duplicated_field, policy_id AS value, COUNT(*) AS occurrences
FROM target_policies
GROUP BY policy_id
HAVING COUNT(*) > 1
UNION ALL
SELECT 'legacy_policies' AS table_name, 'policy_number' AS duplicated_field, policy_number AS value, COUNT(*) AS occurrences
FROM legacy_policies
GROUP BY policy_number
HAVING COUNT(*) > 1
UNION ALL
SELECT 'target_policies' AS table_name, 'policy_number' AS duplicated_field, policy_number AS value, COUNT(*) AS occurrences
FROM target_policies
GROUP BY policy_number
HAVING COUNT(*) > 1;
