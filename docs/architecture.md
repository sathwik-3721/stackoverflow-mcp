# Architecture Specification — `stackoverflow-mcp`

`stackoverflow-mcp` is designed as a single-file-per-concern FastMCP server optimized for low-latency retrieval of Stack Overflow solutions without requiring OAuth or internal LLM inference.

---

## 1. System Topology

```mermaid
graph TD
    subgraph Client["Coding Agent (Client)"]
        IDE["VS Code / Claude Desktop / Antigravity"]
    end

    subgraph Server["stackoverflow_mcp (FastMCP Server)"]
        ServerPy["server.py<br/><i>FastMCP Stdio Server Entrypoint</i>"]
        ToolsPy["tools.py<br/><i>Tool Surface & Markdown Formatting</i>"]
        RankingPy["ranking.py<br/><i>Python Traceback Normalizer & Answer Ranker</i>"]
        SEClient["stackexchange.py<br/><i>HTTP Client, Retries & SSL Truststore</i>"]
        CachePy["cache.py<br/><i>TTLCache (In-Memory SHA-256 Hashing)</i>"]
        ConfigPy["config.py<br/><i>Pydantic BaseSettings (.env Configuration)</i>"]
    end

    subgraph API["Stack Exchange Network"]
        SEAPI["Stack Exchange API v2.3<br/><code>api.stackexchange.com/2.3</code>"]
    end

    IDE -->|"MCP Protocol (stdio)"| ServerPy
    ServerPy --> ToolsPy
    ToolsPy --> RankingPy
    ToolsPy --> SEClient
    SEClient --> CachePy
    SEClient --> ConfigPy
    SEClient -->|"HTTPS GET (site=stackoverflow)"| SEAPI
```

### Request Execution Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Agent as Coding Agent
    participant Tools as tools.py
    participant Normalizer as ranking.py
    participant Client as stackexchange.py
    participant Cache as cache.py
    participant SE as Stack Exchange API

    Agent->>Tools: search_by_error(error_traceback, language="python")
    Tools->>Normalizer: normalize_python_error(error_traceback)
    Normalizer-->>Tools: Clean Exception Query (e.g., "ZeroDivisionError")
    Tools->>Client: search_questions(query, tags=["python"])
    Client->>Cache: get("/search/advanced", params)
    alt Cache Hit
        Cache-->>Client: Cached API Response
    else Cache Miss
        Client->>SE: GET /search/advanced (filter=withbody)
        SE-->>Client: JSON Response (quota_remaining, backoff, items)
        Client->>Cache: set("/search/advanced", params, response, ttl=60s)
    end
    Client-->>Tools: Raw Question Items
    Tools->>Normalizer: rank_and_dedupe_questions(items)
    Normalizer-->>Tools: Deduplicated Accepted-First Ranked Items
    Tools-->>Agent: LLM-Friendly Markdown Summary + Source URLs
```

---

## 2. Design Principles

1. **Deterministic Retrieval**:
   * No internal LLM calls. Eliminates extra token costs and recursive latency.
2. **Accepted-First Ranking**:
   * Deduplicates search items by `question_id`.
   * Sorts questions with accepted answers (`is_answered` / `accepted_answer_id`) above non-accepted questions.
3. **Monotonic Rate-Limit Protection**:
   * Inspects `backoff` fields in Stack Exchange responses.
   * Uses monotonic clock timers (`time.monotonic()`) to enforce cool-down blocks before IP throttling occurs.
4. **Traceback Normalization**:
   * Regex-based cleaner strips noise (hex addresses `0x7f...`, paths, line numbers, timestamps, UUIDs) from error tracebacks to isolate the core Exception class and phrase.

---

## 3. Module Boundaries

| Module | Responsibility |
| :--- | :--- |
| `server.py` | Initializes `FastMCP("stackoverflow-mcp")`, registers tool handlers, starts stdio event loop. |
| `tools.py` | Formats search & question data into LLM-friendly Markdown output with source URLs. |
| `stackexchange.py` | Manages `httpx.AsyncClient`, retries, SSL truststore injection, and SE API v2.3 requests. |
| `ranking.py` | Pure deterministic functions for traceback normalization and accepted-first sorting. |
| `cache.py` | Dict-backed `TTLCache` mapping hashed canonical tuples `(endpoint, sorted_params)` to values. |
| `config.py` | Validates environment configuration using Pydantic `BaseSettings`. |
