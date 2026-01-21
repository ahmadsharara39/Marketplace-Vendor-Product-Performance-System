"""
Database configuration and connection management for Neon PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Neon connection string - check environment first, then Streamlit secrets
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    try:
        import streamlit as st
        DATABASE_URL = st.secrets.get("DATABASE_URL")
    except (ImportError, AttributeError, KeyError):
        pass

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Set it in .env locally or in Streamlit Cloud Secrets")

def get_connection():
    """Get a connection to Neon PostgreSQL"""
    return psycopg2.connect(DATABASE_URL)

def init_database():
    """Initialize database schema"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Create vendors table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                vendor_id VARCHAR(50) PRIMARY KEY,
                vendor_tier VARCHAR(50) NOT NULL,
                vendor_region VARCHAR(100) NOT NULL,
                vendor_quality_score FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create products table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                product_id VARCHAR(50) NOT NULL,
                vendor_id VARCHAR(50) NOT NULL REFERENCES vendors(vendor_id),
                category VARCHAR(100) NOT NULL,
                sub_category VARCHAR(100) NOT NULL,
                price_usd FLOAT NOT NULL,
                discount_rate FLOAT NOT NULL,
                ad_spend_usd FLOAT NOT NULL,
                views INTEGER NOT NULL,
                orders INTEGER NOT NULL,
                gross_revenue_usd FLOAT NOT NULL,
                returns INTEGER NOT NULL,
                rating FLOAT NOT NULL,
                rating_count INTEGER NOT NULL,
                stock_units INTEGER NOT NULL,
                avg_fulfillment_days FLOAT NOT NULL,
                conversion_rate FLOAT NOT NULL,
                return_rate FLOAT NOT NULL,
                net_revenue_usd FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, product_id, vendor_id)
            );
        """)
        
        # Create indexes for faster queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_date ON products(date);
            CREATE INDEX IF NOT EXISTS idx_products_vendor_id ON products(vendor_id);
            CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
            CREATE INDEX IF NOT EXISTS idx_vendors_tier ON vendors(vendor_tier);
            CREATE INDEX IF NOT EXISTS idx_vendors_region ON vendors(vendor_region);
        """)
        
        # Create products_raw table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products_raw (
                product_id VARCHAR(50) PRIMARY KEY,
                vendor_id VARCHAR(50) NOT NULL REFERENCES vendors(vendor_id),
                category VARCHAR(100) NOT NULL,
                sub_category VARCHAR(100) NOT NULL,
                price_usd FLOAT NOT NULL,
                rating FLOAT NOT NULL,
                rating_count INTEGER NOT NULL,
                avg_fulfillment_days FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create vendor_promotion_recommendations table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vendor_promotion_recommendations (
                vendor_id VARCHAR(50) PRIMARY KEY REFERENCES vendors(vendor_id),
                views INTEGER,
                orders INTEGER,
                net_rev FLOAT,
                conversion_rate FLOAT,
                vendor_tier VARCHAR(50),
                vendor_region VARCHAR(100),
                vendor_quality_score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create discount_recommendations table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS discount_recommendations (
                product_id VARCHAR(50) PRIMARY KEY,
                vendor_id VARCHAR(50) NOT NULL REFERENCES vendors(vendor_id),
                category VARCHAR(100),
                sub_category VARCHAR(100),
                price_usd FLOAT,
                views INTEGER,
                orders INTEGER,
                p_order FLOAT,
                avg_discount FLOAT,
                stock INTEGER,
                avg_rating FLOAT,
                avg_fulfillment FLOAT,
                conversion_rate FLOAT,
                suggested_discount FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create marketplace_daily_clean table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_daily_clean (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                product_id VARCHAR(50) NOT NULL,
                vendor_id VARCHAR(50) NOT NULL REFERENCES vendors(vendor_id),
                category VARCHAR(100),
                sub_category VARCHAR(100),
                price_usd FLOAT,
                discount_rate FLOAT,
                ad_spend_usd FLOAT,
                views INTEGER,
                orders INTEGER,
                gross_revenue_usd FLOAT,
                returns INTEGER,
                rating FLOAT,
                rating_count INTEGER,
                stock_units INTEGER,
                avg_fulfillment_days FLOAT,
                conversion_rate FLOAT,
                return_rate FLOAT,
                net_revenue_usd FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, product_id, vendor_id)
            );
        """)
        
        # Create marketplace_daily_raw table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS marketplace_daily_raw (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                product_id VARCHAR(50) NOT NULL,
                vendor_id VARCHAR(50) NOT NULL REFERENCES vendors(vendor_id),
                category VARCHAR(100),
                sub_category VARCHAR(100),
                price_usd FLOAT,
                discount_rate FLOAT,
                ad_spend_usd FLOAT,
                views INTEGER,
                orders INTEGER,
                gross_revenue_usd FLOAT,
                returns INTEGER,
                rating FLOAT,
                rating_count INTEGER,
                stock_units INTEGER,
                avg_fulfillment_days FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, product_id, vendor_id)
            );
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_raw_vendor_id ON products_raw(vendor_id);
            CREATE INDEX IF NOT EXISTS idx_products_raw_category ON products_raw(category);
            CREATE INDEX IF NOT EXISTS idx_vendor_promo_tier ON vendor_promotion_recommendations(vendor_tier);
            CREATE INDEX IF NOT EXISTS idx_discount_promo_product ON discount_recommendations(product_id);
        """)
        
        conn.commit()
        print("✅ Database schema initialized successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error initializing database: {e}")
    finally:
        cur.close()
        conn.close()

def insert_vendor(vendor_id: str, vendor_tier: str, vendor_region: str, vendor_quality_score: float) -> bool:
    """Insert a vendor into the database"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO vendors (vendor_id, vendor_tier, vendor_region, vendor_quality_score)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (vendor_id) DO NOTHING
        """, (vendor_id, vendor_tier, vendor_region, vendor_quality_score))
        
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error inserting vendor: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# def insert_product(date: str, product_id: str, vendor_id: str, category: str, sub_category: str,
#                    price_usd: float, discount_rate: float, ad_spend_usd: float, views: int, orders: int,
#                    gross_revenue_usd: float, returns: int, rating: float, rating_count: int,
#                    stock_units: int, avg_fulfillment_days: float, conversion_rate: float,
#                    return_rate: float, net_revenue_usd: float) -> bool:
#     """Insert a product into the database"""
#     conn = get_connection()
#     cur = conn.cursor()
    
#     try:
#         cur.execute("""
#             INSERT INTO products 
#             (date, product_id, vendor_id, category, sub_category, price_usd, discount_rate, 
#              ad_spend_usd, views, orders, gross_revenue_usd, returns, rating, rating_count, 
#              stock_units, avg_fulfillment_days, conversion_rate, return_rate, net_revenue_usd)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             ON CONFLICT (date, product_id, vendor_id) DO NOTHING
#         """, (date, product_id, vendor_id, category, sub_category, price_usd, discount_rate,
#               ad_spend_usd, views, orders, gross_revenue_usd, returns, rating, rating_count,
#               stock_units, avg_fulfillment_days, conversion_rate, return_rate, net_revenue_usd))
        
#         conn.commit()
#         return cur.rowcount > 0
#     except Exception as e:
#         conn.rollback()
#         print(f"Error inserting product: {e}")
#         return False
#     finally:
#         cur.close()
#         conn.close()

def get_all_vendors():
    """Get all vendors from database"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("SELECT * FROM vendors ORDER BY vendor_id")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def get_all_products():
    """Get all products from database"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("SELECT * FROM products ORDER BY date DESC, product_id")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def get_all_categories():
    """Get all unique categories from products_raw"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT DISTINCT category FROM products_raw ORDER BY category")
        return [row[0] for row in cur.fetchall() if row[0]]
    finally:
        cur.close()
        conn.close()

def get_subcategories_for_category(category: str):
    """Get all subcategories for a given category"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT DISTINCT sub_category FROM products_raw WHERE category = %s ORDER BY sub_category", (category,))
        return [row[0] for row in cur.fetchall() if row[0]]
    finally:
        cur.close()
        conn.close()

def vendor_exists(vendor_id: str) -> bool:
    """Check if a vendor exists in the database"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT 1 FROM vendors WHERE vendor_id = %s", (vendor_id,))
        return cur.fetchone() is not None
    finally:
        cur.close()
        conn.close()

def product_exists(product_id: str) -> bool:
    """Check if a product exists in products_raw"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT 1 FROM products_raw WHERE product_id = %s", (product_id,))
        return cur.fetchone() is not None
    finally:
        cur.close()
        conn.close()

def category_exists(category: str) -> bool:
    """Check if a category exists in products_raw"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT 1 FROM products_raw WHERE category = %s", (category,))
        return cur.fetchone() is not None
    finally:
        cur.close()
        conn.close()

def subcategory_exists(category: str, sub_category: str) -> bool:
    """Check if a subcategory exists for a given category"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT 1 FROM products_raw WHERE category = %s AND sub_category = %s", (category, sub_category))
        return cur.fetchone() is not None
    finally:
        cur.close()
        conn.close()

def insert_product_raw(product_id: str, vendor_id: str, category: str, sub_category: str,
                       price_usd: float, rating: float, rating_count: int,
                       avg_fulfillment_days: float) -> bool:
    """Insert a product into products_raw table"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO products_raw 
            (product_id, vendor_id, category, sub_category, price_usd, rating, rating_count, avg_fulfillment_days)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO NOTHING
        """, (product_id, vendor_id, category, sub_category, price_usd, rating, rating_count, avg_fulfillment_days))
        
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error inserting product_raw: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def insert_vendor_promotion(vendor_id: str, views: int, orders: int, net_rev: float,
                           conversion_rate: float, vendor_tier: str, vendor_region: str,
                           vendor_quality_score: float) -> bool:
    """Insert vendor promotion recommendation"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO vendor_promotion_recommendations 
            (vendor_id, views, orders, net_rev, conversion_rate, vendor_tier, vendor_region, vendor_quality_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (vendor_id) DO UPDATE SET 
                views = EXCLUDED.views,
                orders = EXCLUDED.orders,
                net_rev = EXCLUDED.net_rev,
                conversion_rate = EXCLUDED.conversion_rate
        """, (vendor_id, views, orders, net_rev, conversion_rate, vendor_tier, vendor_region, vendor_quality_score))
        
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error inserting vendor promotion: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def insert_discount_recommendation(product_id: str, vendor_id: str, category: str, sub_category: str,
                                   price_usd: float, views: int, orders: int, p_order: float,
                                   avg_discount: float, stock: int, avg_rating: float,
                                   avg_fulfillment: float, conversion_rate: float,
                                   suggested_discount: float) -> bool:
    """Insert discount recommendation"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO discount_recommendations 
            (product_id, vendor_id, category, sub_category, price_usd, views, orders, p_order,
             avg_discount, stock, avg_rating, avg_fulfillment, conversion_rate, suggested_discount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO UPDATE SET 
                suggested_discount = EXCLUDED.suggested_discount,
                avg_discount = EXCLUDED.avg_discount
        """, (product_id, vendor_id, category, sub_category, price_usd, views, orders, p_order,
              avg_discount, stock, avg_rating, avg_fulfillment, conversion_rate, suggested_discount))
        
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error inserting discount recommendation: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def insert_marketplace_daily_clean(date: str, product_id: str, vendor_id: str, category: str, sub_category: str,
                                    price_usd: float, discount_rate: float, ad_spend_usd: float, views: int, orders: int,
                                    gross_revenue_usd: float, returns: int, rating: float, rating_count: int,
                                    stock_units: int, avg_fulfillment_days: float, conversion_rate: float,
                                    return_rate: float, net_revenue_usd: float) -> bool:
    """Insert marketplace daily clean record"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO marketplace_daily_clean 
            (date, product_id, vendor_id, category, sub_category, price_usd, discount_rate, ad_spend_usd,
             views, orders, gross_revenue_usd, returns, rating, rating_count, stock_units, avg_fulfillment_days,
             conversion_rate, return_rate, net_revenue_usd)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date, product_id, vendor_id) DO NOTHING
        """, (date, product_id, vendor_id, category, sub_category, price_usd, discount_rate, ad_spend_usd,
              views, orders, gross_revenue_usd, returns, rating, rating_count, stock_units, avg_fulfillment_days,
              conversion_rate, return_rate, net_revenue_usd))
        
        if cur.rowcount > 0:
            conn.commit()
            return True
        else:
            conn.rollback()
            return False
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def batch_insert_marketplace_daily_clean(records: list) -> int:
    """Batch insert marketplace daily clean records for better performance"""
    conn = get_connection()
    cur = conn.cursor()
    
    inserted_count = 0
    try:
        for record in records:
            cur.execute("""
                INSERT INTO marketplace_daily_clean 
                (date, product_id, vendor_id, category, sub_category, price_usd, discount_rate, ad_spend_usd,
                 views, orders, gross_revenue_usd, returns, rating, rating_count, stock_units, avg_fulfillment_days,
                 conversion_rate, return_rate, net_revenue_usd)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, product_id, vendor_id) DO NOTHING
            """, record)
            inserted_count += cur.rowcount
        
        conn.commit()
        return inserted_count
    except Exception as e:
        conn.rollback()
        print(f"Error in batch insert: {e}")
        return 0
    finally:
        cur.close()
        conn.close()

def insert_marketplace_daily_raw(date: str, product_id: str, vendor_id: str, category: str, sub_category: str,
                                  price_usd: float, discount_rate: float, ad_spend_usd: float, views: int, orders: int,
                                  gross_revenue_usd: float, returns: int, rating: float, rating_count: int,
                                  stock_units: int, avg_fulfillment_days: float) -> bool:
    """Insert marketplace daily raw record"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO marketplace_daily_raw 
            (date, product_id, vendor_id, category, sub_category, price_usd, discount_rate, ad_spend_usd,
             views, orders, gross_revenue_usd, returns, rating, rating_count, stock_units, avg_fulfillment_days)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date, product_id, vendor_id) DO NOTHING
        """, (date, product_id, vendor_id, category, sub_category, price_usd, discount_rate, ad_spend_usd,
              views, orders, gross_revenue_usd, returns, rating, rating_count, stock_units, avg_fulfillment_days))
        
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error inserting marketplace daily raw: {e}")
        return False
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_database()
