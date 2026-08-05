from typing import Any

from pydantic import BaseModel, Field, field_validator


class EvaluationRequirements(BaseModel):
    """
    Behavioral requirements that a financial evaluation case
    must satisfy.
    """

    must_be_read_only: bool = True
    must_execute: bool = True
    must_not_request_clarification: bool = True


class GoldenFinancialQueryCase(BaseModel):
    """
    One human-verified financial question used for regression testing.
    """

    id: str
    category: str
    difficulty: str
    question: str

    expected_tables: list[str] = Field(
        default_factory=list
    )

    expected_columns: list[str] = Field(
        default_factory=list
    )

    expected_row_count: int = Field(
        ge=0
    )

    expected_rows: list[dict[str, Any]] = Field(
        default_factory=list
    )

    requirements: EvaluationRequirements = Field(
        default_factory=EvaluationRequirements
    )

    notes: str

    @field_validator(
        "id",
        "category",
        "difficulty",
        "question",
        "notes"
    )
    @classmethod
    def reject_empty_text(
        cls,
        value: str
    ) -> str:
        """
        Reject required text fields that contain only whitespace.
        """
        if not value.strip():
            raise ValueError(
                "Value must not be empty."
            )

        return value.strip()

    @field_validator(
        "expected_tables",
        "expected_columns"
    )
    @classmethod
    def reject_empty_names(
        cls,
        values: list[str]
    ) -> list[str]:
        """
        Reject empty table or column names.
        """
        for value in values:
            if not value.strip():
                raise ValueError(
                    "Table and column names must not be empty."
                )

        return [
            value.strip()
            for value in values
        ]
    