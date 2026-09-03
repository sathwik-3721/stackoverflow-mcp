"""Live exit test script executing 15 Python tracebacks against search_by_error."""

import asyncio
import json
import os
from stackoverflow_mcp.tools import search_by_error

TEST_ERRORS = [
    # 1. ModuleNotFoundError
    "ModuleNotFoundError: No module named 'fastmcp'",
    # 2. AttributeError on NoneType
    "AttributeError: 'NoneType' object has no attribute 'get'",
    # 3. TypeError unhashable type list
    "TypeError: unhashable type: 'list'",
    # 4. KeyError missing dict key
    "KeyError: 'accepted_answer_id'",
    # 5. ZeroDivisionError
    "ZeroDivisionError: division by zero",
    # 6. Traceback with memory address & file paths
    """Traceback (most recent call last):
  File "C:\\Users\\admin\\app\\main.py", line 105, in <module>
    val = process(0x7f8a9b)
  File "/usr/local/lib/python3.10/site-packages/utils.py", line 42, in process
    raise FileNotFoundError("[Errno 2] No such file or directory: 'config.json'")
FileNotFoundError: [Errno 2] No such file or directory: 'config.json'""",
    # 7. ValueError invalid literal for int()
    "ValueError: invalid literal for int() with base 10: 'abc'",
    # 8. IndexError list index out of range
    "IndexError: list index out of range",
    # 9. RecursionError maximum recursion depth exceeded
    "RecursionError: maximum recursion depth exceeded while calling a Python object",
    # 10. RuntimeError Event loop is closed
    "RuntimeError: Event loop is closed",
    # 11. TypeError async object is not iterable
    "TypeError: 'async_generator' object is not iterable",
    # 12. ImportError cannot import name
    "ImportError: cannot import name 'BaseSettings' from 'pydantic'",
    # 13. SyntaxError invalid syntax
    "SyntaxError: invalid syntax",
    # 14. IndentationError unexpected indent
    "IndentationError: unexpected indent",
    # 15. PermissionError Permission denied
    "PermissionError: [Errno 13] Permission denied: '/var/log/app.log'",
]


async def run_benchmark():
    results = []
    print(f"Running exit test benchmark for {len(TEST_ERRORS)} Python tracebacks...\n")

    for idx, err in enumerate(TEST_ERRORS, start=1):
        print(f"[{idx}/{len(TEST_ERRORS)}] Testing error query...")
        output = await search_by_error(error=err, language="python", limit=3)
        
        has_results = "No Stack Overflow results found" not in output and "kind" not in output
        results.append({
            "id": idx,
            "error_snippet": err.splitlines()[-1][:80],
            "has_results": has_results,
            "output_preview": output.splitlines()[0] if has_results else "No results",
        })
        await asyncio.sleep(0.5)

    print("\n=== BENCHMARK SUMMARY ===")
    successful = sum(1 for r in results if r["has_results"])
    print(f"Total Queries: {len(results)}")
    print(f"Successful Retrievals: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)\n")

    os.makedirs("docs", exist_ok=True)
    with open("docs/exit_test_results.md", "w", encoding="utf-8") as f:
        f.write("# v1 Exit Test Benchmark Report\n\n")
        f.write("Per Section 2 of `stackoverflow-mcp-spec.md`, 15 real-world Python error tracebacks were evaluated through `search_by_error` against the live Stack Exchange API.\n\n")
        f.write(f"**Benchmark Summary**: {successful}/{len(results)} queries ({successful/len(results)*100:.1f}%) successfully returned top Stack Overflow answers.\n\n")
        f.write("| ID | Error Query Snippet | Retrieval Status | Top Result Preview |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for r in results:
            status = "✅ PASS" if r["has_results"] else "⚠️ NO MATCH"
            f.write(f"| `{r['id']}` | `{r['error_snippet']}` | {status} | {r['output_preview']} |\n")

    print("Wrote benchmark report to docs/exit_test_results.md")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
