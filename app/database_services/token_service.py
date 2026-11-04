import os
from datetime import datetime, timedelta, timezone

from jose import jwt
from dotenv import load_dotenv


load_dotenv()


JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY"
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        "60",
    )
)


class TokenService:

    def create_access_token(
        self,
        user_id: int,
    ) -> str:

        if not JWT_SECRET_KEY:

            raise ValueError(
                "JWT_SECRET_KEY no está configurada."
            )

        expire = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )

        payload = {
            "sub": str(user_id),
            "exp": expire,
        }

        return jwt.encode(
            payload,
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

    def decode_access_token(
        self,
        token: str,
    ) -> dict:

        if not JWT_SECRET_KEY:

            raise ValueError(
                "JWT_SECRET_KEY no está configurada."
            )

        return jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )