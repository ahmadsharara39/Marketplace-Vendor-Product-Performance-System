"""Verify migration success"""
from db_config import get_connection
import pandas as pd
from pathlib import Path

conn = get_connection()
cur = conn.cursor()

# Get total count
cur.execute('SELECT COUNT(*) FROM products_raw')
total = cur.fetchone()[0]
print(f"✅ Total products in Neon: {total}")

# Get sample products
cur.execute('SELECT product_id, vendor_id, category, price_usd FROM products_raw LIMIT 5')
print("\nFirst 5 products:")
for row in cur.fetchall():
    print(f"  {row[0]} - {row[1]} - {row[2]} - ${row[3]}")

# Get distinct categories
cur.execute('SELECT DISTINCT category FROM products_raw ORDER BY category')
categories = [row[0] for row in cur.fetchall()]
print(f"\nCategories ({len(categories)}): {', '.join(categories)}")

# Get vendor distribution
cur.execute('SELECT COUNT(DISTINCT vendor_id) FROM products_raw')
vendor_count = cur.fetchone()[0]
print(f"Unique vendors: {vendor_count}")

# Compare with CSV
csv_file = Path(__file__).resolve().parents[1] / "products_from_raw.csv"
df = pd.read_csv(csv_file)
print(f"\nCSV file has {len(df)} products")
print(f"Migration successful: {total == len(df)}")

cur.close()
conn.close()
