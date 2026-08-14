from dataclasses import dataclass

from sqlglot import exp, parse_one

FINANCIAL_METRIC_ALIASES = {
    "revenue_growth_pct": [
        "revenue growth",
        "sales growth"
    ],
    "operating_margin_pct": [
        "operating margin",
        "operating profit margin"
    ],
    "net_margin_pct": [
        "net margin",
        "net profit margin"
    ],
    "free_cash_flow": [
        "free cash flow",
        "fcf"
    ],
    "return_on_equity_pct": [
        "return on equity",
        "roe"
    ],
    "debt_to_equity": [
        "debt to equity",
        "debt-to-equity"
    ]
}


def detect_requested_metrics(
    question: str
) -> list[str]:
    """
    Detect canonical financial metric columns
    requested in a natural-language question.
    """
    normalized_question = (
        question
        .strip()
        .lower()
    )

    detected_metrics = []

    for metric_name, aliases in (
        FINANCIAL_METRIC_ALIASES.items()
    ):
        for alias in aliases:
            if alias in normalized_question:
                detected_metrics.append(
                    metric_name
                )
                break

    return detected_metrics

@dataclass
class FinancialSemanticValidationResult:
    """
    Result of checking whether generated SQL uses
    the financial metrics requested by the user.
    """

    is_valid: bool
    requested_metrics: list[str]
    referenced_columns: list[str]
    missing_metrics: list[str]


def validate_requested_metrics(
    question: str,
    sql: str
) -> FinancialSemanticValidationResult:
    """
    Check whether generated SQL actually references the
    canonical financial metric columns requested by the user.

    SQL aliases do not count as referenced metric columns.
    """
    requested_metrics = detect_requested_metrics(
        question
    )

    if not requested_metrics:
        return FinancialSemanticValidationResult(
            is_valid=True,
            requested_metrics=[],
            referenced_columns=[],
            missing_metrics=[]
        )

    try:
        expression = parse_one(
            sql,
            read="duckdb"
        )
    except Exception:
        return FinancialSemanticValidationResult(
            is_valid=False,
            requested_metrics=requested_metrics,
            referenced_columns=[],
            missing_metrics=requested_metrics.copy()
        )

    referenced_columns = []

    for column in expression.find_all(
        exp.Column
    ):
        column_name = column.name.lower()

        if column_name not in referenced_columns:
            referenced_columns.append(
                column_name
            )

    missing_metrics = [
        metric
        for metric in requested_metrics
        if metric.lower() not in referenced_columns
    ]

    return FinancialSemanticValidationResult(
        is_valid=len(missing_metrics) == 0,
        requested_metrics=requested_metrics,
        referenced_columns=referenced_columns,
        missing_metrics=missing_metrics
    )
