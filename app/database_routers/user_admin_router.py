from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database_models.user import User
from app.database_schemas.admin_user_schema import (
    AdminUserCreate,
    AdminUserResponse,
    AdminUserUpdate,
)
from app.database_services.auth_dependency import get_current_admin
from app.database_services.password_service import PasswordService
from app.database_services.user_service import UserService


router = APIRouter(
    prefix="/admin/users",
    tags=["User administration"],
)


def _refresh_admin_or_reject(
    user_service: UserService,
    current_admin: User,
) -> User:
    refreshed_admin = user_service.get_user_by_id(current_admin.id)
    if (
        refreshed_admin is None
        or not refreshed_admin.is_active
        or refreshed_admin.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador.",
        )

    return refreshed_admin


@router.get(
    "/",
    response_model=list[AdminUserResponse],
)
def list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return UserService(db).get_users()


@router.post(
    "/",
    response_model=AdminUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: AdminUserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user_service = UserService(db)

    if user_service.get_user_by_email(str(request.email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado.",
        )

    password_hash = PasswordService().hash_password(request.password)
    return user_service.create_user(
        name=request.name,
        email=str(request.email),
        password_hash=password_hash,
        departments=request.departments,
    )


@router.patch(
    "/{user_id}",
    response_model=AdminUserResponse,
)
def update_user_access(
    user_id: int,
    request: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user_service = UserService(db)
    user_service.lock_admin_mutations()
    current_admin = _refresh_admin_or_reject(user_service, current_admin)
    user = user_service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    requested_role = request.role
    requested_is_active = request.is_active
    final_role = requested_role if requested_role is not None else user.role
    final_is_active = (
        requested_is_active
        if requested_is_active is not None
        else user.is_active
    )

    if (
        user.id == current_admin.id
        and user.is_active
        and not final_is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No puedes desactivar tu propia cuenta.",
        )

    removes_active_admin = (
        user.role == "admin"
        and user.is_active
        and (final_role != "admin" or not final_is_active)
    )
    if removes_active_admin and user_service.count_active_admins(
        excluding_user_id=user.id
    ) == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Debe quedar al menos un administrador activo.",
        )

    return user_service.update_access(
        user=user,
        role=requested_role,
        is_active=requested_is_active,
        departments=request.departments,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> Response:
    user_service = UserService(db)
    user_service.lock_admin_mutations()
    current_admin = _refresh_admin_or_reject(user_service, current_admin)
    user = user_service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No puedes eliminar tu propia cuenta.",
        )

    if user.role == "admin" and user_service.count_active_admins(
        excluding_user_id=user.id
    ) == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar al último administrador activo.",
        )

    user_service.delete_user(user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
