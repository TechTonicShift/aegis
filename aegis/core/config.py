import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class Settings:
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Providers
    gemini_api_key: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "")
    )
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_embedding_model: str = "gemini-embedding-001"

    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_model: str = "gpt-4o-mini"

    # Semantic Cache
    cache_enabled: bool = True
    similarity_threshold: float = 0.88  # Cosine similarity threshold for cache hit
    cache_ttl_seconds: int = 86400      # 24 hours
    embedder_type: str = "gemini"       # "gemini" or "fast_local"

    # Circuit Breaker / Failover
    circuit_breaker_failure_threshold: int = 3
    circuit_breaker_cooldown_seconds: int = 30
    provider_cascade: List[str] = field(
        default_factory=lambda: ["gemini", "mock"]
    )

settings = Settings()
