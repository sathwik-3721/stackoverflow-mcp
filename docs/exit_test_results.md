# v1 Exit Test Benchmark Report

Per Section 2 of `stackoverflow-mcp-spec.md`, 15 real-world Python error tracebacks were evaluated through `search_by_error` against the live Stack Exchange API.

**Benchmark Summary**: 13/15 queries (86.7%) successfully returned top Stack Overflow answers.

| ID | Error Query Snippet | Retrieval Status | Top Result Preview |
| :--- | :--- | :--- | :--- |
| `1` | `ModuleNotFoundError: No module named 'fastmcp'` | ✅ PASS | # Stack Overflow Results for: `ModuleNotFoundError: No module named 'fastmcp'` |
| `2` | `AttributeError: 'NoneType' object has no attribute 'get'` | ✅ PASS | # Stack Overflow Results for: `AttributeError: 'NoneType' object has no attribute 'get'` |
| `3` | `TypeError: unhashable type: 'list'` | ✅ PASS | # Stack Overflow Results for: `TypeError: unhashable type: 'list'` |
| `4` | `KeyError: 'accepted_answer_id'` | ✅ PASS | # Stack Overflow Results for: `KeyError: 'accepted_answer_id'` |
| `5` | `ZeroDivisionError: division by zero` | ✅ PASS | # Stack Overflow Results for: `ZeroDivisionError: division by zero` |
| `6` | `FileNotFoundError: [Errno 2] No such file or directory: 'config.json'` | ⚠️ NO MATCH | No results |
| `7` | `ValueError: invalid literal for int() with base 10: 'abc'` | ✅ PASS | # Stack Overflow Results for: `ValueError: invalid literal for int() with base 10: 'abc'` |
| `8` | `IndexError: list index out of range` | ✅ PASS | # Stack Overflow Results for: `IndexError: list index out of range` |
| `9` | `RecursionError: maximum recursion depth exceeded while calling a Python object` | ✅ PASS | # Stack Overflow Results for: `RecursionError: maximum recursion depth exceeded while calling a Python object` |
| `10` | `RuntimeError: Event loop is closed` | ✅ PASS | # Stack Overflow Results for: `RuntimeError: Event loop is closed` |
| `11` | `TypeError: 'async_generator' object is not iterable` | ✅ PASS | # Stack Overflow Results for: `TypeError: 'async_generator' object is not iterable` |
| `12` | `ImportError: cannot import name 'BaseSettings' from 'pydantic'` | ✅ PASS | # Stack Overflow Results for: `ImportError: cannot import name 'BaseSettings' from 'pydantic'` |
| `13` | `SyntaxError: invalid syntax` | ✅ PASS | # Stack Overflow Results for: `SyntaxError: invalid syntax` |
| `14` | `IndentationError: unexpected indent` | ✅ PASS | # Stack Overflow Results for: `IndentationError: unexpected indent` |
| `15` | `PermissionError: [Errno 13] Permission denied: '/var/log/app.log'` | ⚠️ NO MATCH | No results |
