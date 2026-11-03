# Incorporacion de un país nuevo a OPTIMA LATAM

## Contexto

Gallagher esta agregando un país nuevo a OPTIMA LATAM. El sistema legado de ese país tiene mas o menos 500,000 clientes, 2,000,000 polizas, 8,000,000 items y 1,500,000 endosos. 

El diseño sigue el pipeline solicitado: Source, Extraction, Landing/RAW, Profiling, Data Quality, Mapping, Transformation, Migration, Destination, Reconciliation y Reporting. A continuación se evaluará cada etapa indicando que herramienta resulve la solicitud y las estrategias evaluadas: volumen, calidad de datos, manejo de errores, migracion incremental, conciliacion, reporte de avance.

## Que hace cada etapa

**Source:** Es el sistema legado del nuevo país. No se tiene visibilidad completa de como es esta construido, así que asumo que es una base de datos relacional, el mismo supuesto que se hizo para Peru, Chile y Colombia. 

**Extraction:** Aqui es donde los datos salen del sistema legado. Usaría Airbyte, apuntando a la base del legado con un conector JDBC generico, con un flujo por entidad: clientes, polizas, items, endosos. La primera corrida trae todo (carga completa), las siguientes solo traen lo que cambio, usando una columna cursor como created_date o updated_at. Para la tabla de items esto importa bastante: 8 millones de filas no se deben releer y extraer por completo si no presentan ningun cambio.

**Landing/RAW:** Airbyte escribe directo en Snowflake, en un esquema dedicado a este pais, siguiendo el mismo patron que ya se usó para RAW_PERU, RAW_CHILE y RAW_COLOMBIA. Los datos quedan exactamente como llegaron del origen, sin renombrar ni limpiar. La razon para mantener este paso como algo separado, aunque Airbyte sea el que escribe de verdad, es que deja una copia intacta de lo que tenia el sistema legado al momento de extraer. Si en el lapso de unos meses aparece un error de transformacion, se puede reprocesar todo desde RAW sin tener que volver a un sistema legado.

**Profiling:** Antes de escribir una sola regla de mapeo o de calidad para el nuevo pais, alguien tiene que revisar los datos: porcentaje de nulos, cuantos valores distintos tiene cada columna categoríca, que formato siguen realmente los formatos de teléfonos y números de documento para el nuevo país. Esto importa porque las reglas actuales se escribieron revisando los países actualmente migrados. Un país nuevo podria tener un tipo de documento completamente distinto, o un telefono con un formato diferente de digitos, y nada eso no debería representar un error, es simplemente un país distinto. Profiling es casi siempre un ejercicio de una sola vez, hecho por el ingeniero de datos que incorpora el pais, no algo que corre en cada sincronizacion. Es una pasada rapida con consultas de agregacion sobre las tablas RAW, o una herramienta como ydata-profiling si hace falta un reporte mas completo.

**Data Quality:** Aqui vuelve el catalogo de reglas de la pregunta 1, pero no el motor de Python. Las reglas son la misma idea: no nulo, sin duplicados,valores permitidos, formato, rangos de fecha validos, integridad referencial; pero correrlas con pandas significaria sacar millones de filas de Snowflake solo para revisarlas. En vez de eso, las mismas reglas se escriben como pruebas de dbt (not_null, unique, accepted_values, relationships, más un par de pruebas genericas propias para cosas como el formato de telefono o el orden de fechas), asi la revision corre dentro de Snowflake, justo donde ya viven los datos. Los registros que fallan se pueden enviar a una tabla de cuarentena para ser revisados en detalle. Una aclaracion sobre el orden: acá se nombra antes que Mapping porque conceptualmente es sobre los datos crudos, pero en la ejecucion real las pruebas de dbt corren sobre los modelos de staging ya construidos (no se puede probar un modelo que todavia no existe) por eso en el diagrama Mapping aparece primero.

**Mapping:** Tambien conocido, en el proyecto de dbt, como la capa de staging. Un modelo por entidad para este país: stg_pais_clients, stg_pais_policies, stg_pais_items, stg_pais_endosos; cada uno traduciendo los nombres de columna y los valores de ese país al modelo compartido que ya usan los demas países  . Si surgiera una nueva particularidad como que el nuevo país guarda el estado como ACTIVO/INACTIVO en vez de ACTIVE/INACTIVE en inglés, ahi es donde se hace ese cambio, para no tener que lidiar con esta diferencia mas adelante. En la practica, antes de escribir cualquier SQL, esto suele empezar como una hoja de calculo simple: campo del legado a campo estandar, valor del legado a valor estandar; revisada por alguien del lado del negocio para que el mapeo no sea solo una suposicion del ingeniero.

**Transformation.** La capa intermediate. Agregar un país significa agregar una linea más a los UNION ALL existentes en: int_latam_policies, int_latam_items, etc. Simplemente crecen para incluir el nuevo pais, no cambia nada más. Tambien vive la lógica de negocio real: convertir premium a una moneda de reporte común, relacionar items y endosos de vuelta con su poliza. Dado el volumen (la union de items por si sola ya pasa los 8 millones de filas), así que cambiaría los modelos mas pesados de una vista simple a materialización incremental en dbt, para que cada corrida solo procese lo nuevo en vez de recalcular toda la union cada vez que se ejecute el proceso.

**Migration:** Hasta acá todo pasa dentro de Snowflake, para reporting. Migration es el proceso separado y orquestado que de verdad mueve los datos limpios y aprobados hacia OPTIMA, el sistema en el que las diferentes áreas consultaran día a día. Aqui se tiene que respetar el orden de las dependencias: clientes antes que polizas, polizas antes que items y endosos; y deben pasar preferiblemente en lotes (Ejemplo: de 10,000 a 50,000 registros a la vez) en vez de una carga gigante, para que una falla a mitad de camino no signifique empezar de cero. Cada carga de lote a OPTIMA debería ser un upsert, no un insert ciego, para que reinsertar un lote despues de una falla parcial nunca cree duplicados.

**Destination:** En realidad hay dos destinos aca, no uno. OPTIMA es donde el  negocio realmente opera: transaccional, pensado para actualizarse, cargado por el paso de Migration. ANALYTICS.FACT_POLICY (y las tablas de hechos equivalentes para las demas entidades) es el lado de Snowflake, construido por dbt, pensado para reporting a traves de OneSource. No son redundantes: uno esta hecho para la operacion diaria, el otro para el analisis entre países  , y tratar de servir las dos necesidades desde una sola tabla haria
un trabajo mediocre en ambas.

**Reconciliation:** El mismo patron SQL de la pregunta 2: conteos totales,registros que faltan del otro lado, duplicados, comparación campo por campo y un estado final de OK, ERROR o MISSING_TARGET; aplicado ahora a las cuatro entidades en vez de solo polizas. La parte que vale la pena resaltar: conciliar contra la copia analitica solo prueba que la copia analitica esta bien, no dice nada sobre OPTIMA. Por eso hay una pequeña extraccion de solo lectura que trae el estado actual de OPTIMA de vuelta a Snowflake despues de cada lote, y la conciliacion corre contra esa comparación, no solo contra la salida de dbt. Los resultados se guardan en una tabla propia con fecha y número de lote, para llevar una trazabilidad.

**Reporting:** Esta es la clase Report de la pregunta 1, ya más grande: es un conjunto de tablas que se van acumulando con el tiempo: cuantos registros se insertaron, cuantos tuvieron exito, cuantos estan en cuarentena, como se ve la tasa de error de conciliacion por lote. Algún visualizador de datos se puede conectar a esas tablas para generar graficas que faciliten la interpretación de los datos y para hacer un seguimiento de cerca a las migraciones realizadas. También se deberian tener alertas para los casos más graves como por ejemplo: un salto en la tasa de error, un lote que fallo por completo. 

## Tecnologias elegidas

- **Extraction + Landing -> Airbyte:** open source, conector JDBC, sincronización incremental nativa por cursor, escribe directo a Snowflake.
- **Warehouse -> Snowflake:** ya en uso para los tres países existentes, computo elastico que maneja el volumen sin administrar directamente la infraestructura.
- **Profiling -> SQL + ydata-profiling:** paso exploratorio de una sola vez, no necesita ser un componente permanente del pipeline.
- **Transformation + Mapping + Data Quality -> dbt:** mismo proyecto y convenciones ya usadas para Peru, Chile y Colombia, las pruebas corren dentro de Snowflake.
- **Orquestacion de Migration -> Airflow:** secuenciación por lotes, orden de dependencias, reintentos, programación contra la API de carga de OPTIMA.
- **Reporting -> Snowsight, Tableau:** lee directo de las tablas de monitoreo en Snowflake, sin construir una app propia.

## Estrategia: procesamiento de grandes volumenes

No se necesita computo distribuido - los almacenes elasticos de Snowflake manejan unos pocos millones de filas sin problema. La palanca real que usamos para el volumen es evitar recalculos innecesarios: extraccion incremental en el origen, materializacion incremental en dbt para las tablas mas grandes, y migración a OPTIMA por lotes en vez de una carga masiva.

## Estrategia: control de calidad de datos

El catalogo de reglas de la pregunta 1, reimplementado como pruebas de dbt para que corran dentro de Snowflake en vez de sacar datos a pandas. Profiling pasa primero para que las reglas de verdad le queden bien al nuevo país en vez de asumir que se parece a Perú, Chile o Colombia. Todo lo que falla queda en cuarentena, no se descarta ni se deja seguir avanzando en el pipeline.

## Estrategia: manejo de errores y reprocesamiento

Las fallas son esperadas. Una sincronizacion fallida de Airbyte retoma desde su ultimo punto de control en vez de volver a extraer
todo. Los registros que fallan una prueba de dbt quedan en cuarentena para revision en vez de bloquear todo el lote. Un lote de migracion fallido hacia OPTIMA se puede reintentar sin riesgo porque la carga se puede hacer con un upsert. Nada de esto depende de que una persona note primero el problema en tiempo real. El comportamiento de reintento ya viene incorporado en cada paso.

## Estrategia: migración incremental y por lotes

La extracción es incremental despues de la primera carga completa. El movimiento real hacia OPTIMA pasa en lotes de decenas de miles de registros, ordenados por dependencia entre entidades, con conciliacion corriendo despues de cada uno. Hacer el rollout del país por cohortes (por ejemplo, por region) en vez de todo de una vez significa que un problema que aparezca puede quedar solo en una porcion pequeña de los datos, no en el país completo.

## Estrategia: conciliación entre origen y destino

La misma lógica de comparacion de la pregunta 2, corrida por lote en vez de todo al final, y corrida contra el estado real de OPTIMA (no solo la copia analitica) trayendo una foto de solo lectura de OPTIMA de vuelta a Snowflake. Los resultados quedan guardados en su propia tabla para poder seguir el avance de lote por lote. 

## Estrategia: métricas de avance y reporting

Cada etapa deja un rastro (filas extraidas, filas que pasan o fallan los controles de calidad, filas migradas por lote, estado de conciliación por lote) y todo eso termina en un esquema de monitoreo en Snowflake. De ahí en adelante es una solución de dashboard de BI: porcentaje migrado, tendencia de la tasa de error, fecha estimada de finalizacion segun el ritmo actual, con alertas que se disparan cuando algun registro cruza un umbral para evaluar inmediatamente el problema.
