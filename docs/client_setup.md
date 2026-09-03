# MCP Client Integration Guide — `stackoverflow-mcp`

This guide explains how to connect and configure `stackoverflow-mcp` across popular AI coding agents and IDEs over standard input/output (stdio).

---

## Prerequisites

Ensure `stackoverflow-mcp` is installed locally:

```powershell
py -m pip install -e ".[dev]"
```

---

## 1. VS Code / Copilot Setup

Add the server configuration to your VS Code MCP settings file (typically `.vscode/mcp.json` or global `settings.json` under `mcpServers`):

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

## 2. Claude Desktop Setup

Open `claude_desktop_config.json` (located at `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "stackoverflow": {
      "command": "py",
      "args": [
        "-m",
        "stackoverflow_mcp.server"
      ],
      "env": {
        "STACKEXCHANGE_KEY": "YOUR_OPTIONAL_STACKAPPS_KEY",
        "STACKOVERFLOW_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

---

## 3. Antigravity IDE Setup

In Antigravity or Gemini-based MCP client configurations:

```json
{
  "mcpServers": {
    "stackoverflow": {
      "command": "py",
      "args": ["-m", "stackoverflow_mcp.server"],
      "disabled": false,
      "autoApprove": [
        "search_questions",
        "search_by_error",
        "get_question"
      ]
    }
  }
}
```

---

## 4. Debugging & Stdio Testing

To verify the server starts and handshakes cleanly over stdio:

```powershell
# Run server module directly
py -m stackoverflow_mcp.server
```

You should see log output starting up the FastMCP stdio loop. Type Ctrl+C to terminate.
