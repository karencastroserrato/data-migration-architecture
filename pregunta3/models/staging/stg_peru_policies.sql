-- Staging model para las polizas de Perú.
-- Toma los datos crudos y los deja listos para ser consumidos.
-- Agrega una marca de PER para indicar que son registros de Perú. 

select
    policy_id,
    client_id,
    policy_number,
    cast(premium as decimal(18, 2)) as premium,
    currency,
    cast(start_date as date) as start_date,
    cast(end_date as date) as end_date,
    status,
    'PER' as country_code
from {{ source('raw_peru', 'policies') }}
