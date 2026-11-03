-- Clientes quienes son dueños de más de una poliza tanto en legacy como en target

SELECT 'legacy_policies' AS table_name, lp.client_id, a.client_name, COUNT(*) AS policy_count
FROM legacy_policies lp
JOIN accounts a ON a.client_id = lp.client_id
GROUP BY lp.client_id, a.client_name
HAVING COUNT(*) > 1
UNION ALL
SELECT 'target_policies' AS table_name, tp.client_id, a.client_name, COUNT(*) AS policy_count
FROM target_policies tp
JOIN accounts a ON a.client_id = tp.client_id
GROUP BY tp.client_id, a.client_name
HAVING COUNT(*) > 1
ORDER BY table_name, policy_count DESC;
