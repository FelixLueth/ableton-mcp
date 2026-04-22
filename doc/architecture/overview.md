# Architecture Overview

## System Design

AbletonMCP implements a **client-server architecture** with two primary components:

1. **MCP Server** - Acts as intermediary between AI clients and Ableton Live
2. **Ableton Remote Script** - Plugin that runs inside Ableton Live

## Communication Flow

```
┌─────────────────┐      MCP Protocol       ┌─────────────────┐
│ Claude Desktop  │  ◄──────────────────►  │   MCP Server   │
│ (or Cursor)     │    (stdio/stdio)      │  (Python)      │
└─────────────────┘                      └───────┬─────────┘
                                                   │
                                           TCP Socket (9877)
                                                   │
                                            ┌──────▼──────┐
                                            │ Ableton Live │
                                            │ Remote Script│
                                            └─────────────┘
```

## Component Responsibilities

### MCP Server (`MCP_Server/server.py`)

- Listens for MCP protocol requests via stdio
- Manages TCP socket connection to Remote Script
- Translates MCP tool invocations to Ableton commands
- Handles connection pooling and retry logic
- Formats and returns responses to AI clients

### Remote Script (`AbletonMCP_Remote_Script/__init__.py`)

- Hosts TCP socket server on port 9877
- Receives and validates commands
- Executes commands on Ableton's main thread (via `schedule_message`)
- Returns structured JSON responses
- Provides browser navigation and device loading

## Key Design Decisions

### Socket-Based Communication

The Remote Script hosts a TCP server rather than the MCP Server doing so. This design allows:

- Single connection from MCP Server to Ableton
- Ableton controls port availability
- Firewall-friendly configuration (localhost only)

### Synchronous Request-Response

All commands use synchronous request-response with timeouts:

- Read operations: 10 second timeout
- State-modifying operations: 15 second timeout
- 100ms delays before/after state modifications

### Thread-Safe Command Execution

State-modifying commands are scheduled on Ableton's main thread using `schedule_message()` with a response queue for thread-safe result retrieval.

## Architecture Layers

| Layer | Component | Protocol |
|-------|----------|----------|
| AI Client | Claude Desktop / Cursor | MCP (JSON-RPC) |
| Integration | MCP Server | stdio |
| Transport | TCP Socket | JSON |
| Abstraction | Remote Script | Ableton API |
| Platform | Ableton Live | Internal |

## Constraints and Requirements

- Both components must run on the same machine
- Remote Script must be loaded in Ableton Live
- Port 9877 must be available
- Ableton Live must be running when MCP Server connects