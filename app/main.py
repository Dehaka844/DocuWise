from fastapi import FastAPI

from app.api.routes import documents
from app.core.qdrant import qdrant_client


app = FastAPI(
    title="DocuWise API",
    version="0.1.0",
)


app.include_router(
    documents.router
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