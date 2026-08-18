import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    papers_dir: Path = base_dir / "data" / "papers"
    vector_store_dir: Path = base_dir / "data" / "vector_store"

    hf_token: str = ""
    cors_origins: str = "http://localhost:5173"

    environment: str = "development"
    app_name: str = "AI Research Platform"

    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "Qwen/Qwen2.5-7B-Instruct"

    class Config:
        env_file = ".env"

settings = Settings()

settings.papers_dir.mkdir(parents=True, exist_ok=True)
settings.vector_store_dir.mkdir(parents=True, exist_ok=True)