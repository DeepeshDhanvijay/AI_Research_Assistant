from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import papers, qa, analysis

app = FastAPI(title=settings.app_name)

origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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