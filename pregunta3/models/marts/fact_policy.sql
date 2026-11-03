-- Tabla LATAM final de hechos.  
-- Materializada como tabla en el esquema analytics por dbt_project.yml
select
    policy_id,
    client_id,
    policy_number,
    country_code,
    premium,
    currency,
    start_date,
    end_date,
    status
from {{ ref('int_latam_policies') }}
