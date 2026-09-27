# Pharmaceutical Sales Intelligence & Forecasting Platform

End-to-end commercial analytics platform for the diabetes / GLP-1 therapeutic class,
built on real CMS Medicare Part D prescriber-level claims data.

## Business Questions

- Who prescribes each brand, and how is volume concentrated across prescribers?
- How does market share vary across geographies and physician specialties?
- Are regional differences statistically significant, or noise?
- What does the next 12 months of drug-level volume look like?

## Architecture

| Layer | Purpose | Tools |
|-------|---------|-------|
| Ingest | Download and land raw CMS prescriber claims | Python, Pandas |
| Warehouse | Clean, type, and model into a star schema | PostgreSQL, dbt |
| KPI Layer | Prescription volume, market share, prescriber deciles, reach & frequency | SQL |
| Statistics | Hypothesis testing on geographic variation | SAS |
| Forecast | Drug-level time-series forecasting with backtesting | Python, statsmodels |
| Dashboard | Interactive exploration | Streamlit |

## Data Source

CMS Medicare Part D Prescribers — by Provider and Drug (public, de-identified).

## Project Structure


## Setup

```bash
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with your database credentials (see `.env.example`).

## Status

Foundation complete: environment, PostgreSQL warehouse schemas, dbt installed.
Currently building: data ingestion layer.