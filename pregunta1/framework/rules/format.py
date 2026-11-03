from typing import Optional
import pandas as pd

from framework.rule import Rule


class FormatRule(Rule):
    """Regla que valida si una columna tiene valores que no cumplen el patrón o formato regex"""

    def __init__(self, column: str, pattern: str, name: Optional[str] = None):
        super().__init__(column=column, name=name)
        self.pattern = pattern

    def _check(self, df: pd.DataFrame) -> pd.Series:
        return ~df[self.column].astype(str).str.match(self.pattern)
