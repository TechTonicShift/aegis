# Extending Providers & Custom Adapters

Aegis is built around an extensible adapter architecture. You can easily integrate new commercial providers (Anthropic Claude, Mistral, Cohere), open-source inference servers (Ollama, vLLM, TGI), or custom enterprise microservices.

---

## The `BaseProvider` Contract

All model adapters in Aegis inherit from `BaseProvider` located at `aegis/providers/base.py`:

```python
from abc import ABC, abstractmethod
from aegis.core.models import ChatCompletionRequest, ChatCompletionResponse

class BaseProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider identifier (e.g. 'anthropic', 'ollama')."""
        pass

    @abstractmethod
    async def generate_chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Execute chat inference against the upstream provider.
        Must raise an Exception if HTTP 429, 5xx, or network failure occurs.
        """
        pass
```

---

## Example: Building an Ollama Local Model Adapter

Here is a complete, production-ready implementation of an adapter for a locally hosted **Ollama** instance:

```python
import httpx
import uuid
import time
from aegis.providers.base import BaseProvider
from aegis.core.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatChoice,
    ChatChoiceMessage,
    UsageInfo,
)

class OllamaProvider(BaseProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3:8b"):
        self._base_url = base_url.rstrip("/")
        self._model = model

    @property
    def name(self) -> str:
        return f"ollama_{self._model}"

    async def generate_chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        # Format OpenAI messages to Ollama format
        ollama_messages = [
            {"role": m.role, "content": m.content}
            for m in request.messages
        ]

        payload = {
            "model": self._model,
            "messages": ollama_messages,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self._base_url}/api/chat", json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama failure: {resp.status_code} - {resp.text}")

            data = resp.json()
            message_content = data["message"]["content"]
            prompt_tokens = data.get("prompt_eval_count", 0)
            completion_tokens = data.get("eval_count", 0)

            return ChatCompletionResponse(
                id=f"chatcmpl-ollama-{uuid.uuid4().hex[:8]}",
                created=int(time.time()),
                model=self._model,
                provider_used=self.name,
                choices=[
                    ChatChoice(
                        index=0,
                        message=ChatChoiceMessage(role="assistant", content=message_content),
                        finish_reason="stop",
                    )
                ],
                usage=UsageInfo(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                ),
            )
```

---

## Registering Your Custom Provider

To register your custom adapter with the gateway engine:

```python
from aegis.main import app
from my_adapters import OllamaProvider

# Instantiate adapter
ollama = OllamaProvider(model="llama3:8b")

# Register with Aegis Gateway engine
app.state.gateway.register_provider(ollama)
```

Once registered, the custom provider automatically benefits from:
* Automated three-state circuit breaking
* Failover cascade routing
* Semantic caching of its outputs
* Real-time telemetry tracking on the `/dashboard`
