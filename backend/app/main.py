from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.config import settings
from app.extraction.router import router as extraction_router
from app.insurance.router import router as insurance_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Insurance Tracker API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(insurance_router)
app.include_router(extraction_router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
