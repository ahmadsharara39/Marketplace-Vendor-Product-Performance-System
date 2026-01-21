import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Marketplace Performance Dashboard", layout="wide")

# ---- Navigation (Dashboard vs RAG Chatbot) ----
mode = st.sidebar.radio("Mode", ["Dashboard", "RAG Chatbot"], index=0)

if mode == "RAG Chatbot":
    st.title("📊 Marketplace RAG Chatbot")
    st.caption("Ask questions grounded in REPORT.md, tables, and AI recommendation outputs. Answers include sources.")

    # Import only when needed (keeps dashboard fast)
    from rag.rag_core import answer
    from rag.add_data import add_vendor, add_product   # if you want chat-driven inserts later

    if "rag_messages" not in st.session_state:
        st.session_state.rag_messages = []

    # Show chat history
    for m in st.session_state.rag_messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Ask a question (e.g., 'Why are some vendors underperforming?')")
    if prompt:
        st.session_state.rag_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
    prompt_lower = prompt.lower().strip()

    is_add_vendor = ("add" in prompt_lower) and ("vendor" in prompt_lower)
    is_add_product = ("add" in prompt_lower) and ("product" in prompt_lower)

    # ✅ If user wants to add data, DO NOT call OpenAI
    if is_add_vendor and not is_add_product:
        st.markdown("""
### ➕ Add Vendor (empty fields)

**vendor_id (e.g., V050):**  
**vendor_tier (Bronze / Silver / Gold):**  
**vendor_region (Levant / GCC / Europe / North Africa / Asia):**  
**vendor_quality_score (-2 to 2):**  

✅ Add it using your data-entry UI (sidebar form), or tell me the values here and I can format them for you.
""")
        st.session_state.rag_messages.append({"role": "assistant", "content": "Vendor add template shown."})
        st.stop()

    if is_add_product and not is_add_vendor:
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

✅ Add it using your data-entry UI (sidebar form), or tell me the values here and I can format them for you.
""")
        st.session_state.rag_messages.append({"role": "assistant", "content": "Product add template shown."})
        st.stop()

    # Normal RAG flow
    with st.spinner("Retrieving and answering..."):
        out, contexts = answer(prompt)
        st.markdown(out)

        with st.expander("Sources used"):
            for i, c in enumerate(contexts, start=1):
                st.write(f"[{i}] {c['source']} (score={c['score']:.3f})")
                st.code(c["text"][:800] + ("..." if len(c["text"]) > 800 else ""))

        st.session_state.rag_messages.append({"role": "assistant", "content": out})

    st.stop()  # Prevent dashboard code from running under chatbot mode


@st.cache_data
def load_data():
    clean = pd.read_csv("synthetic_marketplace_daily_clean.csv", parse_dates=["date"])
    vendors = pd.read_csv("vendors_master.csv")

    # Optional files (if present)
    ai_discount = None
    ai_promo = None
    try:
        ai_discount = pd.read_csv("ai_discount_recommendations.csv")
    except Exception:
        pass
    try:
        ai_promo = pd.read_csv("ai_vendor_promotion_recommendations.csv")
    except Exception:
        pass

    summary_txt = None
    try:
        with open("AI_management_summary.txt", "r", encoding="utf-8") as f:
            summary_txt = f.read()
    except Exception:
        pass

    return clean, vendors, ai_discount, ai_promo, summary_txt

clean, vendors, ai_discount, ai_promo, summary_txt = load_data()

# ---------------------------
# Sidebar filters
# ---------------------------
st.sidebar.title("Filters")

min_date = clean["date"].min().date()
max_date = clean["date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_date, max_date))

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

categories = ["All"] + sorted(clean["category"].unique().tolist())
category = st.sidebar.selectbox("Category", categories)

vendors_list = ["All"] + sorted(clean["vendor_id"].unique().tolist())
vendor = st.sidebar.selectbox("Vendor", vendors_list)

df = clean[(clean["date"].dt.date >= start_date) & (clean["date"].dt.date <= end_date)].copy()
if category != "All":
    df = df[df["category"] == category]
if vendor != "All":
    df = df[df["vendor_id"] == vendor]

# ---------------------------
# KPI header
# ---------------------------
st.title("Marketplace Vendor & Product Performance Dashboard")

total_views = int(df["views"].sum())
total_orders = int(df["orders"].sum())
net_rev = float(df["net_revenue_usd"].sum())
conv = (total_orders / total_views) if total_views else 0.0
returns = int(df["returns"].sum())
ret_rate = (returns / total_orders) if total_orders else 0.0
avg_fulfill = float(df["avg_fulfillment_days"].mean())

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Views", f"{total_views:,}")
c2.metric("Orders", f"{total_orders:,}")
c3.metric("Net Revenue", f"${net_rev:,.0f}")
c4.metric("Conversion", f"{conv*100:.2f}%")
c5.metric("Return Rate", f"{ret_rate*100:.2f}%")
c6.metric("Avg Fulfillment (days)", f"{avg_fulfill:.1f}")

st.divider()

# ---------------------------
# Charts: Top vendors & categories
# ---------------------------
left, right = st.columns(2)

with left:
    st.subheader("Top Vendors by Net Revenue")
    vend = df.groupby("vendor_id", as_index=False)["net_revenue_usd"].sum().sort_values("net_revenue_usd", ascending=False).head(10)
    fig = plt.figure(figsize=(7,4))
    plt.bar(vend["vendor_id"], vend["net_revenue_usd"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Net Revenue (USD)")
    plt.tight_layout()
    st.pyplot(fig)

with right:
    st.subheader("Top Vendors by Conversion Rate (min views)")
    vend2 = df.groupby("vendor_id", as_index=False).agg(views=("views","sum"), orders=("orders","sum"))
    vend2 = vend2[vend2["views"] > 2000].copy()
    vend2["conversion_rate"] = vend2["orders"] / vend2["views"]
    vend2 = vend2.sort_values("conversion_rate", ascending=False).head(10)

    fig = plt.figure(figsize=(7,4))
    plt.bar(vend2["vendor_id"], vend2["conversion_rate"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Conversion Rate")
    plt.tight_layout()
    st.pyplot(fig)

left2, right2 = st.columns(2)

with left2:
    st.subheader("Net Revenue by Category")
    cat = df.groupby("category", as_index=False)["net_revenue_usd"].sum().sort_values("net_revenue_usd", ascending=False)
    fig = plt.figure(figsize=(7,4))
    plt.bar(cat["category"], cat["net_revenue_usd"])
    plt.xticks(rotation=35, ha="right")
    plt.ylabel("Net Revenue (USD)")
    plt.tight_layout()
    st.pyplot(fig)

with right2:
    st.subheader("Products: Views vs Conversion (sample)")
    prod = df.groupby(["product_id","category"], as_index=False).agg(views=("views","sum"), orders=("orders","sum"))
    prod["conversion_rate"] = prod["orders"] / prod["views"].replace(0, np.nan)
    sample = prod.sample(min(len(prod), 1200), random_state=42) if len(prod) else prod

    fig = plt.figure(figsize=(7,4))
    plt.scatter(sample["views"], sample["conversion_rate"].fillna(0), s=10, alpha=0.6)
    plt.xlabel("Total Views")
    plt.ylabel("Conversion Rate")
    plt.tight_layout()
    st.pyplot(fig)

st.divider()

# ---------------------------
# Tables: AI recommendations
# ---------------------------
st.subheader("AI Recommendations")

tab1, tab2 = st.tabs(["Products to discount", "Vendors to promote"])

with tab1:
    if ai_discount is None:
        st.warning("ai_discount_recommendations.csv not found. Run your recommendation script to generate it.")
    else:
        st.dataframe(ai_discount, use_container_width=True)

with tab2:
    if ai_promo is None:
        st.warning("ai_vendor_promotion_recommendations.csv not found. Run your recommendation script to generate it.")
    else:
        st.dataframe(ai_promo, use_container_width=True)

st.divider()

# ---------------------------
# Management Summary panel
# ---------------------------
st.subheader("Management Summary")
if summary_txt:
    st.text_area("AI-generated summary", summary_txt, height=250)
else:
    st.info("AI_management_summary.txt not found (optional). Add it to show a narrative summary.")
