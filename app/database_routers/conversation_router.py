from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database_models.user import User
from app.database_services.auth_dependency import get_current_user
from app.database_services.conversation_service import ConversationService
from app.database_schemas.conversation_schema import ConversationUpdate


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation_service = ConversationService(db)

    conversation = conversation_service.create_conversation(
        user_id=current_user.id,
    )

    return conversation


@router.get(
    "/",
)
def get_user_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation_service = ConversationService(db)

    conversations = (
        conversation_service.get_user_conversations(
            user_id=current_user.id,
        )
    )

    return conversations


@router.get(
    "/{conversation_id}",
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation_service = ConversationService(db)

    conversation = (
        conversation_service.get_conversation_by_id(
            conversation_id=conversation_id,
            user_id=current_user.id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada.",
        )

    return conversation


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation_service = ConversationService(db)

    conversation = (
        conversation_service.get_conversation_by_id(
            conversation_id=conversation_id,
            user_id=current_user.id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada.",
        )

    conversation_service.delete_conversation(
        conversation
    )

    return None

@router.patch(
    "/{conversation_id}",
)
def update_conversation(
    conversation_id: int,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation_service = ConversationService(db)

    conversation = (
        conversation_service.get_conversation_by_id(
            conversation_id=conversation_id,
            user_id=current_user.id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada.",
        )

    if not data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El título no puede estar vacío.",
        )

    conversation = conversation_service.update_title(
        conversation=conversation,
        title=data.title,
    )

    return conversation