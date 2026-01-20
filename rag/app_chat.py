import streamlit as st
from rag_core import answer

st.set_page_config(page_title="Marketplace RAG Chatbot", layout="wide")
st.title("📊 Marketplace RAG Chatbot (Docs + AI Recommendations)")

st.caption("Ask questions about vendors, categories, performance tables, and recommendations. Answers include sources.")

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
