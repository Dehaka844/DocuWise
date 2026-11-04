from app.database_models.user import User

from app.database_services.user_service import UserService
from app.database_services.password_service import PasswordService
from app.database_services.token_service import TokenService


class AuthService:

    def __init__(
        self,
        user_service: UserService,
        password_service: PasswordService,
        token_service: TokenService,
    ):

        self.user_service = user_service

        self.password_service = password_service

        self.token_service = token_service

    def register(
        self,
        name: str,
        email: str,
        password: str,
    ) -> User:

        existing_user = (
            self.user_service.get_user_by_email(
                email
            )
        )

        if existing_user:

            raise ValueError(
                "El email ya está registrado."
            )

        password_hash = (
            self.password_service.hash_password(
                password
            )
        )

        return self.user_service.create_user(
            name=name,
            email=email,
            password_hash=password_hash,
        )

    def login(
        self,
        email: str,
        password: str,
    ) -> tuple[User, str]:

        user = (
            self.user_service.get_user_by_email(
                email
            )
        )

        if not user:

            raise ValueError(
                "Email o contraseña incorrectos."
            )

        password_valid = (
            self.password_service.verify_password(
                password=password,
                password_hash=user.password_hash,
            )
        )

        if not password_valid:

            raise ValueError(
                "Email o contraseña incorrectos."
            )

        access_token = (
            self.token_service.create_access_token(
                user_id=user.id
            )
        )

        return user, access_token