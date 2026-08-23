import os


class Settings:

    APP_NAME = os.getenv(
        "APP_NAME",
        "DocuWise"
    )

    QDRANT_HOST = os.getenv(
        "QDRANT_HOST",
        "localhost"
    )

    QDRANT_PORT = int(
        os.getenv(
            "QDRANT_PORT",
            "6333"
        )
    )


settings = Settings()