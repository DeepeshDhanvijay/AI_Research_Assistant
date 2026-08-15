from app.services.vector_store import load_store, search
from app.services.llm_service import generate

def get_paper_ids() -> list[str]:
    _, chunks = load_store()
    return list({c.paper_id for c in chunks})

def find_relationships(paper_id: str, top_k_related: int = 3) -> dict:
    """
    Find papers related to a given paper by using that paper's own key content
    as a search query against the rest of the collection.
    """
    from app.services.summarization_service import get_paper_chunks

    chunks = get_paper_chunks(paper_id)
    if not chunks:
        return {"error": "Paper not found."}

    # Use the paper's first substantial chunk (usually abstract/intro) as a
    # representative query — a reasonable proxy for "what is this paper about"
    query_text = chunks[0].text[:300] if len(chunks[0].text) > 100 else chunks[1].text[:300]

    # Search broadly, then group hits by paper and exclude the source paper itself
    raw_results = search(query_text, top_k=30)
    related_by_paper = {}
    for r in raw_results:
        if r["paper_id"] == paper_id:
            continue
        related_by_paper.setdefault(r["paper_id"], []).append(r)

    # Rank candidate papers by how many of their chunks appeared as strong matches
    ranked = sorted(related_by_paper.items(), key=lambda kv: len(kv[1]), reverse=True)
    top_related = ranked[:top_k_related]

    if not top_related:
        return {"paper_id": paper_id, "related_papers": [], "explanation": "No related papers found in the current collection."}

    related_summary = "\n".join(
        f"- Paper {pid}: {matches[0]['text'][:200]}"
        for pid, matches in top_related
    )

    prompt = (
        f"A researcher is reading this paper excerpt:\n{query_text}\n\n"
        f"Here are excerpts from other papers in their collection:\n{related_summary}\n\n"
        "Briefly explain how these other papers might relate to or complement the first one."
    )

    explanation = generate(prompt, max_tokens=300)

    return {
        "paper_id": paper_id,
        "related_papers": [pid for pid, _ in top_related],
        "explanation": explanation,
    }

if __name__ == "__main__":
    paper_ids = get_paper_ids()
    if len(paper_ids) < 2:
        print("Need at least 2 papers to test relationships.")
    else:
        result = find_relationships(paper_ids[0])
        print(f"Paper: {result['paper_id']}")
        print(f"Related papers found: {result['related_papers']}\n")
        print(f"Explanation:\n{result['explanation']}")