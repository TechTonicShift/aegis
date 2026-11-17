"""
Server-Sent Events (SSE) Streaming Formatter for OpenAI-compatible clients.
Enables token-by-token streaming responses while aggregating full completions
for background semantic cache population.
"""

import json
import time
from typing import AsyncGenerator
from aegis.core.models import ChatCompletionResponse

async def format_sse_stream(
    chunks: AsyncGenerator[str, None],
    model: str,
    request_id: str,
) -> AsyncGenerator[str, None]:
    """Format token chunks into standard SSE stream lines."""
    for chunk in chunks:
        payload = {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": chunk},
                    "finish_reason": None,
                }
            ],
        }
        yield f"data: {json.dumps(payload)}\n\n"

    # Final termination frame
    final_payload = {
        "id": request_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    }
    yield f"data: {json.dumps(final_payload)}\n\n"
    yield "data: [DONE]\n\n"
