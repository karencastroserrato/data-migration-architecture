import pandas as pd

from framework.rule import Rule


class DuplicateRule(Rule):
    """Regla que valida si el valor de una columna se repite más de una vez"""

    def _check(self, df: pd.DataFrame) -> pd.Series:
        return df[self.column].duplicated(keep=False)
