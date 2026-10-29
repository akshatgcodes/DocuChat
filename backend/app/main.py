from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import auth
from app.config import settings
from app.db import Base, engine
from app.routers import documents

Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
# Three small tables, so create_all on startup instead of a migration tool
Base.metadata.create_all(engine)

app = FastAPI(title="DocuChat API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)


@app.get("/health")
def health() -> dict:
    base_url, model, _ = settings.llm
    return {"ok": True, "llm": {"provider": settings.llm_provider, "model": model}}
