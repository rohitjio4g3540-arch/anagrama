import asyncio
from collections.abc import AsyncIterator

from openai import OpenAI

from backend.llm.base import LLMProvider


class NvidiaProvider(LLMProvider):
    """NVIDIA NIM / Build provider using the OpenAI-compatible API."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
    ) -> None:
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
        )
        self.model = model

    def _generate(self, *, system: str, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return completion.choices[0].message.content or ""

    async def generate(self, *, system: str, prompt: str) -> str:
        return await asyncio.to_thread(
            self._generate,
            system=system,
            prompt=prompt,
        )

    async def stream(
        self,
        *,
        system: str,
        prompt: str,
    ) -> AsyncIterator[str]:
        # Temporary compatibility implementation.
        # Real token streaming can be added after basic connectivity works.
        yield await self.generate(
            system=system,
            prompt=prompt,
        )

    def _embed(self, text: str) -> list[float]:
        resp = self.client.embeddings.create(
            model="nvidia/nv-embedqa-e5-v5",
            input=[text],
            encoding_format="float"
        )
        return resp.data[0].embedding

    async def embed(self, text: str) -> list[float]:
        return await asyncio.to_thread(self._embed, text)