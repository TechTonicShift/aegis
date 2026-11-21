from aegis.storage.vector_store import InMemoryVectorStore

def test_insert_and_exact_match():
    store = InMemoryVectorStore()
    vec = [1.0, 0.0, 0.0, 0.0]
    store.insert(
        key="test prompt",
        embedding=vec,
        response_content="test response",
        model="gemini",
        prompt_tokens=10,
        completion_tokens=20,
    )

    # Search with identical vector -> similarity should be ~1.0
    match = store.search_nearest([1.0, 0.0, 0.0, 0.0], min_threshold=0.99)
    assert match is not None
    entry, score = match
    assert entry.response_content == "test response"
    assert score >= 0.999

def test_threshold_rejection():
    store = InMemoryVectorStore()
    # Stored vector along X axis
    store.insert(
        key="hello",
        embedding=[1.0, 0.0, 0.0],
        response_content="hi",
        model="gemini",
        prompt_tokens=5,
        completion_tokens=5,
    )

    # Query vector orthogonal along Y axis (similarity = 0.0)
    match = store.search_nearest([0.0, 1.0, 0.0], min_threshold=0.5)
    assert match is None

def test_stats_tracking():
    store = InMemoryVectorStore()
    store.insert(
        key="query",
        embedding=[0.5, 0.5, 0.0],
        response_content="answer",
        model="gemini",
        prompt_tokens=100,
        completion_tokens=200,
    )

    # 1 Hit
    store.search_nearest([0.5, 0.5, 0.0], min_threshold=0.8)
    # 1 Miss
    store.search_nearest([0.0, 0.0, 1.0], min_threshold=0.8)

    stats = store.get_stats()
    assert stats["total_queries"] == 2
    assert stats["total_hits"] == 1
    assert stats["hit_ratio_percent"] == 50.0
    assert stats["total_tokens_saved"] == 300
