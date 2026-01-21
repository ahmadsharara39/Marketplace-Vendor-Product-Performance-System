"""
Migration script to transfer data from CSV files to Neon PostgreSQL
"""
import pandas as pd
from pathlib import Path
from db_config import (insert_vendor, insert_product_raw, insert_vendor_promotion, 
                       insert_discount_recommendation, get_connection)

ROOT = Path(__file__).resolve().parents[1]

def migrate_products_from_raw():
    """Migrate products from products_from_raw.csv to Neon"""
    products_csv = ROOT / "products_from_raw.csv"
    
    if not products_csv.exists():
        print(f"❌ Products CSV not found: {products_csv}")
        return False
    
    try:
        df = pd.read_csv(products_csv)
        count = 0
        
        for _, row in df.iterrows():
            success = insert_product_raw(
                product_id=row['product_id'],
                vendor_id=row['vendor_id'],
                category=row['category'],
                sub_category=row['sub_category'],
                price_usd=float(row['price_usd']),
                rating=float(row['rating']),
                rating_count=int(row['rating_count']),
                avg_fulfillment_days=float(row['avg_fulfillment_days'])
            )
            if success:
                count += 1
        
        print(f"✅ Migrated {count} products from products_from_raw.csv to Neon")
        return True
    except Exception as e:
        print(f"❌ Error migrating products: {e}")
        return False

def migrate_vendor_promotions():
    """Migrate vendor promotion recommendations to Neon"""
    promotions_csv = ROOT / "ai_vendor_promotion_recommendations.csv"
    
    if not promotions_csv.exists():
        print(f"❌ Vendor promotions CSV not found: {promotions_csv}")
        return False
    
    try:
        df = pd.read_csv(promotions_csv)
        count = 0
        
        for _, row in df.iterrows():
            success = insert_vendor_promotion(
                vendor_id=row['vendor_id'],
                views=int(row['views']),
                orders=int(row['orders']),
                net_rev=float(row['net_rev']),
                conversion_rate=float(row['conversion_rate']),
                vendor_tier=row['vendor_tier'],
                vendor_region=row['vendor_region'],
                vendor_quality_score=float(row['vendor_quality_score'])
            )
            if success:
                count += 1
        
        print(f"✅ Migrated {count} vendor promotion recommendations to Neon")
        return True
    except Exception as e:
        print(f"❌ Error migrating vendor promotions: {e}")
        return False

def migrate_discount_recommendations():
    """Migrate discount recommendations to Neon"""
    discounts_csv = ROOT / "ai_discount_recommendations.csv"
    
    if not discounts_csv.exists():
        print(f"❌ Discount recommendations CSV not found: {discounts_csv}")
        return False
    
    try:
        df = pd.read_csv(discounts_csv)
        count = 0
        
        for _, row in df.iterrows():
            success = insert_discount_recommendation(
                product_id=row['product_id'],
                vendor_id=row['vendor_id'],
                category=row['category'],
                sub_category=row['sub_category'],
                price_usd=float(row['price_usd']),
                views=int(row['views']),
                orders=int(row['orders']),
                p_order=float(row['p_order']),
                avg_discount=float(row['avg_discount']),
                stock=int(row['stock']),
                avg_rating=float(row['avg_rating']),
                avg_fulfillment=float(row['avg_fulfillment']),
                conversion_rate=float(row['conversion_rate']),
                suggested_discount=float(row['suggested_discount'])
            )
            if success:
                count += 1
        
        print(f"✅ Migrated {count} discount recommendations to Neon")
        return True
    except Exception as e:
        print(f"❌ Error migrating discount recommendations: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Starting data migration from CSV files to Neon...\n")
    
    print("1. Migrating products_from_raw.csv...")
    migrate_products_from_raw()
    
    print("\n2. Migrating ai_vendor_promotion_recommendations.csv...")
    migrate_vendor_promotions()
    
    print("\n3. Migrating ai_discount_recommendations.csv...")
    migrate_discount_recommendations()
    
    print("\n✅ Migration complete!")
