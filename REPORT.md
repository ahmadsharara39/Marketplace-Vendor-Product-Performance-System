# Marketplace Vendor & Product Performance Report

**Period:** 2025-09-01 to 2025-12-29  
**Data grain:** daily × product (marketplace/ERP-style)  
**Files:**  
- `synthetic_marketplace_daily_raw.csv` (contains injected issues)  
- `synthetic_marketplace_daily_clean.csv` (cleaned, modeled)  
- `data_dictionary.csv` (column definitions)  
- Charts: `fig_*.png`  
- Key tables: `table_*.csv`  
- AI outputs: `AI_management_summary.txt`, `ai_*_recommendations.csv`

---

## Approach (what I did)

1) **Generated synthetic data** mimicking a real marketplace:
- Vendors, products, categories, pricing, stock, fulfillment time, ratings.
- Daily funnel metrics: views → orders → revenue, plus ad spend and returns.
- Realistic effects (seasonality, promotions, vendor quality, lead time).

2) **Intentionally injected “real-world mess”**:
- Missing values (views/ratings/fulfillment)
- Negative ad spend values
- Discounts above 100%
- Orders > views (tracking inconsistencies)

3) **Cleaned and standardized the dataset**:
- Imputed missing values using category or product-level medians/means.
- Capped invalid discounts and ad spend.
- Enforced logical constraints (orders ≤ views, returns ≤ orders).
- Recomputed revenue consistently.
- Produced derived KPIs: conversion, return rate, net revenue.

4) **Produced business insights** at vendor, product, and category levels.

5) **AI component (mandatory):** trained a lightweight ML model to estimate purchase probability and built a decision system for:
- Products to discount (high traffic, low predicted conversion, enough stock)
- Vendors to promote (strong conversion, low visibility)

---

## Key findings (plain business language)

### Marketplace-wide funnel
- Total net revenue: **$9,724,319**
- Total orders: **310,106** from **2,878,331** views
- Overall conversion: **10.8%**
- Average fulfillment time: **3.6 days**

**Interpretation:** overall conversion is driven heavily by a subset of vendors/products with good ratings and fast fulfillment. Inventory availability is a major gating factor (stock-outs suppress conversion sharply).

### Vendor performance
- Top vendors by net revenue are concentrated in the top tier (see `table_top_vendors_by_net_revenue.csv`).
- Top vendors by conversion (with sufficient traffic) show:
  - stronger average ratings
  - shorter fulfillment times
  - slightly higher, but controlled discounting

**Underperforming vendors** (high views but weak outcomes) often combine:
- **long fulfillment times**
- **lower ratings**
- **heavy reliance on low-quality traffic** (views without orders)

See: `table_underperforming_vendors.csv`.

### Product & demand
- **High views but low orders** products (see `table_high_views_low_orders_products.csv`) are classic “funnel leak” candidates:
  - price not competitive
  - low rating / low review confidence
  - slow delivery expectations
  - weak merchandising (title/images/specs) or mismatched traffic

### Category performance
- Best category by net revenue: **Electronics**
- Lowest category by net revenue: **Grocery**

See: `table_category_performance.csv` and `fig_category_net_revenue.png`.

### Outliers & unusual patterns
- Outlier days (z-score ≥ 3.2) typically align with:
  - marketing bursts (traffic spikes)
  - category-specific issues (stock-outs or tracking anomalies)

See: `table_outlier_days_by_category.csv`.

---

## What surprised me
- **Fulfillment time** had a bigger impact on conversion than modest discounting. Even a 2–3 day increase in expected delivery correlated with noticeably weaker conversion, especially in fast-moving categories.
- Some vendors can have **excellent conversion but low visibility**—suggesting the platform may benefit from reallocating traffic via ranking/ads.

---

## AI-driven output (decision system)

### Model
- Logistic regression predicting whether a product-day gets ≥1 order.
- Performance (hold-out): **ROC-AUC=0.841**, **Average Precision=0.996**.

### Recommendations
- **Discount candidates**: `ai_discount_recommendations.csv`  
  Rationale: high traffic + low predicted purchase probability + enough stock + currently low discount.
- **Vendors to promote**: `ai_vendor_promotion_recommendations.csv`  
  Rationale: strong conversion but low visibility—boosting them should lift orders without sacrificing quality.

---

## How to automate/scale this in production

1) **Data pipeline**
- Daily ingestion (events + orders + returns + ads)
- Data quality checks (constraints: orders ≤ views, discount bounds, negative spend, etc.)
- Feature store for vendor/product features (rating, fulfillment SLA, stock status)

2) **Monitoring**
- Vendor scorecards (revenue, conversion, return rate, fulfillment SLA)
- Product funnel leak detection (high views, low orders)
- Category anomaly detection (revenue z-scores)

3) **Decision automation**
- Scheduled recommendations: discount tests, vendor promotion boosts
- Human-in-the-loop approvals
- A/B testing framework for discount/promo interventions

4) **Model lifecycle**
- Weekly retrain with drift detection
- Backtesting and uplift measurement
- Explainability: top drivers per recommendation (fulfillment, rating, price, discount)

---

## Where to look
- Notebook: `analysis.ipynb`
- Management summary: `AI_management_summary.txt`
- Charts: `fig_*.png`
- Tables: `table_*.csv`
