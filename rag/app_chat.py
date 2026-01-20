import streamlit as st
from rag_core import answer
from add_data import add_vendor, add_product, get_vendor_suggestions, get_product_suggestions

st.set_page_config(page_title="Marketplace RAG Chatbot", layout="wide")
st.title("📊 Marketplace RAG Chatbot (Docs + AI Recommendations)")

st.caption("Ask questions about vendors, categories, performance tables, and recommendations. Answers include sources.")

# Sidebar for adding vendors/products
with st.sidebar:
    st.header("➕ Add Data to CSV")
    st.caption("Fill the form below to add vendor or product data directly to the CSV files")
    tab1, tab2 = st.tabs(["Add Vendor", "Add Product"])
    
    with tab1:
        st.subheader("Add New Vendor to vendors_master.csv")
        
        with st.form("vendor_form", clear_on_submit=True):
            vendor_id = st.text_input("Vendor ID (e.g., V050)")
            vendor_tier = st.selectbox("Vendor Tier", ["Bronze", "Silver", "Gold"])
            vendor_region = st.selectbox("Vendor Region", ["Levant", "GCC", "Europe", "North Africa", "Asia"])
            vendor_quality_score = st.slider("Quality Score", -2.0, 2.0, 0.0, 0.1)
            
            if st.form_submit_button("✓ Add Vendor to CSV", use_container_width=True):
                if vendor_id and len(vendor_id) > 1:
                    result = add_vendor(vendor_id.upper(), vendor_tier, vendor_region, vendor_quality_score)
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
                else:
                    st.error("Please enter a valid Vendor ID")
    
    with tab2:
        st.subheader("Add New Product to synthetic_marketplace_daily_clean.csv")
        
        with st.form("product_form", clear_on_submit=True):
            date = st.date_input("Date")
            product_id = st.text_input("Product ID (e.g., P00100)")
            vendor_id = st.text_input("Vendor ID (e.g., V050)")
            category = st.text_input("Category (e.g., Electronics)")
            sub_category = st.text_input("Sub-Category (e.g., Laptops)")
            price_usd = st.number_input("Price (USD)", min_value=0.01, value=0.0, step=1.0)
            discount_rate = st.slider("Discount Rate", 0.0, 1.0, 0.0, 0.01)
            ad_spend_usd = st.number_input("Ad Spend (USD)", min_value=0.0, value=0.0, step=1.0)
            views = st.number_input("Views", min_value=0, value=0, step=1)
            orders = st.number_input("Orders", min_value=0, value=0, step=1)
            returns = st.number_input("Returns", min_value=0, value=0, step=1)
            rating = st.slider("Rating", 1.0, 5.0, 3.0, 0.1)
            rating_count = st.number_input("Rating Count", min_value=0, value=0, step=1)
            stock_units = st.number_input("Stock Units", min_value=0, value=0, step=1)
            avg_fulfillment_days = st.number_input("Fulfillment Days", min_value=0.1, value=0.1, step=0.1)
            gross_revenue_usd = st.number_input("Gross Revenue (USD)", min_value=0.0, value=0.0, step=1.0)
            
            if st.form_submit_button("✓ Add Product to CSV", use_container_width=True):
                if product_id and len(product_id) > 1 and vendor_id and len(vendor_id) > 1:
                    result = add_product(
                        str(date), product_id.upper(), vendor_id.upper(), category, sub_category,
                        price_usd, discount_rate, ad_spend_usd, views, orders,
                        gross_revenue_usd, returns, rating, rating_count,
                        stock_units, avg_fulfillment_days
                    )
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
                else:
                    st.error("Please fill in all required fields")

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
        with st.spinner("Retrieving and answering..."):
            out, contexts = answer(prompt)
            st.markdown(out)

            with st.expander("Sources used"):
                for i, c in enumerate(contexts, start=1):
                    st.write(f"[{i}] {c['source']} (score={c['score']:.3f})")
                    st.code(c["text"][:800] + ("..." if len(c["text"]) > 800 else ""))

    st.session_state.messages.append({"role": "assistant", "content": out})
