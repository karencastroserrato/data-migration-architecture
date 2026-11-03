from typing import List
import pandas as pd

from framework.rule import Rule, ValidationResult


class ValidationEngine:
    def __init__(self, rules: List[Rule]):
        """Constructor que guarda la lista de reglas pasadas"""
        self.rules = rules

    def run(self, df: pd.DataFrame) -> List[ValidationResult]:
        """Recorre cada regla y junta los resultados en una nuevas lista"""
        return [rule.validate(df) for rule in self.rules]
