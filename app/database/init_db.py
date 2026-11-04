from app.database.base import Base
from app.database.connection import engine

from app.database_models.user import User


def init_db():

    Base.metadata.create_all(
        bind=engine
    )


if __name__ == "__main__":

    init_db()

    print(
        "Base de datos inicializada correctamente."
    )