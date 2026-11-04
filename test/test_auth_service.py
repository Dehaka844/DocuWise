from app.database.connection import SessionLocal
from app.database_services.user_service import UserService
from app.database_services.auth_service import AuthService
from app.database_services.password_service import PasswordService


def test_register_user():

    db = SessionLocal()

    try:

        user_service = UserService(db)

        password_service = PasswordService()

        auth_service = AuthService(
            user_service=user_service,
            password_service=password_service,
        )

        email = "auth-test@docuwise.com"

        existing_user = (
            user_service.get_user_by_email(
                email
            )
        )

        if existing_user:

            print()
            print(
                "El usuario de prueba ya existe."
            )

            print(
                f"ID: {existing_user.id}"
            )

            return

        user = auth_service.register(
            name="Usuario Auth",
            email=email,
            password="Password123!",
        )

        print()
        print(
            "Registro realizado correctamente."
        )

        print(
            f"ID: {user.id}"
        )

        print(
            f"Nombre: {user.name}"
        )

        print(
            f"Email: {user.email}"
        )

        print(
            f"Password hash: {user.password_hash}"
        )

        assert user.id is not None

        assert user.email == email

        assert user.password_hash != "Password123!"

        assert password_service.verify_password(
            "Password123!",
            user.password_hash,
        )

    finally:

        db.close()

    def test_register_duplicate_email():

        db = SessionLocal()

        try:

            user_service = UserService(db)

            password_service = PasswordService()

            auth_service = AuthService(
                user_service=user_service,
                password_service=password_service,
            )

            email = "duplicate@docuwise.com"

            existing_user = (
                user_service.get_user_by_email(
                    email
                )
            )

            if not existing_user:

                auth_service.register(
                    name="Primer usuario",
                    email=email,
                    password="Password123!",
                )

            try:

                auth_service.register(
                    name="Segundo usuario",
                    email=email,
                    password="Password123!",
                )

                assert False, (
                    "Se permitió registrar "
                    "un email duplicado."
                )

            except ValueError as error:

                assert str(error) == (
                    "El email ya está registrado."
                )

                print()
                print(
                    "El registro duplicado "
                    "fue rechazado correctamente."
                )

        finally:

            db.close()


if __name__ == "__main__":

    test_register_user()