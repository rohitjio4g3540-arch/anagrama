from backend.llm.base import LLMProvider
from backend.llm.gemini import GeminiProvider
from backend.llm.nvidia_provider import NvidiaProvider
from backend.config.settings import get_settings


def get_llm() -> LLMProvider | None:

    settings = get_settings()

    # Use NVIDIA when selected in .env.local
    if settings.llm_provider == "nvidia":
        if not settings.nvidia_api_key or not settings.nvidia_model:
            return None

        return NvidiaProvider(
            api_key=settings.nvidia_api_key,
            model=settings.nvidia_model,
        )

    # Otherwise use Gemini
    if not settings.gemini_configured:
        return None

    return GeminiProvider(
        api_key=settings.gemini_api_key or "",
        model=settings.gemini_model,
        fallback_model=settings.gemini_fallback_model,
    )