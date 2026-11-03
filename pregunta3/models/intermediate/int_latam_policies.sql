-- Intermediate model: combina los tres modelos estandarizados en staging en un solo conjunto de datos LATAM.

select * from {{ ref('stg_peru_policies') }}
union all
select * from {{ ref('stg_chile_policies') }}
union all
select * from {{ ref('stg_colombia_policies') }}
