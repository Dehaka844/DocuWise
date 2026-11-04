from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database_models.conversation import Conversation


class ConversationService:

    def __init__(
        self,
        db: Session,
    ):

        self.db = db

    def create_conversation(
        self,
        user_id: int,
        title: str = "Nueva conversación",
    ) -> Conversation:

        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        self.db.add(conversation)

        self.db.commit()

        self.db.refresh(conversation)

        return conversation

    def get_conversation_by_id(
        self,
        conversation_id: int,
        user_id: int,
    ) -> Conversation | None:

        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )

        return self.db.scalar(statement)

    def get_user_conversations(
        self,
        user_id: int,
    ) -> list[Conversation]:

        statement = (
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
            )
            .order_by(
                Conversation.updated_at.desc(),
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def delete_conversation(
        self,
        conversation: Conversation,
    ) -> None:

        self.db.delete(conversation)

        self.db.commit()

    def update_title(
        self,
        conversation: Conversation,
        title: str,
    ) -> Conversation:
        conversation.title = title.strip()

        self.db.commit()
        self.db.refresh(conversation)

        return conversation