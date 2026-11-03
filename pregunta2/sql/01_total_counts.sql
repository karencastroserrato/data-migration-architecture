-- Cantidad total de registros en legacy y en target.

SELECT 'legacy_policies' AS table_name, COUNT(*) AS total_records FROM legacy_policies
UNION ALL
SELECT 'target_policies' AS table_name, COUNT(*) AS total_records FROM target_policies;
