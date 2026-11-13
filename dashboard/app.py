"""GLP-1 Market Intelligence dashboard.

Reads two small Parquet snapshots of the dbt marts (made by src/export_dashboard_data.py),
so it runs without a database connection and can be deployed as is.

Run from the project root:
    streamlit run dashboard/app.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats

DATA_DIR = Path(__file__).resolve().parent / "data"

st.set_page_config(page_title="GLP-1 Market Intelligence", layout="wide")

# ---------------------------------------------------------------------------
# Colours. Each brand keeps the same colour whatever the filters show.
# Palette validated for colour-blind separation in both light and dark mode.
# ---------------------------------------------------------------------------
PALETTE = {
    "light": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6"],
    "dark": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#0ca30c", "#9085e9"],
}
OTHER_COLOUR = {"light": "#a3a29c", "dark": "#6b6a65"}
SURFACE = {"light": "#ffffff", "dark": "#0e1117"}
SEQUENTIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

# Brand order sets colour slots. Brands not listed fold into "Other".
SEGMENT_BRANDS = {
    "glp1_diabetes": ["Ozempic", "Mounjaro", "Trulicity", "Victoza", "Rybelsus", "Bydureon", "Byetta"],
    "glp1_obesity": ["Wegovy", "Zepbound", "Saxenda"],
    "glp1_insulin_combo": ["Soliqua", "Xultophy"],
}
SEGMENT_LABELS = {
    "glp1_diabetes": "Type 2 diabetes",
    "glp1_obesity": "Obesity",
    "glp1_insulin_combo": "Insulin + GLP-1 combinations",
}
REGION_ORDER = ["South", "Midwest", "West", "Northeast"]
LILLY_BRANDS = ["Mounjaro", "Trulicity"]


def theme_mode():
    """Return 'dark' or 'light' to match the viewer's Streamlit theme."""
    try:
        return "dark" if st.context.theme.type == "dark" else "light"
    except Exception:
        return "light"


MODE = theme_mode()


def colour_map(segment):
    brands = SEGMENT_BRANDS[segment]
    mapping = dict(zip(brands, PALETTE[MODE]))
    mapping["Other"] = OTHER_COLOUR[MODE]
    return mapping


def brand_group(series, segment):
    keep = set(SEGMENT_BRANDS[segment])
    return series.where(series.isin(keep), "Other")


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    national = pd.read_parquet(DATA_DIR / "fct_glp1_brand_national_year.parquet")
    state = pd.read_parquet(DATA_DIR / "fct_glp1_brand_state_year.parquet")
    return national, state


def region_test(df, value_col):
    """One-way ANOVA and Kruskal-Wallis of a value across Census regions."""
    groups = [g[value_col].dropna().to_numpy() for _, g in df.groupby("census_region")]
    groups = [g for g in groups if len(g) >= 2]
    if len(groups) < 2:
        return None
    values = np.concatenate(groups)
    grand_mean = values.mean()
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    ss_total = ((values - grand_mean) ** 2).sum()
    f_stat, p_anova = stats.f_oneway(*groups)
    _, p_kruskal = stats.kruskal(*groups)
    return {
        "f": f_stat,
        "p": p_anova,
        "r2": ss_between / ss_total if ss_total else float("nan"),
        "p_kruskal": p_kruskal,
        "n": len(values),
        "groups": len(groups),
    }


def fmt_p(p):
    """Format a p-value for reading: very small values show as p < 0.0001."""
    return "p < 0.0001" if p < 0.0001 else f"p = {p:.4f}"


def describe_test(result, subject):
    if result is None:
        return "Not enough states with data to test."
    verdict = (
        f"**The regional difference is statistically significant** ({fmt_p(result['p'])}). "
        f"Region explains about {result['r2']:.0%} of the variation between states."
        if result["p"] < 0.05
        else f"**No significant regional difference** (p = {result['p']:.2f})."
    )
    return (
        f"{verdict}  \n"
        f"One-way ANOVA F = {result['f']:.2f} across {result['groups']} regions and "
        f"{result['n']} states. Kruskal-Wallis {fmt_p(result['p_kruskal'])}. "
        f"Subject: {subject}."
    )


def region_summary(df, value_col):
    summary = (
        df.groupby("census_region")[value_col]
        .agg(states="count", average="mean", lowest="min", highest="max")
        .reindex(REGION_ORDER)
        .dropna(how="all")
        .round(1)
    )
    summary.index.name = "Region"
    return summary


def style_lines(fig):
    fig.update_traces(line={"width": 2}, marker={"size": 8})
    fig.update_layout(
        hovermode="x unified",
        legend_title_text="",
        margin={"l": 10, "r": 10, "t": 40, "b": 10},
    )
    return fig


national, state = load_data()

# ---------------------------------------------------------------------------
# Header and filters
# ---------------------------------------------------------------------------
st.title("GLP-1 Market Intelligence")
st.caption(
    "Medicare Part D prescriptions, 2013 to 2024. Source: CMS Medicare Part D Prescribers by "
    "Geography and Drug. Built with PostgreSQL, dbt, SAS and Streamlit."
)

filter_segment, filter_year, _ = st.columns([2, 1, 3])
segment = filter_segment.selectbox(
    "Market segment",
    options=list(SEGMENT_LABELS),
    format_func=SEGMENT_LABELS.get,
    key="segment",
)
seg_national = national[national["market_segment"] == segment].copy()
seg_state = state[state["market_segment"] == segment].copy()
years = sorted(seg_national["data_year"].unique())
year = filter_year.selectbox("Year", options=years, index=len(years) - 1, key="year")

seg_national["brand"] = brand_group(seg_national["brand_family"], segment)
seg_state["brand"] = brand_group(seg_state["brand_family"], segment)
colours = colour_map(segment)
brand_order = [b for b in SEGMENT_BRANDS[segment] + ["Other"] if b in set(seg_national["brand"])]

# ---------------------------------------------------------------------------
# Headline numbers for the selected year
# ---------------------------------------------------------------------------
by_brand_year = (
    seg_national.groupby(["data_year", "brand"], as_index=False)[["trx", "drug_cost"]].sum()
)
totals = by_brand_year.groupby("data_year")[["trx", "drug_cost"]].sum()
this_year = by_brand_year[by_brand_year["data_year"] == year].sort_values("trx", ascending=False)
year_trx = totals.loc[year, "trx"]
prior_trx = totals["trx"].get(year - 1)
leader = this_year.iloc[0]

tile_1, tile_2, tile_3, tile_4 = st.columns(4)
tile_1.metric(
    "Prescriptions (TRx)",
    f"{year_trx / 1e6:.2f} M",
    delta=f"{year_trx / prior_trx - 1:+.0%} vs {year - 1}" if prior_trx else None,
)
tile_2.metric(f"Leading brand: {leader['brand']}", f"{leader['trx'] / year_trx:.1%} share")
tile_3.metric("Drug cost", f"${totals.loc[year, 'drug_cost'] / 1e9:.2f} B")
tile_4.metric("Cost per prescription", f"${totals.loc[year, 'drug_cost'] / year_trx:,.0f}")

tab_trend, tab_states, tab_lilly, tab_about = st.tabs(
    ["National trend", "By state", "Lilly portfolio", "About the data"]
)

# ---------------------------------------------------------------------------
# Tab 1: national trend
# ---------------------------------------------------------------------------
with tab_trend:
    trend = by_brand_year.copy()
    trend["share_pct"] = trend["trx"] / trend.groupby("data_year")["trx"].transform("sum") * 100
    trend["trx_m"] = trend["trx"] / 1e6

    left, right = st.columns(2)
    fig_trx = px.line(
        trend,
        x="data_year",
        y="trx_m",
        color="brand",
        markers=True,
        category_orders={"brand": brand_order},
        color_discrete_map=colours,
        labels={"data_year": "Year", "trx_m": "Prescriptions (millions)", "brand": "Brand"},
        title="Prescriptions by brand",
    )
    fig_trx.update_traces(hovertemplate="%{y:.2f} M")
    left.plotly_chart(style_lines(fig_trx), width="stretch")

    fig_share = px.line(
        trend,
        x="data_year",
        y="share_pct",
        color="brand",
        markers=True,
        category_orders={"brand": brand_order},
        color_discrete_map=colours,
        labels={"data_year": "Year", "share_pct": "Share of segment prescriptions (%)", "brand": "Brand"},
        title="Market share by brand",
    )
    fig_share.update_traces(hovertemplate="%{y:.1f}%")
    right.plotly_chart(style_lines(fig_share), width="stretch")

    st.caption(
        "Brands are grouped by family: Victoza 2-Pak and 3-Pak count as Victoza, and the three "
        "Bydureon versions count as Bydureon. Smaller brands are grouped as Other."
    )
    with st.expander("View data"):
        table = trend.pivot(index="data_year", columns="brand", values="share_pct").round(1)
        table = table[[b for b in brand_order if b in table.columns]]
        table.index.name = "Year"
        st.dataframe(table, width="stretch")

# ---------------------------------------------------------------------------
# Tab 2: by state
# ---------------------------------------------------------------------------
with tab_states:
    year_state = seg_state[seg_state["data_year"] == year].copy()
    brands_here = [b for b in SEGMENT_BRANDS[segment] if b in set(year_state["brand_family"])]

    if not brands_here:
        st.info(f"No state-level data for this segment in {year}.")
    else:
        default_brand = "Mounjaro" if "Mounjaro" in brands_here else brands_here[0]
        brand = st.selectbox("Brand", brands_here, index=brands_here.index(default_brand), key="state_brand")
        one = year_state[year_state["brand_family"] == brand].copy()
        one["share_pct"] = one["trx_share_in_segment"] * 100

        map_col, test_col = st.columns([3, 2])
        scale = SEQUENTIAL if MODE == "light" else SEQUENTIAL[::-1]
        fig_map = px.choropleth(
            one,
            locations="state_abbr",
            locationmode="USA-states",
            color="share_pct",
            scope="usa",
            color_continuous_scale=scale,
            hover_name="state_name",
            hover_data={"state_abbr": False, "census_region": True, "share_pct": ":.1f"},
            labels={"share_pct": "Share (%)", "census_region": "Region"},
            title=f"{brand} share of {SEGMENT_LABELS[segment].lower()} prescriptions, {year}",
        )
        fig_map.update_geos(bgcolor="rgba(0,0,0,0)", showlakes=False)
        fig_map.update_layout(margin={"l": 0, "r": 0, "t": 40, "b": 0})
        map_col.plotly_chart(fig_map, width="stretch")

        with test_col:
            st.subheader("Is the regional gap real?")
            st.markdown(describe_test(region_test(one, "share_pct"), f"{brand} share, {year}"))
            st.dataframe(region_summary(one, "share_pct"), width="stretch")
            st.caption(
                "Averages count every state equally. Pairwise comparisons (Tukey) were run in "
                "SAS; see sas/ and docs/findings.md."
            )

        with st.expander("View all states"):
            ranked = (
                one[["state_name", "census_region", "share_pct", "trx"]]
                .sort_values("share_pct", ascending=False)
                .rename(columns={
                    "state_name": "State", "census_region": "Region",
                    "share_pct": "Share (%)", "trx": "Prescriptions",
                })
                .round({"Share (%)": 1})
            )
            st.dataframe(ranked, hide_index=True, width="stretch")

# ---------------------------------------------------------------------------
# Tab 3: the Lilly portfolio finding
# ---------------------------------------------------------------------------
with tab_lilly:
    st.subheader("Where did Mounjaro's Southern share come from?")
    year_state = seg_state[seg_state["data_year"] == year]

    if segment != "glp1_diabetes":
        st.info("This analysis covers the Type 2 diabetes segment. Choose it in the filter above.")
    elif "Mounjaro" not in set(year_state["brand_family"]):
        st.info(f"Mounjaro launched in 2022, so there is nothing to compare in {year}. Choose 2022 or later.")
    else:
        per_state = (
            year_state.pivot_table(index=["state_abbr", "census_region"], columns="brand_family",
                                   values="trx", aggfunc="sum", fill_value=0)
            .reset_index()
        )
        brand_cols = [c for c in per_state.columns if c not in ("state_abbr", "census_region")]
        per_state["segment_trx"] = per_state[brand_cols].sum(axis=1)
        for col in ["Mounjaro", "Trulicity", "Ozempic"]:
            if col not in per_state:
                per_state[col] = 0
        per_state["lilly_trx"] = per_state["Mounjaro"] + per_state["Trulicity"]
        per_state["Mounjaro share"] = per_state["Mounjaro"] / per_state["segment_trx"] * 100
        per_state["Trulicity share"] = per_state["Trulicity"] / per_state["segment_trx"] * 100
        per_state["Ozempic share"] = per_state["Ozempic"] / per_state["segment_trx"] * 100
        per_state["All other share"] = 100 - per_state[["Mounjaro share", "Trulicity share", "Ozempic share"]].sum(axis=1)
        per_state["lilly_share"] = per_state["lilly_trx"] / per_state["segment_trx"] * 100
        per_state["mounjaro_pct_of_lilly"] = per_state["Mounjaro"] / per_state["lilly_trx"] * 100

        mix = (
            per_state.groupby("census_region")[["Mounjaro share", "Trulicity share", "Ozempic share", "All other share"]]
            .mean()
            .reindex(REGION_ORDER)
            .dropna(how="all")
            .reset_index()
            .melt(id_vars="census_region", var_name="part", value_name="share")
        )
        mix["part"] = mix["part"].str.replace(" share", "", regex=False)
        part_colours = {
            "Mounjaro": colours["Mounjaro"],
            "Trulicity": colours["Trulicity"],
            "Ozempic": colours["Ozempic"],
            "All other": OTHER_COLOUR[MODE],
        }
        fig_mix = px.bar(
            mix,
            x="share",
            y="census_region",
            color="part",
            orientation="h",
            text="share",
            category_orders={"census_region": REGION_ORDER, "part": list(part_colours)},
            color_discrete_map=part_colours,
            labels={"share": "Average state share (%)", "census_region": "", "part": ""},
            title=f"Average state share of diabetes GLP-1 prescriptions by region, {year}",
        )
        fig_mix.update_traces(
            texttemplate="%{x:.1f}",
            textposition="inside",
            marker_line_width=2,
            marker_line_color=SURFACE[MODE],
            hovertemplate="%{y}: %{x:.1f}%<extra>%{fullData.name}</extra>",
        )
        fig_mix.update_layout(barmode="stack", legend_title_text="", margin={"l": 10, "r": 10, "t": 40, "b": 10})
        st.plotly_chart(fig_mix, width="stretch")

        left, right = st.columns(2)
        with left:
            st.markdown("**Test 1: Lilly's combined share (Mounjaro + Trulicity)**")
            st.markdown(describe_test(region_test(per_state, "lilly_share"), f"Lilly combined share, {year}"))
            st.dataframe(region_summary(per_state, "lilly_share"), width="stretch")
        with right:
            st.markdown("**Test 2: Mounjaro's share of Lilly's prescriptions**")
            st.markdown(describe_test(region_test(per_state, "mounjaro_pct_of_lilly"), f"Mounjaro share of Lilly, {year}"))
            st.dataframe(region_summary(per_state, "mounjaro_pct_of_lilly"), width="stretch")

        st.markdown(
            "**Reading it:** if Lilly's combined share is flat across regions while Mounjaro's share "
            "of Lilly varies, the regional pattern is a shift inside Lilly's own portfolio rather "
            "than share taken from Ozempic. In 2024 both held (SAS: p = 0.71 and p = 0.0003). "
            "State totals show the mix of prescriptions, not individual patients switching."
        )

# ---------------------------------------------------------------------------
# Tab 4: about the data
# ---------------------------------------------------------------------------
with tab_about:
    st.markdown(
        """
**Source.** CMS Medicare Part D Prescribers by Geography and Drug, 2013 to 2024, loaded raw into
PostgreSQL, then cleaned, tested and aggregated with dbt (28 automated tests).

**What the numbers mean**
- **Prescriptions (TRx)** are claims, including refills. CMS does not separate new prescriptions (NRx).
- **Share** is a brand's prescriptions divided by all prescriptions in its segment, in the same place and year.
- **Brand families** combine pack sizes and devices of the same drug.
- **Drug cost** is what Medicare, patients and other payers paid before manufacturer rebates, so it is not net revenue.

**Limits**
- Medicare Part D only. Commercial insurance, Medicaid and cash prescriptions are not included.
- CMS hides counts from 1 to 10 to protect privacy, so very small markets are understated.
- State views cover the 50 states and DC. Territories, Armed Forces and unknown locations are excluded.
- Regional tests treat each state as one observation. Neighbouring states tend to behave alike, so p-values may look slightly stronger than they are.
- State totals show where prescriptions go, not why.
"""
    )