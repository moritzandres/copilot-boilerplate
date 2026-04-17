---
name: add-mcp
description: Scaffold a new custom MCP server for this repository. Use this skill whenever the user wants to create, add, scaffold, or wire up a new MCP server, local tool server, or Model Context Protocol integration for the project. Trigger on phrases like "add an MCP", "create an MCP", "new MCP server", "scaffold MCP", or "custom MCP".
---

# Add MCP

Scaffold a new repository-local MCP server under `.github/mcps/` and register it in `.github/.mcp.json`.

## When to use

Use this skill when the user wants a new custom MCP server for this repository, especially a local stdio MCP implemented in Python.

## Default approach

Prefer a local Python MCP using `FastMCP`, `uv run`, and PEP 723 inline script metadata. This keeps dependencies isolated to the MCP script instead of the main project environment.

## Process

### 1. Gather requirements

Ask for:
1. **Server name** — short kebab-case name such as `paper-search`
2. **Purpose** — what the MCP should help with
3. **Tools** — the tool names and what each one should do
4. **Dependencies** — required Python packages beyond `mcp`

### 2. Create the MCP script

Create a script at:

```text
.github/mcps/<normalized_server_name>_mcp.py
```

Normalize the script stem before creating the file:
- convert hyphens to underscores
- if the name already ends in `_mcp`, strip that suffix before appending `_mcp.py`

Examples:
- `paper-search` -> `.github/mcps/paper_search_mcp.py`
- `sample-mcp` -> `.github/mcps/sample_mcp.py`

Use this template and adjust it to the requested tools:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "mcp[cli]>=1.0.0",
# ]
# ///
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Server Name")


@mcp.tool()
def example_tool(query: str) -> str:
    """Describe exactly what the tool does."""
    return f"TODO: implement {query}"


if __name__ == "__main__":
    mcp.run()
```

Add any extra dependencies to the inline metadata block.

### 3. Register the MCP in `.github/.mcp.json`

Add an entry like:

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "uv",
      "args": [
        "run",
        "mcps/<normalized_server_name>_mcp.py"
      ]
    }
  }
}
```

Preserve existing MCP entries.

### 4. Verify the MCP

Run at least one of these checks:

```bash
copilot mcp get <server-name>
```

```bash
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | uv run .github/mcps/<normalized_server_name>_mcp.py
```

Then start a new Copilot session and confirm the MCP is actually used, not just listed. Do not claim it works until you have seen a tool invocation from that MCP.

## Guidelines

- Prefer explicit, narrow tool names and descriptions.
- Keep errors actionable and specific.
- Use inline script metadata for MCP-only dependencies.
- Do not add MCP dependencies to the main `pyproject.toml` unless the user explicitly wants shared project dependencies.
