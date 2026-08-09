import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.process import aggregate, daily_series
from src.analytics import pacing_status, learning_phase_flag, optimization_mismatch, period_delta
from src.formatting import fmt_money, fmt_pct, fmt_num, status_badge, clean_result_label, fmt_results

st.title("Performance Analysis")

if "df1" not in st.session_state:
    st.warning("Upload your files on the main page first.")
    st.stop()

df1 = st.session_state["df1"]
min_date, max_date = st.session_state["min_date"], st.session_state["max_date"]
as_of_date = max_date

# --- Filters ---
date_range = st.sidebar.date_input(
    "Date range", value=(min_date.date(), max_date.date()),
    min_value=min_date.date(), max_value=max_date.date()
)
date_start, date_end = (pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])) \
    if len(date_range) == 2 else (min_date, max_date)

objective_filter = st.sidebar.multiselect(
    "Objective", options=sorted(df1["objective"].dropna().unique()),
    default=sorted(df1["objective"].dropna().unique())
)
df1f = df1[df1["objective"].isin(objective_filter)]

level = st.radio("Level", ["Campaign", "Ad Set", "Ad"], horizontal=True)

working = df1f.copy()
if level in ("Ad Set", "Ad"):
    camp_options = ["All Campaigns"] + sorted(working["campaign_name"].dropna().unique().tolist())
    camp_pick = st.selectbox("Drill into Campaign", camp_options)
    if camp_pick != "All Campaigns":
        working = working[working["campaign_name"] == camp_pick]
if level == "Ad":
    as_options = ["All Ad Sets"] + sorted(working["ad_set_name"].dropna().unique().tolist())
    as_pick = st.selectbox("Drill into Ad Set", as_options)
    if as_pick != "All Ad Sets":
        working = working[working["ad_set_name"] == as_pick]

agg = aggregate(working, level, date_start, date_end)
agg["pacing"] = agg.apply(lambda r: pacing_status(r, as_of_date), axis=1)
agg["learning_flag"] = agg.apply(lambda r: learning_phase_flag(r, as_of_date), axis=1)
agg["status"] = agg["pacing"].apply(status_badge)
agg["result_action"] = agg["result_indicator"].apply(
    lambda lst: clean_result_label(lst[0]) if len(lst) == 1 else ("mixed" if len(lst) > 1 else "—")
)
agg["results_display"] = agg.apply(lambda r: fmt_results(r["results"], r["result_indicator"]), axis=1)

name_col = {"Campaign": "campaign_name", "Ad Set": "ad_set_name", "Ad": "ad_name"}[level]

st.subheader(f"{level} Table")
display_cols = [name_col, "objective", "spend", "planned_budget",
                 "budget_utilization_pct", "pacing", "results_display", "cost_per_result",
                 "ctr", "cpc", "cpm", "frequency", "learning_flag", "status"]
show = agg[display_cols].copy()
show["spend"] = show["spend"].apply(fmt_money)
show["planned_budget"] = show["planned_budget"].apply(fmt_money)
show["budget_utilization_pct"] = show["budget_utilization_pct"].apply(fmt_pct)
show["cost_per_result"] = show["cost_per_result"].apply(fmt_money)
show["ctr"] = show["ctr"].apply(fmt_pct)
show["cpc"] = show["cpc"].apply(fmt_money)
show["cpm"] = show["cpm"].apply(fmt_money)
show["frequency"] = show["frequency"].apply(lambda x: "N/A" if pd.isna(x) else f"{x:.2f}")
show["learning_flag"] = show["learning_flag"].apply(lambda x: "⚠️ Recently edited" if x else "")
show = show.rename(columns={
    name_col: level, "objective": "Objective",
    "spend": "Spend", "planned_budget": "Planned Budget",
    "budget_utilization_pct": "Budget Used %", "pacing": "Pacing",
    "results_display": "Results", "cost_per_result": "Cost / Result", "ctr": "CTR",
    "cpc": "CPC", "cpm": "CPM", "frequency": "Frequency",
    "learning_flag": "Flag", "status": ""
})
st.dataframe(show, use_container_width=True, hide_index=True)

mismatch, indicators = optimization_mismatch(agg)
if mismatch:
    st.warning(
        f"⚠️ These {level.lower()}s are optimizing for **different result types** "
        f"({', '.join(clean_result_label(i) for i in indicators)}). "
        "Cost per Result is not directly comparable across them."
    )

st.divider()
st.subheader("Trend & Period Comparison")
entity_names = agg[name_col].dropna().unique().tolist()

if entity_names:
    selected_entity = st.selectbox(f"Select a {level} to inspect", entity_names)
    compare_days = st.slider("Compare last N days vs prior N days", 3, 21, 7)

    ent_df = working[working[name_col] == selected_entity]
    daily = daily_series(ent_df)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=daily["date"], y=daily["spend"], name="Spend", yaxis="y1", opacity=0.4))
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["results"], name="Results", yaxis="y2", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["cost_per_result"], name="Cost / Result", yaxis="y3", mode="lines+markers"))
    fig.update_layout(
        xaxis=dict(title="Date"),
        yaxis=dict(title="Spend ($)", side="left"),
        yaxis2=dict(title="Results", overlaying="y", side="right"),
        yaxis3=dict(title="Cost/Result", overlaying="y", side="right", position=0.95, showgrid=False),
        legend=dict(orientation="h", y=1.15), height=420,
    )
    st.plotly_chart(fig, use_container_width=True)

    delta_df = period_delta(ent_df, level, max_date, compare_days, aggregate)
    delta_display = delta_df.copy()
    money_metrics = {"Spend", "CPM", "Cost / Result"}
    pct_metrics = {"CTR", "Conv. Rate"}
    delta_display["last"] = delta_display.apply(
        lambda r: fmt_money(r["last"]) if r["metric"] in money_metrics
        else (fmt_pct(r["last"]) if r["metric"] in pct_metrics
              else (f"{r['last']:.2f}" if pd.notna(r["last"]) else "N/A")), axis=1)
    delta_display["prior"] = delta_display.apply(
        lambda r: fmt_money(r["prior"]) if r["metric"] in money_metrics
        else (fmt_pct(r["prior"]) if r["metric"] in pct_metrics
              else (f"{r['prior']:.2f}" if pd.notna(r["prior"]) else "N/A")), axis=1)
    delta_display["pct_change"] = delta_display["pct_change"].apply(
        lambda x: "N/A" if pd.isna(x) else f"{x:+.1f}%")
    delta_display = delta_display.rename(columns={
        "metric": "Metric", "last": f"Last {compare_days}d",
        "prior": f"Prior {compare_days}d", "pct_change": "% Change"
    })
    st.dataframe(delta_display, use_container_width=True, hide_index=True)

st.divider()
st.subheader(f"Compare Multiple {level}s")
compare_picks = st.multiselect(f"Select 2-4 {level.lower()}s to compare", entity_names, max_selections=4)
if len(compare_picks) >= 2:
    comp_agg = agg[agg[name_col].isin(compare_picks)]
    cm_mismatch, cm_ind = optimization_mismatch(comp_agg)
    if cm_mismatch:
        st.warning(
            f"⚠️ Selected items have different result types "
            f"({', '.join(clean_result_label(i) for i in cm_ind)}). "
            "Treat Cost per Result comparisons with caution."
        )
    cols = st.columns(len(compare_picks))
    for i, name in enumerate(compare_picks):
        row = comp_agg[comp_agg[name_col] == name].iloc[0]
        with cols[i]:
            st.markdown(f"**{name}**")
            st.metric("Spend", fmt_money(row["spend"]))
            st.metric("Results", fmt_num(row["results"]))
            st.metric("Cost / Result", fmt_money(row["cost_per_result"]))
            st.metric("Budget Used", fmt_pct(row["budget_utilization_pct"]))
            st.caption(f"Pacing: {status_badge(row['pacing'])} {row['pacing']}")
elif len(compare_picks) == 1:
    st.caption("Pick at least 2 to compare.")
