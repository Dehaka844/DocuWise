from typing import Any

from pydantic import BaseModel


class SearchResult(BaseModel):

    content: str

    score: float

    metadata: dict[str, Any]