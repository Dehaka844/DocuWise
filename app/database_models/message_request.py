from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=5000,
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )