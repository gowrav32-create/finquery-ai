import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.regression_detection.models import (EvaluationRequirements, GoldenFinancialQueryCase)


def test_loads_golden_financial_query_case():
    dataset_path = Path("datasets/golden_financial_queries_v1.json")

    dataset_data = json.loads(dataset_path.read_text(encoding="utf-8"))

    test_case = GoldenFinancialQueryCase(**dataset_data[0])

    assert test_case.id == "finance_001"
    assert test_case.category == "ranking"
    assert test_case.question == ("Which company had the highest revenue growth in 2024?")

    assert test_case.expected_tables == ["financial_metrics"]

    assert test_case.expected_columns == ["ticker", "revenue_growth_pct"]

    assert test_case.expected_row_count == 1

    assert test_case.expected_rows == [{"ticker": "NSS", "revenue_growth_pct": 22.92}]

    assert(test_case.requirements.must_be_read_only is True)

    assert(test_case.requirements.must_execute is True)

def test_rejects_negative_expected_row_count():
    with pytest.raises(ValidationError):
        GoldenFinancialQueryCase(
            id="finance_invalid",
            category="ranking",
            difficulty="standard",
            question="Which company ranks first?",
            expected_tables=["financial_metrics"],
            expected_columns=["ticker"],
            expected_row_count=-1,
            expected_rows=[],
            requirements=EvaluationRequirements(),
            notes="Invalid row-count example."
        )

def test_rejects_empty_financial_question():
    with pytest.raises(ValidationError, match="must not be empty"):
            GoldenFinancialQueryCase(
                id="finance_invalid",
                category="ranking",
                difficulty="standard",
                question="   ",
                expected_tables=["financial_metrics"],
                expected_columns=["ticker"],
                expected_row_count=1,
                expected_rows=[{"ticker": "NSS"}],
                requirements=EvaluationRequirements(),
                notes="Invalid empty question example."
            )
            