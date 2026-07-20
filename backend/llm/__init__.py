from backend.llm.base import LLMProvider
from backend.llm.gemini import GeminiProvider
from backend.config.settings import get_settings

def get_llm() -> LLMProvider | None:
    settings = get_settings()
    if not settings.gemini_configured:
        return None
    return GeminiProvider(
        api_key=settings.gemini_api_key or "",
        model=settings.gemini_model,
        fallback_model=settings.gemini_fallback_model,
    )
