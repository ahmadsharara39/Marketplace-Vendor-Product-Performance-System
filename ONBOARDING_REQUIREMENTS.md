# Vendor & Product Onboarding Requirements

## Adding a New Vendor

To add a new vendor to the marketplace, you must provide the following information in the vendor master file:

### Required Vendor Fields:
1. **vendor_id** (Text, unique)
   - Format: V followed by numbers (e.g., V001, V002)
   - Must be unique across all vendors
   - Cannot be duplicated

2. **vendor_tier** (Category)
   - Valid values: Bronze, Silver, Gold
   - Indicates vendor performance/reliability tier
   - Bronze: Entry-level vendors
   - Silver: Mid-tier vendors
   - Gold: Top-tier vendors

3. **vendor_region** (Text)
   - Valid regions: Levant, GCC, Europe, North Africa, Asia
   - Geographic location of the vendor
   - Determines regional performance metrics

4. **vendor_quality_score** (Numeric, -2 to 2 range)
   - Quality score between -2 and 2
   - Higher scores indicate better vendor quality
   - Reflects historical performance, ratings, and reliability

**Example:**
```
vendor_id,vendor_tier,vendor_region,vendor_quality_score
V050,Gold,GCC,1.5
```

---

## Adding a New Product

To add a new product to the marketplace, you must provide the following information in the daily marketplace file:

### Required Product Fields:
1. **date** (Date)
   - Format: YYYY-MM-DD
   - Date the product data is recorded

2. **product_id** (Text, unique)
   - Format: P followed by numbers (e.g., P00001)
   - Must be unique across all products

3. **vendor_id** (Text)
   - Must reference an existing vendor_id
   - Links product to a vendor

4. **category** (Text)
   - Valid categories: Grocery, Home, Automotive, Kids, Electronics, Fashion, Health & Beauty, Sports
   - Primary product category

5. **sub_category** (Text)
   - Examples: Fresh, Furniture, Parts, Baby Care, Laptops, Shoes, Supplements, Outdoor
   - More specific classification within category

6. **price_usd** (Numeric, positive)
   - Price in USD
   - Must be greater than 0

7. **discount_rate** (Numeric, 0-1 range)
   - Discount as decimal (0 to 1)
   - 0 = no discount, 0.2 = 20% discount
   - Must be between 0 and 1

8. **ad_spend_usd** (Numeric, non-negative)
   - Advertising spend in USD for the day
   - Must be >= 0

9. **views** (Integer, non-negative)
   - Number of product page views
   - Must be >= 0

10. **orders** (Integer, non-negative)
    - Number of orders placed
    - Must be <= views

11. **gross_revenue_usd** (Numeric, non-negative)
    - Total revenue before returns (price × orders)
    - Must be >= 0

12. **returns** (Integer, non-negative)
    - Number of returned orders
    - Must be <= orders

13. **rating** (Numeric, 1-5 range)
    - Average product rating
    - Must be between 1 and 5

14. **rating_count** (Integer, non-negative)
    - Number of ratings received
    - Must be >= 0

15. **stock_units** (Integer, non-negative)
    - Units in stock
    - Must be >= 0

16. **avg_fulfillment_days** (Numeric, positive)
    - Average delivery time in days
    - Must be > 0
    - Typically 1-7 days range

17. **conversion_rate** (Numeric, 0-1 range)
    - Percentage of views that convert to orders
    - Calculated as orders/views
    - Must be between 0 and 1

18. **return_rate** (Numeric, 0-1 range)
    - Percentage of orders returned
    - Calculated as returns/orders
    - Must be between 0 and 1

19. **net_revenue_usd** (Numeric, non-negative)
    - Revenue after returns (gross_revenue - returns value)
    - Must be >= 0

**Example:**
```
date,product_id,vendor_id,category,sub_category,price_usd,discount_rate,ad_spend_usd,views,orders,gross_revenue_usd,returns,rating,rating_count,stock_units,avg_fulfillment_days,conversion_rate,return_rate,net_revenue_usd
2025-09-15,P00100,V050,Electronics,Laptops,899.99,0.1,50.0,200,20,17999.8,1,4.5,350,15,2.5,0.1,0.05,17099.85
```

---

## Data Validation Rules

### Vendor Addition:
- vendor_id must be unique and follow V + number format
- vendor_tier must be one of: Bronze, Silver, Gold
- vendor_region must be one of: Levant, GCC, Europe, North Africa, Asia
- vendor_quality_score must be numeric, ideally between -2 and 2

### Product Addition:
- product_id must be unique and follow P + number format
- vendor_id must reference an existing vendor
- orders must be <= views
- returns must be <= orders
- gross_revenue should equal price_usd × orders
- net_revenue should equal gross_revenue - (returns × price_usd)
- conversion_rate should equal orders / views
- return_rate should equal returns / orders
- All numeric fields must be non-negative unless specified otherwise
- price_usd and avg_fulfillment_days must be > 0
- rating must be between 1 and 5

---

## File Locations

- **Vendors Master:** `vendors_master.csv`
- **Products Daily Data:** `synthetic_marketplace_daily_clean.csv`
