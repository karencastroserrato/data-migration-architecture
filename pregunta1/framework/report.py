from typing import List
import pandas as pd

from framework.rule import ValidationResult


class Report:
    def __init__(self, results: List[ValidationResult]):
        """Guarda una lista de resultados"""
        self.results = results

    def summary(self) -> pd.DataFrame:
        """A partir de una lista de diccionario pasada, construye un df:
        Una fila con los resultados por cada regla ejecutada"""
        return pd.DataFrame(
            [
                {
                    "rule_name": r.rule_name,
                    "column": r.column,
                    "passed": r.passed,
                    "failed_count": r.failed_count,
                }
                for r in self.results
            ]
        )

    def details(self) -> pd.DataFrame:
        """Junta todos los registros que fallaron en una sola tabla"""
        frames = []
        for r in self.results:
            if r.failed_count == 0:
                continue
            frame = r.failed_records.copy()
            frame.insert(0, "rule_name", r.rule_name)
            frames.append(frame)

        if not frames:
            return pd.DataFrame()

        return pd.concat(frames, ignore_index=True)

    def to_csv(self, path: str) -> None:
        """Exporta la informacion en formato .csv"""
        self.details().to_csv(path, index=False)

    def to_excel(self, path: str) -> None:
        """Exporta la informacion en formato .xlsx"""
        self.details().to_excel(path, index=False)
