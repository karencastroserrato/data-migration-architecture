from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class ValidationResult:
    """Resultado de la regla"""
    rule_name: str
    column: Optional[str]
    passed: bool
    failed_count: int
    failed_records: pd.DataFrame


class Rule(ABC):
    def __init__(self, column: str, name: Optional[str] = None):
        """Incializador o constructor de la regla"""
        self.column = column
        self.name = name or self.__class__.__name__

    @abstractmethod
    def _check(self, df: pd.DataFrame) -> pd.Series:
        """Método que cada regla debe implementar obligatoriamente.
        Retorna usa serie booleana: True, cuando las filas incumplen la regla"""
        raise NotImplementedError

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """Método completo. Filtra df con mascara para quedarse solo con los registros que fallaron
        y empaqueta todo en ValidationResult. Calcula si el df esta vacio y cuantas filas tiene"""
        failing_mask = self._check(df)
        failed_records = df[failing_mask]
        return ValidationResult(
            rule_name=self.name,
            column=self.column,
            passed=failed_records.empty,
            failed_count=len(failed_records),
            failed_records=failed_records,
        )
