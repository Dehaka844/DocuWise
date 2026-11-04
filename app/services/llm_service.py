import json

from openai import OpenAI

from app.exceptions.llm_exception import LLMServiceError
from app.prompts.rag_prompt import QUERY_REWRITE_SYSTEM_PROMPT

class LLMService:

    def __init__(self):

        self.client = OpenAI()

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        try:
            response = self.client.responses.create(
                model="gpt-5.6-luna",
                instructions=system_prompt,
                input=user_prompt,
            )
        except Exception as error:

            raise LLMServiceError(
                "Error al generar la respuesta con el modelo de lenguaje."
            ) from error

        return response.output_text

    def rewrite_query(
        self,
        query: str,
        conversation_history: list,
    ) -> str:
        history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in conversation_history
        ]

        user_prompt = json.dumps(
            {
                "conversation_history": history,
                "current_question": query,
            },
            ensure_ascii=False,
        )

        try:
            response = self.client.responses.create(
                model="gpt-5.6-luna",
                instructions=QUERY_REWRITE_SYSTEM_PROMPT,
                input=user_prompt,
            )
        except Exception as error:
            raise LLMServiceError(
                "Error al reformular la pregunta para la búsqueda."
            ) from error

        rewritten_query = (response.output_text or "").strip()
        if not rewritten_query:
            raise LLMServiceError(
                "El modelo no devolvió una consulta reformulada."
            )

        return rewritten_query
