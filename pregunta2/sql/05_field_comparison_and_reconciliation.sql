-- Vista que compara campo por campo, los datos de cada poliza entre legacy y target

CREATE OR REPLACE VIEW policy_field_comparison AS
    SELECT l.policy_id, 'client_id' AS field, l.client_id AS legacy_value, t.client_id AS target_value,
           l.client_id IS DISTINCT FROM t.client_id AS different
    FROM legacy_policies l JOIN target_policies t ON l.policy_id = t.policy_id
    UNION ALL
    SELECT l.policy_id, 'policy_number', l.policy_number, t.policy_number,
           l.policy_number IS DISTINCT FROM t.policy_number
    FROM legacy_policies l JOIN target_policies t ON l.policy_id = t.policy_id
    UNION ALL
    SELECT l.policy_id, 'premium', CAST(l.premium AS VARCHAR), CAST(t.premium AS VARCHAR),
           l.premium IS DISTINCT FROM t.premium
    FROM legacy_policies l JOIN target_policies t ON l.policy_id = t.policy_id
    UNION ALL
    SELECT l.policy_id, 'currency', l.currency, t.currency,
           l.currency IS DISTINCT FROM t.currency
    FROM legacy_policies l JOIN target_policies t ON l.policy_id = t.policy_id
    UNION ALL
    SELECT l.policy_id, 'start_date', CAST(l.start_date AS VARCHAR), CAST(t.start_date AS VARCHAR),
           l.start_date IS DISTINCT FROM t.start_date
    FROM legacy_policies l JOIN target_policies t ON l.policy_id = t.policy_id
    UNION ALL
    SELECT l.policy_id, 'end_date', CAST(l.end_date AS VARCHAR), CAST(t.end_date AS VARCHAR),
           l.end_date IS DISTINCT FROM t.end_date
    FROM legacy_policies l JOIN target_policies t ON l.policy_id = t.policy_id
    UNION ALL
    SELECT l.policy_id, 'status', l.status, t.status,
           l.status IS DISTINCT FROM t.status
    FROM legacy_policies l JOIN target_policies t ON l.policy_id = t.policy_id;


-- Usa la vista creada para identificar que campos no coinciden entre legacy y target
SELECT policy_id, field, legacy_value, target_value, different
FROM policy_field_comparison
WHERE different
ORDER BY policy_id, field;


-- Resultado final: Por cada poliza indica si el registro es:
-- OK: sin diferencias 
-- ERROR: existe en ambos lados pero algo no coincide
-- MISSING_TARGET: nunca llegó a target
WITH per_policy AS (
    SELECT
        policy_id,
        bool_or(different) AS has_differences,
        string_agg(field, ',') FILTER (WHERE different) AS differing_fields
    FROM policy_field_comparison
    GROUP BY policy_id
)
SELECT
    l.policy_id AS Policy_id,
    CASE
        WHEN t.policy_id IS NULL THEN 'MISSING_TARGET'
        WHEN p.has_differences THEN 'ERROR'
        ELSE 'OK'
    END AS Validation_status,
    p.differing_fields AS Fields_with_differences
FROM legacy_policies l
LEFT JOIN target_policies t ON l.policy_id = t.policy_id
LEFT JOIN per_policy p ON p.policy_id = l.policy_id
ORDER BY Policy_id;
