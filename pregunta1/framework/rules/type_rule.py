from typing import Optional
import pandas as pd

from framework.rule import Rule


class TypeRule(Rule):
    """Valida el tipo de dato de la columna evaluada.
    Falla si los registros de la columna no pueden ser convertidos a un formato especifico"""

    def __init__(self, column: str, expected_type: type, name: Optional[str] = None):
        super().__init__(column=column, name=name)
        self.expected_type = expected_type

    def _check(self, df: pd.DataFrame) -> pd.Series:
        """Define una función propia para validar un solo valor a la vez"""
        def is_invalid(value) -> bool:
            if pd.isna(value):
                return False  

            try:
                self.expected_type(value)
                return False
            except (ValueError, TypeError):
                return True

        return df[self.column].apply(is_invalid)
