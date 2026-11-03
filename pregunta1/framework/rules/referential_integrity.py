from typing import Optional
import pandas as pd

from framework.rule import Rule


class ReferentialIntegrityRule(Rule):
    """Compara dos Dataframes. 
    Valida si los registros de una columna del df base no existen 
    en el df con el que se esta comparando"""

    def __init__(
        self,
        column: str,
        reference_df: pd.DataFrame,
        reference_column: str,
        name: Optional[str] = None,
    ):
        """Inicializa las columnas de cada Dataframe"""
        super().__init__(column=column, name=name)
        self.reference_df = reference_df
        self.reference_column = reference_column

    def _check(self, df: pd.DataFrame) -> pd.Series:
        """Valida si cada valor del df base esta dentro df de refencia"""
        valid_values = set(self.reference_df[self.reference_column])
        return ~df[self.column].isin(valid_values)
