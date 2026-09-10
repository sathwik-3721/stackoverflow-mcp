"""FastMCP tool functions for stackoverflow-mcp."""

import json
import logging
from typing import Any

from stackoverflow_mcp.ranking import normalize_python_error, rank_and_dedupe_questions
from stackoverflow_mcp.stackexchange import StackExchangeClient, StackOverflowMCPError

logger = logging.getLogger("stackoverflow_mcp.tools")

_client: StackExchangeClient | None = None


def get_client() -> StackExchangeClient:
    """Get or create the global StackExchangeClient instance."""
    global _client
    if _client is None:
        _client = StackExchangeClient()
    return _client


def set_client(client: StackExchangeClient) -> None:
    """Set custom client instance (used for testing/mocking)."""
    global _client
    _client = client


def _format_search_results(query: str, questions: list[dict[str, Any]]) -> str:
    """Format question search results into LLM-friendly Markdown."""
    if not questions:
        return f"No Stack Overflow results found for query: '{query}'."

    ranked = rank_and_dedupe_questions(questions)
    output_lines = [f"# Stack Overflow Results for: `{query}`\n"]

    for idx, q in enumerate(ranked, start=1):
        q_id = q.get("question_id")
        title = q.get("title", "Untitled Question")
        score = q.get("score", 0)
        link = q.get("link", f"https://stackoverflow.com/q/{q_id}")
        is_answered = q.get("is_answered", False)
        has_accepted = bool(q.get("accepted_answer_id"))
        tags = q.get("tags", [])

        status_str = "[Accepted Answer]" if has_accepted else ("[Answered]" if is_answered else "[Unanswered]")
        tag_str = ", ".join(f"`{t}`" for t in tags)

        output_lines.append(f"### {idx}. [{title}]({link})")
        output_lines.append(f"- **ID**: `{q_id}` | **Score**: `{score}` | **Status**: {status_str}")
        if tag_str:
            output_lines.append(f"- **Tags**: {tag_str}")

        body_md = q.get("body_markdown", "")
        if body_md:
            excerpt = body_md.strip()[:250].replace("\n", " ")
            output_lines.append(f"- **Excerpt**: {excerpt}...")

        output_lines.append("\n---\n")

    return "\n".join(output_lines)


def _format_question_detail(q: dict[str, Any]) -> str:
    """Format full question and answer details into Markdown."""
    q_id = q.get("question_id")
    title = q.get("title", "Untitled Question")
    score = q.get("score", 0)
    link = q.get("link", f"https://stackoverflow.com/q/{q_id}")
    tags = ", ".join(f"`{t}`" for t in q.get("tags", []))
    body = q.get("body_markdown", "No content available.").strip()

    output = [
        f"# [{title}]({link})",
        f"**Question ID**: `{q_id}` | **Score**: `{score}` | **Tags**: {tags}\n",
        "## Question Body\n",
        body,
        "\n---\n",
    ]

    answers = q.get("answers", [])
    if answers:
        output.append(f"## Answers ({len(answers)})\n")
        for idx, a in enumerate(answers, start=1):
            a_id = a.get("answer_id")
            a_score = a.get("score", 0)
            is_acc = a.get("is_accepted", False)
            a_link = a.get("link", f"https://stackoverflow.com/a/{a_id}")
            acc_str = " (Accepted Answer)" if is_acc else ""
            a_body = a.get("body_markdown", "No content.").strip()

            output.append(f"### Answer {idx}{acc_str} — Score: `{a_score}` ([Link]({a_link}))")
            output.append(a_body)
            output.append("\n---\n")

    return "\n".join(output)


async def search_questions(
    query: str,
    tags: list[str] | None = None,
    limit: int = 5,
) -> str:
    """Search Stack Overflow questions matching a query and optional tags."""
    try:
        if not query or not query.strip():
            return json.dumps({
                "kind": "validation_error",
                "message": "Search query cannot be empty or whitespace.",
                "retryable": False,
            })

        client = get_client()
        questions = await client.search_questions(query=query, tags=tags, limit=limit)
        return _format_search_results(query, questions)
    except StackOverflowMCPError as exc:
        return json.dumps(exc.to_dict())
    except Exception as exc:
        logger.error(f"Error in search_questions tool: {exc}")
        return json.dumps({"kind": "api_error", "message": str(exc), "retryable": False})


async def search_by_error(
    error: str,
    language: str | None = None,
    limit: int = 5,
) -> str:
    """Search Stack Overflow using a Python traceback or error log."""
    try:
        normalized_query = normalize_python_error(error)
        if not normalized_query:
            return json.dumps({
                "kind": "validation_error",
                "message": "Input error string is empty or invalid.",
                "retryable": False,
            })

        tag_list = None
        if language:
            tag_list = [language.strip().lower()]

        client = get_client()
        questions = await client.search_questions(query=normalized_query, tags=tag_list, limit=limit)
        return _format_search_results(normalized_query, questions)
    except StackOverflowMCPError as exc:
        return json.dumps(exc.to_dict())
    except Exception as exc:
        logger.error(f"Error in search_by_error tool: {exc}")
        return json.dumps({"kind": "api_error", "message": str(exc), "retryable": False})


async def get_question(
    question_id: int,
    include_answers: bool = True,
) -> str:
    """Fetch details and answers for a specific Stack Overflow question by ID."""
    try:
        client = get_client()
        question = await client.get_question(question_id, include_answers=include_answers)
        if not question:
            return f"Question `{question_id}` not found on Stack Overflow."
        return _format_question_detail(question)
    except StackOverflowMCPError as exc:
        return json.dumps(exc.to_dict())
    except Exception as exc:
        logger.error(f"Error in get_question tool: {exc}")
        return json.dumps({"kind": "api_error", "message": str(exc), "retryable": False})
