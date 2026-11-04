from app.database.connection import SessionLocal

from app.database_services.user_service import UserService
from app.database_services.conversation_service import ConversationService
from app.database_services.message_service import MessageService


def test_conversation_services():

    db = SessionLocal()

    try:

        user_service = UserService(db)

        conversation_service = ConversationService(db)

        message_service = MessageService(db)

        user = user_service.get_user_by_email(
            "test@test.com"
        )

        if user is None:

            print(
                "No existe el usuario test@test.com"
            )

            return

        conversation = (
            conversation_service.create_conversation(
                user_id=user.id,
                title="Conversación de prueba",
            )
        )

        print(
            "Conversación creada:",
            conversation.id,
        )

        message_1 = (
            message_service.create_message(
                conversation_id=conversation.id,
                role="user",
                content="¿Cómo se gestionan las vacaciones?",
            )
        )

        print(
            "Mensaje de usuario creado:",
            message_1.id,
        )

        message_2 = (
            message_service.create_message(
                conversation_id=conversation.id,
                role="assistant",
                content="Las vacaciones se gestionan según la normativa y las políticas internas.",
            )
        )

        print(
            "Mensaje de assistant creado:",
            message_2.id,
        )

        messages = (
            message_service.get_conversation_messages(
                conversation_id=conversation.id,
            )
        )

        print()
        print("Mensajes de la conversación:")

        for message in messages:

            print(
                f"[{message.role}] {message.content}"
            )

        recent_messages = (
            message_service.get_recent_messages(
                conversation_id=conversation.id,
                limit=2,
            )
        )

        print()
        print("Últimos mensajes:")

        for message in recent_messages:

            print(
                f"[{message.role}] {message.content}"
            )

        conversations = (
            conversation_service.get_user_conversations(
                user_id=user.id,
            )
        )

        print()
        print("Conversaciones del usuario:")

        for item in conversations:

            print(
                f"{item.id} - {item.title}"
            )

    finally:

        db.close()


if __name__ == "__main__":

    test_conversation_services()