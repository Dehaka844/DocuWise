from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database_models.message import Message
from app.database_models.message_source import MessageSource


class MessageService:
    ALLOWED_ROLES = {"user", "assistant"}

    def __init__(self, db: Session):
        self.db = db

    def create_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        sources: list | None = None,
    ) -> Message:

        if role not in self.ALLOWED_ROLES:
            raise ValueError(
                f"Rol de mensaje no válido: {role}"
            )

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        if sources:
            for source in sources:

                message.sources.append(
                    MessageSource(
                        filename=source.filename,
                        page_number=source.page_number,
                    )
                )

        self.db.add(message)

        from app.database_models.conversation import Conversation

        conversation = self.db.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id
            )
        )

        if conversation:
            conversation.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)

        return message

    def get_conversation_messages(
        self,
        conversation_id: int,
    ) -> list[Message]:
        statement = (
            select(Message)
            .options(
                selectinload(Message.sources)
            )
            .where(
                Message.conversation_id == conversation_id
            )
            .order_by(
                Message.created_at.asc()
            )
        )

        return list(self.db.scalars(statement).all())

    def get_recent_messages(
        self,
        conversation_id: int,
        limit: int = 10,
    ) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        messages = list(self.db.scalars(statement).all())
        messages.reverse()

        return messages