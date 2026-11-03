-- Preparando el entorno de trabajo:
-- Crear vistas para leer los 3 archivos planos
-- Motor usado: DuckDB (https://duckdb.org). Las vistas leen los .csv directamente con read_csv_auto(), una función propia de DuckDB.

CREATE OR REPLACE VIEW accounts AS
    SELECT * FROM read_csv_auto('../../accounts.csv');

CREATE OR REPLACE VIEW legacy_policies AS
    SELECT * FROM read_csv_auto('../../legacy_policies.csv');

CREATE OR REPLACE VIEW target_policies AS
    SELECT * FROM read_csv_auto('../../target_policies.csv');
