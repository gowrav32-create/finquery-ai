import json
from dataclasses import dataclass, field
from pathlib import Path

from src.query_engine.service import run_financial_query
from src.regression_detection.evaluator import (
    FinancialCaseEvaluationResult,
    evaluate_financial_case
)
from src.regression_detection.models import (
    GoldenFinancialQueryCase
)


@dataclass
class FinancialEvaluationRun:
    """
    Summary of one complete regression evaluation run.
    """

    prompt_version: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float

    failed_case_ids: list[str] = field(
        default_factory=list
    )

    results: list[FinancialCaseEvaluationResult] = field(
        default_factory=list
    )


def load_golden_financial_cases(
    dataset_path: Path
) -> list[GoldenFinancialQueryCase]:
    """
    Load and validate the financial golden dataset.
    """
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Golden dataset not found: {dataset_path}"
        )

    with dataset_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        dataset_data = json.load(file)

    if not isinstance(dataset_data, list):
        raise ValueError(
            "Golden financial dataset must contain a JSON list."
        )

    return [
        GoldenFinancialQueryCase(**case)
        for case in dataset_data
    ]


def run_financial_evaluation(
    dataset_path: Path,
    database_path: Path,
    prompt_path: Path
) -> FinancialEvaluationRun:
    """
    Run every golden financial question through FinQuery AI.

    Each response is compared against its human-verified expected
    result and summarized into one evaluation run.
    """
    test_cases = load_golden_financial_cases(
        dataset_path
    )

    results: list[FinancialCaseEvaluationResult] = []

    prompt_version = "unknown"

    for test_case in test_cases:
        response = run_financial_query(
            question=test_case.question,
            database_path=database_path,
            prompt_path=prompt_path
        )

        prompt_version = response.prompt_version

        evaluation_result = evaluate_financial_case(
            test_case=test_case,
            response=response
        )

        results.append(
            evaluation_result
        )

    total_cases = len(results)

    passed_cases = sum(
        1
        for result in results
        if result.passed
    )

    failed_cases = (
        total_cases - passed_cases
    )

    if total_cases == 0:
        pass_rate = 0.0
    else:
        pass_rate = round(
            (passed_cases / total_cases) * 100,
            2
        )

    failed_case_ids = [
        result.case_id
        for result in results
        if not result.passed
    ]

    return FinancialEvaluationRun(
        prompt_version=prompt_version,
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        pass_rate=pass_rate,
        failed_case_ids=failed_case_ids,
        results=results
    )
