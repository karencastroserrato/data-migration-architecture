from typing import Iterable, Optional
import pandas as pd

from framework.rule import Rule


class AllowedValuesRule(Rule):
    """Regla que valida si en una columna existen valores fuera de los valores definidos o permitidos"""

    def __init__(self, column: str, allowed_values: Iterable, name: Optional[str] = None):
        super().__init__(column=column, name=name)
        self.allowed_values = set(allowed_values)

    def _check(self, df: pd.DataFrame) -> pd.Series:
        return ~df[self.column].isin(self.allowed_values)
