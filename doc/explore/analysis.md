# Repository Exploration Analysis

**Repository:** `ableton-mcp` - Ableton Live Model Context Protocol Integration
**Analysis Date:** 2026-04-22

---

## 1. Architecture Overview

### System Type
The repository implements a **client-server architecture** with two primary components:

1. **MCP Server** - Acts as an intermediary between AI clients (Claude Desktop, Cursor) and Ableton Live
2. **Ableton Remote Script** - A MIDI Remote Script that runs inside Ableton Live, exposing its functionality via TCP sockets

### Communication Pattern
- **Protocol:** JSON-based command/response over TCP sockets
- **Port:** 9877 (hardcoded in Remote Script)
- **Connection Initiation:** MCP Server connects to Remote Script (not vice versa)
- **Transport:** Synchronous request-response with timeout handling (10-15 seconds)

### Architecture Diagram

```
┌─────────────────┐     MCP Protocol      ┌─────────────────┐
│  Claude Desktop │  ◄──────────────────►  │   MCP Server   │
│  (or Cursor)    │   (stdio/stdin-out)    │  (Python 3.10+) │
└─────────────────┘                        └────────┬────────┘
                                                     │
                                             TCP Socket (9877)
                                                     │
                                              ┌──────▼───────┐
                                              │ Ableton Live │
                                              │ Remote Script│
                                              │   (Python)   │
                                              └──────────────┘
```

---

## 2. Directory Structure

```
ableton-mcp/
├── .git/                          # Git repository
├── .python-version                # Python 3.13
├── README.md                      # Project README
├── pyproject.toml                 # Python project configuration
├── Dockerfile                      # Container definition (Smithery)
├── smithery.yaml                   # Smithery MCP configuration
├── LICENSE                         # MIT License
├── MCP_Server/                     # MCP Server implementation
│   ├── __init__.py
│   └── server.py                  # Main MCP server (660 lines)
└── AbletonMCP_Remote_Script/       # Ableton Live MIDI Remote Script
    └── __init__.py                 # Remote Script implementation (1062 lines)
```

---

## 3. Tech Stack

### Languages
- **Python:** Primary language for both MCP Server and Remote Script
  - MCP Server: Python 3.10+ (declared in pyproject.toml)
  - Remote Script: Python 2/3 compatible (uses `__future__` imports, try/except for Queue)

### Frameworks and Libraries
| Library | Purpose | Version |
|---------|---------|---------|
| `mcp[cli]` | Model Context Protocol implementation | >= 1.3.0 |
| `fastmcp` | FastMCP server framework | (via mcp) |
| `_Framework` (Ableton) | Ableton Live Python framework | Built-in |

### Build Tools
- **setuptools** - Package build backend
- **uv** - Package manager (referenced in README)

### Deployment
- **Docker** - Python 3.10-alpine base image
- **Smithery** - MCP server hosting platform

---

## 4. Entry Points and Main Execution Flows

### MCP Server Entry Point
**File:** `MCP_Server/server.py:655-660`

```python
def main():
    """Run the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()
```

The server is exposed as:
- **Console script:** `ableton-mcp` (via pyproject.toml)
- **Module:** `python -m MCP_Server.server`

### Remote Script Entry Point
**File:** `AbletonMCP_Remote_Script/__init__.py:21-23`

```python
def create_instance(c_instance):
    """Create and return the AbletonMCP script instance"""
    return AbletonMCP(c_instance)
```

This follows Ableton's standard Remote Script plugin pattern.

### Execution Flow

1. **Server Startup:**
   - MCP Server starts via `mcp.run()` (FastMCP stdio mode)
   - Lifespan manager attempts connection to Ableton on port 9877
   - Connection validated with `get_session_info` command

2. **Client Request Flow:**
   - Claude/Cursor sends request via MCP protocol
   - MCP Server receives via stdio
   - Server sends JSON command via TCP socket to Remote Script
   - Remote Script processes command on Ableton's main thread (via `schedule_message`)
   - Response sent back via TCP socket
   - MCP Server formats and returns to client

---

## 5. Feature Inventory

### Implemented Features

| Feature | Command | Implementation Location |
|---------|---------|------------------------|
| Session Info | `get_session_info` | server.py:260-269 |
| Track Info | `get_track_info` | server.py:271-285 |
| Create MIDI Track | `create_midi_track` | server.py:287-301 |
| Set Track Name | `set_track_name` | server.py:304-319 |
| Create Clip | `create_clip` | server.py:321-341 |
| Add Notes to Clip | `add_notes_to_clip` | server.py:343-368 |
| Set Clip Name | `set_clip_name` | server.py:370-390 |
| Set Tempo | `set_tempo` | server.py:392-406 |
| Load Instrument/Effect | `load_instrument_or_effect` | server.py:408-437 |
| Fire Clip | `fire_clip` | server.py:439-457 |
| Stop Clip | `stop_clip` | server.py:459-477 |
| Start Playback | `start_playback` | server.py:479-488 |
| Stop Playback | `stop_playback` | server.py:490-499 |
| Get Browser Tree | `get_browser_tree` | server.py:501-562 |
| Get Browser Items at Path | `get_browser_items_at_path` | server.py:564-603 |
| Load Drum Kit | `load_drum_kit` | server.py:605-652 |

### Remote Script Command Handlers

| Handler | Command Types | Location |
|---------|--------------|----------|
| `_get_session_info` | Session metadata | line 342-360 |
| `_get_track_info` | Track details | line 362-415 |
| `_create_midi_track` | Track creation | line 417-434 |
| `_set_track_name` | Track naming | line 437-453 |
| `_create_clip` | Clip creation | line 455-482 |
| `_add_notes_to_clip` | MIDI note input | line 484-522 |
| `_set_clip_name` | Clip naming | line 524-549 |
| `_set_tempo` | Tempo control | line 551-562 |
| `_fire_clip` | Clip triggering | line 564-588 |
| `_stop_clip` | Clip stopping | line 590-611 |
| `_start_playback` | Transport start | line 614-625 |
| `_stop_playback` | Transport stop | line 627-638 |
| `_load_browser_item` | Device loading | line 726-759 |
| `get_browser_tree` | Browser navigation | line 823-937 |
| `get_browser_items_at_path` | Browser lookup | line 939-1062 |

---

## 6. Key Modules and Responsibilities

### MCP_Server/server.py

| Component | Responsibility |
|-----------|---------------|
| `AbletonConnection` class | TCP socket connection management, command sending, response receiving |
| `server_lifespan()` | Server lifecycle management (startup/shutdown connection handling) |
| `get_ableton_connection()` | Connection pooling and retry logic (3 attempts) |
| `@mcp.tool()` decorated functions | 16 MCP tool endpoints exposing Ableton functionality |

### AbletonMCP_Remote_Script/__init__.py

| Component | Responsibility |
|-----------|---------------|
| `AbletonMCP` class | Main Remote Script controller |
| `start_server()` | TCP server initialization on port 9877 |
| `_server_thread()` | Client connection accept loop |
| `_handle_client()` | Single client command processing |
| `_process_command()` | Command routing to handlers |
| Helper methods | Browser navigation, device type detection |

---

## 7. Data Flow and Control Flow

### Command Protocol

**Request Format:**
```json
{
  "type": "<command_type>",
  "params": { /* command-specific parameters */ }
}
```

**Response Format:**
```json
{
  "status": "success" | "error",
  "result": { /* result data */ },
  "message": "optional error message"
}
```

### Control Flow for State-Modifying Commands

1. MCP Server marks command as "modifying" (line 104-109 in server.py)
2. Small delay (100ms) before sending
3. Increased timeout (15s vs 10s)
4. Small delay after receiving response

### Thread Safety

The Remote Script uses Ableton's `schedule_message()` to execute state-modifying commands on the main thread, with a `queue.Queue` for thread-safe response retrieval.

---

## 8. External Dependencies and Integrations

### External Systems

| System | Integration Type | Details |
|--------|-----------------|---------|
| **Ableton Live** | via Remote Script API | Access to `Song`, `Track`, `Clip`, `Device`, `Browser` objects |
| **Claude Desktop** | MCP Protocol | Tool invocations via stdio |
| **Cursor** | MCP Protocol | Alternative MCP client |
| **Smithery** | Deployment | Cloud MCP hosting |

### Python Dependencies

```
mcp[cli]>=1.3.0
```

### Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python project metadata, dependencies, entry points |
| `Dockerfile` | Container build for Smithery deployment |
| `smithery.yaml` | Smithery MCP server configuration |

---

## 9. Testing Strategy

**Observation:** No test files were found in the repository. There is no `tests/` directory or test-related configuration in `pyproject.toml`.

---

## 10. Configuration Patterns

### Environment Configuration
- No `.env` file or environment variable handling
- All configuration is hardcoded:
  - TCP port: 9877
  - Host: localhost
  - Socket timeouts: 10-15 seconds

### Remote Script Configuration
- **No external configuration file**
- All parameters are Python constants at module level
- Port and host defined at lines 17-19 in `__init__.py`

---

## 11. Observations

### Gaps and Risks

1. **No Authentication:** The TCP socket connection has no authentication. Any local process can connect to port 9877.

2. **No Encryption:** All communication is in plaintext JSON over TCP.

3. **Hardcoded Configuration:** Port and host are hardcoded; no environment-based configuration.

4. **No Connection Health Monitoring:** The connection validation (line 201-206 in server.py) uses an empty send which may not reliably detect dead connections.

5. **Python 2/3 Compatibility:** The Remote Script maintains Python 2 compatibility (Queue vs queue, string/bytes handling), adding complexity.

6. **No Error Recovery for Partial Failures:** If a response is partially received, the code may not clean up properly.

7. **Browser Availability Assumption:** Browser-related commands assume Ableton's browser is fully loaded; no robust fallback.

### Inconsistencies

1. **Command Naming Mismatch:** Server uses `load_instrument_or_effect` (line 408) but Remote Script handles both `load_instrument_or_effect` and `load_browser_item` (lines 277-284).

2. **Python Version Mismatch:** `.python-version` specifies Python 3.13, but `pyproject.toml` requires >=3.10, and Dockerfile uses 3.10-alpine.

3. **Drum Kit Helper:** The `load_drum_kit` function (server.py:605-652) implements multi-step logic but is not exposed as a separate Remote Script command—it's composed of existing commands.

### Potential Improvements (Not Recommendations)

- Add configuration file support
- Implement connection encryption
- Add authentication
- Comprehensive test coverage
- Structured logging with correlation IDs
- Health check endpoint
- Async/await refactoring

---

## Summary

This is a **specialized integration project** connecting AI assistants to Ableton Live via the Model Context Protocol. It consists of two well-defined components:

1. **MCP Server** - Thin shim translating MCP protocol to TCP socket commands
2. **Remote Script** - Ableton Live plugin exposing DAW functionality via TCP

The implementation is **feature-complete for its scope** with 16 tool endpoints covering session management, track/clip manipulation, transport control, and browser navigation. The codebase is **straightforward and readable** but lacks production-grade features like testing, configuration management, and security controls.
