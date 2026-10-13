"""Print a quick profile of a CSV file: shape, columns, blanks, sample values."""

import sys

import pandas as pd


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python src\\profile_csv.py <path-to-csv>")

    df = pd.read_csv(
        sys.argv[1], dtype=str, keep_default_na=False, encoding="utf-8-sig"
    )
    print(f"Rows: {len(df):,}    Columns: {df.shape[1]}\n")
    print(f"{'column':<30}{'distinct':>9}{'blank':>8}   sample values")
    print("-" * 90)

    for col in df.columns:
        distinct = df[col].nunique()
        blank = int((df[col].str.strip() == "").sum())
        sample = ", ".join(df[col].drop_duplicates().head(4)).replace("\n", " ")
        print(f"{col:<30}{distinct:>9,}{blank:>8,}   {sample[:45]}")

    print("\nColumns with 12 or fewer distinct values (full list):")
    for col in df.columns:
        values = sorted(df[col].unique())
        if len(values) <= 12:
            print(f"  {col}: {values}")


if __name__ == "__main__":
    main()