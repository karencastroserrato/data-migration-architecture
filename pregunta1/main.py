import pandas as pd

from framework.rules.not_null import NotNullRule
from framework.rules.duplicate import DuplicateRule
from framework.rules.allowed_values import AllowedValuesRule
from framework.rules.format import FormatRule
from framework.rules.date_range import DateRangeRule
from framework.rules.date_order import DateOrderRule
from framework.rules.referential_integrity import ReferentialIntegrityRule
from framework.rules.type_rule import TypeRule
from framework.engine import ValidationEngine
from framework.report import Report

accounts_df = pd.read_csv("../accounts.csv")
legacy_policies_df = pd.read_csv("../legacy_policies.csv")
target_policies_df = pd.read_csv("../target_policies.csv")


def build_accounts_rules():
    """Define cuales son las reglas que aplican para Account. 
    Arma la lista completa para las validaciones."""
    return [
        NotNullRule(column="client_id"),
        DuplicateRule(column="client_id"),
        NotNullRule(column="client_name"),
        NotNullRule(column="document_type"),
        AllowedValuesRule(column="document_type", allowed_values=["DNI", "RUT"]),
        NotNullRule(column="document_number"),
        DuplicateRule(column="document_number"),
        NotNullRule(column="country_code"),
        AllowedValuesRule(column="country_code", allowed_values=["PER"]),
        NotNullRule(column="email"),
        FormatRule(column="email", pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
        NotNullRule(column="phone"),
        FormatRule(column="phone", pattern=r"^\d{7,8}$"),
        NotNullRule(column="birthdate"),
        DateRangeRule(column="birthdate", max_date=pd.Timestamp.now()),
        NotNullRule(column="status"),
        AllowedValuesRule(column="status", allowed_values=["ACTIVE", "INACTIVE"]),
        NotNullRule(column="created_date"),
        DateRangeRule(column="created_date", min_date="2014-01-01"),
    ]


def build_policy_rules(reference_accounts_df):
    """Define cuales son las reglas que aplican para las polizas. 
    Arma la lista completa para las validaciones."""
    return [
        NotNullRule(column="policy_id"),
        DuplicateRule(column="policy_id"),
        NotNullRule(column="client_id"),
        ReferentialIntegrityRule(
            column="client_id",
            reference_df=reference_accounts_df,
            reference_column="client_id",
        ),
        NotNullRule(column="policy_number"),
        DuplicateRule(column="policy_number"),
        NotNullRule(column="premium"),
        TypeRule(column="premium", expected_type=float),
        NotNullRule(column="currency"),
        AllowedValuesRule(column="currency", allowed_values=["PEN", "USD"]),
        NotNullRule(column="start_date"),
        NotNullRule(column="end_date"),
        DateOrderRule(before_column="start_date", after_column="end_date"),
        NotNullRule(column="status"),
        AllowedValuesRule(column="status", allowed_values=["ACTIVE", "INACTIVE"]),
    ]


all_results = []

"""Ejecuta las reglas sobre Accounts y sobre polizas, concatenando los resultados"""
all_results += ValidationEngine(build_accounts_rules()).run(accounts_df)
all_results += ValidationEngine(build_policy_rules(accounts_df)).run(legacy_policies_df)
all_results += ValidationEngine(build_policy_rules(accounts_df)).run(target_policies_df)

"""Genera el reporte final e imprime el resultad """
report = Report(all_results)

print(report.summary())
report.to_csv("report.csv")
