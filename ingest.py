import os
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
from config import get_embedding_device
device = get_embedding_device()
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
INDEX_PATH = "vectorstore/index.faiss"
META_PATH = "vectorstore/index.pkl"
IGNORE_FOLDERS = {".git", ".venv", "__pycache__", "node_modules"}
IGNORE_FILES = {".DS_Store"}  # optional for single-file ignores

# Ensure the vectorstore folder exists
os.makedirs("vectorstore", exist_ok=True)

def load_files_from_path(path: str, extensions=(".pdf", ".py", ".md", ".txt", ".ts", ".tsx", ".js", ".jsx")):
    from utils.pdf_parser import extract_text_from_pdf  # import your PDF parser
    IGNORE_FOLDERS = {".git", ".venv", "__pycache__", "node_modules", "lib", "bin", "dist", "site-packages"}
    IGNORE_FILES = {".DS_Store", "yarn.lock", "package-lock.json"}

    docs = []
    path_obj = Path(path)
    for file in path_obj.rglob("*"):
        # Skip big or irrelevant folders
        if any(ignored in file.parts for ignored in IGNORE_FOLDERS):
            continue

        # Skip single-file ignores
        if file.name in IGNORE_FILES:
            continue

        # Skip if extension not in the set
        if file.suffix.lower() not in extensions:
            continue

        # Now load the content differently for PDF vs text
        try:
            if file.suffix.lower() == ".pdf":
                # Use your existing PyMuPDF-based parser
                text = extract_text_from_pdf(str(file))  
            else:
                # For normal text-based files
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()

            # Only add if there's actually text
            if text.strip():
                docs.append((str(file), text))
            else:
                print(f"Warning: No text extracted from {file}")
        except Exception as e:
            print(f"Error reading file {file}: {e}")

    return docs


def chunk_text(text: str, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    return chunks

def ingest(path: str):
    print(f"Ingesting files from: {path}")
    documents = load_files_from_path(path)

    corpus = []
    metadata = []

    for filename, text in documents:
        chunks = chunk_text(text)
        for chunk in chunks:
            corpus.append(chunk)
            metadata.append({"filename": filename, "content": chunk})

    print(f"Embedding {len(corpus)} chunks...")
    embeddings = model.encode(corpus, show_progress_bar=True)

    dimension = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print("Ingestion complete. Vector store saved.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest reference files for Speed Chaser")
    parser.add_argument("--path", type=str, default="refs/", help="Path to reference folder")
    args = parser.parse_args()
    ingest(args.path)
