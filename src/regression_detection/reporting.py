def format_percentage(value: float | None) -> str:
    if value is None:
        return "N/A"

    return f"{value:.2f}%"


def build_markdown_report(report_data: dict) -> str:
    comparison = report_data.get("comparison", {})
    quality_gates = report_data.get("quality_gates", {})
    confusion_matrix = report_data.get("confusion_matrix", {})
    category_metrics = report_data.get("category_metrics", {})

    regression_detected = comparison.get(
        "regression_detected",
        False
    )

    quality_gate_failures = quality_gates.get(
        "failures",
        []
    )

    evaluation_failed = (
        regression_detected
        or bool(quality_gate_failures)
    )

    status = "FAILED" if evaluation_failed else "PASSED"

    case_regressions = comparison.get(
        "case_regressions",
        []
    )

    case_regression_text = (
        ", ".join(case_regressions)
        if case_regressions
        else "None"
    )

    baseline = comparison.get("previous_report") or "None"

    lines = [
        "# LLM Evaluation Report",
        "",
        f"**Status:** {status}",
        "",
        "## Evaluation Summary",
        "",
        f"- Prompt version: `{report_data['prompt_version']}`",
        f"- Model: `{report_data['model']}`",
        (
            f"- Passed cases: "
            f"{report_data['passed_cases']}/"
            f"{report_data['total_cases']}"
        ),
        (
            f"- Pass rate: "
            f"{format_percentage(report_data['pass_rate'])}"
        ),
        "",
        "## Baseline Comparison",
        "",
        f"- Baseline report: `{baseline}`",
        (
            "- Shared current pass rate: "
            f"{format_percentage(
                comparison.get('shared_current_pass_rate')
            )}"
        ),
        (
            "- Shared previous pass rate: "
            f"{format_percentage(
                comparison.get('shared_previous_pass_rate')
            )}"
        ),
        (
            "- Pass-rate change: "
            f"{format_percentage(
                comparison.get('pass_rate_change')
            )}"
        ),
        f"- Case regressions: {case_regression_text}",
        (
            "- Regression detected: "
            f"{regression_detected}"
        ),
        "",
        "## Quality Gates",
        "",
        (
            "- Minimum pass rate: "
            f"{format_percentage(
                quality_gates.get('minimum_pass_rate')
            )}"
        ),
        (
            "- Maximum allowed drop: "
            f"{format_percentage(
                quality_gates.get('maximum_drop')
            )}"
        ),
        (
            "- Failures: "
            f"{', '.join(quality_gate_failures)
               if quality_gate_failures else 'None'}"
        ),
        ""
    ]

    lines.extend([
    "## Confusion Matrix",
    "",
    "| Expected \\ Predicted | Billing | Technical | Account | General |",
    "|---|---:|---:|---:|---:|"
    ])

    for expected_category in [
        "billing",
        "technical",
        "account",
        "general"
    ]:
        row = confusion_matrix.get(expected_category, {})

        lines.append(
            "| "
            f"{expected_category.title()} | "
            f"{row.get('billing', 0)} | "
            f"{row.get('technical', 0)} | "
            f"{row.get('account', 0)} | "
            f"{row.get('general', 0)} |"
        )
    lines.extend([
        "## Category Metrics",
        "",
        "| Category | Precision | Recall | F1 |",
        "|---|---:|---:|---:|"
    ])

    for category in [
        "billing",
        "technical",
        "account",
        "general"
    ]:
        metrics = category_metrics.get(category, {})

        precision = metrics.get("precision", 0.0)
        recall = metrics.get("recall", 0.0)
        f1 = metrics.get("f1", 0.0)

        lines.append(
            "| "
            f"{category.title()} | "
            f"{precision:.2f}% | "
            f"{recall:.2f}% | "
            f"{f1:.2f}% |"
        )

    lines.append("")

    lines.append("")

    return "\n".join(lines)
