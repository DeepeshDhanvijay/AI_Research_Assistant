from app.services.vector_store import search
from app.services.llm_service import generate

MAX_CONTEXT_CHUNKS = 5
MAX_CHUNK_CHARS = 400

def answer_question(query: str, paper_id: str | None = None) -> dict:
    """
    RAG-based Q&A: retrieve relevant chunks (optionally scoped to one paper),
    then generate a grounded answer citing which chunks were used.
    """
    results = search(query, top_k=MAX_CONTEXT_CHUNKS, paper_id=paper_id)

    if not results:
        return {
            "answer": "No relevant content found to answer this question.",
            "sources": [],
        }

    context = "\n\n".join(
        f"[{i+1}] {r['text'][:MAX_CHUNK_CHARS]}" for i, r in enumerate(results)
    )

    prompt = (
        "Answer the question using ONLY the numbered context below. "
        "Cite sources using [1], [2], etc. If the context doesn't contain the answer, say so.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )

    answer = generate(prompt, max_tokens=400)

    return {
        "answer": answer,
        "sources": [
            {"paper_id": r["paper_id"], "chunk_id": r["chunk_id"], "text": r["text"]}
            for r in results
        ],
    }

if __name__ == "__main__":
    result = answer_question("What routing protocol is implemented and what is it compared against?")
    print(f"Answer: {result['answer']}\n")
    print("Sources:")
    for s in result["sources"]:
        print(f"  {s['paper_id']} / {s['chunk_id']}: {s['text'][:80]}")