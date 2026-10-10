from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
import time
import uuid

class ChatMessage(BaseModel):
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o-mini"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None
    user: Optional[str] = None

    def get_prompt_text(self) -> str:
        """Extract a canonical text representation of the conversation for semantic comparison."""
        parts = []
        for msg in self.messages:
            parts.append(f"{msg.role}: {msg.content}")
        return "\n".join(parts)

class ChatChoiceMessage(BaseModel):
    role: str = "assistant"
    content: str

class ChatChoice(BaseModel):
    index: int = 0
    message: ChatChoiceMessage
    finish_reason: str = "stop"

class UsageStats(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    estimated_cost_saved_usd: float = 0.0

class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:12]}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatChoice]
    usage: UsageStats
    cached: bool = False
    provider_used: str = "unknown"
    latency_ms: float = 0.0
