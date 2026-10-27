# Data Dictionary

## Source

CMS Medicare Part D Prescribers, public use files.
Coverage: 2013-2024. Published with an approximately 18-month lag.

Two datasets are used:

| Dataset | Grain | Used for |
|---------|-------|----------|
| by Geography and Drug | state x drug x year | Trends, market share, geographic variation, forecasting |
| by Provider and Drug | prescriber x drug x year | Prescriber concentration, deciles, specialty mix |

## Columns: Provider and Drug

| Column | Type | Meaning | Commercial term |
|--------|------|---------|-----------------|
| PRSCRBR_NPI | number | Prescriber National Provider Identifier | HCP key |
| PRSCRBR_LAST_ORG_NAME | text | Prescriber last or organization name | |
| PRSCRBR_FIRST_NAME | text | Prescriber first name | |
| PRSCRBR_CITY | text | Practice city | |
| PRSCRBR_STATE_ABRVTN | text | Practice state code | Geography |
| PRSCRBR_STATE_FIPS | number | State FIPS code | Geography join key |
| PRSCRBR_TYPE | text | Prescriber specialty | Specialty segment |
| PRSCRBR_TYPE_SRC | text | Source of the specialty value | |
| BRND_NAME | text | Brand name | Brand |
| GNRC_NAME | text | Generic / molecule name | Molecule |
| TOT_CLMS | number | Total claims including refills | TRx |
| TOT_30DAY_FILLS | number | Claims standardized to 30-day equivalents | Normalized volume |
| TOT_DAY_SUPLY | number | Total days supplied | Duration |
| TOT_DRUG_CST | number | Total cost, all payers | Revenue proxy |
| TOT_BENES | number | Distinct beneficiaries | Patients |
| GE65_* | mixed | Same metrics restricted to age 65+ | Age segment |
| GE65_SPRSN_FLAG | text | Suppression indicator for claim counts | Data quality |
| GE65_BENE_SPRSN_FLAG | text | Suppression indicator for beneficiary counts | Data quality |

## Derived metrics

| Metric | Definition | Notes |
|--------|------------|-------|
| TRx | SUM(TOT_CLMS) | Direct measure |
| Writers | COUNT(DISTINCT PRSCRBR_NPI) where TOT_CLMS > 0 | Reach |
| Reach | Writers as a share of all prescribers in the class | Breadth of adoption |
| Frequency | TRx / Writers | Depth of adoption |
| Market share | Brand TRx / Class TRx | Within defined class |
| Cost per claim | TOT_DRUG_CST / TOT_CLMS | Not a true net price |
| New patient proxy | Year-over-year change in TOT_BENES | PROXY ONLY, not NRx |

## Known limitations

1. **No NRx.** CMS reports annual totals with no new-versus-refill split.
   All volume metrics here are TRx. The new patient proxy is labelled as a proxy.
2. **Suppression.** Cells with counts of 1-10 are redacted. Blank does not mean zero.
   Treating blanks as zero understates small states, rare specialties, and new launches.
3. **Medicare only.** Excludes commercial insurance, Medicaid, and cash. Skews older.
4. **Weight-loss indications excluded.** Part D historically did not cover drugs
   prescribed for weight loss, so Wegovy and Saxenda are largely absent while
   Ozempic is well represented.
5. **Cost is not net price.** TOT_DRUG_CST excludes manufacturer rebates, which are
   substantial and confidential in this category.
6. **Annual grain.** No monthly seasonality is observable.
7. **Unknown state rows.** 29 state-level rows (27 in 2020, 1 in 2023, 1 in 2024)
   have no state code or name. They total about 1,700 claims and include no GLP-1
   drugs. They are kept in staging, excluded from state-level comparisons, and
   monitored by a dbt test that warns above 0 rows and fails above 100.

## Drug universe: Type 2 Diabetes

GLP-1 receptor agonists: Ozempic, Mounjaro, Trulicity, Rybelsus, Victoza, Bydureon, Byetta
SGLT2 inhibitors: Jardiance, Farxiga, Invokana
DPP-4 inhibitors: Januvia, Tradjenta, Onglyza
Insulins: Lantus, Basaglar, Tresiba, Toujeo, Levemir, Humalog, Novolog
Older generics: metformin, glipizide, glyburide, glimepiride