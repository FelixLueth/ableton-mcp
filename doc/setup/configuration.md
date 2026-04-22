# Configuration

## Overview

AbletonMCP uses minimal configuration with most parameters hardcoded.

## Runtime Configuration

### Network Settings

| Parameter | Default | Location |
|-----------|---------|----------|
| Host | localhost | Remote Script: line 19 |
| Port | 9877 | Remote Script: line 18 |

To modify these values, edit the constants in:

**File:** `AbletonMCP_Remote_Script/__init__.py`

```python
DEFAULT_PORT = 9877
HOST = "localhost"
```

### Socket Timeouts

| Parameter | Default | Description |
|-----------|---------|-------------|
| Default timeout | 10 seconds | Used for read operations |
| Modifying timeout | 15 seconds | Used for state-modifying operations |
| Chunked receive | 15 seconds | For multi-chunk responses |

To modify timeouts, edit values in:

**File:** `MCP_Server/server.py`

```python
# Line 49
sock.settimeout(15.0)

# Line 124
timeout = 15.0 if is_modifying_command else 10.0
```

---

## Claude Desktop Configuration

### Basic Configuration

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "uvx",
      "args": ["ableton-mcp"]
    }
  }
}
```

### Custom Python Path

To use a specific Python installation:

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "/path/to/python",
      "args": ["-m", "MCP_Server.server"]
    }
  }
}
```

### Development Mode

For local development with live reloading:

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "python",
      "args": ["-m", "MCP_Server.server"]
    }
  }
}
```

---

## Environment Variables

Currently, no environment variables are used by AbletonMCP.

---

## MCP Server Configuration

### Via pyproject.toml

The MCP Server is defined as a console script in `pyproject.toml`:

```toml
[project.scripts]
ableton-mcp = "MCP_Server.server:main"
```

### Via Docker

The `Dockerfile` provides a containerized deployment:

```dockerfile
CMD ["python", "-m", "MCP_Server.server"]
```

---

## Connection Management

### Retry Configuration

The MCP Server attempts to connect to Ableton up to 3 times on startup:

**File:** `MCP_Server/server.py` lines 217-253

```python
max_attempts = 3
for attempt in range(1, max_attempts + 1):
    # Connection attempt logic
```

### Delay Between Retries

```python
time.sleep(1.0)  # 1 second between attempts
```

### State-Modifying Command Delays

Small delays are added for state-modifying commands to ensure Ableton has time to process:

```python
time.sleep(0.1)  # 100ms before and after commands
```

---

## Ableton Live Configuration

### Required Settings

1. **Control Surface:** Select "AbletonMCP"
2. **Input:** Set to "None"
3. **Output:** Set to "None"

### MIDI Remote Scripts Location

| OS | Path |
|----|------|
| macOS | `~/Library/Preferences/Ableton/Live XX/User Remote Scripts/` |
| Windows | `C:\Users\[Username]\AppData\Roaming\Ableton\Live x.x.x\Preferences\User Remote Scripts` |

Replace `XX` or `x.x.x` with your Ableton version number.