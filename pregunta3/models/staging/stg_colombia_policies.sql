-- Staging model para las polizas de Colombia.
-- Toma los datos crudos y los deja listos para ser consumidos.
-- Agrega una marca de COL para indicar que son registros de Colombia

select
    policy_id,
    client_id,
    policy_number,
    cast(premium as decimal(18, 2)) as premium,
    currency,
    cast(start_date as date) as start_date,
    cast(end_date as date) as end_date,
    status,
    'COL' as country_code
from {{ source('raw_colombia', 'policies') }}
