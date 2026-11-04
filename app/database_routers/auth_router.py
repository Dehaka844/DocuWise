from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.database_services.user_service import UserService
from app.database_services.password_service import PasswordService
from app.database_services.token_service import TokenService
from app.database_services.auth_service import AuthService
from app.database_models.user import User
from app.database_services.auth_dependency import get_current_user

from app.database_schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    LoginResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):

    user_service = UserService(db)

    password_service = PasswordService()

    token_service = TokenService()

    auth_service = AuthService(
        user_service=user_service,
        password_service=password_service,
        token_service=token_service,
    )

    try:

        user = auth_service.register(
            name=request.name,
            email=request.email,
            password=request.password,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    return user


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):

    user_service = UserService(db)

    password_service = PasswordService()

    token_service = TokenService()

    auth_service = AuthService(
        user_service=user_service,
        password_service=password_service,
        token_service=token_service,
    )

    try:

        user, access_token = auth_service.login(
            email=request.email,
            password=request.password,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_current_user_info(
    current_user: User = Depends(
        get_current_user
    ),
):

    return current_user