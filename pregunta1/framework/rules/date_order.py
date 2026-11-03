from typing import Optional
import pandas as pd

from framework.rule import Rule


class DateOrderRule(Rule):
    """Valida la relación entre dos columnas. 
    Falla donde los registros 'before_column' sean despues de 'after_column'"""

    def __init__(self, before_column: str, after_column: str, name: Optional[str] = None):
        """Inicializa dos parametros o columnas"""
        super().__init__(column=f"{before_column} -> {after_column}", name=name)
        self.before_column = before_column
        self.after_column = after_column

    def _check(self, df: pd.DataFrame) -> pd.Series:
        """Convierte ambas columnas a formato tipo fecha y compara las dos series:
        Lo hace fila por fila y devuelve unas nueva serie booleana"""
        before = pd.to_datetime(df[self.before_column], errors="coerce")
        after = pd.to_datetime(df[self.after_column], errors="coerce")

        return before > after
