import pandas as pd

from framework.rule import Rule


class NotNullRule(Rule):
    """Regla que valida si existen registros vacios (NaN/None) en una columna"""

    def _check(self, df: pd.DataFrame) -> pd.Series:
        return df[self.column].isna()
