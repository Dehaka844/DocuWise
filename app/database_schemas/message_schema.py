from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.rag_response import RAGSource


class MessageSourceResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    message_id: int
    filename: str
    page_number: int | None
    created_at: datetime


class MessageResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime
    sources: list[MessageSourceResponse] = Field(
        default_factory=list
    )


class CreateMessageResponse(BaseModel):

    user_message: MessageResponse
    assistant_message: MessageResponse
    sources: list[RAGSource]
    has_sufficient_context: bool
