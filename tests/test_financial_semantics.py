from src.query_engine.semantics import (
    detect_requested_metrics
)


def test_detects_operating_margin():
    metrics = detect_requested_metrics(
        "What was NSS's operating margin in 2024?"
    )

    assert metrics == [
        "operating_margin_pct"
    ]


def test_detects_revenue_growth():
    metrics = detect_requested_metrics(
        "Which company had the highest revenue growth in 2024?"
    )

    assert metrics == [
        "revenue_growth_pct"
    ]


def test_detects_multiple_financial_metrics():
    metrics = detect_requested_metrics(
        "Compare net margin and return on equity for NSS."
    )

    assert metrics == [
        "net_margin_pct",
        "return_on_equity_pct"
    ]


def test_returns_empty_list_when_no_known_metric_is_requested():
    metrics = detect_requested_metrics(
        "Show me information about NSS."
    )

    assert metrics == []
    