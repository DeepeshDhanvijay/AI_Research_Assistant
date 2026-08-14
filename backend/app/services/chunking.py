from app.schemas.paper import Chunk

def chunk_text(text: str, paper_id: str, chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Split a paper's text into overlapping chunks, tagged with its paper_id."""
    chunks = []
    start = 0
    index = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk_text_content = text[start:end]
        chunks.append(Chunk(
            chunk_id=f"{paper_id}_{index}",
            paper_id=paper_id,
            text=chunk_text_content,
            chunk_index=index,
        ))
        start += chunk_size - overlap
        index += 1

    return chunks