from pydantic import BaseModel


class IngestionResult(BaseModel):

    page_count: int

    chunk_count: int

    embedding_count: int

    stored_points: int