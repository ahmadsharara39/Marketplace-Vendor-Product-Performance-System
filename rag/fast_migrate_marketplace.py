"""
Fast migration using COPY FROM for bulk data loading
"""
import pandas as pd
import psycopg2
from pathlib import Path
import io

DATABASE_URL = "postgresql://neondb_owner:npg_yFpPzO2Di8gL@ep-hidden-sea-ahsxt09w-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
ROOT = Path(__file__).resolve().parents[1]

def copy_marketplace_daily_clean():
    """Use COPY FROM for fast bulk loading of clean marketplace data"""
    clean_csv = ROOT / "synthetic_marketplace_daily_clean.csv"
    
    if not clean_csv.exists():
        print(f"❌ Clean CSV not found: {clean_csv}")
        return False
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Truncate existing data
        print(f"🔄 Clearing existing marketplace_daily_clean data...")
        cur.execute("TRUNCATE marketplace_daily_clean;")
        conn.commit()
        
        print(f"🔄 Loading synthetic_marketplace_daily_clean.csv using COPY FROM...")
        
        with open(clean_csv, 'r') as f:
            cur.copy_expert("""
                COPY marketplace_daily_clean
                (date, product_id, vendor_id, category, sub_category, price_usd, discount_rate, ad_spend_usd,
                 views, orders, gross_revenue_usd, returns, rating, rating_count, stock_units, avg_fulfillment_days,
                 conversion_rate, return_rate, net_revenue_usd)
                FROM STDIN WITH (FORMAT csv, HEADER true)
            """, f)
        
        row_count = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Loaded {row_count} records from marketplace_daily_clean.csv")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def copy_marketplace_daily_raw():
    """Use COPY FROM for fast bulk loading of raw marketplace data, with type conversion"""
    raw_csv = ROOT / "synthetic_marketplace_daily_raw.csv"
    
    if not raw_csv.exists():
        print(f"❌ Raw CSV not found: {raw_csv}")
        return False
    
    try:
        # Read and fix data types before loading
        df = pd.read_csv(raw_csv)
        
        # Convert float columns to int where needed
        int_columns = ['views', 'orders', 'returns', 'rating_count', 'stock_units']
        for col in int_columns:
            if col in df.columns:
                df[col] = df[col].fillna(0).astype(int)
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Truncate existing data
        print(f"🔄 Clearing existing marketplace_daily_raw data...")
        cur.execute("TRUNCATE marketplace_daily_raw;")
        conn.commit()
        
        print(f"🔄 Loading synthetic_marketplace_daily_raw.csv using COPY FROM...")
        
        # Convert dataframe to CSV in memory
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=True)
        buffer.seek(0)
        
        cur.copy_expert("""
            COPY marketplace_daily_raw
            (date, product_id, vendor_id, category, sub_category, price_usd, discount_rate, ad_spend_usd,
             views, orders, gross_revenue_usd, returns, rating, rating_count, stock_units, avg_fulfillment_days)
            FROM STDIN WITH (FORMAT csv, HEADER true)
        """, buffer)
        
        row_count = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Loaded {row_count} records from marketplace_daily_raw.csv")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔄 Starting fast marketplace migration using COPY FROM...\n")
    
    print("1. Loading marketplace_daily_clean.csv...")
    clean_success = copy_marketplace_daily_clean()
    
    print("\n2. Loading marketplace_daily_raw.csv...")
    raw_success = copy_marketplace_daily_raw()
    
    if clean_success and raw_success:
        print("\n✅ All marketplace data loaded successfully!")
    else:
        print("\n⚠️  Some loads failed")
