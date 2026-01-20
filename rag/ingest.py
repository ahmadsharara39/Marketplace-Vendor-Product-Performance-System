import os
import json
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss

ROOT = Path(__file__).resolve().parents[1]
RAG_DIR = ROOT / "rag"
SOURCES_FILE = RAG_DIR / "data_sources.txt"

MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, good for RAG
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

def read_file(path: Path) -> str:
    if path.suffix.lower() in [".md", ".txt"]:
        return path.read_text(encoding="utf-8", errors="ignore")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
        # turn table into readable text (limit width for embeddings)
        return df.head(200).to_csv(index=False)  # keep it smaller for better retrieval

    # fallback
    return path.read_text(encoding="utf-8", errors="ignore")

def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = text.replace("\r\n", "\n")
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0:
            start = 0
        if end == len(text):
            break
    return chunks

def main():
    RAG_DIR.mkdir(parents=True, exist_ok=True)

    sources = [line.strip() for line in SOURCES_FILE.read_text().splitlines() if line.strip()]
    docs = []

    for rel in sources:
        p = (ROOT / rel).resolve()
        if not p.exists():
            print(f"[WARN] Missing: {rel}")
            continue
        text = read_file(p)
        for i, ch in enumerate(chunk_text(text)):
            docs.append({
                "id": f"{rel}::chunk{i}",
                "source": rel,
                "text": ch
            })

    print(f"Loaded chunks: {len(docs)}")

    # Embed
    emb_model = SentenceTransformer(MODEL_NAME)
    vectors = emb_model.encode([d["text"] for d in docs], normalize_embeddings=True, show_progress_bar=True)
    vectors = vectors.astype("float32")

    # FAISS index
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    faiss.write_index(index, str(RAG_DIR / "index.faiss"))

    with open(RAG_DIR / "chunks.jsonl", "w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print("Saved: rag/index.faiss and rag/chunks.jsonl")

if __name__ == "__main__":
    main()
