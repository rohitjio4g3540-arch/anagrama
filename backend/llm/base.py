from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

class LLMProvider(ABC):
    """Stable boundary for Gemini, OpenAI, Ollama, Anthropic, Groq, or OpenRouter."""
    @abstractmethod
    async def generate(self, *, system: str, prompt: str) -> str: ...

    @abstractmethod
    async def stream(self, *, system: str, prompt: str) -> AsyncIterator[str]: ...
