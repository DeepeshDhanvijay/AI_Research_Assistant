from fastapi import FastAPI
from app.core.config import settings
from app.routers import papers, qa, analysis

app = FastAPI(title=settings.app_name)

app.include_router(papers.router)
app.include_router(qa.router)
app.include_router(analysis.router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
        "app_name": settings.app_name,
    }