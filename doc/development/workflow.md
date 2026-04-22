# Development Workflow

## Repository Structure

```
ableton-mcp/
├── MCP_Server/                     # MCP Server (Python package)
│   ├── __init__.py
│   └── server.py                  # Main server implementation
├── AbletonMCP_Remote_Script/       # Ableton Remote Script
│   └── __init__.py               # Remote Script implementation
├── doc/                         # Documentation
│   ├── explore/                # Analysis documents
│   ├── architecture/          # Architecture docs
│   ├── features/              # Feature docs
│   ├── api/                 # API docs
│   ├── setup/                # Setup docs
│   └── development/          # Development docs
├── pyproject.toml                 # Python project config
├── Dockerfile                     # Container definition
└── uv.lock                        # Dependency lock file
```

---

## Development Setup

### 1. Clone and Install

```bash
git clone https://github.com/ahujasid/ableton-mcp.git
cd ableton-mcp
uv sync
```

### 2. Run MCP Server Locally

```bash
python -m MCP_Server.server
```

Or with uv:

```bash
uv run ableton-mcp
```

### 3. Test with Ableton

1. Start Ableton Live with the Remote Script loaded
2. Run the MCP Server
3. Connect Claude Desktop or Cursor to the MCP Server
4. Test basic commands

---

## Code Organization

### MCP Server (`MCP_Server/server.py`)

| Section | Lines | Purpose |
|---------|-------|---------|
| Imports and logging | 1-13 | Dependencies |
| `AbletonConnection` class | 15-162 | Socket communication |
| Lifespan manager | 164-184 | Server lifecycle |
| Connection management | 192-255 | Connection pooling |
| Tool decorators | 257-652 | MCP endpoints |

### Remote Script (`AbletonMCP_Remote_Script/__init__.py`)

| Section | Lines | Purpose |
|---------|-------|---------|
| Imports and constants | 1-19 | Dependencies |
| `AbletonMCP` class | 25-132 | Main controller |
| Server thread | 93-131 | Socket server |
| Client handler | 133-208 | Command processing |
| Command router | 210-338 | Command dispatch |
| Command handlers | 340-638 | Implementation |
| Browser methods | 640-1062 | Browser navigation |

---

## Adding New Commands

### 1. Add to Remote Script

In `AbletonMCP_Remote_Script/__init__.py`:

```python
def _new_command_handler(self, param1, param2):
    """Handle new command"""
    # Implementation
    return {"result_key": "value"}
```

Add to `_process_command()` routing:

```python
elif command_type == "new_command":
    param1 = params.get("param1")
    param2 = params.get("param2")
    response["result"] = self._new_command_handler(param1, param2)
```

### 2. Add to MCP Server

In `MCP_Server/server.py`:

```python
@mcp.tool()
def new_command(ctx: Context, param1: str, param2: int) -> str:
    """Description"""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("new_command", {
            "param1": param1,
            "param2": param2
        })
        return f"Result: {result}"
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"
```

---

## Logging

### MCP Server Logging

Log level and format configured at `server.py:11-12`:

```python
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
```

### Remote Script Logging

Uses Ableton's built-in logging:

```python
self.log_message("Message")  # Ableton log
self.show_message("Message")  # Ableton status bar
```

---

## Code Style

- Use `__future__` imports for Python 2/3 compatibility in Remote Script
- Use dataclass for connection management in MCP Server
- Follow existing docstring format
- Use type hints where applicable