import pytest
from aegis.core.config import Settings
from aegis.core.models import ChatCompletionRequest, ChatMessage
from aegis.brain.gateway_engine import GatewayEngine
from aegis.providers.mock_provider import MockProvider

@pytest.mark.asyncio
async def test_cache_miss_then_hit():
    settings = Settings(
        cache_enabled=True,
        similarity_threshold=0.85,
        embedder_type="fast_local",
        provider_cascade=["primary_mock"],
    )
    gateway = GatewayEngine(settings)
    primary = MockProvider(name="primary_mock", simulated_delay_ms=50.0)
    gateway.register_provider(primary)

    # First request: Cache Miss
    req1 = ChatCompletionRequest(
        messages=[ChatMessage(role="user", content="How do I configure Docker container networking?")]
    )
    res1 = await gateway.execute(req1)
    assert res1.cached is False
    assert res1.provider_used == "primary_mock"

    # Second request: Semantically similar prompt -> Cache Hit!
    req2 = ChatCompletionRequest(
        messages=[ChatMessage(role="user", content="How to configure Docker container networking?")]
    )
    res2 = await gateway.execute(req2)
    assert res2.cached is True
    assert res2.provider_used == "aegis_semantic_cache"
    assert res2.latency_ms < res1.latency_ms

@pytest.mark.asyncio
async def test_automated_failover_on_rate_limit():
    settings = Settings(
        cache_enabled=False,
        provider_cascade=["failing_provider", "backup_provider"],
    )
    gateway = GatewayEngine(settings)

    # Provider 1: Fails with 429
    failing = MockProvider(name="failing_provider", simulated_delay_ms=10.0, fail_rate_limit=True)
    # Provider 2: Backup succeeds
    backup = MockProvider(name="backup_provider", simulated_delay_ms=10.0)

    gateway.register_provider(failing)
    gateway.register_provider(backup)

    req = ChatCompletionRequest(
        messages=[ChatMessage(role="user", content="Explain quantum computing.")]
    )
    res = await gateway.execute(req)

    # Should have seamlessly fallen back to backup_provider
    assert res.provider_used == "backup_provider"
    assert "quantum computing" in res.choices[0].message.content

def test_dashboard_and_telemetry_routes():
    from fastapi.testclient import TestClient
    from aegis.main import create_app

    app = create_app()
    client = TestClient(app)

    # Health route
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # Metrics route
    res_metrics = client.get("/metrics")
    assert res_metrics.status_code == 200
    assert "cache" in res_metrics.json()

    # Dashboard UI route
    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    assert "AEGIS GATEWAY" in res_dash.text
    assert "<!DOCTYPE html>" in res_dash.text
