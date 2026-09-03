"""Unit tests for FastMCP server initialization."""

import pytest
from stackoverflow_mcp.server import mcp


@pytest.mark.asyncio
async def test_server_registration():
    assert mcp.name == "stackoverflow-mcp"
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "search_questions" in tool_names
    assert "search_by_error" in tool_names
    assert "get_question" in tool_names
