# Meta Ads Manager Export Spec

Three files, pulled fresh from Meta Ads Manager each reporting cycle.
File 2 (Age & Gender) is currently loaded by the app but not yet used in
any page — it's wired up for when Audience Analysis gets built. Use the
same date range across File 1 and File 2.

## File 1 — Base Performance (Ad level, By Day)

1. Ads reporting → set date range (previous cycle to present)
2. Level = **Ad**
3. Breakdown → By Time → **Day**
4. Columns → Customize Columns, select:

**Identification**
Campaign Name, Campaign ID, Campaign Objective, Campaign Delivery Status,
Ad Set Name, Ad Set ID, Ad Set Budget, Bid Strategy, Ad Set Delivery Status,
Ad Name, Ad ID, Ad Delivery Status

**Spend & Delivery**
Amount Spent (USD), Impressions, Reach, Frequency, CPM

**Traffic**
Link Clicks, CTR (Link Click-Through Rate), CPC (Cost per Link Click),
Outbound Clicks, Outbound CTR, Landing Page Views, Cost per Landing Page View

**Conversion**
Results, Cost per Result, Result Type, Purchases, Purchase Conversion Value,
Purchase ROAS, Adds to Cart, Cost per Add to Cart, Checkouts Initiated,
Cost per Checkout Initiated, Leads, Cost per Lead

**Engagement/Video**
Video Plays, ThruPlays, 3-Second Video Views, Video Average Play Time

**Quality signals**
Quality Ranking, Engagement Rate Ranking, Conversion Rate Ranking

5. Export as **.xlsx** (not CSV — CSV can mangle currency/percent formatting)

## File 2 — Age & Gender Breakdown (Ad Set level, By Week) — optional, not yet used

1. Level = **Ad Set**
2. Breakdown → By Time → **Week**, plus Age and Gender
3. Columns: Campaign Name, Campaign ID, Ad Set Name, Ad Set ID, Age, Gender,
   Amount Spent, Impressions, Reach, Results, Cost per Result, Purchases,
   Purchase Conversion Value, Purchase ROAS, CTR, CPC
4. Export as .xlsx

## File 3 — Campaign Budget Lookup

1. Level = **Campaign** (not Ad — the numeric budget field isn't always
   exposed at Ad level)
2. No date breakdown needed
3. Columns: Campaign Name, Campaign ID, Ad Set Budget (this is the field
   that carries the campaign-level budget number, despite the misleading
   name — a Meta export quirk), Ad Set Budget Type, Objective
4. Export as .xlsx

## Known account-specific notes (Massage Heights)

- Budget type is **Lifetime**, and campaigns are rebuilt fresh each cycle
  (naming convention: `[N]. [Month-Month 'YY] | [description]`) — so the
  Lifetime figure equals the planned budget for that cycle. **This
  assumption was confirmed with the client directly — re-confirm if the
  campaign-naming pattern ever changes.**
- Purchase Conversion Value is not tracked on this account, so
  Revenue/ROAS will always show N/A. This is an ad-account setup gap
  (Conversions API / pixel value parameter), not a dashboard limitation.
- Result Indicator is used as a proxy for Optimization Goal, since Optimization
  Goal isn't in the standard export. It correctly identifies when
  campaigns/ad sets/ads are optimizing for different actions (e.g. Leads vs
  Reach vs Initiate Checkout).

## Skipped for now

Placement breakdown (File 3 in earlier drafts) and Age/Gender breakdown are
not currently wired into the dashboard. If reintroduced, follow the same
pattern: Ad Set level, By Week breakdown, joined on Campaign ID / Ad Set ID.
