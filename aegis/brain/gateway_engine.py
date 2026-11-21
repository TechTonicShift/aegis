import time
import logging
from typing import Dict
from aegis.core.config import Settings
from aegis.core.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatChoice,
    ChatChoiceMessage,
    UsageStats,
)
from aegis.storage.vector_store import InMemoryVectorStore
from aegis.brain.embedder import BaseEmbedder, get_embedder
from aegis.brain.circuit_breaker import CircuitBreakerManager
from aegis.providers.base import BaseLLMProvider
from aegis.providers.gemini_provider import GeminiProvider
from aegis.providers.openai_provider import OpenAIProvider
from aegis.providers.mock_provider import MockProvider

logger = logging.getLogger("aegis.gateway")

class GatewayEngine:
    """
    Core orchestration engine for Aegis:
    - Semantic Caching via dense vector cosine matching
    - Multi-provider cascade with circuit breaking & automated failover
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.vector_store = InMemoryVectorStore()
        self.circuit_breaker = CircuitBreakerManager(
            failure_threshold=settings.circuit_breaker_failure_threshold,
            cooldown_seconds=settings.circuit_breaker_cooldown_seconds,
        )

        # Initialize embedder
        self.embedder: BaseEmbedder = get_embedder(
            embedder_type=settings.embedder_type,
            gemini_api_key=settings.gemini_api_key,
            gemini_model=settings.gemini_embedding_model,
        )

        # Register providers
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._init_providers()

    def _init_providers(self):
        # Gemini
        if self.settings.gemini_api_key:
            self.providers["gemini"] = GeminiProvider(
                api_key=self.settings.gemini_api_key,
                default_model=self.settings.gemini_model,
            )

        # OpenAI
        if self.settings.openai_api_key:
            self.providers["openai"] = OpenAIProvider(
                api_key=self.settings.openai_api_key,
                default_model=self.settings.openai_model,
            )

        # Default fallback mock provider
        self.providers["mock"] = MockProvider(
            name="mock",
            simulated_delay_ms=80.0,
        )

    def register_provider(self, provider: BaseLLMProvider):
        self.providers[provider.name] = provider

    async def execute(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        start_time = time.time()
        prompt_text = request.get_prompt_text()

        # Step 1: Semantic Cache Check
        if self.settings.cache_enabled:
            cache_match = await self._check_cache(prompt_text)
            if cache_match:
                cached_entry, similarity_score = cache_match
                elapsed_ms = (time.time() - start_time) * 1000.0

                logger.info(f"[CACHE HIT] Similarity: {similarity_score:.4f} in {elapsed_ms:.2f}ms")

                # Record live query log for dashboard
                tokens_saved = cached_entry.prompt_tokens + cached_entry.completion_tokens
                self.vector_store.record_query_log(
                    prompt=prompt_text,
                    cached=True,
                    provider="aegis_semantic_cache",
                    latency_ms=elapsed_ms,
                    tokens_saved=tokens_saved
                )

                return ChatCompletionResponse(
                    model=f"{cached_entry.model} (cached)",
                    choices=[
                        ChatChoice(
                            message=ChatChoiceMessage(role="assistant", content=cached_entry.response_content),
                            finish_reason="stop",
                        )
                    ],
                    usage=UsageStats(
                        prompt_tokens=cached_entry.prompt_tokens,
                        completion_tokens=cached_entry.completion_tokens,
                        total_tokens=cached_entry.prompt_tokens + cached_entry.completion_tokens,
                        cached_tokens=cached_entry.prompt_tokens + cached_entry.completion_tokens,
                        estimated_cost_saved_usd=(cached_entry.prompt_tokens + cached_entry.completion_tokens) * 0.0000025,
                    ),
                    cached=True,
                    provider_used="aegis_semantic_cache",
                    latency_ms=round(elapsed_ms, 2),
                )

        # Step 2: Cache Miss - Cascade through providers with Circuit Breakers
        cascade = self.settings.provider_cascade
        last_error = None

        for provider_name in cascade:
            provider = self.providers.get(provider_name)
            if not provider:
                continue

            if not self.circuit_breaker.can_call(provider_name):
                logger.warning(f"[CIRCUIT OPEN] Skipping provider '{provider_name}' due to repeated failures.")
                continue

            try:
                logger.info(f"[ROUTING] Forwarding request to provider '{provider_name}'...")
                response = await provider.generate(request)

                # Record success
                self.circuit_breaker.record_success(provider_name)

                # Step 3: Populate Semantic Cache
                if self.settings.cache_enabled:
                    await self._populate_cache(prompt_text, response)

                # Record live query log for dashboard
                elapsed_ms = (time.time() - start_time) * 1000.0
                self.vector_store.record_query_log(
                    prompt=prompt_text,
                    cached=False,
                    provider=response.provider_used,
                    latency_ms=elapsed_ms,
                    tokens_saved=0
                )

                return response

            except Exception as e:
                logger.error(f"[FAILOVER TRIGGERED] Provider '{provider_name}' failed: {e}. Cascading...")
                self.circuit_breaker.record_failure(provider_name, e)
                last_error = e

        raise RuntimeError(f"All upstream providers failed in cascade {cascade}. Last error: {last_error}")

    async def _check_cache(self, prompt_text: str):
        try:
            query_embedding = self.embedder.embed_text(prompt_text)
            match = self.vector_store.search_nearest(
                query_embedding=query_embedding,
                min_threshold=self.settings.similarity_threshold,
            )
            return match
        except Exception as e:
            logger.warning(f"Cache lookup failed, proceeding to live provider: {e}")
            return None

    async def _populate_cache(self, prompt_text: str, response: ChatCompletionResponse):
        try:
            content = response.choices[0].message.content
            embedding = self.embedder.embed_text(prompt_text)
            self.vector_store.insert(
                key=prompt_text,
                embedding=embedding,
                response_content=content,
                model=response.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                ttl_seconds=self.settings.cache_ttl_seconds,
            )
        except Exception as e:
            logger.warning(f"Failed to populate semantic cache: {e}")
