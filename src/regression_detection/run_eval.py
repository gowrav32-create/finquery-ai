from datetime import datetime
from pathlib import Path

from src.database.build_database import (
    build_financial_database,
    create_financial_metrics_view,
    seed_demo_data
)
from src.regression_detection.baseline import (
    load_evaluation_report
)
from src.regression_detection.regression import (
    compare_financial_runs
)
from src.regression_detection.reporting import (
    save_financial_evaluation_report
)
from src.regression_detection.runner import (
    run_financial_evaluation
)


def main() -> None:
    """
    Run the FinQuery AI golden-dataset regression evaluation
    against the current SQL-generation prompt.
    """
    database_path = Path(
        "data/financial_data.duckdb"
    )

    dataset_path = Path(
        "datasets/golden_financial_queries_v1.json"
    )

    prompt_path = Path(
        "prompts/sql_generation_v1.yaml"
    )

    baseline_path = Path(
        "baselines/trusted_baseline_v1.json"
    )

    # Make sure the deterministic financial database exists
    # and contains the data expected by the golden dataset.
    build_financial_database(database_path)
    seed_demo_data(database_path)
    create_financial_metrics_view(database_path)

    print("FinQuery AI Regression Evaluation")
    print("=" * 40)
    print()

    evaluation_run = run_financial_evaluation(
        dataset_path=dataset_path,
        database_path=database_path,
        prompt_path=prompt_path
    )

    baseline_data = load_evaluation_report(
        baseline_path
    )

    comparison = compare_financial_runs(
        current_results=evaluation_run.results,
        previous_results=baseline_data["results"]
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    report_path = Path(
        "runs"
    ) / (
        f"{evaluation_run.prompt_version}_"
        f"{timestamp}.json"
    )

    save_financial_evaluation_report(
        evaluation_run=evaluation_run,
        report_path=report_path
    )

    print(
        "Prompt version:",
        evaluation_run.prompt_version
    )

    print(
        "Total cases:",
        evaluation_run.total_cases
    )

    print(
        "Passed:",
        evaluation_run.passed_cases
    )

    print(
        "Failed:",
        evaluation_run.failed_cases
    )

    print(
        f"Pass rate: {evaluation_run.pass_rate:.2f}%"
    )

    print()
    print("Baseline comparison")
    print("-" * 40)

    print(
        "Trusted baseline:",
        baseline_path
    )

    print(
        "Shared cases:",
        comparison.shared_case_count
    )

    print(
        "Previous shared pass rate:",
        comparison.previous_pass_rate
    )

    print(
        "Current shared pass rate:",
        comparison.current_pass_rate
    )

    print(
        "Pass-rate change:",
        comparison.pass_rate_change
    )

    print(
        "Regressions:",
        comparison.regressions
    )

    print(
        "Improvements:",
        comparison.improvements
    )

    print()
    print("Report saved:", report_path)
    print()

    if evaluation_run.failed_cases == 0:
        print(
            "All financial evaluation cases passed."
        )
        return

    print("Failed cases:")
    print()

    for result in evaluation_run.results:
        if result.passed:
            continue

        print(
            f"Case: {result.case_id}"
        )

        if result.generated_sql:
            print("Generated SQL:")
            print(result.generated_sql)

        print("Failure reasons:")

        for reason in result.failure_reasons:
            print(
                f"- {reason}"
            )

        print()


if __name__ == "__main__":
    main()
