import json
from app.core.config import settings
from app.schemas.paper import PaperMetadata

REGISTRY_PATH = settings.vector_store_dir / "paper_registry.json"

def load_registry() -> dict:
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_registry(registry: dict):
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, default=str)

def register_paper(metadata: PaperMetadata):
    registry = load_registry()
    registry[metadata.paper_id] = metadata.model_dump(mode="json")
    save_registry(registry)

def get_paper(paper_id: str) -> dict | None:
    return load_registry().get(paper_id)

def list_papers() -> list[dict]:
    return list(load_registry().values())

def find_by_hash(file_hash: str) -> dict | None:
    """Duplicate detection — the piece we deferred back in Step 6."""
    for paper in load_registry().values():
        if paper.get("file_hash") == file_hash:
            return paper
    return None