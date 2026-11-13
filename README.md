# GLP-1 Market Intelligence

**Live dashboard:** https://pharma-market-intelligence.streamlit.app

End-to-end commercial analytics on 12 years of real Medicare Part D prescription data (CMS, 2013 to 2024),
focused on the GLP-1 market: Ozempic, Mounjaro, Trulicity, Victoza and their competitors.

## Key finding

Mounjaro's 2024 share of GLP-1 diabetes prescriptions is significantly higher in Southern states (26.7%)
than in the Northeast (19.2%) and West (20.8%) (one-way ANOVA, p = 0.0014). Follow-up tests with
predictions written in advance show this is a shift **inside Eli Lilly's portfolio**, not share taken from Ozempic:

- Lilly's combined share (Mounjaro + Trulicity) is flat across regions (p = 0.71)
- Ozempic's share is flat across regions, about 48% (p = 0.89)
- Mounjaro's share of Lilly's prescriptions is 60.5% in the South against 43.8% in the Northeast (p = 0.0003, R² = 0.33)

Full results: [docs/findings.md](docs/findings.md)

## Architecture

| Layer | What it does | Tools |
|-------|--------------|-------|
| Ingest | Loads 1.35M rows exactly as delivered; idempotent, one transaction per year, row-count checks | Python, pandas, SQLAlchemy |
| Warehouse | Staging, intermediate and mart layers; market-basket and Census-region seeds | PostgreSQL, dbt |
| Quality | 28 automated tests: nulls, accepted values, grain uniqueness, relationships, unmapped brands | dbt tests |
| Statistics | One-way ANOVA with Levene, Welch, Tukey and Kruskal-Wallis | SAS (PROC GLM, NPAR1WAY, SQL, macros) |
| Dashboard | Brand trends, state map, live regional tests, Lilly portfolio view | Streamlit, Plotly, SciPy |

The dashboard's SciPy tests reproduce the SAS results exactly.

## Design decisions

- **Raw data is never edited.** Every clean table can be rebuilt from the original files.
- **Brand families.** Pack sizes and devices of the same drug are grouped. Without this, raw CMS names make Trulicity look like the 2018 leader when Victoza was.
- **Writers as a range.** Prescriber counts cannot be added across brand names, so families report a low and high bound.
- **Two share measures.** Prescription share and 30-day-fill share, so 30-day and 90-day prescriptions compare fairly.
- **Known data issues are monitored, not hidden.** 29 state rows with no location are excluded from state views and tracked by a warning-level test.

## Data limits

- Medicare Part D only. Volume is TRx (claims including refills); CMS does not publish new prescriptions (NRx).
- Counts from 1 to 10 are suppressed by CMS for privacy.
- State totals show where prescriptions go, not why, and not individual patient switching.

See [docs/data-dictionary.md](docs/data-dictionary.md).

## Project structure

```
src/            Python: ingestion, exports
pharma_dbt/     dbt project: models, seeds, tests, macros
sas/            SAS programs for the regional analysis
dashboard/      Streamlit app and its data snapshot
docs/           Data dictionary and findings
```

## Run it locally

```bash
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

The dashboard runs from the snapshot in `dashboard/data/`. Rebuilding the warehouse needs PostgreSQL
and a `.env` file (see `.env.example`).

## Status

Done: ingestion, dbt warehouse, tests, SAS analysis, dashboard. Next: brand-level forecasting.