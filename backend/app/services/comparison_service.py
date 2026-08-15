from app.services.summarization_service import summarize_paper, get_paper_chunks
from app.services.llm_service import generate

MAX_CHUNK_CHARS = 400
CHUNKS_PER_PAPER = 8   # smaller than summarization's cap, since we're feeding TWO papers' worth of context now

def compare_papers(paper_id_a: str, paper_id_b: str) -> dict:
    """Compare two papers: their individual summaries, plus an LLM-generated contrast."""
    chunks_a = get_paper_chunks(paper_id_a)[:CHUNKS_PER_PAPER]
    chunks_b = get_paper_chunks(paper_id_b)[:CHUNKS_PER_PAPER]

    if not chunks_a or not chunks_b:
        return {"error": "One or both papers not found."}

    text_a = "\n".join(c.text[:MAX_CHUNK_CHARS] for c in chunks_a)
    text_b = "\n".join(c.text[:MAX_CHUNK_CHARS] for c in chunks_b)

    prompt = (
        "Compare the following two research paper excerpts. Discuss: "
        "(1) their research focus/topic, (2) their methods, (3) key differences.\n\n"
        f"Paper A:\n{text_a}\n\n"
        f"Paper B:\n{text_b}\n\n"
        "Comparison:"
    )

    comparison = generate(prompt, max_tokens=500)

    return {
        "paper_a": paper_id_a,
        "paper_b": paper_id_b,
        "comparison": comparison,
    }

def generate_literature_review(paper_ids: list[str] | None = None, max_papers: int = 5) -> dict:
    """
    Generate a literature-review-style synthesis across multiple papers.
    If paper_ids is None, uses all papers currently in the collection (capped at max_papers).
    """
    from app.services.vector_store import load_store

    if paper_ids is None:
        _, chunks = load_store()
        paper_ids = list({c.paper_id for c in chunks})

    paper_ids = paper_ids[:max_papers]  # cap for token budget — same discipline as comparison

    if len(paper_ids) < 2:
        return {"error": "Need at least 2 papers to generate a literature review."}

    paper_excerpts = []
    for pid in paper_ids:
        chunks = get_paper_chunks(pid)[:5]  # fewer chunks per paper as N grows, same budget-splitting logic as comparison
        if chunks:
            text = " ".join(c.text[:300] for c in chunks)
            paper_excerpts.append(f"Paper {pid}:\n{text}")

    combined = "\n\n".join(paper_excerpts)

    prompt = (
        "Write a brief literature review (4-6 sentences) synthesizing the following research "
        "papers. Identify common themes, methodological approaches, and how the papers relate "
        "to or differ from each other.\n\n"
        f"{combined}\n\n"
        "Literature Review:"
    )

    review = generate(prompt, max_tokens=500)

    return {
        "papers_included": paper_ids,
        "literature_review": review,
    }

if __name__ == "__main__":
    from app.services.vector_store import load_store

    _, chunks = load_store()
    paper_ids = list({c.paper_id for c in chunks})

    if len(paper_ids) < 2:
        print("Need at least 2 papers in the store to test comparison.")
    else:
        result = compare_papers(paper_ids[0], paper_ids[1])
        print(f"Comparing {result['paper_a']} vs {result['paper_b']}\n")
        print(result["comparison"])