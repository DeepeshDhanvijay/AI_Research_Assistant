from app.services.vector_store import load_store
from app.services.llm_service import generate

MAX_SUMMARY_INPUT_CHUNKS = 15   # cap how much of a paper we feed in, for cost/latency control
MAX_CHUNK_CHARS = 400

def get_paper_chunks(paper_id: str) -> list[dict]:
    """Retrieve all chunks for a specific paper, in original order."""
    _, chunks = load_store()
    paper_chunks = [c for c in chunks if c.paper_id == paper_id]
    paper_chunks.sort(key=lambda c: c.chunk_index)
    return paper_chunks

def summarize_paper(paper_id: str) -> str:
    """Generate a summary of a paper using its chunks (capped for token budget)."""
    chunks = get_paper_chunks(paper_id)

    if not chunks:
        return "Paper not found or contains no content."

    selected = chunks[:MAX_SUMMARY_INPUT_CHUNKS]
    combined_text = "\n\n".join(c.text[:MAX_CHUNK_CHARS] for c in selected)

    prompt = (
        "Summarize the following excerpt from a research paper in 3-4 sentences. "
        "Focus on the problem addressed, the method used, and key findings.\n\n"
        f"Paper excerpt:\n{combined_text}\n\n"
        "Summary:"
    )

    return generate(prompt, max_tokens=300)

if __name__ == "__main__":
    from app.services.vector_store import load_store

    _, chunks = load_store()
    paper_ids = list({c.paper_id for c in chunks})

    for pid in paper_ids:
        print(f"=== Paper {pid} ===")
        summary = summarize_paper(pid)
        print(f"{summary}\n")