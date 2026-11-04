from app.database.base import Base
from app.database.connection import engine

from app.database_models import (
    User,
    Conversation,
    Message,
)

from dotenv import load_dotenv

load_dotenv()


def test_database_models():

    print("Tablas detectadas:")

    for table in Base.metadata.tables:

        print(f"- {table}")


if __name__ == "__main__":

    test_database_models()