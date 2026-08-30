from pydantic import BaseModel


class RAGSource(BaseModel):

    filename: str

    page_number: int


class RAGResponse(BaseModel):

    answer: str

    sources: list[RAGSource]

    has_sufficient_context: bool