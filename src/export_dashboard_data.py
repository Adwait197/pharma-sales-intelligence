"""Snapshot the two dbt marts into small Parquet files for the Streamlit dashboard.

The dashboard reads these files instead of PostgreSQL, so it runs anywhere,
including Streamlit Community Cloud, which cannot reach your laptop's database.
Re-run this after every dbt build that changes the marts.
"""

from decimal import Decimal
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import get_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "dashboard" / "data"
TABLES = ["fct_glp1_brand_state_year", "fct_glp1_brand_national_year"]


def decimals_to_float(df):
    """PostgreSQL numeric columns arrive as Python Decimal objects. Convert them to floats."""
    for col in df.columns:
        if df[col].map(lambda v: isinstance(v, Decimal)).any():
            df[col] = df[col].astype(float)
    return df


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with get_engine().connect() as conn:
        for table in TABLES:
            df = pd.read_sql(text(f"select * from marts.{table}"), conn)
            df = decimals_to_float(df)
            path = OUT_DIR / f"{table}.parquet"
            df.to_parquet(path, index=False)
            print(f"{table}: {len(df):,} rows -> {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()