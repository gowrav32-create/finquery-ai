from src.query_engine.validator import validate_sql_schema


TEST_SCHEMA = {
    "companies": {
        "ticker": "VARCHAR",
        "company_name": "VARCHAR",
        "sector": "VARCHAR",
        "industry": "VARCHAR",
        "country": "VARCHAR"
    },
    "financial_metrics": {
        "ticker": "VARCHAR",
        "fiscal_year": "INTEGER",
        "revenue": "DOUBLE",
        "revenue_growth_pct": "DOUBLE",
        "operating_margin_pct": "DOUBLE",
        "free_cash_flow": "DOUBLE",
        "return_on_equity_pct": "DOUBLE",
        "debt_to_equity": "DOUBLE"
    },
    "valuation_snapshots": {
        "ticker": "VARCHAR",
        "snapshot_date": "DATE",
        "stock_price": "DOUBLE",
        "market_cap": "DOUBLE",
        "price_to_earnings": "DOUBLE"
    }
}


def test_accepts_valid_table_and_columns():
    result = validate_sql_schema(
        sql="""
            SELECT
                ticker,
                company_name
            FROM companies
            ORDER BY ticker
        """,
        schema=TEST_SCHEMA
    )

    assert result.is_valid is True
    assert result.unknown_tables == []
    assert result.unknown_columns == []


def test_accepts_valid_join_with_aliases():
    result = validate_sql_schema(
        sql="""
            SELECT
                c.ticker,
                c.company_name,
                fm.revenue_growth_pct
            FROM companies AS c
            JOIN financial_metrics AS fm
                ON c.ticker = fm.ticker
            WHERE fm.fiscal_year = 2024
        """,
        schema=TEST_SCHEMA
    )

    assert result.is_valid is True
    assert result.unknown_tables == []
    assert result.unknown_columns == []


def test_detects_hallucinated_table():
    result = validate_sql_schema(
        sql="""
            SELECT ticker
            FROM stock_fundamentals
        """,
        schema=TEST_SCHEMA
    )

    assert result.is_valid is False
    assert result.unknown_tables == [
        "stock_fundamentals"
    ]


def test_detects_hallucinated_column():
    result = validate_sql_schema(
        sql="""
            SELECT
                ticker,
                profit_growth
            FROM financial_metrics
        """,
        schema=TEST_SCHEMA
    )

    assert result.is_valid is False
    assert result.unknown_columns == [
        "profit_growth"
    ]


def test_detects_hallucinated_qualified_column():
    result = validate_sql_schema(
        sql="""
            SELECT
                fm.ticker,
                fm.ebitda_growth
            FROM financial_metrics AS fm
        """,
        schema=TEST_SCHEMA
    )

    assert result.is_valid is False
    assert result.unknown_columns == [
        "fm.ebitda_growth"
    ]


def test_allows_select_star():
    result = validate_sql_schema(
        sql="SELECT * FROM companies",
        schema=TEST_SCHEMA
    )

    assert result.is_valid is True
    assert result.unknown_tables == []
    assert result.unknown_columns == []
    