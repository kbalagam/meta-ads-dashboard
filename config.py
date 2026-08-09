"""
Central config: column name mappings and tunable thresholds.

If Meta ever renames an export column, fix it here — nowhere else.
If pacing/learning-phase thresholds need adjusting, fix them here too.
"""

# --- File 1: Base performance (Ad level, daily) ---
F1_RENAME = {
    "Reporting starts": "date",
    "Reporting ends": "date_end",
    "Ad name": "ad_name",
    "Ad delivery": "ad_delivery",
    "Results": "results",
    "Result indicator": "result_indicator",
    "Cost per results": "cost_per_result",
    "Amount spent (USD)": "spend",
    "Impressions": "impressions",
    "Reach": "reach",
    "Ends": "campaign_end",
    "Attribution setting": "attribution_setting",
    "Quality ranking": "quality_ranking",
    "Engagement rate ranking": "engagement_rate_ranking",
    "Conversion rate ranking": "conversion_rate_ranking",
    "Ad set name": "ad_set_name",
    "Campaign name": "campaign_name",
    "Campaign ID": "campaign_id",
    "Objective": "objective",
    "Ad set ID": "ad_set_id",
    "Ad set delivery": "ad_set_delivery",
    "Ad ID": "ad_id",
    "Frequency": "frequency",
    "CPM (cost per 1,000 impressions) (USD)": "cpm",
    "Link clicks": "link_clicks",
    "CTR (link click-through rate)": "ctr",
    "CPC (cost per link click) (USD)": "cpc",
    "Outbound clicks": "outbound_clicks",
    "Outbound CTR (click-through rate)": "outbound_ctr",
    "Landing page views": "landing_page_views",
    "Cost per landing page view (USD)": "cost_per_lpv",
    "Purchases": "purchases",
    "Average purchases conversion value [Incremental attribution all conversions]": "purchase_value",
    "Purchase ROAS (return on ad spend)": "roas",
    "Adds to cart": "add_to_cart",
    "Cost per add to cart (USD)": "cost_per_atc",
    "Checkouts initiated": "checkouts_initiated",
    "Cost per checkout initiated (USD)": "cost_per_checkout",
    "Leads": "leads",
    "Cost per lead (USD)": "cost_per_lead",
    "Last significant edit": "last_significant_edit",
}

# --- File 2: Age & Gender breakdown (Ad Set level, weekly) ---
F2_RENAME = {
    "Reporting starts": "date",
    "Reporting ends": "date_end",
    "Ad set name": "ad_set_name",
    "Age": "age",
    "Gender": "gender",
    "Results": "results",
    "Result indicator": "result_indicator",
    "Cost per results": "cost_per_result",
    "Amount spent (USD)": "spend",
    "Impressions": "impressions",
    "Reach": "reach",
    "Campaign name": "campaign_name",
    "Campaign ID": "campaign_id",
    "Ad set ID": "ad_set_id",
    "Purchases": "purchases",
    "Purchase ROAS (return on ad spend)": "roas",
    "Average purchases conversion value [Incremental attribution all conversions]": "purchase_value",
    "CTR (all)": "ctr",
    "CPC (all) (USD)": "cpc",
}

# --- File 3: Campaign budget lookup ---
F3_RENAME = {
    "Campaign name": "campaign_name",
    "Campaign ID": "campaign_id",
    "Ad set budget": "planned_budget",   # Meta labels this generically even on a Campaign-level pull
    "Ad set budget type": "budget_type",
    "Objective": "objective",
}

# --- Hierarchy keys for aggregation ---
LEVEL_KEYS = {
    "Campaign": ["campaign_id", "campaign_name"],
    "Ad Set": ["campaign_id", "campaign_name", "ad_set_id", "ad_set_name"],
    "Ad": ["campaign_id", "campaign_name", "ad_set_id", "ad_set_name", "ad_id", "ad_name"],
}

# --- Thresholds (tune as needed) ---
PACING_TOLERANCE_PCT = 10       # +/- this % vs expected pace = "On Track"
LEARNING_PHASE_WINDOW_DAYS = 4  # proxy: edited within this many days = possible learning phase
DEFAULT_COMPARE_WINDOW_DAYS = 7
