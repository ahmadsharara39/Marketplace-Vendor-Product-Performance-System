import streamlit as st
from rag_core import answer
from add_data import add_vendor, add_product
from db_config import get_all_vendors
import datetime

st.set_page_config(page_title="Marketplace RAG Chatbot", layout="wide")
st.title("📊 Marketplace RAG Chatbot (Docs + AI Recommendations)")

st.caption("Ask questions about vendors, categories, performance tables, and recommendations. Answers include sources.")

# Initialize session state for form clearing
if "vendor_form_submitted" not in st.session_state:
    st.session_state.vendor_form_submitted = False
if "product_form_submitted" not in st.session_state:
    st.session_state.product_form_submitted = False

# Sidebar for adding vendors/products
with st.sidebar:
    st.header("➕ Add Data to Database")
    st.caption("Fill the form below to add vendor or product data directly to the database")
    tab1, tab2 = st.tabs(["Add Vendor", "Add Product"])
    
    with tab1:
        st.subheader("Add New Vendor")
        
        with st.form("vendor_form"):
            vendor_id = st.text_input("Vendor ID (e.g., V050)", placeholder="Enter Vendor ID", key="vendor_id_input")
            vendor_tier = st.selectbox("Vendor Tier", ["Bronze", "Silver", "Gold"], key="vendor_tier_select")
            vendor_region = st.selectbox("Vendor Region", ["Levant", "GCC", "Europe", "North Africa", "Asia"], key="vendor_region_select")
            vendor_quality_score = st.slider("Quality Score", -2.0, 2.0, 0.0, 0.1, key="vendor_score_slider")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✓ Add Vendor to Database", use_container_width=True):
                    if vendor_id and len(vendor_id) > 1:
                        result = add_vendor(vendor_id.upper(), vendor_tier, vendor_region, vendor_quality_score)
                        if result["success"]:
                            st.success(result["message"])
                            st.session_state.vendor_form_submitted = True
                            st.rerun()
                        else:
                            st.error(result["message"])
                    else:
                        st.error("Please enter a valid Vendor ID")
            with col2:
                if st.form_submit_button("Clear Fields", use_container_width=True):
                    st.session_state.vendor_id_input = ""
                    st.session_state.vendor_tier_select = "Bronze"
                    st.session_state.vendor_region_select = "Levant"
                    st.session_state.vendor_score_slider = 0.0
                    st.rerun()
    
    with tab2:
        st.subheader("Add New Product")
        
        # Get existing vendors from database for selection
        try:
            vendors_list = get_all_vendors()
            vendor_ids = [v['vendor_id'] for v in vendors_list]
        except:
            vendor_ids = []
            st.warning("Could not load vendors from database")
        
        with st.form("product_form"):
            col_left, col_right = st.columns(2)
            
            with col_left:
                date = st.date_input("Date", value=datetime.date.today(), key="product_date_input")
                product_id = st.text_input("Product ID (e.g., P00100)", placeholder="Enter Product ID", key="product_id_input")
                category = st.text_input("Category (e.g., Electronics)", placeholder="Enter Category", key="product_category_input")
                sub_category = st.text_input("Sub-Category (e.g., Laptops)", placeholder="Enter Sub-Category", key="product_subcategory_input")
                price_usd = st.number_input("Price (USD)", min_value=0.01, value=0.0, step=1.0, key="product_price_input")
                discount_rate = st.slider("Discount Rate", 0.0, 1.0, 0.0, 0.01, key="product_discount_slider")
                ad_spend_usd = st.number_input("Ad Spend (USD)", min_value=0.0, value=0.0, step=1.0, key="product_adspend_input")
            
            with col_right:
                if vendor_ids:
                    vendor_id = st.selectbox("Select Vendor", vendor_ids, key="product_vendor_select")
                else:
                    vendor_id = st.text_input("Vendor ID (e.g., V050)", placeholder="Enter Vendor ID", key="product_vendor_input")
                
                views = st.number_input("Views", min_value=0, value=0, step=1, key="product_views_input")
                orders = st.number_input("Orders", min_value=0, value=0, step=1, key="product_orders_input")
                returns = st.number_input("Returns", min_value=0, value=0, step=1, key="product_returns_input")
                rating = st.slider("Rating", 1.0, 5.0, 3.0, 0.1, key="product_rating_slider")
                rating_count = st.number_input("Rating Count", min_value=0, value=0, step=1, key="product_rating_count_input")
                stock_units = st.number_input("Stock Units", min_value=0, value=0, step=1, key="product_stock_input")
                avg_fulfillment_days = st.number_input("Fulfillment Days", min_value=0.1, value=0.1, step=0.1, key="product_fulfillment_input")
                gross_revenue_usd = st.number_input("Gross Revenue (USD)", min_value=0.0, value=0.0, step=1.0, key="product_gross_revenue_input")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✓ Add Product to Database", use_container_width=True):
                    if product_id and len(product_id) > 1 and vendor_id and len(vendor_id) > 1:
                        result = add_product(
                            str(date), product_id.upper(), vendor_id.upper(), category, sub_category,
                            price_usd, discount_rate, ad_spend_usd, views, orders,
                            gross_revenue_usd, returns, rating, rating_count,
                            stock_units, avg_fulfillment_days
                        )
                        if result["success"]:
                            st.success(result["message"])
                            st.session_state.product_form_submitted = True
                            st.rerun()
                        else:
                            st.error(result["message"])
                    else:
                        st.error("Please fill in all required fields")
            
            with col2:
                if st.form_submit_button("Clear All Fields", use_container_width=True):
                    # Clear all product form fields
                    for key in list(st.session_state.keys()):
                        if 'product_' in key:
                            del st.session_state[key]
                    st.rerun()


st.divider()
st.info("💡 **To add a new vendor or product:** Use the '➕ Add Data to Database' forms in the sidebar on the left. You'll see blank cells to fill in.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ask a question (e.g., 'Why are some vendors underperforming?' )")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Check if user is asking about adding vendor or product
        prompt_lower = prompt.lower().strip()
        
        # More comprehensive keywords to detect add vendor/product requests
        add_vendor_keywords = [
            "add new vendor", "add vendor", "add a vendor", "new vendor", "create vendor", 
            "want to add vendor", "i want to add vendor", "adding vendor",
            "how to add vendor", "add new vendor", "create new vendor",
            "onboard vendor", "add vendor to marketplace", "vendor to the marketplace",
            "to add a vendor", "to add vendor", "please consider", "vendor performance",
            "vendor tier", "vendor region", "vendor quality", "vendor overview",
            "current vendor", "35 vendors", "bronze", "silver", "gold",
            "current vendor landscape", "vendor evaluation", "vendor addition"
        ]
        add_product_keywords = [
            "add new product", "add product", "add a product", "new product", "create product", 
            "want to add product", "i want to add product", "adding product",
            "how to add product", "add new product", "create new product",
            "onboard product", "add product to marketplace"
        ]
        
        # Check if any keyword matches (even partial)
        is_add_vendor = any(keyword in prompt_lower for keyword in add_vendor_keywords)
        is_add_product = any(keyword in prompt_lower for keyword in add_product_keywords)
        
        # Also check if message contains "Current Vendor" or looks like RAG output being re-sent
        looks_like_vendor_rag = "current vendor" in prompt_lower or "vendor overview" in prompt_lower
        looks_like_add_request = "to add" in prompt_lower and ("vendor" in prompt_lower or "product" in prompt_lower)
        
        if is_add_vendor and not is_add_product:
            st.markdown("""
### ➕ Add Vendor (empty fields)

**vendor_id (e.g., V050):**  
**vendor_tier (Bronze / Silver / Gold):**  
**vendor_region (Levant / GCC / Europe / North Africa / Asia):**  
**vendor_quality_score (-2 to 2):**  

✅ Fill these in the left sidebar → **Add Vendor** tab, then click **✓ Add Vendor to Database**.
""")

elif is_add_product and not is_add_vendor:
    st.markdown("""
### ➕ Add Product (empty fields)

**date (YYYY-MM-DD):**  
**product_id (e.g., P00100):**  
**vendor_id (e.g., V050):**  
**category:**  
**sub_category:**  
**price_usd:**  
**discount_rate (0–1):**  
**ad_spend_usd:**  
**views:**  
**orders:**  
**gross_revenue_usd:**  
**returns:**  
**rating (1–5):**  
**rating_count:**  
**stock_units:**  
**avg_fulfillment_days:**  

✅ Fill these in the left sidebar → **Add Product** tab, then click **✓ Add Product to Database**.
""")

elif (looks_like_vendor_rag or looks_like_add_request) and not (is_add_vendor or is_add_product):
    st.markdown("""
Do you want to add a **vendor** or a **product**?

- Type **add vendor**
- Or type **add product**
""")

else:
    with st.spinner("Retrieving and answering..."):
        out, contexts = answer(prompt)
        st.markdown(out)

        with st.expander("Sources used"):
            for i, c in enumerate(contexts, start=1):
                st.write(f"[{i}] {c['source']} (score={c['score']:.3f})")
                st.code(c["text"][:800] + ("..." if len(c["text"]) > 800 else ""))

    st.session_state.messages[-1] = {"role": "assistant", "content": out}
