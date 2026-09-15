import asyncio
from collections.abc import AsyncIterator

from openai import OpenAI

from backend.llm.base import LLMProvider


class NVIDIAProvider(LLMProvider):
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://integrate.api.nvidia.com/v1",
    ) -> None:
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.model = model

    def _generate(self, *, system: str, prompt: str) -> str:
        response = self.client.chat.completions.create(
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
            temperature=0.6,
            top_p=0.95,
            max_tokens=4096,
            stream=False,
        )

        return response.choices[0].message.content or ""

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
        # Initial implementation preserves Anagrama's existing provider contract.
        # True NVIDIA token streaming can be added after basic validation.
        yield await self.generate(system=system, prompt=prompt)