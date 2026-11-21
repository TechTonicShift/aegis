import time
import httpx
from aegis.providers.base import BaseLLMProvider
from aegis.core.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatChoice,
    ChatChoiceMessage,
    UsageStats,
)

class GeminiProvider(BaseLLMProvider):
    """Adapter for Google Gemini models converting to/from OpenAI schema."""

    def __init__(self, api_key: str, default_model: str = "gemini-3.5-flash-lite"):
        self.api_key = api_key
        self.default_model = default_model

    @property
    def name(self) -> str:
        return "gemini"

    async def generate(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        start_time = time.time()
        model_name = self.default_model

        # Convert OpenAI messages to Gemini contents format
        contents = []
        for msg in request.messages:
            role = "user" if msg.role in ("user", "system") else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature or 0.7,
                "maxOutputTokens": request.max_tokens or 1000,
            }
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API returned {resp.status_code}: {resp.text}")

            data = resp.json()

        latency_ms = (time.time() - start_time) * 1000.0

        # Extract generated content
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned empty candidate list.")

        text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")

        # Extract or estimate token usage
        usage_meta = data.get("usageMetadata", {})
        prompt_tokens = usage_meta.get("promptTokenCount", len(request.get_prompt_text().split()))
        completion_tokens = usage_meta.get("candidatesTokenCount", len(text_content.split()))

        return ChatCompletionResponse(
            model=f"gemini/{model_name}",
            choices=[
                ChatChoice(
                    message=ChatChoiceMessage(role="assistant", content=text_content),
                    finish_reason="stop",
                )
            ],
            usage=UsageStats(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            cached=False,
            provider_used="gemini",
            latency_ms=round(latency_ms, 2),
        )
