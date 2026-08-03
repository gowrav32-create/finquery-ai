import json
from types import SimpleNamespace

from src.query_engine import generator
from src.query_engine.generator import generate_financial_sql
from src.query_engine.prompt_config import SQLPromptConfig


def create_prompt_config() -> SQLPromptConfig:
    return SQLPromptConfig(
        version="v1",
        feature_name="financial_sql_generation",
        model="llama3.2:3b",
        temperature=0.0,
        system_prompt=(
            "Generate safe DuckDB SQL using only "
            "the provided database schema."
        )
    )


def test_generates_structured_financial_sql(
    monkeypatch
):
    captured_request = {}

    model_response = {
        "sql": (
            "SELECT ticker, revenue_growth_pct "
            "FROM financial_metrics "
            "WHERE fiscal_year = 2024 "
            "ORDER BY revenue_growth_pct DESC"
        ),
        "explanation": (
            "Returns companies ranked by 2024 "
            "revenue growth."
        ),
        "confidence": 0.96,
        "tables_used": ["financial_metrics"],
        "columns_used": [
            "ticker",
            "revenue_growth_pct",
            "fiscal_year"
        ],
        "clarification_needed": False,
        "clarification_question": None
    }

    def fake_chat(**kwargs):
        captured_request.update(kwargs)

        return SimpleNamespace(
            message=SimpleNamespace(
                content=json.dumps(model_response)
            )
        )

    monkeypatch.setattr(
        generator,
        "chat",
        fake_chat
    )

    result = generate_financial_sql(
        question=(
            "Rank companies by revenue growth "
            "for 2024."
        ),
        schema_context=(
            "TABLE financial_metrics\n"
            "- ticker: VARCHAR\n"
            "- fiscal_year: INTEGER\n"
            "- revenue_growth_pct: DOUBLE"
        ),
        prompt_config=create_prompt_config()
    )

    assert result.sql == model_response["sql"]
    assert result.confidence == 0.96
    assert result.tables_used == [
        "financial_metrics"
    ]
    assert result.clarification_needed is False

    assert captured_request["model"] == (
        "llama3.2:3b"
    )

    assert captured_request["options"] == {
        "temperature": 0.0
    }

    assert (
        "TABLE financial_metrics"
        in captured_request["messages"][1]["content"]
    )

    assert (
        "Rank companies by revenue growth"
        in captured_request["messages"][1]["content"]
    )


def test_returns_structured_clarification(
    monkeypatch
):
    model_response = {
        "sql": None,
        "explanation": (
            "The term best revenue is ambiguous."
        ),
        "confidence": 0.35,
        "tables_used": [],
        "columns_used": [],
        "clarification_needed": True,
        "clarification_question": (
            "Do you mean highest total revenue "
            "or highest revenue growth?"
        )
    }

    def fake_chat(**kwargs):
        return SimpleNamespace(
            message=SimpleNamespace(
                content=json.dumps(model_response)
            )
        )

    monkeypatch.setattr(
        generator,
        "chat",
        fake_chat
    )

    result = generate_financial_sql(
        question=(
            "Which company has the best revenue?"
        ),
        schema_context=(
            "TABLE financial_metrics\n"
            "- ticker: VARCHAR\n"
            "- revenue: DOUBLE\n"
            "- revenue_growth_pct: DOUBLE"
        ),
        prompt_config=create_prompt_config()
    )

    assert result.sql is None
    assert result.clarification_needed is True
    assert result.confidence == 0.35
    assert result.clarification_question == (
        "Do you mean highest total revenue "
        "or highest revenue growth?"
    )
    