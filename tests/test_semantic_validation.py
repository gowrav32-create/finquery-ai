from src.query_engine.semantics import (
    validate_requested_metrics
)


def test_accepts_requested_operating_margin_column():
    result = validate_requested_metrics(
        question="What was NSS's operating margin in 2024?",
        sql=(
            "SELECT ticker, operating_margin_pct "
            "FROM financial_metrics "
            "WHERE ticker = 'NSS' "
            "AND fiscal_year = 2024"
        )
    )

    assert result.is_valid is True
    assert result.requested_metrics == [
        "operating_margin_pct"
    ]
    assert result.missing_metrics == []


def test_rejects_wrong_metric_column():
    result = validate_requested_metrics(
        question="What was NSS's operating margin in 2024?",
        sql=(
            "SELECT ticker, revenue_growth_pct "
            "FROM financial_metrics "
            "WHERE ticker = 'NSS' "
            "AND fiscal_year = 2024"
        )
    )

    assert result.is_valid is False
    assert result.missing_metrics == [
        "operating_margin_pct"
    ]


def test_rejects_recalculation_when_canonical_metric_exists():
    result = validate_requested_metrics(
        question="What was NSS's operating margin in 2024?",
        sql=(
            "SELECT operating_income / revenue * 100 "
            "AS operating_margin_pct "
            "FROM financial_metrics "
            "WHERE ticker = 'NSS' "
            "AND fiscal_year = 2024"
        )
    )

    assert result.is_valid is False
    assert result.missing_metrics == [
        "operating_margin_pct"
    ]


def test_no_requested_metric_is_valid():
    result = validate_requested_metrics(
        question="Show me information about NSS.",
        sql=(
            "SELECT ticker "
            "FROM companies "
            "WHERE ticker = 'NSS'"
        )
    )

    assert result.is_valid is True
    assert result.requested_metrics == []
    assert result.missing_metrics == []
    