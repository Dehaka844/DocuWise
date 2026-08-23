from typing import Any

from pydantic import BaseModel


class PageContent(BaseModel):
    page_number: int
    content: str


class ParsedDocument(BaseModel):
    pages: list[PageContent]
    metadata: dict[str, Any]


class DocumentChunk(BaseModel):
    content: str
    metadata: dict[str, Any]