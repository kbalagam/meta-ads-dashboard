"""
Analytics layer: the "why" logic — pacing status, learning-phase flag,
optimization-goal mismatch detection, and period-over-period deltas.

This is where business rules live. If a threshold needs tuning, check
config.py first before editing logic here.
"""

import pandas as pd
import numpy as np
from config import PACING_TOLERANCE_PCT, LEARNING_PHASE_WINDOW_DAYS


def pacing_status(row, as_of_date) -> str:
    """Classify budget pacing based on elapsed-time vs elapsed-spend."""
    if pd.isna(row.get("cycle_start")) or pd.isna(row.get("cycle_end")) or pd.isna(row.get("planned_budget")):
        return "No budget/date data"
    total_days = (row["cycle_end"] - row["cycle_start"]).days
    elapsed_days = (as_of_date - row["cycle_start"]).days
    if total_days <= 0:
        return "No budget/date data"
    expected_pct = min(max(elapsed_days / total_days, 0), 1) * 100
    actual_pct = row.get("budget_utilization_pct", np.nan)
    if pd.isna(actual_pct):
        return "No budget/date data"
    diff = actual_pct - expected_pct
    if diff > PACING_TOLERANCE_PCT:
        return "Ahead of Pace"
    elif diff < -PACING_TOLERANCE_PCT:
        return "Behind Pace"
    return "On Track"


def learning_phase_flag(row, as_of_date, window_days=LEARNING_PHASE_WINDOW_DAYS) -> bool:
    """Proxy flag: recently-edited entities may still be in Meta's learning phase.
    NOTE: approximation based on 'Last significant edit' recency — Meta's real
    delivery/learning status field is not present in this export."""
    if pd.isna(row.get("last_edit")):
        return False
    return (as_of_date - row["last_edit"]).days <= window_days


def optimization_mismatch(agg_df: pd.DataFrame):
    """True if the selected rows mix different result_indicator values,
    meaning Cost per Result isn't measuring the same underlying action
    across them."""
    all_indicators = set()
    for lst in agg_df["result_indicator"]:
        all_indicators.update(lst)
    return len(all_indicators) > 1, sorted(all_indicators)


def period_delta(entity_df: pd.DataFrame, level: str, max_date, compare_days: int,
                  aggregate_fn):
    """
    Compare 'last N days' vs 'prior N days' for a single entity.
    aggregate_fn should be process.aggregate (passed in to avoid a circular import).
    Returns a tidy DataFrame: Metric | Last Nd | Prior Nd | % Change
    """
    last_start = max_date - pd.Timedelta(days=compare_days - 1)
    prior_end = last_start - pd.Timedelta(days=1)
    prior_start = prior_end - pd.Timedelta(days=compare_days - 1)

    last_agg = aggregate_fn(entity_df, level, last_start, max_date)
    prior_agg = aggregate_fn(entity_df, level, prior_start, prior_end)

    def get_val(df_, col):
        return df_[col].iloc[0] if len(df_) and col in df_.columns else np.nan

    metrics = ["spend", "frequency", "ctr", "cpm", "cost_per_result", "cvr"]
    labels = {"spend": "Spend", "frequency": "Frequency", "ctr": "CTR",
              "cpm": "CPM", "cost_per_result": "Cost / Result", "cvr": "Conv. Rate"}

    rows = []
    for m in metrics:
        last_v = get_val(last_agg, m)
        prior_v = get_val(prior_agg, m)
        delta = (np.nan if pd.isna(last_v) or pd.isna(prior_v) or prior_v == 0
                 else (last_v - prior_v) / prior_v * 100)
        rows.append({"metric": labels[m], "last": last_v, "prior": prior_v, "pct_change": delta})
    return pd.DataFrame(rows)
