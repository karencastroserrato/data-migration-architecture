# Arquitectura dbt para polizas LATAM

## Capas

### Raw

Las tres tablas de países tal como llegan a Snowflake (RAW_PERU.POLICIES, RAW_CHILE.POLICIES, RAW_COLOMBIA.POLICIES), declaradas como source de dbt en models/staging/sources.yml. Dbt no crea ni modifica nada acá en este proceso. La carga de los datos de cada país se debe hacer un proceso aparte en Snowflake.

### Staging

Un modelo por cada tabla de origen (stg_peru_policies, stg_chile_policies,stg_colombia_policies). Cada uno hace lo mismo con su propio pais: toma solo las columnas que existen en los tres países (policy_id, client_id, policy_number, premium, currency, start_date, end_date, status), las deja con el mismo nombre y el mismo tipo de dato en los tres modelos y le agrega
un country_code fijo por cada país. Todavia no hay joins ni logica de negocio, aca solo se ordena el set de datos de cada país por
separado. Se guarda como view porque es solo un paso de estandarizacion, no vale la pena duplicar almacenamiento para esto.

### Intermediate

int_latam_policies junta los tres modelos de staging con un UNION ALL (une todos los registros). Este es el primer punto donde los tres países existen como un solo conjunto de datos. Sigue siendo view, y sigue sin tener logica de negocio. Más allá de la union su unico trabajo es dejar listo "un solo set de polizas LATAM" para que la capa de marts lo use.

### Marts

fact_policy, guardado como tabla fisica en el esquema analytics (ANALYTICS.FACT_POLICY). Esta es la tabla de hechos que consume OneSource. Es una tabla y no una vista porque se consulta todo el tiempo desde reportes y no tiene sentido volver a calcular la union cada vez que alguien la consulta.

## Por que se diseño asi

**Tres capas, cada una con su propio trabajo:** Staging estandariza por pais, intermediate junta los paises, marts entrega el resultado final. Separarlo asi significa que cada capa se puede probar, revisar y cambiar por su lado. Si hay un error en como se mapea una columna de Chile, se arregla en stg_chile_policies sin tocar la logica de union ni la tabla final. Lo más importante es que se utilizan buenas practicas de arquitectura, como la arquitectura medallón, un patrón de diseño que organiza y refina los datos a través de tres capas principales. 

**Staging solo deja pasar las columnas compartidas:** Cada país puede tener columnas propias que los otros dos países no tienen. El contrato de staging es a proposito: solo las columnas que estan en los tres países pasan de esta capa, con el mismo nombre y tipo de dato. Gracias a esto, el UNION ALL de intermediate funciona sin tener que mapear columnas puesto que cuando los datos llegan a intermediate, los tres ya vienen con exactamente la misma estructura.

**El country_code se agrega, no viene heredado:** Ninguna de las tablas crudas trae una columna de pais. Cada modelo de staging crea ese nuevo campo que lo agrega como un valor fijo (PER, COL, CHL), porque una vez que se unen los tres paises, ya no hay otra forma de saber de donde viene cada registro.

**Staging e intermediate son vistas, marts es tabla:** Staging e intermediate son solo pasos de estandarizacion y union, no se guardan físicamente. La tabla fact_policy si se consulta todo el tiempo desde OneSource y otros reportes, por eso se guarda como tabla, para no recalcular la union en cada consulta.

**La unicidad se revisa por país + ID, no por ID solo:** El policy_id solo es unico dentro de la secuencia de cada país (Perú, Chile y Colombia generan cada uno su propio POL-000001, POL-000002, etc). Despues del UNION ALL, puede llegar repetirce un policy_id entre países distintos, por eso las pruebas de unicidad en int_latam_policies y fact_policy tienen en cuenta la combinación (country_code y policy_id), no solo el policy_id.

**Las pruebas estan en la capa donde realmente aparece el riesgo:** Las pruebas de staging (not_null, unique en policy_id, accepted_values en country_code) atrapan problemas de un solo país lo antes posible, antes de que se propaguen. Intermediate y marts agregan la prueba de la llave compuesta, porque ese riesgo (que choquen los IDs de dos paises) solo existe una vez que los países ya estan juntos. No se puede probar en staging, porque cada modelo de staging solo ve un país a la vez.

**Se reutilizo una prueba de dbt_utils en vez de escribir SQL propio:** Se utilizó el paquete dbt_utils (declarado en packages.yml). Reutilizar algo que ya existe y ya esta probado sigue el mismo principio de reutilizacion que se usó en este proyecto, en vez de escribir y mantener SQL propio para revisar una llave compuesta.
