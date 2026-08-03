import pytest
from pydantic import ValidationError

from src.query_engine.models import SQLGenerationResult


def test_accepts_valid_sql_generation_result():
    result = SQLGenerationResult(
        sql="""
            SELECT
                ticker,
                revenue_growth_pct
            FROM financial_metrics
            WHERE fiscal_year = 2024
        """,
        explanation=(
            "Returns 2024 revenue growth for each company."
        ),
        confidence=0.95,
        tables_used=["financial_metrics"],
        columns_used=[
            "ticker",
            "revenue_growth_pct",
            "fiscal_year"
        ],
        clarification_needed=False,
        clarification_question=None
    )

    assert result.confidence == 0.95
    assert result.tables_used == ["financial_metrics"]
    assert result.clarification_needed is False


def test_rejects_confidence_above_one():
    with pytest.raises(ValidationError):
        SQLGenerationResult(
            sql="SELECT * FROM companies",
            explanation="Returns all companies.",
            confidence=1.5,
            tables_used=["companies"],
            columns_used=[],
            clarification_needed=False,
            clarification_question=None
        )


def test_requires_sql_when_clarification_is_not_needed():
    with pytest.raises(
        ValidationError,
        match="SQL is required"
    ):
        SQLGenerationResult(
            sql=None,
            explanation="The question is clear.",
            confidence=0.8,
            tables_used=[],
            columns_used=[],
            clarification_needed=False,
            clarification_question=None
        )


def test_allows_clarification_instead_of_guessing():
    result = SQLGenerationResult(
        sql=None,
        explanation=(
            "Revenue could mean total revenue or "
            "year-over-year revenue growth."
        ),
        confidence=0.4,
        tables_used=[],
        columns_used=[],
        clarification_needed=True,
        clarification_question=(
            "Do you want total revenue or revenue growth?"
        )
    )

    assert result.sql is None
    assert result.clarification_needed is True
    assert result.clarification_question is not None


def test_requires_question_when_clarification_is_needed():
    with pytest.raises(
        ValidationError,
        match="clarification question is required"
    ):
        SQLGenerationResult(
            sql=None,
            explanation="The financial term is ambiguous.",
            confidence=0.3,
            tables_used=[],
            columns_used=[],
            clarification_needed=True,
            clarification_question=None
        )
        