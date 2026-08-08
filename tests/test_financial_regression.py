from types import SimpleNamespace

from src.regression_detection.regression import (
    compare_financial_runs
)


def test_detects_case_improvement():
    previous_results = [
        SimpleNamespace(
            case_id="finance_001",
            passed=False
        )
    ]

    current_results = [
        SimpleNamespace(
            case_id="finance_001",
            passed=True
        )
    ]

    comparison = compare_financial_runs(
        current_results=current_results,
        previous_results=previous_results
    )

    assert comparison.regressions == []
    assert comparison.improvements == [
        "finance_001"
    ]

    assert comparison.shared_case_count == 1
    assert comparison.previous_pass_rate == 0.0
    assert comparison.current_pass_rate == 100.0
    assert comparison.pass_rate_change == 100.0


def test_detects_case_regression():
    previous_results = [
        SimpleNamespace(
            case_id="finance_001",
            passed=True
        ),
        SimpleNamespace(
            case_id="finance_002",
            passed=True
        )
    ]

    current_results = [
        SimpleNamespace(
            case_id="finance_001",
            passed=False
        ),
        SimpleNamespace(
            case_id="finance_002",
            passed=True
        )
    ]

    comparison = compare_financial_runs(
        current_results=current_results,
        previous_results=previous_results
    )

    assert comparison.regressions == [
        "finance_001"
    ]

    assert comparison.improvements == []

    assert comparison.previous_pass_rate == 100.0
    assert comparison.current_pass_rate == 50.0
    assert comparison.pass_rate_change == -50.0


def test_new_case_is_not_called_regression():
    previous_results = [
        SimpleNamespace(
            case_id="finance_001",
            passed=True
        )
    ]

    current_results = [
        SimpleNamespace(
            case_id="finance_001",
            passed=True
        ),
        SimpleNamespace(
            case_id="finance_002",
            passed=False
        )
    ]

    comparison = compare_financial_runs(
        current_results=current_results,
        previous_results=previous_results
    )

    assert comparison.regressions == []
    assert comparison.improvements == []
    assert comparison.shared_case_count == 1
    assert comparison.current_pass_rate == 100.0
    assert comparison.previous_pass_rate == 100.0
    