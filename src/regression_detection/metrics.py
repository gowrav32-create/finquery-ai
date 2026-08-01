def build_confusion_matrix(
    results: list[dict],
    categories: list[str]
) -> dict[str, dict[str, int]]:
    matrix = {
        expected: {
            predicted: 0
            for predicted in categories
        }
        for expected in categories
    }

    for result in results:
        expected = result["expected_category"]
        predicted = result["predicted_category"]

        matrix[expected][predicted] += 1

    return matrix

def calculate_category_metrics(
    confusion_matrix: dict[str, dict[str, int]]
) -> dict[str, dict[str, float]]:
    metrics = {}

    categories = list(confusion_matrix.keys())

    for category in categories:
        true_positive = confusion_matrix[category][category]

        false_positive = sum(
            confusion_matrix[expected][category]
            for expected in categories
            if expected != category
        )

        false_negative = sum(
            confusion_matrix[category][predicted]
            for predicted in categories
            if predicted != category
        )

        precision_denominator = (
            true_positive + false_positive
        )

        recall_denominator = (
            true_positive + false_negative
        )

        precision = (
            true_positive / precision_denominator
            if precision_denominator > 0
            else 0.0
        )

        recall = (
            true_positive / recall_denominator
            if recall_denominator > 0
            else 0.0
        )

        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall > 0
            else 0.0
        )

        metrics[category] = {
            "precision": round(precision * 100, 2),
            "recall": round(recall * 100, 2),
            "f1": round(f1 * 100, 2)
        }

    return metrics
