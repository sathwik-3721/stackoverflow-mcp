"""Unit tests for FastMCP tools."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from stackoverflow_mcp.stackexchange import StackOverflowMCPError
from stackoverflow_mcp.tools import get_question, search_by_error, search_questions, set_client


@pytest.mark.asyncio
async def test_search_questions_tool():
    mock_client = MagicMock()
    mock_client.search_questions = AsyncMock(return_value=[
        {
            "question_id": 100,
            "title": "Fixing AttributeError in Python",
            "score": 50,
            "is_answered": True,
            "accepted_answer_id": 200,
            "tags": ["python", "attributeerror"],
            "body_markdown": "How to resolve this issue?",
            "link": "https://stackoverflow.com/q/100",
        }
    ])
    set_client(mock_client)

    res = await search_questions(query="AttributeError", tags=["python"], limit=5)
    assert "# Stack Overflow Results for: `AttributeError`" in res
    assert "Fixing AttributeError in Python" in res
    assert "✅ Accepted Answer" in res
    assert "`100`" in res


@pytest.mark.asyncio
async def test_search_by_error_tool():
    mock_client = MagicMock()
    mock_client.search_questions = AsyncMock(return_value=[
        {
            "question_id": 101,
            "title": "ImportError: No module named foo",
            "score": 10,
            "is_answered": True,
            "accepted_answer_id": 201,
            "tags": ["python"],
            "link": "https://stackoverflow.com/q/101",
        }
    ])
    set_client(mock_client)

    tb = "Traceback (most recent call last):\n  File 'app.py', line 10\nModuleNotFoundError: No module named foo"
    res = await search_by_error(error=tb, language="python")
    assert "ModuleNotFoundError: No module named foo" in res
    assert "ImportError: No module named foo" in res


@pytest.mark.asyncio
async def test_search_by_error_empty():
    res = await search_by_error(error="   \n ")
    data = json.loads(res)
    assert data["kind"] == "validation_error"


@pytest.mark.asyncio
async def test_get_question_tool():
    mock_client = MagicMock()
    mock_client.get_question = AsyncMock(return_value={
        "question_id": 500,
        "title": "What is Python FastMCP?",
        "score": 30,
        "tags": ["python", "mcp"],
        "body_markdown": "Detailed question body text.",
        "link": "https://stackoverflow.com/q/500",
        "answers": [
            {
                "answer_id": 600,
                "score": 25,
                "is_accepted": True,
                "body_markdown": "FastMCP simplifies MCP server creation.",
                "link": "https://stackoverflow.com/a/600",
            }
        ],
    })
    set_client(mock_client)

    res = await get_question(question_id=500)
    assert "# [What is Python FastMCP?]" in res
    assert "Detailed question body text." in res
    assert "FastMCP simplifies MCP server creation." in res
    assert "(Accepted Answer)" in res


@pytest.mark.asyncio
async def test_tool_error_handling():
    mock_client = MagicMock()
    mock_client.search_questions = AsyncMock(side_effect=StackOverflowMCPError(
        kind="rate_limited",
        message="Daily quota exceeded",
        retryable=False,
    ))
    set_client(mock_client)

    res = await search_questions("query")
    data = json.loads(res)
    assert data["kind"] == "rate_limited"
    assert "Daily quota exceeded" in data["message"]
