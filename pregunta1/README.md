# Framework de validacion de calidad de datos

Framework en Python para correr controles de calidad sobre datasets tabulares (DataFrames de pandas). Permite definir reglas de validación de forma sencilla, ejecutar varias reglas sobre un mismo dataset y generar un reporte con los registros que incumplieron cada una. No esta atado a ningun dataset en particular, se puede usar sobre cualquier tabla que se le pase. Osea, es agnostico.

## Estructura

### rule.py

Contiene la base de todo el framework.

- ValidationResult: contenedor del resultado de una regla ejecutada - nombre de la regla, columna, si paso o no, cuantos registros fallaron y cuales son.
- Rule: clase abstracta de la que heredan todas las reglas. Cada regla nueva solo tiene que implementar _check, que devuelve una serie booleana (True donde el registro incumple la regla). El método validate ya esta
implementado y es el que arma el ValidationResult a partir de esa serie por lo tanto no es necesario modificarlo, o al menos no hacerlo frecuentemente.

### engine.py

ValidationEngine recibe una lista de reglas y las corre todas sobre un mismo DataFrame, devolviendo la lista de resultados. No sabe nada de que hace cada regla, solo que cada una tiene un método llamado validate.

### report.py

Report recibe la lista de resultados que devuelve el engine y la convierte en algo legible:

- summary(): una fila por regla ejecutada con: si pasó y cuantos fallaron.
- details(): todos los registros que fallaron, de todas las reglas, juntos en una sola tabla.
- to_csv() / to_excel(): exporta el detalle en ese formato.

### rules/

Ya hay un set de reglas concretas implementadas, listas para usar o para tomar de ejemplo si se necesita crear una nueva: nulos, duplicados, valores permitidos, formato (regex), rango de fechas, orden entre dos fechas,
integridad referencial y tipo de dato.

Las reglas que vienen armadas en main.py se definieron en base a tres archivos planos ya existentes - accounts, legacy_policies y target_policies.
