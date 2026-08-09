"""
Meta Ads Performance Dashboard — entrypoint.
Run with: streamlit run app.py

Uploads the three cycle exports and stores the processed data in
st.session_state so every page under pages/ can access it without
re-uploading. This is the standard pattern for Streamlit multipage apps —
each page in pages/ reruns independently and has no shared memory except
via session_state.
"""

import streamlit as st

from src.load import load_file1, load_file2, load_file3
from src.process import build_campaign_dates, attach_planned_budget

st.set_page_config(page_title="Meta Ads Performance Dashboard", layout="wide")

st.title("Meta Ads Performance Dashboard")
st.caption("Upload this cycle's exports, then use the pages in the sidebar.")

st.sidebar.title("Data Files")
f1_file = st.sidebar.file_uploader("File 1 — Base Performance (Ad, Daily)", type=["xlsx"])
f2_file = st.sidebar.file_uploader("File 2 — Age & Gender (Ad Set, Weekly) — optional", type=["xlsx"])
f3_file = st.sidebar.file_uploader("File 3 — Campaign Budget Lookup", type=["xlsx"])

if not (f1_file and f3_file):
    st.info(
        "Upload **File 1** and **File 3** in the sidebar to get started. "
        "File 2 (Age & Gender) is optional. See docs/meta_export_spec.md for "
        "exact export instructions."
    )
    st.stop()

df1 = load_file1(f1_file)
active_ids = df1["campaign_id"].unique()
budget = load_file3(f3_file, active_ids)
campaign_dates = build_campaign_dates(df1)
df1 = attach_planned_budget(df1, budget, campaign_dates)
df2 = load_file2(f2_file) if f2_file else None

# Shared across pages
st.session_state["df1"] = df1
st.session_state["df2"] = df2
st.session_state["min_date"] = df1["date"].min()
st.session_state["max_date"] = df1["date"].max()

st.success(
    f"Loaded {len(df1):,} rows | "
    f"{df1['campaign_id'].nunique()} campaigns | "
    f"{df1['date'].min().date()} to {df1['date'].max().date()}"
)
st.write("Use the pages in the left sidebar: **Performance Analysis**, **Creative Analysis**, **Funnel Diagnosis**.")
