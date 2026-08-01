from pathlib import Path

import duckdb


def build_financial_database(database_path: Path) -> None:
    """
    Create the FinQuery AI financial database and its core tables.

    The database is intentionally separated into:
    - company reference data
    - historical annual financial statements
    - point-in-time valuation data
    """
    database_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with duckdb.connect(str(database_path)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS companies (
                ticker VARCHAR PRIMARY KEY,
                company_name VARCHAR NOT NULL,
                sector VARCHAR NOT NULL,
                industry VARCHAR NOT NULL,
                country VARCHAR NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS annual_financials (
                ticker VARCHAR NOT NULL,
                fiscal_year INTEGER NOT NULL,
                revenue DOUBLE NOT NULL,
                operating_income DOUBLE NOT NULL,
                net_income DOUBLE NOT NULL,
                total_assets DOUBLE NOT NULL,
                total_debt DOUBLE NOT NULL,
                shareholder_equity DOUBLE NOT NULL,
                operating_cash_flow DOUBLE NOT NULL,
                capital_expenditures DOUBLE NOT NULL,
                PRIMARY KEY (ticker, fiscal_year)
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS valuation_snapshots (
                ticker VARCHAR NOT NULL,
                snapshot_date DATE NOT NULL,
                stock_price DOUBLE NOT NULL,
                market_cap DOUBLE NOT NULL,
                enterprise_value DOUBLE NOT NULL,
                price_to_earnings DOUBLE,
                price_to_sales DOUBLE,
                enterprise_value_to_ebitda DOUBLE,
                PRIMARY KEY (ticker, snapshot_date)
            )
            """
        )

def seed_demo_data(database_path: Path) -> None:
    """
    Insert deterministic demonstration data used for development,
    automated tests, and financial-query examples.

    The values are illustrative and do not represent actual companies.
    """
    companies = [
        (
            "NSS",
            "Northstar Software",
            "Technology",
            "Enterprise Software",
            "United States"
        ),
        (
            "ART",
            "Apex Retail",
            "Consumer Cyclical",
            "Specialty Retail",
            "United States"
        ),
        (
            "HEN",
            "Harbor Energy",
            "Energy",
            "Integrated Energy",
            "United States"
        ),
        (
            "MFB",
            "Metro Financial Bank",
            "Financial Services",
            "Regional Banking",
            "United States"
        )
    ]

    annual_financials = [
        # Northstar Software
        ("NSS", 2022, 8000, 1600, 1200, 14000, 2500, 7500, 1800, 400),
        ("NSS", 2023, 9600, 2100, 1600, 15800, 2300, 8900, 2300, 500),
        ("NSS", 2024, 11800, 2900, 2200, 18100, 2000, 10800, 3100, 650),

        # Apex Retail
        ("ART", 2022, 15000, 900, 500, 12000, 4200, 3800, 1100, 700),
        ("ART", 2023, 16200, 850, 420, 12600, 4600, 3600, 980, 750),
        ("ART", 2024, 17100, 1000, 560, 13200, 4400, 4100, 1250, 800),

        # Harbor Energy
        ("HEN", 2022, 21000, 3600, 2500, 30000, 9000, 14000, 4200, 2100),
        ("HEN", 2023, 19500, 2800, 1900, 29400, 8500, 14300, 3500, 1900),
        ("HEN", 2024, 22500, 3900, 2700, 31500, 7900, 15800, 4700, 2200),

        # Metro Financial Bank
        ("MFB", 2022, 6200, 1700, 1100, 52000, 18000, 7200, 1500, 300),
        ("MFB", 2023, 6800, 1900, 1250, 55800, 19500, 7600, 1700, 350),
        ("MFB", 2024, 7500, 2250, 1480, 60100, 20500, 8300, 1950, 400)
    ]

    valuation_snapshots = [
        (
            "NSS",
            "2025-01-02",
            142.50,
            72000,
            73500,
            32.73,
            6.10,
            21.40
        ),
        (
            "ART",
            "2025-01-02",
            48.20,
            18400,
            22100,
            18.50,
            1.08,
            9.60
        ),
        (
            "HEN",
            "2025-01-02",
            76.40,
            42000,
            47000,
            15.56,
            1.87,
            7.80
        ),
        (
            "MFB",
            "2025-01-02",
            39.80,
            12600,
            30800,
            8.51,
            1.68,
            6.90
        )
    ]

    with duckdb.connect(str(database_path)) as connection:
        connection.executemany(
            """
            INSERT OR REPLACE INTO companies
            VALUES (?, ?, ?, ?, ?)
            """,
            companies
        )

        connection.executemany(
            """
            INSERT OR REPLACE INTO annual_financials
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            annual_financials
        )

        connection.executemany(
            """
            INSERT OR REPLACE INTO valuation_snapshots
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            valuation_snapshots
        )

def create_financial_metrics_view(
    database_path: Path
) -> None:
    """
    Create an analytical view containing calculated financial metrics.

    The view keeps the original financial-statement values and adds
    commonly used investment-analysis measures.
    """
    with duckdb.connect(str(database_path)) as connection:
        connection.execute(
            """
            CREATE OR REPLACE VIEW financial_metrics AS

            WITH financials_with_prior_year AS (
                SELECT
                    ticker,
                    fiscal_year,
                    revenue,
                    operating_income,
                    net_income,
                    total_assets,
                    total_debt,
                    shareholder_equity,
                    operating_cash_flow,
                    capital_expenditures,

                    LAG(revenue) OVER (
                        PARTITION BY ticker
                        ORDER BY fiscal_year
                    ) AS prior_year_revenue

                FROM annual_financials
            )

            SELECT
                ticker,
                fiscal_year,
                revenue,
                operating_income,
                net_income,
                total_assets,
                total_debt,
                shareholder_equity,
                operating_cash_flow,
                capital_expenditures,

                ROUND(
                    CASE
                        WHEN prior_year_revenue IS NULL
                             OR prior_year_revenue = 0
                        THEN NULL
                        ELSE (
                            (
                                revenue - prior_year_revenue
                            ) / prior_year_revenue
                        ) * 100
                    END,
                    2
                ) AS revenue_growth_pct,

                ROUND(
                    (
                        operating_income
                        / NULLIF(revenue, 0)
                    ) * 100,
                    2
                ) AS operating_margin_pct,

                ROUND(
                    (
                        net_income
                        / NULLIF(revenue, 0)
                    ) * 100,
                    2
                ) AS net_margin_pct,

                ROUND(
                    operating_cash_flow
                    - capital_expenditures,
                    2
                ) AS free_cash_flow,

                ROUND(
                    (
                        net_income
                        / NULLIF(shareholder_equity, 0)
                    ) * 100,
                    2
                ) AS return_on_equity_pct,

                ROUND(
                    total_debt
                    / NULLIF(shareholder_equity, 0),
                    2
                ) AS debt_to_equity

            FROM financials_with_prior_year
            """
        )
