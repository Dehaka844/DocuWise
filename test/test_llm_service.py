from dotenv import load_dotenv

load_dotenv()

from app.services.llm_service import LLMService


def main():
    llm_service = LLMService()

    response = llm_service.generate(
        prompt=(
            "Explica brevemente qué es un "
            "sistema RAG."
        )
    )

    print("Respuesta:")
    print()
    print(response)


if __name__ == "__main__":
    main()