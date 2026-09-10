# stackoverflow-mcp

A focused **Model Context Protocol (MCP)** server for AI coding agents (VS Code Copilot, Antigravity, Claude Desktop) that retrieves Stack Overflow knowledge through the official Stack Exchange API (`api.stackexchange.com/2.3`). Built with Python 3.10+ and FastMCP.

---

## Key Features

* **Deterministic & Pure**: No internal LLM calls. Returns clean Markdown and direct Stack Overflow URLs without added token cost or latency.
* **Universal Technology Support**: `search_questions` and `get_question` support **all** programming languages and framework topics on Stack Overflow (JavaScript, TypeScript, Java, Python, Go, Rust, C++, SQL, Docker, etc.).
* **Python Traceback Normalization**: `search_by_error` automatically strips file paths, memory addresses (`0x7f...`), line numbers, UUIDs, and timestamps from Python error tracebacks to isolate the core Exception phrase.
* **No Account / OAuth Required**: Operates locally over stdio transport using Stack Exchange's free API quota (~300 requests/day unauthenticated, 10,000 requests/day with an optional free app key).
* **Accepted-First Ranking**: Deduplicates search results by `question_id` and prioritizes accepted answers and highest-scored answers.
* **In-Memory TTL Caching**: Prevents redundant API requests (`60s` search TTL, `300s` content TTL).
* **Enterprise SSL & Rate Limit Protection**: Integrates Python `truststore` for corporate proxy SSL certificate trust and enforces Stack Exchange `backoff` headers with exponential retries on transient network errors.

---

## Documentation Index

For detailed guides and architecture specifications, see the `docs/` folder:

* 📚 **[Architecture Specification](docs/architecture.md)** — System design, module responsibilities, Mermaid topology, and sequence flow.
* ⚙️ **[Client Integration Guide](docs/client_setup.md)** — Comprehensive setup guide for VS Code, Claude Desktop, and Antigravity.
* 📊 **[Exit Test Benchmark Report](docs/exit_test_results.md)** — Live benchmark evaluating 15 Python error tracebacks (**86.7% retrieval accuracy**).

---

## Language & Technology Support

| Capability | Scope | Description |
| :--- | :--- | :--- |
| **General Search (`search_questions`)** | 🌐 **All Languages & Tools** | Search Stack Overflow for any keyword, language, or tag (`python`, `javascript`, `docker`, `rust`, etc.). |
| **Question Details (`get_question`)** | 🌐 **All Languages & Tools** | Retrieve full question text and top answer bodies by Question ID. |
| **Traceback Normalization (`search_by_error`)** | 🐍 **Python-Tuned (v1)** | Strips Python stack frames and memory hex addresses. *(JS, Java, Go trace normalizers scheduled for v1.x)*. |

---

## Installation

### Prerequisites
* **Python**: `>= 3.10`

### Step 1: Clone and Install
```powershell
# Clone the repository
git clone https://github.com/sathwik-3721/stackoverflow-mcp.git
cd stackoverflow-mcp

# Install package in editable mode with dev dependencies
py -m pip install -e ".[dev]"
```

---

## MCP Client Configuration

To register `stackoverflow-mcp` with your AI coding agent, add the stdio server snippet to your client's configuration file:

### VS Code / Claude Desktop Configuration (`mcpServers`)

```json
{
  "mcpServers": {
    "stackoverflow": {
      "command": "py",
      "args": [
        "-m",
        "stackoverflow_mcp.server"
      ],
      "cwd": "D:/MCP/stackoverflow-mcp",
      "env": {
        "STACKEXCHANGE_KEY": "",
        "STACKOVERFLOW_MAX_RESULTS": "10",
        "STACKOVERFLOW_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

---

## Available Tools

The server exposes 3 purpose-built tools:

### 1. `search_questions`
Search Stack Overflow questions matching a query and optional tags across any programming language.
* **Parameters**:
  * `query` (str): Search keywords (e.g. `"AttributeError NoneType"` or `"React useEffect infinite loop"`).
  * `tags` (list[str], optional): Tag filters (e.g. `["python"]` or `["javascript", "react"]`).
  * `limit` (int, default: 5): Number of results (max 10).

### 2. `search_by_error`
Pass raw Python error tracebacks or exception logs directly. The server automatically cleans noise and queries Stack Overflow for matching solutions.
* **Parameters**:
  * `error` (str): Raw Python traceback or exception log string.
  * `language` (str, optional): Programming language (default: `"python"`).
  * `limit` (int, default: 5): Max search results.

### 3. `get_question`
Retrieve complete question details and top answer bodies by ID.
* **Parameters**:
  * `question_id` (int): Stack Overflow Question ID.
  * `include_answers` (bool, default: `true`): Include top answer markdown bodies.

---

## Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `STACKEXCHANGE_KEY` | `None` | Optional free API key from [Stack Apps](https://stackapps.com/) (boosts quota from 300 to 10,000/day). |
| `STACKOVERFLOW_MAX_RESULTS` | `10` | Maximum search results returned per tool call (capped at 10). |
| `STACKOVERFLOW_API_TIMEOUT_SECONDS` | `15` | Network request timeout in seconds. |
| `STACKOVERFLOW_API_MAX_RETRIES` | `3` | Max retry attempts for transient API errors. |
| `STACKOVERFLOW_LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

---

## Running Tests

Run the full automated test suite using `pytest`:

```powershell
py -m pytest -v
```

---

## License

MIT License
