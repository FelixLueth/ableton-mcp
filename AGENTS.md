# AGENTS.md

## Project Overview

AbletonMCP connects AI assistants (via MCP) to Ableton Live. The system operates as ONE integrated pipeline:

```
LLM (MCP Client) → MCP Server (Python) → TCP (port 9877) → Ableton Remote Script → Ableton Live
```

Treat all layers as a single system. Changes in one layer affect the entire flow.

---

## Architecture Summary

| Layer | Component | File | Protocol |
|-------|-----------|------|----------|
| AI Client | Claude/Cursor/Opencode | External | MCP (JSON-RPC) |
| Integration | MCP Server | `MCP_Server/server.py` | stdio |
| Transport | TCP Socket | `MCP_Server/connection.py` | JSON (port 9877) |
| Execution | Remote Script | `AbletonMCP_Remote_Script/__init__.py` | Ableton API |
| Platform | Ableton Live | Internal | Live API |

### Tool Domains

MCP tools are grouped by domain:

- **session**: `get_session_info`, `set_tempo`
- **tracks**: `get_track_info`, `create_midi_track`, `set_track_name`
- **clips**: `create_clip`, `add_notes_to_clip`, `set_clip_name`, `fire_clip`, `stop_clip`
- **transport**: `start_playback`, `stop_playback`
- **browser**: `get_browser_tree`, `get_browser_items_at_path`, `load_instrument_or_effect`, `load_drum_kit`

---

## Core Principles

1. **Never break existing MCP tools** - Changing a tool signature affects every AI client using it
2. **Never change public tool interfaces without strong reason** - Backward compatibility matters
3. **Prefer incremental changes** - Small, focused changes over large rewrites
4. **Avoid demo or mock logic** - Production behavior only unless explicitly requested
5. **Think end-to-end** - Every change must work through the full pipeline
6. **Maintain production-like behavior** - Even in early stages of development

---

## Workflow for Agents

### Step 1: Understand the Request

Identify what the user wants. Map it to a tool domain (session, tracks, clips, transport, browser).

### Step 2: Identify Affected Layer(s)

Determine which component(s) need changes:

| If the task is about... | Then modify... |
|------------------------|----------------|
| Tool parameters, CLI | MCP Server (`server.py`) |
| TCP communication | `connection.py` |
| Command execution inside Ableton | Remote Script (`__init__.py`) |

### Step 3: Minimize Changes

- Change only what is necessary
- Do not refactor unrelated code
- Avoid touching multiple layers unless the request explicitly requires it

### Step 4: Validate the Flow

After changes, verify:
1. MCP Server starts without errors
2. TCP connection establishes
3. Commands execute correctly in Ableton

---

## Adding New Commands

### 1. Add to Remote Script

In `AbletonMCP_Remote_Script/__init__.py`:

```python
def _new_command_handler(self, param1, param2):
    return {"result_key": value}

# Add routing in _process_command()
elif command_type == "new_command":
    response["result"] = self._new_command_handler(param1, param2)
```

### 2. Add to MCP Server

In `MCP_Server/server.py`:

```python
@mcp.tool()
def new_command(ctx: Context, param1: str, param2: int) -> str:
    """Description of what the tool does."""
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

### 3. Document the Tool

Add docstring with:
- Purpose
- Input parameters
- Output example
- Limitations

---

## Error Handling Rules

### MCP Server

- Never crash on errors
- Return structured JSON errors
- Distinguish between:
  - **Connection errors** (Ableton not running, port unavailable)
  - **Execution errors** (command failed, invalid parameters)
  - **Timeout errors** (command taking too long)

### Error Response Format

```json
{
  "error": "error_code",
  "message": "Human-readable message",
  "hint": "Suggested action"
}
```

### Common Error Codes

| Error Code | Meaning | Resolution |
|------------|---------|-------------|
| `ableton_not_running` | Cannot connect to Ableton | Ensure Ableton is running with Remote Script loaded |
| `timeout` | Command timed out | Try again or restart Ableton |
| `port_unavailable` | Port 9877 in use | Kill process using the port |
| `invalid_track_index` | Track index out of range | Use valid track index |
| `no_clip` | Clip slot is empty | Create clip first |

---

## Testing Strategy

### Unit Tests

- Run without Ableton installed
- Use mocked TCP communication (`tests/mock_ableton.py`)
- Focus on MCP Server behavior

```bash
python -m unittest discover -s tests -v
```

### Integration Tests

- Require Ableton running with Remote Script loaded
- Test full end-to-end flow
- Perform manually during development

### Testing Constraints

- **No Ableton in CI** - Tests must pass without Ableton
- **OS-agnostic** - No hardcoded paths (macOS/Windows/Linux)
- **Fast execution** - Keep tests lightweight

---

## Feature Development Priority

When adding new tools, prioritize:

1. **Introspection** (read-only tools) - Get session info, track info, browser browsing
2. **Stability** - Error handling, connection recovery
3. **Deterministic creation** - Create track, create clip, set tempo
4. **Advanced features** - Browser presets, device loading

### Guidelines

- Return structured JSON
- Keep responses compact
- Avoid large payloads in first iteration
- Extend incrementally

---

## Operating System Constraints

- **OS-agnostic** - Project must work on macOS, Windows, Linux
- **No hardcoded paths** - Use relative paths or environment variables
- **Document OS-specific differences** - When needed (e.g., Remote Script path)

---

## What Agents Must NOT Do

- **Do not rewrite large parts** - Avoid unnecessary refactoring
- **Do not break existing tools** - Backward compatibility is critical
- **Do not add heavy dependencies** - Keep the project lightweight
- **Do not assume Ableton in CI** - Tests must run without Ableton
- **Do not introduce hidden behavior** - All behavior must be explicit and documented
- **Do not create demo logic** - Production behavior only

---

## Code Style

- Use type hints where applicable
- Follow existing docstring format
- Keep functions focused (single responsibility)
- Group related tools by domain
- Use dataclasses for structured data

---

## Documentation Requirements

- All new tools must be documented (docstring)
- Include: purpose, input, output example, limitations
- Keep code in English
- Update relevant docs in `doc/` when adding major features

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `MCP_Server/server.py` | MCP tools and error handling |
| `MCP_Server/connection.py` | TCP socket communication |
| `MCP_Server/*_helpers.py` | Helper functions by domain |
| `AbletonMCP_Remote_Script/__init__.py` | Remote Script command execution |
| `doc/api/contracts.md` | Tool input/output contracts |
| `doc/development/testing.md` | Testing documentation |

---

## Communication Paths

### MCP → Remote Script

Commands sent via TCP to port 9877:

```json
{
  "type": "command_name",
  "params": {"param1": "value1"}
}
```

Response:

```json
{
  "status": "success",
  "result": {...}
}
```

### Must Not Break

- Tool decorator signatures in `server.py`
- Command routing in Remote Script `_process_command()`
- TCP message format in `connection.py`

Any change to these interfaces requires careful consideration and testing.