"""Pure logic module for Python error normalization and question/answer ranking."""

import re
from typing import Any


def normalize_python_error(error: str) -> str:
    """Normalize a Python error string or traceback into a clean search query.

    Strips:
    - Memory addresses (e.g. 0x7f8a9b1c)
    - File paths and line numbers (e.g. File "/path/to/file.py", line 42)
    - ISO/Standard Timestamps
    - UUIDs / GUIDs
    - Common log level prefixes ([ERROR], INFO:, etc.)

    Extracts the core exception type and message phrase.
    """
    if not error or not error.strip():
        return ""

    text = error.strip()

    # 1. Strip timestamps (e.g. 2026-09-03 17:51:37,123 or 2026-09-03T17:51:37Z)
    text = re.sub(
        r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?Z?",
        "",
        text,
    )

    # 2. Strip UUIDs / GUIDs
    text = re.sub(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        "",
        text,
    )

    # 3. Strip hex memory addresses (e.g. at 0x7ff89123a0)
    text = re.sub(r"\b0x[0-9a-fA-F]+\b", "", text)

    # 4. Strip Python stack frame lines (File ".../foo.py", line 123, in bar)
    text = re.sub(
        r'File\s+["\'][^"\']+["\'],\s+line\s+\d+(?:,\s+in\s+\w+)?',
        "",
        text,
        flags=re.IGNORECASE,
    )

    # 5. Strip standalone absolute or relative file paths (e.g. C:\path\to\file.py or /usr/lib/foo.py)
    text = re.sub(
        r'(?:[a-zA-Z]:\\|\B/)?(?:[\w.-]+[/\\])+[\w.-]+\.py(?::\d+)?',
        "",
        text,
    )

    # 6. Strip standard log prefixes like [ERROR], ERROR:, WARNING:
    text = re.sub(
        r"^\s*\[?(?:CRITICAL|ERROR|WARNING|INFO|DEBUG)\]?:?\s*",
        "",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    # 7. Locate the final exception line if a full traceback was provided
    # Python exceptions typically look like: "ExceptionName: message" or "ExceptionName"
    exception_matches = list(
        re.finditer(
            r"^([A-Z]\w*(?:Error|Exception|Interrupt|Exit|Warning)|KeyError|IndexError|ValueError|TypeError|AttributeError|ImportError|ModuleNotFoundError|NameError|RuntimeError|SyntaxError|IndentationError|TabError|ZeroDivisionError|FileNotFoundError|PermissionError|OSError|ConnectionError|TimeoutError)\b.*$",
            text,
            flags=re.MULTILINE,
        )
    )

    if exception_matches:
        # Take the last exception line in the traceback
        core_line = exception_matches[-1].group(0).strip()
    else:
        # Fall back to non-empty lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        core_line = lines[-1] if lines else text

    # Clean up duplicate whitespace and cap to 200 characters to avoid API bounds errors
    cleaned = re.sub(r"\s+", " ", core_line).strip()
    if len(cleaned) > 200:
        truncated = cleaned[:197]
        if " " in truncated:
            truncated = truncated.rsplit(" ", 1)[0]
        cleaned = truncated + "..."
    return cleaned


def rank_and_dedupe_questions(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate questions by question_id and rank them deterministically.

    Ranking policy:
    1. Accepted answers first (is_answered is True AND accepted_answer_id is present)
    2. Sort by highest answer score / question score descending
    """
    if not questions:
        return []

    # Deduplicate by question_id while preserving object data
    seen_ids: set[int] = set()
    deduped: list[dict[str, Any]] = []

    for q in questions:
        q_id = q.get("question_id")
        if q_id is not None and q_id not in seen_ids:
            seen_ids.add(q_id)
            deduped.append(q)
        elif q_id is None:
            deduped.append(q)

    # Sorting key:
    # Key 1: 1 if accepted answer exists, else 0
    # Key 2: highest score (max of question score and top answer score if present)
    def sort_key(q: dict[str, Any]) -> tuple[int, int, int]:
        has_accepted = 1 if q.get("accepted_answer_id") or q.get("is_answered") else 0
        q_score = q.get("score", 0) or 0
        
        # Check answer score if top answer attached
        top_answer = q.get("top_answer", {}) or {}
        a_score = top_answer.get("score", 0) or 0

        return (has_accepted, max(q_score, a_score), q_score)

    # Sort descending
    return sorted(deduped, key=sort_key, reverse=True)
