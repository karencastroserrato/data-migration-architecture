from typing import Optional
import pandas as pd

from framework.rule import Rule


class DateRangeRule(Rule):
    """Regla que valida si una columna contiene valores fuera de la fecha del rango permitido"""

    def __init__(
        self,
        column: str,
        min_date: Optional[str] = None,
        max_date: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Inicializa dos parametros nuevos opcionales: min_date y max_date"""
        super().__init__(column=column, name=name)
        self.min_date = pd.to_datetime(min_date) if min_date else None
        self.max_date = pd.to_datetime(max_date) if max_date else None

    def _check(self, df: pd.DataFrame) -> pd.Series:
        """Convierte toda la columna a valores de fecha reales (no texto)
        Compara todas la columna de fecha con el límite"""
        dates = pd.to_datetime(df[self.column], errors="coerce")

        too_early = dates < self.min_date if self.min_date is not None else False
        too_late = dates > self.max_date if self.max_date is not None else False

        return too_early | too_late
