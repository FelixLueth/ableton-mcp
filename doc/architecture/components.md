# Components

## MCP Server

**File:** `MCP_Server/server.py`
**Entry Point:** `MCP_Server.server:main()`

### Core Classes

#### `AbletonConnection`

Manages the TCP socket connection to Ableton Live.

| Method | Purpose |
|--------|---------|
| `connect()` | Establish socket connection |
| `disconnect()` | Close socket connection |
| `send_command()` | Send command and receive response |
| `receive_full_response()` | Handle chunked response reception |

#### `mcp` (FastMCP instance)

The main MCP server instance with lifespan management.

### Tool Endpoints

16 MCP tool decorators exposing Ableton functionality:

| Tool | Purpose | Location |
|------|---------|---------|
| `get_session_info` | Session metadata | line 260 |
| `get_track_info` | Track details | line 272 |
| `create_midi_track` | Track creation | line 288 |
| `set_track_name` | Track naming | line 305 |
| `create_clip` | Clip creation | line 322 |
| `add_notes_to_clip` | MIDI note input | line 344 |
| `set_clip_name` | Clip naming | line 371 |
| `set_tempo` | Tempo control | line 393 |
| `load_instrument_or_effect` | Device loading | line 410 |
| `fire_clip` | Clip triggering | line 440 |
| `stop_clip` | Clip stopping | line 460 |
| `start_playback` | Transport start | line 480 |
| `stop_playback` | Transport stop | line 491 |
| `get_browser_tree` | Browser categories | line 502 |
| `get_browser_items_at_path` | Browser lookup | line 565 |
| `load_drum_kit` | Drum kit loading | line 606 |

---

## Remote Script

**File:** `AbletonMCP_Remote_Script/__init__.py`
**Entry Point:** `create_instance(c_instance)`

### Main Class

#### `AbletonMCP(ControlSurface)`

Extends Ableton's `ControlSurface` class.

| Method | Purpose |
|--------|---------|
| `start_server()` | Initialize TCP server on port 9877 |
| `_server_thread()` | Accept client connections |
| `_handle_client()` | Process client commands |
| `_process_command()` | Route commands to handlers |

### Command Handlers

| Handler | Commands | Location |
|---------|----------|---------|
| `_get_session_info` | `get_session_info` | line 342 |
| `_get_track_info` | `get_track_info` | line 362 |
| `_create_midi_track` | `create_midi_track` | line 417 |
| `_set_track_name` | `set_track_name` | line 437 |
| `_create_clip` | `create_clip` | line 455 |
| `_add_notes_to_clip` | `add_notes_to_clip` | line 484 |
| `_set_clip_name` | `set_clip_name` | line 524 |
| `_set_tempo` | `set_tempo` | line 551 |
| `_fire_clip` | `fire_clip` | line 564 |
| `_stop_clip` | `stop_clip` | line 590 |
| `_start_playback` | `start_playback` | line 614 |
| `_stop_playback` | `stop_playback` | line 627 |
| `_load_browser_item` | `load_instrument_or_effect`, `load_browser_item` | line 726 |
| `get_browser_tree` | `get_browser_tree` | line 823 |
| `get_browser_items_at_path` | `get_browser_items_at_path` | line 939 |

### Internal Methods

| Method | Purpose |
|--------|---------|
| `_get_device_type()` | Classify device type |
| `_find_browser_item_by_uri()` | Recursive URI lookup |
| `_get_session_info()` | Session metadata extraction |
| `_get_track_info()` | Track details extraction |