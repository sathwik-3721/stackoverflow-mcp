"""FastMCP server entrypoint for stackoverflow-mcp."""

import logging
from fastmcp import FastMCP

from stackoverflow_mcp.config import settings
from stackoverflow_mcp.tools import get_question, search_by_error, search_questions

# Configure logging verbosity
logging.basicConfig(
    level=getattr(logging, settings.STACKOVERFLOW_LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Instantiate FastMCP server
mcp = FastMCP(
    "stackoverflow-mcp",
    instructions="A Model Context Protocol server for retrieving Stack Overflow coding knowledge.",
)

# Register tool functions
mcp.tool()(search_questions)
mcp.tool()(search_by_error)
mcp.tool()(get_question)


def main() -> None:
    """Start FastMCP server over stdio transport."""
    mcp.run()


if __name__ == "__main__":
    main()
