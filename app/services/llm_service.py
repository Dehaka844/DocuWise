from openai import OpenAI

from app.exceptions.llm_exception import LLMServiceError

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