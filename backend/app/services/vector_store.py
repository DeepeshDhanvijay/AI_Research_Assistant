import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.schemas.paper import Chunk

INDEX_PATH = settings.vector_store_dir / "papers.index"
METADATA_PATH = settings.vector_store_dir / "papers_metadata.pkl"

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model

def load_store() -> tuple[faiss.Index, list[Chunk]]:
    """Load the existing index + chunk metadata, or create empty ones if none exist yet."""
    if INDEX_PATH.exists() and METADATA_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
        with open(METADATA_PATH, "rb") as f:
            chunks = pickle.load(f)
        return index, chunks
    else:
        model = get_embedding_model()
        dimension = model.get_sentence_embedding_dimension()
        index = faiss.IndexFlatL2(dimension)
        return index, []

def save_store(index: faiss.Index, chunks: list[Chunk]):
    faiss.write_index(index, str(INDEX_PATH))
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(chunks, f)

def add_paper_chunks(new_chunks: list[Chunk]):
    """
    Embed and add a new paper's chunks to the existing store — additive, not a
    full rebuild. This is a deliberate upgrade from Project 1, where uploading
    meant re-indexing everything from scratch every time.
    """
    index, existing_chunks = load_store()
    model = get_embedding_model()

    texts = [c.text for c in new_chunks]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

    index.add(embeddings.astype(np.float32))
    all_chunks = existing_chunks + new_chunks

    save_store(index, all_chunks)
    return len(all_chunks)

def search(query: str, top_k: int = 5, paper_id: str | None = None) -> list[dict]:
    """
    Semantic search across all papers, or scoped to one paper_id if provided.
    """
    index, chunks = load_store()
    if index.ntotal == 0:
        return []

    model = get_embedding_model()
    query_vector = model.encode([query], convert_to_numpy=True).astype(np.float32)

    if paper_id:
        # Scoped search: fetch enough candidates to cover the WHOLE index, not just a
        # small multiple of top_k — otherwise a paper whose content is only weakly
        # related to the query can get silently filtered down to zero results, even
        # though it may still contain the best available match for that paper.
        fetch_k = index.ntotal
    else:
        fetch_k = top_k

    distances, indices = index.search(query_vector, fetch_k)

    results = []
    for rank, idx in enumerate(indices[0]):
        chunk = chunks[idx]
        if paper_id and chunk.paper_id != paper_id:
            continue
        results.append({
            "chunk_id": chunk.chunk_id,
            "paper_id": chunk.paper_id,
            "text": chunk.text,
            "chunk_index": chunk.chunk_index,
            "distance": float(distances[0][rank]),
        })
        if len(results) >= top_k:
            break

    return results