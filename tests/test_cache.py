"""Unit tests for in-memory TTL cache."""

import time
from stackoverflow_mcp.cache import TTLCache


def test_cache_hit_and_miss():
    cache = TTLCache()

    # Miss before set
    assert cache.get("/search/advanced", {"q": "python"}) is None

    # Set and hit
    data = [{"question_id": 1, "title": "Test"}]
    cache.set("/search/advanced", {"q": "python"}, data, ttl_seconds=60)
    assert cache.get("/search/advanced", {"q": "python"}) == data


def test_canonical_key_sorting():
    cache = TTLCache()

    # Differing parameter key orders should hit the same cache entry
    params1 = {"q": "error", "site": "stackoverflow", "tagged": ["python", "asyncio"]}
    params2 = {"tagged": ["python", "asyncio"], "site": "stackoverflow", "q": "error"}

    data = {"results": "success"}
    cache.set("/search/advanced", params1, data, ttl_seconds=60)

    assert cache.get("/search/advanced", params2) == data


def test_ttl_expiration():
    cache = TTLCache()

    cache.set("/search/advanced", {"q": "expired"}, "value", ttl_seconds=1)
    assert cache.get("/search/advanced", {"q": "expired"}) == "value"

    # Wait for expiration
    time.sleep(1.1)
    assert cache.get("/search/advanced", {"q": "expired"}) is None


def test_cache_clear_and_len():
    cache = TTLCache()

    cache.set("/endpoint1", {"a": 1}, "val1", ttl_seconds=60)
    cache.set("/endpoint2", {"b": 2}, "val2", ttl_seconds=60)
    assert len(cache) == 2

    cache.clear()
    assert len(cache) == 0
    assert cache.get("/endpoint1", {"a": 1}) is None
