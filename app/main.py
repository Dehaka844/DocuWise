from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from app.api.routes import documents
from app.core.qdrant import qdrant_client
from app.api.routes import search
from app.api.routes import query
from app.database_routers import auth_router
from app.database_routers import conversation_router
from app.database_routers import message_router
from app.database_routers import user_admin_router

from pathlib import Path

from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="DocuWise API",
    version="0.1.0",
)

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"

app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend",
)


app.include_router(
    documents.router
)

app.include_router(
    search.router
)

app.include_router(
    query.router
)

app.include_router(
    auth_router.router
)

app.include_router(
    conversation_router.router
)

app.include_router(
    message_router.router
)

app.include_router(
    user_admin_router.router
)

@app.get("/health")
def health_check():

    try:
        qdrant_client.get_collections()

        qdrant_status = "ok"

    except Exception:
        qdrant_status = "error"

    return {
        "status": "ok",
        "qdrant": qdrant_status,
    }
