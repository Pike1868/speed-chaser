# retriever.py
import os, pickle
import faiss
from sentence_transformers import SentenceTransformer
from config import get_embedding_device
device = get_embedding_device()
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)


INDEX_PATH = "vectorstore/index.faiss"
META_PATH = "vectorstore/index.pkl"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # match your ingest.py


def load_index_and_metadata():
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        raise FileNotFoundError("No FAISS index found. Please run ingestion first.")
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def retrieve(query, top_k=15):
    """
    Embeds the user query, does a vector search, 
    and returns top_k chunk results from the store.
    """
    index, meta = load_index_and_metadata()
    query_embedding = model.encode([query])
    D, I = index.search(query_embedding, top_k)
    results = []
    for idx in I[0]:
        if 0 <= idx < len(meta):
            results.append(meta[idx])  # each meta entry has {filename, content}
    return results
