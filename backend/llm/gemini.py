import asyncio
from collections.abc import AsyncIterator
from google import genai
from google.genai.errors import ClientError
from backend.llm.base import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, *, api_key: str, model: str, fallback_model: str | None = None) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.fallback_model = fallback_model

    def _generate(self, *, model: str, system: str, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config={"system_instruction": system},
        )
        return response.text or ""

    async def generate(self, *, system: str, prompt: str) -> str:
        def request() -> str:
            try:
                return self._generate(model=self.model, system=system, prompt=prompt)
            except ClientError as error:
                if getattr(error, "code", None) == 404 and self.fallback_model and self.fallback_model != self.model:
                    return self._generate(model=self.fallback_model, system=system, prompt=prompt)
                raise
        return await asyncio.to_thread(request)

    async def stream(self, *, system: str, prompt: str) -> AsyncIterator[str]:
        # Gemini's synchronous streaming iterator is collected off the event loop.
        # The same fallback behavior applies to streamed UI output.
        yield await self.generate(system=system, prompt=prompt)
