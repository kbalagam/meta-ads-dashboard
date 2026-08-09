"""
Sanity tests for src/load.py.

These exist to catch the two failure modes that actually matter for this
project: (1) Meta renames/reorders an export column and the rename map
silently breaks, (2) the budget file join drops campaigns it shouldn't.

Fixtures in tests/fixtures/ are small synthetic files matching Meta's real
column structure — not real client data. Regenerate them if the column
mapping in config.py ever changes shape.

Run with: pytest tests/
"""

import pandas as pd
from src.load import load_file1, load_file3

SAMPLE_FILE1 = "tests/fixtures/sample_file1.xlsx"
SAMPLE_FILE3 = "tests/fixtures/sample_file3.xlsx"


def test_load_file1_has_expected_columns():
    df = load_file1(SAMPLE_FILE1)
    expected = {"date", "campaign_id", "campaign_name", "ad_set_id", "ad_id",
                "spend", "impressions", "results", "objective"}
    assert expected.issubset(set(df.columns))
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_load_file1_row_count_preserved():
    df = load_file1(SAMPLE_FILE1)
    assert len(df) == 3  # matches the fixture — catches silent row drops


def test_load_file3_filters_to_active_campaigns():
    df1 = load_file1(SAMPLE_FILE1)
    active_ids = df1["campaign_id"].unique()
    budget = load_file3(SAMPLE_FILE3, active_ids)
    assert set(budget["campaign_id"]).issubset(set(active_ids))
    assert not budget.empty
    assert len(budget) == 2  # both campaigns in fixture are active
