from pydantic import BaseModel

from app.models.search_result import SearchResult


class SearchResponse(BaseModel):

    query: str

    results: list[SearchResult]