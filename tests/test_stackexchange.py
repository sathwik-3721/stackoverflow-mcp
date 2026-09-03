"""Unit tests for Stack Exchange API client."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from stackoverflow_mcp.cache import TTLCache
from stackoverflow_mcp.stackexchange import StackExchangeClient, StackOverflowMCPError


def test_error_to_dict():
    err = StackOverflowMCPError(
        kind="rate_limited",
        message="Backoff active",
        retryable=False,
        backoff_seconds=30,
    )
    d = err.to_dict()
    assert d == {
        "kind": "rate_limited",
        "message": "Backoff active",
        "retryable": False,
        "backoff_seconds": 30,
    }


@pytest.mark.asyncio
async def test_search_questions_success():
    cache = TTLCache()
    client = StackExchangeClient(cache=cache)

    mock_data = {
        "items": [
            {"question_id": 100, "title": "How to fix AttributeError?", "score": 25}
        ],
        "quota_remaining": 9999,
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        items = await client.search_questions("AttributeError", tags=["python"], limit=5)
        assert len(items) == 1
        assert items[0]["title"] == "How to fix AttributeError?"
        assert client.quota_remaining == 9999

        # Test cache hit on subsequent call
        items_cached = await client.search_questions("AttributeError", tags=["python"], limit=5)
        assert items_cached == items
        # HTTP client get should only have been called once due to cache
        assert mock_get.call_count == 1


@pytest.mark.asyncio
async def test_backoff_enforcement():
    cache = TTLCache()
    client = StackExchangeClient(cache=cache)

    mock_data = {
        "items": [],
        "backoff": 10,
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        await client.search_questions("test query")

    # Second call should raise rate_limited error immediately without hitting network
    with pytest.raises(StackOverflowMCPError) as exc_info:
        await client.search_questions("another query")

    assert exc_info.value.kind == "rate_limited"
    assert exc_info.value.backoff_seconds is not None
    assert exc_info.value.backoff_seconds > 0


@pytest.mark.asyncio
async def test_api_error_response():
    cache = TTLCache()
    client = StackExchangeClient(cache=cache)

    mock_data = {
        "error_id": 400,
        "error_name": "bad_parameter",
        "error_message": "Invalid page size",
    }

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = mock_data

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        with pytest.raises(StackOverflowMCPError) as exc_info:
            await client.search_questions("invalid")

        assert exc_info.value.kind == "api_error"
        assert "Invalid page size" in exc_info.value.message
