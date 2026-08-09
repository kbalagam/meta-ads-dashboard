import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.process import aggregate, daily_series
from src.formatting import fmt_money, fmt_pct

st.title("Creative Analysis — Ad Fatigue Tracking")
st.caption(
    "Simplified view: Meta's export doesn't include creative metadata "
    "(format/theme/hook/CTA), so this page tracks fatigue signals at the "
    "Ad level using performance data only. Add a creative-tagging file "
    "later to unlock the full creative-pattern breakdown."
)

if "df1" not in st.session_state:
    st.warning("Upload your files on the main page first.")
    st.stop()

df1 = st.session_state["df1"]
min_date, max_date = st.session_state["min_date"], st.session_state["max_date"]

date_range = st.sidebar.date_input(
    "Date range", value=(min_date.date(), max_date.date()),
    min_value=min_date.date(), max_value=max_date.date()
)
date_start, date_end = (pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])) \
    if len(date_range) == 2 else (min_date, max_date)

ad_agg = aggregate(df1, "Ad", date_start, date_end)
display_cols = ["ad_name", "campaign_name", "spend", "frequency", "ctr", "cpm", "cost_per_result", "results"]
show = ad_agg[display_cols].copy()
show["spend"] = show["spend"].apply(fmt_money)
show["ctr"] = show["ctr"].apply(fmt_pct)
show["cpm"] = show["cpm"].apply(fmt_money)
show["cost_per_result"] = show["cost_per_result"].apply(fmt_money)
show["frequency"] = show["frequency"].apply(lambda x: "N/A" if pd.isna(x) else f"{x:.2f}")
show = show.rename(columns={
    "ad_name": "Ad", "campaign_name": "Campaign", "spend": "Spend",
    "frequency": "Frequency", "ctr": "CTR", "cpm": "CPM",
    "cost_per_result": "Cost / Result", "results": "Results"
})
st.dataframe(show, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Fatigue Trend for a Selected Ad")
ad_names = ad_agg["ad_name"].dropna().unique().tolist()
if ad_names:
    pick = st.selectbox("Select an Ad", ad_names)
    ad_daily = daily_series(df1[df1["ad_name"] == pick])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ad_daily["date"], y=ad_daily["frequency"], name="Frequency", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=ad_daily["date"], y=ad_daily["ctr"], name="CTR (%)", mode="lines+markers", yaxis="y2"))
    fig.add_trace(go.Scatter(x=ad_daily["date"], y=ad_daily["cost_per_result"], name="Cost/Result", mode="lines+markers", yaxis="y3"))
    fig.update_layout(
        yaxis=dict(title="Frequency"),
        yaxis2=dict(title="CTR (%)", overlaying="y", side="right"),
        yaxis3=dict(title="Cost/Result", overlaying="y", side="right", position=0.9, showgrid=False),
        legend=dict(orientation="h", y=1.15), height=420,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Watch for: Frequency rising while CTR falls and Cost/Result rises — "
        "a classic fatigue or audience-saturation pattern."
    )
