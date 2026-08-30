from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(
        self,
        model_name: str = (
            "sentence-transformers/"
            "paraphrase-multilingual-MiniLM-L12-v2"
        ),
    ):
        self.model_name = model_name

        self.model = SentenceTransformer(
            self.model_name
        )

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        if not text.strip():
            raise ValueError(
                "Cannot generate an embedding "
                "for empty text"
            )

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_texts(
        self,
        texts: list[str],
        batch_size: int = 32,
    ) -> list[list[float]]:

        if not texts:
            return []

        if batch_size <= 0:
            raise ValueError(
                "Batch size must be greater than 0"
            )

        for text in texts:

            if not text.strip():
                raise ValueError(
                    "Cannot generate an embedding "
                    "for empty text"
                )

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
        )

        return embeddings.tolist()