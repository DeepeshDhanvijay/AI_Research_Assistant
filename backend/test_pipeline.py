from pathlib import Path
from app.services.ingestion import ingest_paper
from app.services.chunking import chunk_text
from app.services.vector_store import add_paper_chunks, search
from app.core.config import settings

paper_ids = {}

for pdf_path in settings.papers_dir.glob("*.pdf"):
    metadata, text = ingest_paper(pdf_path, pdf_path.name)
    print(f"Ingested: {metadata.title} ({metadata.paper_id})")
    paper_ids[pdf_path.name] = metadata.paper_id

    chunks = chunk_text(text, metadata.paper_id)
    total = add_paper_chunks(chunks)
    print(f"  {len(chunks)} chunks added — store now has {total} total\n")

query = "wireless body area network routing"

print(f"=== Unfiltered search: '{query}' ===")
for r in search(query, top_k=3):
    print(f"  [{r['distance']:.3f}] paper {r['paper_id']}: {r['text'][:80]}")

# Scope to just the second paper, whatever its actual topic is
second_paper_id = list(paper_ids.values())[-1]
print(f"\n=== Filtered to paper {second_paper_id} ===")
for r in search(query, top_k=3, paper_id=second_paper_id):
    print(f"  [{r['distance']:.3f}] paper {r['paper_id']}: {r['text'][:80]}")