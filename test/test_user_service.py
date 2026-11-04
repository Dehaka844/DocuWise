from app.database.connection import SessionLocal
from app.database_services.user_service import UserService
from app.database_services.password_service import PasswordService


def test_user_service():

    db = SessionLocal()

    try:

        user_service = UserService(db)
        password_service = PasswordService()

        email = "test@docuwise.com"

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

            print(
                f"Nombre: {existing_user.name}"
            )

            print(
                f"Email: {existing_user.email}"
            )

            return

        password = "TestPassword123!"

        password_hash = (
            password_service.hash_password(
                password
            )
        )

        user = user_service.create_user(
            name="Usuario de prueba",
            email=email,
            password_hash=password_hash,
        )

        print()
        print(
            "Usuario creado correctamente."
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

        found_user = (
            user_service.get_user_by_email(
                email
            )
        )

        assert found_user is not None

        assert found_user.email == email

        assert password_service.verify_password(
            password,
            found_user.password_hash,
        )

        print()
        print(
            "Usuario recuperado correctamente."
        )

        print(
            f"ID: {found_user.id}"
        )

    finally:

        db.close()


if __name__ == "__main__":

    test_user_service()