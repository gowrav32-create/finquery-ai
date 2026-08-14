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
