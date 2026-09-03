# v1 Exit Test Benchmark Report

Per Section 2 of `stackoverflow-mcp-spec.md`, 15 real-world Python error tracebacks were evaluated through `search_by_error` against the live Stack Exchange API.

**Benchmark Summary**: 0/15 queries (0.0%) successfully returned top Stack Overflow answers.

| ID | Error Query Snippet | Retrieval Status | Top Result Preview |
| :--- | :--- | :--- | :--- |
| `1` | `ModuleNotFoundError: No module named 'fastmcp'` | ⚠️ NO MATCH | No results |
| `2` | `AttributeError: 'NoneType' object has no attribute 'get'` | ⚠️ NO MATCH | No results |
| `3` | `TypeError: unhashable type: 'list'` | ⚠️ NO MATCH | No results |
| `4` | `KeyError: 'accepted_answer_id'` | ⚠️ NO MATCH | No results |
| `5` | `ZeroDivisionError: division by zero` | ⚠️ NO MATCH | No results |
| `6` | `FileNotFoundError: [Errno 2] No such file or directory: 'config.json'` | ⚠️ NO MATCH | No results |
| `7` | `ValueError: invalid literal for int() with base 10: 'abc'` | ⚠️ NO MATCH | No results |
| `8` | `IndexError: list index out of range` | ⚠️ NO MATCH | No results |
| `9` | `RecursionError: maximum recursion depth exceeded while calling a Python object` | ⚠️ NO MATCH | No results |
| `10` | `RuntimeError: Event loop is closed` | ⚠️ NO MATCH | No results |
| `11` | `TypeError: 'async_generator' object is not iterable` | ⚠️ NO MATCH | No results |
| `12` | `ImportError: cannot import name 'BaseSettings' from 'pydantic'` | ⚠️ NO MATCH | No results |
| `13` | `SyntaxError: invalid syntax` | ⚠️ NO MATCH | No results |
| `14` | `IndentationError: unexpected indent` | ⚠️ NO MATCH | No results |
| `15` | `PermissionError: [Errno 13] Permission denied: '/var/log/app.log'` | ⚠️ NO MATCH | No results |
