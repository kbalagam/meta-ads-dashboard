"""
Sanity tests for src/process.py — mainly guarding against the aggregation
bug that's easy to reintroduce: averaging pre-calculated ratio metrics
instead of recomputing them from summed numerator/denominator.
"""

import pandas as pd
from src.load import load_file1, load_file3
from src.process import build_campaign_dates, attach_planned_budget, aggregate

SAMPLE_FILE1 = "tests/fixtures/sample_file1.xlsx"
SAMPLE_FILE3 = "tests/fixtures/sample_file3.xlsx"


def _prepped():
    df1 = load_file1(SAMPLE_FILE1)
    active_ids = df1["campaign_id"].unique()
    budget = load_file3(SAMPLE_FILE3, active_ids)
    cdates = build_campaign_dates(df1)
    return attach_planned_budget(df1, budget, cdates)


def test_aggregate_campaign_spend_matches_raw_sum():
    df1 = _prepped()
    agg = aggregate(df1, "Campaign")
    assert agg["spend"].sum() == df1["spend"].sum()


def test_aggregate_does_not_drop_campaigns():
    df1 = _prepped()
    agg = aggregate(df1, "Campaign")
    assert agg["campaign_name"].nunique() == df1["campaign_name"].nunique()


def test_ctr_recomputed_not_averaged():
    """Campaign A fixture: 40+45 clicks / 1000+1100 impressions, not a mean of daily CTRs."""
    df1 = _prepped()
    agg = aggregate(df1, "Campaign")
    camp_a = agg[agg["campaign_name"] == "Campaign A"].iloc[0]
    expected_ctr = (40 + 45) / (1000 + 1100) * 100
    assert abs(camp_a["ctr"] - expected_ctr) < 0.01


def test_budget_utilization_computed_correctly():
    df1 = _prepped()
    agg = aggregate(df1, "Campaign")
    camp_a = agg[agg["campaign_name"] == "Campaign A"].iloc[0]
    expected = (50.0 + 57.0) / 500.0 * 100
    assert abs(camp_a["budget_utilization_pct"] - expected) < 0.01
