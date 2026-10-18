from fastapi import APIRouter, Response, HTTPException, status
from aegis.core.models import ChatCompletionRequest, ChatCompletionResponse
from aegis.brain.gateway_engine import GatewayEngine

def create_router(gateway: GatewayEngine) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/v1/chat/completions",
        response_model=ChatCompletionResponse,
        summary="OpenAI-Compatible Chat Completions with Semantic Caching & Failover",
    )
    async def chat_completions(request: ChatCompletionRequest, response: Response):
        try:
            result = await gateway.execute(request)

            # Set observability headers
            response.headers["X-Aegis-Cache"] = "HIT" if result.cached else "MISS"
            response.headers["X-Aegis-Provider"] = result.provider_used
            response.headers["X-Aegis-Latency-Ms"] = str(result.latency_ms)

            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Gateway execution failure: {str(e)}"
            )

    @router.get("/v1/models", summary="List Available Models")
    async def list_models():
        return {
            "object": "list",
            "data": [
                {"id": "gpt-4o-mini", "object": "model", "owned_by": "openai"},
                {"id": "gemini-3.5-flash-lite", "object": "model", "owned_by": "google"},
                {"id": "aegis-auto", "object": "model", "owned_by": "aegis"},
            ]
        }

    @router.get("/health", summary="Health Check")
    async def health():
        return {
            "status": "healthy",
            "service": "aegis-ai-gateway",
            "active_providers": list(gateway.providers.keys()),
        }

    @router.get("/metrics", summary="Telemetry & Telemetry Stats")
    async def metrics():
        cache_stats = gateway.vector_store.get_stats()
        circuits = gateway.circuit_breaker.get_all_states()
        return {
            "cache": cache_stats,
            "circuit_breakers": circuits,
        }

    @router.post("/cache/clear", summary="Flush Semantic Cache")
    async def clear_cache():
        gateway.vector_store.clear()
        return {"status": "cache_flushed"}

    return router
