"""Display-only formatting helpers. No calculations happen here — anything
that produces a number belongs in process.py or analytics.py."""

import pandas as pd


def fmt_money(x):
    return "N/A" if pd.isna(x) else f"${x:,.2f}"


def fmt_pct(x):
    return "N/A" if pd.isna(x) else f"{x:,.1f}%"


def fmt_num(x):
    return "N/A" if pd.isna(x) else f"{x:,.0f}"


def fmt_ratio(x):
    return "N/A" if pd.isna(x) else f"{x:.2f}"


def status_badge(pacing: str) -> str:
    return {"On Track": "🟢", "Ahead of Pace": "🟡", "Behind Pace": "🔴"}.get(pacing, "⚪")


def clean_result_label(indicator: str) -> str:
    """'actions:offsite_conversion.fb_pixel_initiate_checkout' -> 'offsite conversion fb pixel initiate checkout'"""
    return indicator.replace("actions:", "").replace("_", " ").replace(".", " ")


# Maps Meta's raw result_indicator strings to a clean, human-readable noun.
# Add to this as new campaign types/optimizations show up in your accounts —
# anything not listed here falls back to a title-cased version of the raw
# indicator, so it degrades gracefully rather than breaking.
RESULT_LABELS = {
    "actions:leadgen.other": "Leads",
    "actions:offsite_conversion.fb_pixel_initiate_checkout": "Checkouts Initiated",
    "actions:offsite_conversion.fb_pixel_purchase": "Purchases",
    "actions:offsite_conversion.fb_pixel_add_to_cart": "Adds to Cart",
    "actions:offsite_conversion.fb_pixel_lead": "Leads",
    "actions:link_click": "Link Clicks",
    "actions:landing_page_view": "Landing Page Views",
    "actions:post_engagement": "Engagements",
    "actions:video_view": "Video Views",
    "reach": "Reach",
}


def result_label(indicator: str) -> str:
    """Human-readable label for a single result_indicator value."""
    if indicator in RESULT_LABELS:
        return RESULT_LABELS[indicator]
    return clean_result_label(indicator).title()


def fmt_results(count, indicators: list) -> str:
    """
    Combines the raw result count with what it's actually counting.
    e.g. 24 + ['actions:leadgen.other'] -> '24 Leads'
    Falls back to a plain number if indicator info is missing, and flags
    mixed indicators explicitly rather than picking one arbitrarily.
    """
    if pd.isna(count):
        return "N/A"
    if not indicators:
        return fmt_num(count)
    if len(indicators) == 1:
        return f"{count:,.0f} {result_label(indicators[0])}"
    return f"{count:,.0f} (mixed result types)"
