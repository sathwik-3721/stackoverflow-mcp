"""In-memory TTL cache for Stack Exchange API responses."""

import hashlib
import json
import time
from typing import Any


class TTLCache:
    """In-memory TTL cache using canonical (endpoint, sorted_params) key hashing."""

    DEFAULT_SEARCH_TTL = 60      # 60 seconds for search results
    DEFAULT_CONTENT_TTL = 300    # 5 minutes for question/answer details

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}

    @staticmethod
    def _make_key(endpoint: str, params: dict[str, Any] | None = None) -> str:
        """Create a deterministic SHA-256 key from endpoint and sorted params."""
        if not params:
            canonical_params = []
        else:
            canonical_params = []
            for k in sorted(params.keys()):
                val = params[k]
                if isinstance(val, (list, tuple)):
                    val = ",".join(sorted(str(x) for x in val))
                elif val is None:
                    val = ""
                else:
                    val = str(val)
                canonical_params.append((k, val))

        raw_key = f"{endpoint}:{json.dumps(canonical_params, sort_keys=True)}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any | None:
        """Retrieve cached value if present and not expired."""
        key = self._make_key(endpoint, params)
        entry = self._store.get(key)
        if entry is None:
            return None

        value, expire_at = entry
        if time.monotonic() > expire_at:
            del self._store[key]
            return None

        return value

    def set(
        self,
        endpoint: str,
        params: dict[str, Any] | None,
        value: Any,
        ttl_seconds: int,
    ) -> None:
        """Cache a value with a specified TTL in seconds."""
        key = self._make_key(endpoint, params)
        expire_at = time.monotonic() + ttl_seconds
        self._store[key] = (value, expire_at)

    def clear(self) -> None:
        """Purge all entries from the cache."""
        self._store.clear()

    def __len__(self) -> int:
        """Return count of non-expired entries in cache."""
        now = time.monotonic()
        expired_keys = [k for k, (_, exp) in self._store.items() if now > exp]
        for k in expired_keys:
            del self._store[k]
        return len(self._store)
