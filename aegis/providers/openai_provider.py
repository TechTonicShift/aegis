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

class OpenAIProvider(BaseLLMProvider):
    """Adapter for OpenAI models."""

    def __init__(self, api_key: str, default_model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.default_model = default_model

    @property
    def name(self) -> str:
        return "openai"

    async def generate(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        start_time = time.time()
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": request.model or self.default_model,
            "messages": [m.model_dump() for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"OpenAI API returned {resp.status_code}: {resp.text}")

            data = resp.json()

        latency_ms = (time.time() - start_time) * 1000.0
        choice = data["choices"][0]
        usage = data.get("usage", {})

        return ChatCompletionResponse(
            model=data.get("model", request.model),
            choices=[
                ChatChoice(
                    message=ChatChoiceMessage(
                        role=choice["message"]["role"],
                        content=choice["message"]["content"],
                    ),
                    finish_reason=choice.get("finish_reason", "stop"),
                )
            ],
            usage=UsageStats(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
            ),
            cached=False,
            provider_used="openai",
            latency_ms=round(latency_ms, 2),
        )
