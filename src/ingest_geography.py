"""Load CMS Part D 'by Geography and Drug' CSVs into raw.geography_drug.

Expects files named geo_YYYY.csv in data/raw/geography/.
Safe to re-run: each year is deleted and reloaded inside one transaction,
so a failed load never leaves a half-loaded year behind.
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import inspect, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "geography"
SCHEMA = "raw"
TABLE = "geography_drug"
FILE_PATTERN = re.compile(r"^geo_(\d{4})\.csv$")


def clean_columns(columns):
    """Lowercase and snake_case column names: 'Tot_Clms ' -> 'tot_clms'."""
    return [re.sub(r"[^0-9a-z]+", "_", c.strip().lower()).strip("_") for c in columns]


def read_year_file(path, year):
    """Read one CSV exactly as delivered (all text) and add lineage columns."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df.columns = clean_columns(df.columns)
    df["data_year"] = year
    df["source_file"] = path.name
    df["loaded_at"] = datetime.now(timezone.utc)
    return df


def main():
    from db import get_engine

    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        sys.exit(f"No CSV files found in {RAW_DIR}")

    badly_named = [f.name for f in files if not FILE_PATTERN.match(f.name)]
    if badly_named:
        sys.exit(f"Rename these to geo_YYYY.csv first: {badly_named}")

    engine = get_engine()

    for path in files:
        year = int(FILE_PATTERN.match(path.name).group(1))
        df = read_year_file(path, year)

        with engine.begin() as conn:
            if inspect(conn).has_table(TABLE, schema=SCHEMA):
                conn.execute(
                    text(f"DELETE FROM {SCHEMA}.{TABLE} WHERE data_year = :y"),
                    {"y": year},
                )
            df.to_sql(
                TABLE, conn, schema=SCHEMA, if_exists="append",
                index=False, chunksize=5000, method="multi",
            )
            loaded = conn.execute(
                text(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE data_year = :y"),
                {"y": year},
            ).scalar()
            if loaded != len(df):
                raise RuntimeError(
                    f"{year}: file has {len(df):,} rows but table has {loaded:,}"
                )

        print(f"{year}: loaded {loaded:,} rows from {path.name}")

    print("\nDone. Verify in psql: SELECT data_year, COUNT(*) FROM raw.geography_drug GROUP BY 1 ORDER BY 1;")


if __name__ == "__main__":
    main()