"""
Load layer: read raw Meta export files and normalize them into clean,
consistently-typed DataFrames. No aggregation or business logic here —
that belongs in process.py and analytics.py.
"""

import pandas as pd
from config import F1_RENAME, F2_RENAME, F3_RENAME


def load_file1(path) -> pd.DataFrame:
    """Base performance export: Ad level, daily breakdown."""
    df = pd.read_excel(path)
    df = df.rename(columns=F1_RENAME)
    df["date"] = pd.to_datetime(df["date"])
    df["campaign_end"] = pd.to_datetime(df["campaign_end"], errors="coerce")
    df["last_significant_edit"] = pd.to_datetime(
        df["last_significant_edit"], errors="coerce", utc=True
    ).dt.tz_localize(None)
    return df


def load_file2(path) -> pd.DataFrame:
    """Age & Gender breakdown: Ad Set level, weekly breakdown."""
    df = pd.read_excel(path)
    df = df.rename(columns=F2_RENAME)
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_file3(path, active_campaign_ids) -> pd.DataFrame:
    """Campaign-level planned budget lookup, filtered to currently active campaigns."""
    df = pd.read_excel(path)
    df = df.rename(columns=F3_RENAME)
    df = df[df["campaign_id"].isin(active_campaign_ids)].copy()
    return df[["campaign_id", "planned_budget", "budget_type"]]
