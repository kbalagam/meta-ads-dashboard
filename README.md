# Meta Ads Performance Dashboard

Local Streamlit dashboard for analyzing Meta Ads performance across
Campaign → Ad Set → Ad, with budget pacing and diagnostic tools built for
mid-cycle reallocation decisions.

## Architecture

```
Load (src/load.py)        → read raw Meta exports, normalize columns/types
Process (src/process.py)  → joins, hierarchy aggregation, derived metrics
Analytics (src/analytics.py) → pacing status, flags, mismatch detection, deltas
Dashboard (app.py + pages/)  → Streamlit UI
```

Each layer only depends on the one below it. `src/formatting.py` is
presentation-only and used by the dashboard layer, never by process/analytics.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Upload this cycle's exports in the sidebar on the landing page — nothing is
sent anywhere, it all runs locally. Then use the pages in the left sidebar.

## Every reporting cycle

1. Export fresh files from Meta Ads Manager — see `docs/meta_export_spec.md`
   for exact columns and steps.
2. Run the app, upload the files. No code changes needed as long as Meta's
   column names stay consistent with the spec.

## Tests

```bash
PYTHONPATH=. pytest tests/
```

Fixtures in `tests/fixtures/` are small synthetic files, not real client
data — safe to commit.

## Known limitations

- **Revenue/ROAS shows N/A everywhere.** This ad account doesn't track
  purchase conversion value, so Meta never sends a dollar figure. Fix is on
  the ad-account side (Conversions API / pixel value parameter), not here.
- **"Recently edited" flag is a proxy for learning phase**, not Meta's real
  delivery status — that field isn't in the standard export.
- **Creative Analysis is fatigue-only.** Format/Theme/Hook/CTA breakdown
  needs a manual tagging file that doesn't exist yet.
- **Budget pacing assumes each cycle's campaigns are freshly created**
  (confirmed true for this account's naming convention). If that changes,
  pacing math needs to be revisited.
- **Age/Gender file (File 2) is loaded but not yet used** in any page —
  reserved for a future Audience Analysis page.
