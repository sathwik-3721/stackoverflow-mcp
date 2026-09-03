"""Stack Exchange API v2.3 client module for stackoverflow-mcp."""

import asyncio
import logging
import random
import time
from typing import Any

import httpx

from stackoverflow_mcp.cache import TTLCache
from stackoverflow_mcp.config import settings

logger = logging.getLogger("stackoverflow_mcp.stackexchange")

BASE_URL = "https://api.stackexchange.com/2.3"
DEFAULT_FILTER = "withbody"  # Built-in SE filter including body_markdown for questions & answers


class StackOverflowMCPError(Exception):
    """Structured exception for Stack Overflow MCP operations."""

    def __init__(
        self,
        kind: str,  # "api_error" | "rate_limited" | "validation_error"
        message: str,
        retryable: bool = False,
        backoff_seconds: int | None = None,
    ) -> None:
        super().__init__(message)
        self.kind = kind
        self.message = message
        self.retryable = retryable
        self.backoff_seconds = backoff_seconds

    def to_dict(self) -> dict[str, Any]:
        result = {
            "kind": self.kind,
            "message": self.message,
            "retryable": self.retryable,
        }
        if self.backoff_seconds is not None:
            result["backoff_seconds"] = self.backoff_seconds
        return result


class StackExchangeClient:
    """Async API client for Stack Exchange v2.3 with caching and rate limit backoff."""

    RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}

    def __init__(self, cache: TTLCache | None = None) -> None:
        self.cache = cache or TTLCache()
        self._backoff_until: float = 0.0
        self._quota_remaining: int | None = None

    @property
    def quota_remaining(self) -> int | None:
        """Return remaining daily API quota reported by Stack Exchange."""
        return self._quota_remaining

    def _check_backoff(self) -> None:
        """Enforce API backoff timer if set by Stack Exchange response."""
        now = time.monotonic()
        if now < self._backoff_until:
            wait_time = int(self._backoff_until - now) + 1
            raise StackOverflowMCPError(
                kind="rate_limited",
                message=f"Stack Exchange API backoff active. Please try again in {wait_time} seconds.",
                retryable=False,
                backoff_seconds=wait_time,
            )

    async def _request(
        self,
        endpoint: str,
        params: dict[str, Any],
        ttl_seconds: int = 60,
    ) -> dict[str, Any]:
        """Execute HTTP GET request against Stack Exchange API with cache, retries, and backoff."""
        self._check_backoff()

        # Check in-memory cache first
        cached = self.cache.get(endpoint, params)
        if cached is not None:
            logger.debug(f"Cache hit for endpoint {endpoint}")
            return cached

        # Prepare query parameters
        request_params = dict(params)
        request_params["site"] = "stackoverflow"
        request_params["filter"] = DEFAULT_FILTER
        if settings.STACKEXCHANGE_KEY:
            request_params["key"] = settings.STACKEXCHANGE_KEY

        url = f"{BASE_URL}{endpoint}"
        max_retries = settings.STACKOVERFLOW_API_MAX_RETRIES
        timeout = settings.STACKOVERFLOW_API_TIMEOUT_SECONDS

        attempt = 0
        last_exception: Exception | None = None

        async with httpx.AsyncClient(timeout=timeout) as client:
            while attempt <= max_retries:
                attempt += 1
                try:
                    logger.debug(f"Fetching {url} (attempt {attempt}/{max_retries + 1})")
                    response = await client.get(url, params=request_params)

                    # Update quota and backoff state if present in JSON payload
                    try:
                        data = response.json()
                    except Exception:
                        data = {}

                    if isinstance(data, dict):
                        if "quota_remaining" in data:
                            self._quota_remaining = data["quota_remaining"]

                        if "backoff" in data:
                            backoff_sec = int(data["backoff"])
                            self._backoff_until = time.monotonic() + backoff_sec
                            logger.warning(f"Stack Exchange requested backoff for {backoff_sec}s")

                        if "error_id" in data or "error_message" in data:
                            err_msg = data.get("error_message", "Unknown Stack Exchange API error")
                            err_name = data.get("error_name", "api_error")
                            if response.status_code == 429 or "throttle" in err_name.lower():
                                raise StackOverflowMCPError(
                                    kind="rate_limited",
                                    message=f"Rate limit exceeded: {err_msg}",
                                    retryable=False,
                                )
                            raise StackOverflowMCPError(
                                kind="api_error",
                                message=f"Stack Exchange error ({err_name}): {err_msg}",
                                retryable=False,
                            )

                    # Handle HTTP status codes
                    if response.status_code == 200:
                        self.cache.set(endpoint, params, data, ttl_seconds=ttl_seconds)
                        return data

                    if response.status_code in self.RETRYABLE_STATUS_CODES and attempt <= max_retries:
                        delay = (2 ** attempt) + random.uniform(0.1, 0.5)
                        logger.warning(
                            f"HTTP {response.status_code} from SE API, retrying in {delay:.2f}s"
                        )
                        await asyncio.sleep(delay)
                        continue

                    response.raise_for_status()

                except (httpx.TimeoutException, httpx.TransportError) as exc:
                    last_exception = exc
                    if attempt <= max_retries:
                        delay = (2 ** attempt) + random.uniform(0.1, 0.5)
                        logger.warning(f"Network error ({exc}), retrying in {delay:.2f}s")
                        await asyncio.sleep(delay)
                        continue
                    break

        if last_exception:
            raise StackOverflowMCPError(
                kind="api_error",
                message=f"Stack Exchange request failed after {max_retries} retries: {last_exception}",
                retryable=True,
            )

        raise StackOverflowMCPError(
            kind="api_error",
            message="Stack Exchange API request failed with unknown error.",
            retryable=False,
        )

    async def search_questions(
        self,
        query: str,
        tags: list[str] | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Search questions via /search/advanced endpoint."""
        bounded_limit = min(max(1, limit), settings.STACKOVERFLOW_MAX_RESULTS)
        params: dict[str, Any] = {
            "q": query,
            "pagesize": bounded_limit,
            "sort": "relevance",
            "order": "desc",
        }
        if tags:
            params["tagged"] = ";".join(tags)

        data = await self._request("/search/advanced", params=params, ttl_seconds=TTLCache.DEFAULT_SEARCH_TTL)
        return data.get("items", [])

    async def get_question(
        self,
        question_id: int,
        include_answers: bool = True,
    ) -> dict[str, Any] | None:
        """Fetch question details (and optional answers) by question_id."""
        endpoint = f"/questions/{question_id}"
        params: dict[str, Any] = {}
        data = await self._request(endpoint, params=params, ttl_seconds=TTLCache.DEFAULT_CONTENT_TTL)
        items = data.get("items", [])
        if not items:
            return None

        question = items[0]
        if include_answers and not question.get("answers"):
            answers = await self.get_answers(question_id)
            question["answers"] = answers

        return question

    async def get_answers(self, question_id: int) -> list[dict[str, Any]]:
        """Fetch answers for a specific question."""
        endpoint = f"/questions/{question_id}/answers"
        params: dict[str, Any] = {"sort": "votes", "order": "desc"}
        data = await self._request(endpoint, params=params, ttl_seconds=TTLCache.DEFAULT_CONTENT_TTL)
        return data.get("items", [])
