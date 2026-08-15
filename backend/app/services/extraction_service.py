from app.services.summarization_service import get_paper_chunks
from app.services.llm_service import generate
import re

MAX_CHUNK_CHARS = 400
EXTRACTION_CHUNK_LIMIT = 15

def extract_methodology_and_results(paper_id: str) -> dict:
    """
    Extract the paper's methodology and key results as separate, structured fields.
    Combines early chunks (methodology usually appears in the intro/methods sections)
    with chunks matched to results-related keywords (which often appear later in
    the paper and would otherwise fall outside a simple "first N chunks" window).
    """
    all_chunks = get_paper_chunks(paper_id)
    if not all_chunks:
        return {"error": "Paper not found."}

    # Methodology context: early chunks, where methods are typically introduced
    methodology_chunks = all_chunks[:8]

    # Results context: scan the WHOLE paper for chunks that look results-related,
    # rather than assuming they fall within the first N chunks in document order
    results_keywords = re.compile(
        r"\b(result|finding|performance|evaluat|throughput|accuracy|achiev|outperform|compar\w*\s+(with|to|against))\b",
        re.IGNORECASE
    )
    results_chunks = [c for c in all_chunks if results_keywords.search(c.text)][:8]

    # Combine, keeping methodology chunks first for readable ordering, avoiding duplicates
    combined_chunks = methodology_chunks + [c for c in results_chunks if c not in methodology_chunks]
    text = "\n".join(c.text[:MAX_CHUNK_CHARS] for c in combined_chunks)

    prompt = (
        "From the following research paper excerpt, extract two things:\n"
        "1. METHODOLOGY: What method, approach, or technique did the researchers use?\n"
        "2. RESULTS: What were the key quantitative or qualitative findings?\n"
        "If either is not present in the excerpt, say 'Not found in available content.'\n\n"
        f"Paper excerpt:\n{text}\n\n"
        "METHODOLOGY:"
    )

    result_text = generate(prompt, max_tokens=400)

    return {
        "paper_id": paper_id,
        "extraction": result_text,
    }

def extract_citations(paper_id: str) -> dict:
    """
    Extract citation references from a paper's LATER chunks (since references
    typically appear toward the end) — but recall Project 1/2 taught us
    reference sections get stripped during cleaning, so this needs the RAW text.
    """
    chunks = get_paper_chunks(paper_id)
    if not chunks:
        return {"error": "Paper not found."}

    # Look for chunks containing bracket-style citation markers like [1], [12], etc. —
    # a lightweight heuristic signal that a chunk discusses/references other work,
    # even after reference-section stripping (in-text citations remain in the body).
    import re
    citation_pattern = re.compile(r"\[\d+\]")
    citation_chunks = [c for c in chunks if citation_pattern.search(c.text)]

    if not citation_chunks:
        return {"paper_id": paper_id, "citations_found": [], "note": "No in-text citation markers detected."}

    combined = "\n".join(c.text[:MAX_CHUNK_CHARS] for c in citation_chunks[:10])

    prompt = (
        "The following text contains in-text citation markers like [1], [2], etc. "
        "List each distinct citation number found and briefly note what claim or topic "
        "it's attached to, based on the surrounding text.\n\n"
        f"Text:\n{combined}\n\n"
        "Citations found:"
    )

    result = generate(prompt, max_tokens=400)

    return {
        "paper_id": paper_id,
        "citation_analysis": result,
    }

if __name__ == "__main__":
    from app.services.vector_store import load_store

    _, chunks = load_store()
    paper_ids = list({c.paper_id for c in chunks})
    test_paper = paper_ids[0]

    print("=== Methodology & Results ===")
    result = extract_methodology_and_results(test_paper)
    print(result["extraction"])

    print("\n=== Citations ===")
    citations = extract_citations(test_paper)
    print(citations.get("citation_analysis", citations.get("note")))