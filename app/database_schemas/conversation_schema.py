from pydantic import BaseModel, Field


class ConversationUpdate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100,
    )