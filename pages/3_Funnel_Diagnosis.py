import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("Funnel Diagnosis")

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

level = st.radio("Analyze at", ["Account (All)", "Campaign"], horizontal=True)
if level == "Campaign":
    camp_options = sorted(df1["campaign_name"].dropna().unique().tolist())
    pick = st.selectbox("Campaign", camp_options)
    fdf = df1[df1["campaign_name"] == pick]
else:
    fdf = df1

fdf = fdf[(fdf["date"] >= date_start) & (fdf["date"] <= date_end)]

stages = [
    ("Impressions", fdf["impressions"].sum()),
    ("Link Clicks", fdf["link_clicks"].sum()),
    ("Landing Page Views", fdf["landing_page_views"].sum()),
    ("Add to Cart", fdf["add_to_cart"].sum()),
    ("Checkout Initiated", fdf["checkouts_initiated"].sum()),
    ("Purchases", fdf["purchases"].sum()),
    ("Leads", fdf["leads"].sum()),
]
stages = [s for s in stages if pd.notna(s[1]) and s[1] > 0]

fig = go.Figure(go.Funnel(
    y=[s[0] for s in stages], x=[s[1] for s in stages],
    textinfo="value+percent initial"
))
fig.update_layout(height=450)
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Purchases and Leads are shown separately since this account mixes "
    "Sales, Leads, and Awareness objectives with different end goals — "
    "combining them into one 'final conversion' number would be misleading."
)

rows = []
prev = None
for name, val in stages:
    drop = "" if prev is None else (f"{(val/prev*100):.1f}% of prior stage" if prev else "N/A")
    rows.append({"Stage": name, "Volume": f"{val:,.0f}", "Retained from prior stage": drop})
    prev = val
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
