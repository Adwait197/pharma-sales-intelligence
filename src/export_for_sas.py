"""Export GLP-1 diabetes-segment state shares to CSV for analysis in SAS."""

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import get_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = PROJECT_ROOT / "data" / "processed" / "sas_glp1_state_share.csv"

QUERY = """
    select data_year,
           state_fips,
           state_abbr,
           state_name,
           census_region,
           census_division,
           brand_family,
           trx,
           fills_30day,
           trx_share_in_segment,
           fills_share_in_segment
    from marts.fct_glp1_brand_state_year
    where market_segment = 'glp1_diabetes'
    order by data_year, state_abbr, brand_family
"""


def main():
    with get_engine().connect() as conn:
        df = pd.read_sql(text(QUERY), conn)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    print(f"Wrote {len(df):,} rows to {OUT_FILE}\n")

    # First look at the question SAS will test properly
    mounjaro_2024 = df[(df["data_year"] == 2024) & (df["brand_family"] == "Mounjaro")]
    summary = (
        mounjaro_2024.groupby("census_region")["trx_share_in_segment"]
        .agg(states="count", average="mean", lowest="min", highest="max")
        .round(3)
        .sort_values("average", ascending=False)
    )
    print("Mounjaro share of GLP-1 diabetes prescriptions, 2024, by region:")
    print(summary)


if __name__ == "__main__":
    main()