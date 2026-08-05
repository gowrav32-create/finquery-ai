from types import SimpleNamespace

from src.regression_detection.evaluator import (
    evaluate_financial_case
)
from src.regression_detection.models import (
    EvaluationRequirements,
    GoldenFinancialQueryCase
)


def create_golden_case() -> GoldenFinancialQueryCase:
    return GoldenFinancialQueryCase(
        id="finance_001",
        category="ranking",
        difficulty="standard",
        question=(
            "Which company had the highest "
            "revenue growth in 2024?"
        ),
        expected_tables=[
            "financial_metrics"
        ],
        expected_columns=[
            "ticker",
            "revenue_growth_pct"
        ],
        expected_row_count=1,
        expected_rows=[
            {
                "ticker": "NSS",
                "revenue_growth_pct": 22.92
            }
        ],
        requirements=EvaluationRequirements(
            must_be_read_only=True,
            must_execute=True,
            must_not_request_clarification=True
        ),
        notes=(
            "The answer must include the ticker "
            "and supporting growth value."
        )
    )


def test_financial_case_passes_when_all_results_match():
    test_case = create_golden_case()

    response = SimpleNamespace(
        generation_result=SimpleNamespace(
            sql=(
                "SELECT ticker, revenue_growth_pct "
                "FROM financial_metrics "
                "WHERE fiscal_year = 2024 "
                "ORDER BY revenue_growth_pct DESC "
                "LIMIT 1"
            ),
            tables_used=["financial_metrics"],
            clarification_needed=False
        ),
        execution=SimpleNamespace(
            safety_result=SimpleNamespace(
                is_safe=True
            ),
            query_result=SimpleNamespace(
                columns=[
                    "ticker",
                    "revenue_growth_pct"
                ],
                row_count=1,
                rows=[
                    {
                        "ticker": "NSS",
                        "revenue_growth_pct": 22.92
                    }
                ]
            )
        )
    )

    result = evaluate_financial_case(
        test_case=test_case,
        response=response
    )

    assert result.case_id == "finance_001"
    assert result.passed is True
    assert result.tables_match is True
    assert result.columns_match is True
    assert result.row_count_match is True
    assert result.rows_match is True
    assert result.failure_reasons == []


def test_financial_case_fails_when_result_column_is_missing():
    test_case = create_golden_case()

    response = SimpleNamespace(
        generation_result=SimpleNamespace(
            sql=(
                "SELECT ticker "
                "FROM financial_metrics "
                "WHERE fiscal_year = 2024 "
                "ORDER BY revenue_growth_pct DESC "
                "LIMIT 1"
            ),
            tables_used=["financial_metrics"],
            clarification_needed=False
        ),
        execution=SimpleNamespace(
            safety_result=SimpleNamespace(
                is_safe=True
            ),
            query_result=SimpleNamespace(
                columns=["ticker"],
                row_count=1,
                rows=[
                    {
                        "ticker": "NSS"
                    }
                ]
            )
        )
    )

    result = evaluate_financial_case(
        test_case=test_case,
        response=response
    )

    assert result.passed is False
    assert result.columns_match is False
    assert result.rows_match is False

    assert "result_columns_mismatch" in (
        result.failure_reasons
    )

    assert "row_values_mismatch" in (
        result.failure_reasons
    )


def test_financial_case_fails_when_extra_table_is_used():
    test_case = create_golden_case()

    response = SimpleNamespace(
        generation_result=SimpleNamespace(
            sql=(
                "SELECT fm.ticker, "
                "fm.revenue_growth_pct "
                "FROM financial_metrics AS fm "
                "JOIN annual_financials AS af "
                "ON fm.ticker = af.ticker "
                "AND fm.fiscal_year = af.fiscal_year "
                "WHERE fm.fiscal_year = 2024 "
                "ORDER BY fm.revenue_growth_pct DESC "
                "LIMIT 1"
            ),
            tables_used=[
                "financial_metrics",
                "annual_financials"
            ],
            clarification_needed=False
        ),
        execution=SimpleNamespace(
            safety_result=SimpleNamespace(
                is_safe=True
            ),
            query_result=SimpleNamespace(
                columns=[
                    "ticker",
                    "revenue_growth_pct"
                ],
                row_count=1,
                rows=[
                    {
                        "ticker": "NSS",
                        "revenue_growth_pct": 22.92
                    }
                ]
            )
        )
    )

    result = evaluate_financial_case(test_case=test_case, response=response)

    assert result.passed is False
    assert result.tables_match is False

    assert "unexpected_tables" in (result.failure_reasons)
