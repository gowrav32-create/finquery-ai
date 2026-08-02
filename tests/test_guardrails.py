import pytest

from src.query_engine.guardrails import check_sql_safety


def test_allows_read_only_select_query():
    result = check_sql_safety(
        """
        SELECT
            ticker,
            revenue_growth_pct
        FROM financial_metrics
        WHERE fiscal_year = 2024
        """
    )

    assert result.is_safe is True
    assert result.violations == []


def test_allows_read_only_common_table_expression():
    result = check_sql_safety(
        """
        WITH growing_companies AS (
            SELECT
                ticker,
                revenue_growth_pct
            FROM financial_metrics
            WHERE revenue_growth_pct > 10
        )
        SELECT *
        FROM growing_companies
        """
    )

    assert result.is_safe is True
    assert result.violations == []


@pytest.mark.parametrize(
    "unsafe_sql",
    [
        "INSERT INTO companies VALUES ('BAD', 'Bad Company', 'X', 'X', 'X')",
        "UPDATE companies SET company_name = 'Changed' WHERE ticker = 'NSS'",
        "DELETE FROM companies WHERE ticker = 'NSS'",
        "DROP TABLE companies",
        "CREATE TABLE unsafe_table (id INTEGER)",
        "ALTER TABLE companies ADD COLUMN unsafe_column VARCHAR"
    ]
)
def test_blocks_destructive_sql_operations(unsafe_sql):
    result = check_sql_safety(unsafe_sql)

    assert result.is_safe is False
    assert "non_read_only_statement" in result.violations


def test_blocks_multiple_sql_statements():
    result = check_sql_safety(
        """
        SELECT * FROM companies;
        DROP TABLE companies;
        """
    )

    assert result.is_safe is False
    assert "multiple_statements" in result.violations


def test_blocks_invalid_sql():
    result = check_sql_safety(
        "SELECT FROM WHERE"
    )

    assert result.is_safe is False
    assert "invalid_sql" in result.violations
    