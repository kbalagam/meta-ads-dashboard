"""
Process layer: joins, hierarchy aggregation, and derived-metric calculation.

Ratio metrics (CTR, CPC, CPM, Cost/Result, CVR) are always recomputed from
summed numerators/denominators after aggregation — never averaged from
pre-calculated daily ratios, which is statistically wrong.
"""

import pandas as pd
import numpy as np
from config import LEVEL_KEYS


def build_campaign_dates(df1: pd.DataFrame) -> pd.DataFrame:
    """
    Cycle start/end per campaign, used for budget pacing.
    Start = earliest reporting date observed for that campaign in File 1
    (Meta doesn't export a 'Starts' field at Ad level, so this is the best
    available proxy). End = the 'campaign_end' (Ends) field from Meta.
    """
    g = df1.groupby("campaign_id").agg(
        cycle_start=("date", "min"),
        cycle_end=("campaign_end", "max"),
        campaign_name=("campaign_name", "first"),
    ).reset_index()
    return g


def attach_planned_budget(df1: pd.DataFrame, budget_lookup: pd.DataFrame,
                           campaign_dates: pd.DataFrame) -> pd.DataFrame:
    """Merge planned budget and cycle dates onto the base performance frame."""
    df = df1.merge(budget_lookup, on="campaign_id", how="left")
    df = df.merge(
        campaign_dates[["campaign_id", "cycle_start", "cycle_end"]],
        on="campaign_id", how="left",
    )
    return df


def aggregate(df: pd.DataFrame, level: str, date_start=None, date_end=None) -> pd.DataFrame:
    """Aggregate the base performance frame to Campaign / Ad Set / Ad level
    over an optional date window."""
    d = df.copy()
    if date_start is not None:
        d = d[(d["date"] >= date_start) & (d["date"] <= date_end)]

    keys = LEVEL_KEYS[level]
    grouped = d.groupby(keys, dropna=False).agg(
        spend=("spend", "sum"),
        impressions=("impressions", "sum"),
        reach=("reach", "max"),  # reach isn't additive across days; max is a rough proxy
        link_clicks=("link_clicks", "sum"),
        landing_page_views=("landing_page_views", "sum"),
        purchases=("purchases", "sum"),
        add_to_cart=("add_to_cart", "sum"),
        checkouts_initiated=("checkouts_initiated", "sum"),
        leads=("leads", "sum"),
        results=("results", "sum"),
        objective=("objective", "first"),
        result_indicator=("result_indicator", lambda x: sorted(set(x.dropna()))),
        planned_budget=("planned_budget", "first"),
        cycle_start=("cycle_start", "first"),
        cycle_end=("cycle_end", "first"),
        last_edit=("last_significant_edit", "max"),
        quality_ranking=("quality_ranking", lambda x: x.dropna().iloc[-1] if x.dropna().any() else "-"),
    ).reset_index()

    grouped["ctr"] = np.where(grouped["impressions"] > 0,
                               grouped["link_clicks"] / grouped["impressions"] * 100, np.nan)
    grouped["cpc"] = np.where(grouped["link_clicks"] > 0,
                               grouped["spend"] / grouped["link_clicks"], np.nan)
    grouped["cpm"] = np.where(grouped["impressions"] > 0,
                               grouped["spend"] / grouped["impressions"] * 1000, np.nan)
    grouped["cost_per_result"] = np.where(grouped["results"] > 0,
                                           grouped["spend"] / grouped["results"], np.nan)
    grouped["cvr"] = np.where(grouped["landing_page_views"] > 0,
                               grouped["results"] / grouped["landing_page_views"] * 100, np.nan)
    grouped["budget_utilization_pct"] = np.where(
        grouped["planned_budget"] > 0,
        grouped["spend"] / grouped["planned_budget"] * 100, np.nan
    )
    grouped["frequency"] = np.where(grouped["reach"] > 0,
                                     grouped["impressions"] / grouped["reach"], np.nan)

    return grouped


def daily_series(df: pd.DataFrame) -> pd.DataFrame:
    """Day-by-day series for a single entity, used for trend charts."""
    daily = df.groupby("date").agg(
        spend=("spend", "sum"), results=("results", "sum"),
        impressions=("impressions", "sum"), link_clicks=("link_clicks", "sum"),
        reach=("reach", "max"),
    ).reset_index()
    daily["cost_per_result"] = np.where(daily["results"] > 0, daily["spend"] / daily["results"], np.nan)
    daily["ctr"] = np.where(daily["impressions"] > 0, daily["link_clicks"] / daily["impressions"] * 100, np.nan)
    daily["frequency"] = np.where(daily["reach"] > 0, daily["impressions"] / daily["reach"], np.nan)
    return daily
