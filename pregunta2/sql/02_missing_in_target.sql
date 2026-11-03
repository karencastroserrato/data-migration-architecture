-- Polizas presentes en legacy que no fueron migradas a target.

SELECT l.*
FROM legacy_policies l
LEFT JOIN target_policies t ON l.policy_id = t.policy_id
WHERE t.policy_id IS NULL;
