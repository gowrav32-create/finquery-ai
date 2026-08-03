from pydantic import BaseModel, Field, model_validator


class SQLGenerationResult(BaseModel):
    """
    Structured response produced by the LLM SQL generator.

    The model may either:
    - generate a SQL query, or
    - request clarification when the financial question is ambiguous.
    """

    sql: str | None = None
    explanation: str

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    tables_used: list[str] = Field(
        default_factory=list
    )

    columns_used: list[str] = Field(
        default_factory=list
    )

    clarification_needed: bool = False
    clarification_question: str | None = None

    @model_validator(mode="after")
    def validate_sql_or_clarification(
        self
    ) -> "SQLGenerationResult":
        """
        Ensure the response either contains executable SQL or a
        meaningful clarification question.
        """
        if self.clarification_needed:
            if (
                self.clarification_question is None
                or not self.clarification_question.strip()
            ):
                raise ValueError(
                    "A clarification question is required "
                    "when clarification is needed."
                )

            return self

        if self.sql is None or not self.sql.strip():
            raise ValueError(
                "SQL is required when clarification "
                "is not needed."
            )

        return self
    