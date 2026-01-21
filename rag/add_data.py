"""
Module for adding vendors and products to the Neon PostgreSQL database
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
from rag.db_config import insert_vendor, insert_product_raw, insert_marketplace_daily_raw, insert_marketplace_daily_clean, get_all_vendors

ROOT = Path(__file__).resolve().parents[1]

def add_vendor(vendor_id: str, vendor_tier: str, vendor_region: str, vendor_quality_score: float) -> dict:
    """
    Add a new vendor to the Neon database.
    
    Args:
        vendor_id: Unique vendor identifier (e.g., V001)
        vendor_tier: Tier level (Bronze, Silver, Gold)
        vendor_region: Region (Levant, GCC, Europe, North Africa, Asia)
        vendor_quality_score: Quality score (-2 to 2 range)
    
    Returns:
        dict with status and message
    """
    try:
        # Validate inputs
        if not vendor_id.startswith("V"):
            return {"success": False, "message": "vendor_id must start with 'V' (e.g., V001)"}
        
        valid_tiers = ["Bronze", "Silver", "Gold"]
        if vendor_tier not in valid_tiers:
            return {"success": False, "message": f"vendor_tier must be one of: {', '.join(valid_tiers)}"}
        
        valid_regions = ["Levant", "GCC", "Europe", "North Africa", "Asia"]
        if vendor_region not in valid_regions:
            return {"success": False, "message": f"vendor_region must be one of: {', '.join(valid_regions)}"}
        
        if not isinstance(vendor_quality_score, (int, float)) or vendor_quality_score < -2 or vendor_quality_score > 2:
            return {"success": False, "message": "vendor_quality_score must be numeric between -2 and 2"}
        
        # Check if vendor already exists
        existing_vendors = get_all_vendors()
        vendor_ids = [v['vendor_id'] for v in existing_vendors]
        
        if vendor_id in vendor_ids:
            return {"success": False, "message": f"vendor_id {vendor_id} already exists"}
        
        # Add new vendor to Neon
        success = insert_vendor(vendor_id, vendor_tier, vendor_region, vendor_quality_score)
        
        if success:
            return {
                "success": True,
                "message": f"✅ Vendor {vendor_id} added successfully to Neon!\nTier: {vendor_tier}, Region: {vendor_region}, Quality Score: {vendor_quality_score}"
            }
        else:
            return {"success": False, "message": "Failed to add vendor to database"}
    except Exception as e:
        return {"success": False, "message": f"Error adding vendor: {str(e)}"}


def add_product(date: str, product_id: str, vendor_id: str, category: str, sub_category: str,
                price_usd: float, discount_rate: float, ad_spend_usd: float, views: int, orders: int,
                gross_revenue_usd: float, returns: int, rating: float, rating_count: int,
                stock_units: int, avg_fulfillment_days: float) -> dict:
    """
    Add a new product to the Neon database.
    
    Args:
        date: Date in YYYY-MM-DD format
        product_id: Unique product identifier (e.g., P00001)
        vendor_id: Must reference an existing vendor
        category: Product category
        sub_category: Product sub-category
        price_usd: Price in USD
        discount_rate: Discount rate (0-1)
        ad_spend_usd: Advertising spend
        views: Number of product views
        orders: Number of orders
        gross_revenue_usd: Total revenue before returns
        returns: Number of returns
        rating: Product rating (1-5)
        rating_count: Number of ratings
        stock_units: Units in stock
        avg_fulfillment_days: Average fulfillment time
    
    Returns:
        dict with status and message
    """
    try:
        # Validate basic inputs
        if not product_id.startswith("P"):
            return {"success": False, "message": "product_id must start with 'P' (e.g., P00001)"}
        
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"success": False, "message": "date must be in YYYY-MM-DD format"}
        
        # Check vendor exists
        existing_vendors = get_all_vendors()
        vendor_ids = [v['vendor_id'] for v in existing_vendors]
        
        if vendor_id not in vendor_ids:
            return {"success": False, "message": f"vendor_id {vendor_id} does not exist. Please add the vendor first."}
        
        # Validate numeric ranges
        if not 0 <= discount_rate <= 1:
            return {"success": False, "message": "discount_rate must be between 0 and 1"}
        if price_usd <= 0:
            return {"success": False, "message": "price_usd must be > 0"}
        if ad_spend_usd < 0:
            return {"success": False, "message": "ad_spend_usd must be >= 0"}
        if views < 0 or orders < 0:
            return {"success": False, "message": "views and orders must be >= 0"}
        if orders > views:
            return {"success": False, "message": "orders cannot exceed views"}
        if returns < 0 or returns > orders:
            return {"success": False, "message": "returns must be between 0 and orders"}
        if not 1 <= rating <= 5:
            return {"success": False, "message": "rating must be between 1 and 5"}
        if rating_count < 0:
            return {"success": False, "message": "rating_count must be >= 0"}
        if stock_units < 0:
            return {"success": False, "message": "stock_units must be >= 0"}
        if avg_fulfillment_days <= 0:
            return {"success": False, "message": "avg_fulfillment_days must be > 0"}
        
        # Calculate derived metrics
        conversion_rate = orders / views if views > 0 else 0
        return_rate = returns / orders if orders > 0 else 0
        net_revenue_usd = gross_revenue_usd - (returns * price_usd)
        
        # Add new product to Neon
        # 1) Insert into products_raw (dimension)
        insert_product_raw(
            product_id=product_id,
            vendor_id=vendor_id,
            category=category,
            sub_category=sub_category,
            price_usd=price_usd,
            rating=rating,
            rating_count=rating_count,
            avg_fulfillment_days=avg_fulfillment_days
        )

        # 2) Insert into marketplace_daily_raw (fact - raw metrics)
        insert_marketplace_daily_raw(
            date=date,
            product_id=product_id,
            vendor_id=vendor_id,
            category=category,
            sub_category=sub_category,
            price_usd=price_usd,
            discount_rate=discount_rate,
            ad_spend_usd=ad_spend_usd,
            views=views,
            orders=orders,
            gross_revenue_usd=gross_revenue_usd,
            returns=returns,
            rating=rating,
            rating_count=rating_count,
            stock_units=stock_units,
            avg_fulfillment_days=avg_fulfillment_days
        )

        # 3) Insert into marketplace_daily_clean (fact - with calculated metrics)
        success = insert_marketplace_daily_clean(
            date=date,
            product_id=product_id,
            vendor_id=vendor_id,
            category=category,
            sub_category=sub_category,
            price_usd=price_usd,
            discount_rate=discount_rate,
            ad_spend_usd=ad_spend_usd,
            views=views,
            orders=orders,
            gross_revenue_usd=gross_revenue_usd,
            returns=returns,
            rating=rating,
            rating_count=rating_count,
            stock_units=stock_units,
            avg_fulfillment_days=avg_fulfillment_days,
            conversion_rate=conversion_rate,
            return_rate=return_rate,
            net_revenue_usd=net_revenue_usd,
        )

        if success:
            return {
                "success": True,
                "message": f"""✅ Product {product_id} added successfully to Neon!
Date: {date}
Vendor: {vendor_id}
Category: {category} > {sub_category}
Price: ${price_usd}
Conversion Rate: {conversion_rate:.2%}
Return Rate: {return_rate:.2%}
Net Revenue: ${net_revenue_usd:.2f}"""
            }
        else:
            return {"success": False, "message": "Failed to add product to database"}
    except Exception as e:
        return {"success": False, "message": f"Error adding product: {str(e)}"}
