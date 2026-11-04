from app.database_services.password_service import PasswordService


def test_hash_password():

    service = PasswordService()

    password = "MiPassword123!"

    password_hash = service.hash_password(
        password
    )

    assert password_hash != password
    assert password_hash


def test_verify_correct_password():

    service = PasswordService()

    password = "MiPassword123!"

    password_hash = service.hash_password(
        password
    )

    result = service.verify_password(
        password,
        password_hash,
    )

    assert result is True


def test_verify_incorrect_password():

    service = PasswordService()

    password = "MiPassword123!"

    password_hash = service.hash_password(
        password
    )

    result = service.verify_password(
        "PasswordIncorrecta123!",
        password_hash,
    )

    assert result is False
