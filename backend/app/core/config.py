import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Paths — computed relative to this file, so they work regardless of where
    # the app is run from (local dev, Docker container, deployed server)
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    papers_dir: Path = base_dir / "data" / "papers"
    vector_store_dir: Path = base_dir / "data" / "vector_store"

    # API keys / secrets — loaded from .env automatically
    hf_token: str = ""

    # App metadata
    environment: str = "development"
    app_name: str = "AI Research Platform"

    # Model config — centralized so changing models later means editing one place
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "Qwen/Qwen2.5-7B-Instruct"  # general-purpose, not the -Coder variant

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure required directories exist at startup
settings.papers_dir.mkdir(parents=True, exist_ok=True)
settings.vector_store_dir.mkdir(parents=True, exist_ok=True)