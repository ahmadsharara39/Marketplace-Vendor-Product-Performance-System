import os, json
from pathlib import Path
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from openai import RateLimitError

ROOT = Path(__file__).resolve().parents[1]
RAG_DIR = ROOT / "rag"

MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5

def load_chunks():
    chunks = []
    with open(RAG_DIR / "chunks.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

_chunks = None
_index = None
_emb = None

def init():
    global _chunks, _index, _emb
    if _chunks is None:
        _chunks = load_chunks()
    if _index is None:
        _index = faiss.read_index(str(RAG_DIR / "index.faiss"))
    if _emb is None:
        _emb = SentenceTransformer(MODEL_NAME)

def retrieve(query: str, k=TOP_K):
    init()

def answer(query: str):
    # retrieval
    contexts = retrieve(query)

    # build prompt with citations
    context_text = "\n\n".join(
        [f"[{i+1}] Source: {c['source']}\n{c['text']}" for i, c in enumerate(contexts)]
    )

    system = (
        "You are a marketplace analytics assistant. "
        "Answer using ONLY the provided sources. "
        "If the sources do not contain the answer, say you don't have enough info. "
        "Always include citations like [1], [2] referencing the source chunks."
    )

    user = f"""
Question: {query}

Sources:
{context_text}

Write a concise, management-friendly answer with bullet points and citations.
"""

    # LLM (OpenAI)
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )

    return resp.choices[0].message.content, contexts
