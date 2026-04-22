# API Contracts

## Communication Protocol

The MCP Server communicates with the Ableton Remote Script using a JSON-based protocol over TCP sockets.

## Request Format

All requests follow this structure:

```json
{
  "type": "<command_type>",
  "params": { }
}
```

### Command Types

| Command | Required Parameters |
|---------|---------------------|
| `get_session_info` | None |
| `get_track_info` | `track_index` |
| `create_midi_track` | `index` |
| `set_track_name` | `track_index`, `name` |
| `create_clip` | `track_index`, `clip_index`, `length` |
| `add_notes_to_clip` | `track_index`, `clip_index`, `notes` |
| `set_clip_name` | `track_index`, `clip_index`, `name` |
| `set_tempo` | `tempo` |
| `fire_clip` | `track_index`, `clip_index` |
| `stop_clip` | `track_index`, `clip_index` |
| `start_playback` | None |
| `stop_playback` | None |
| `load_browser_item` | `track_index`, `item_uri` |
| `get_browser_tree` | `category_type` |
| `get_browser_items_at_path` | `path` |

---

## Response Format

### Success Response

```json
{
  "status": "success",
  "result": {
    "key": "value"
  }
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Error description"
}
```

---

## Data Types

### Note Object

```json
{
  "pitch": 60,
  "start_time": 0.0,
  "duration": 0.25,
  "velocity": 100,
  "mute": false
}
```

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `pitch` | integer | 0-127 | MIDI note number |
| `start_time` | float | 0.0+ | Start time in beats |
| `duration` | float | 0.0+ | Duration in beats |
| `velocity` | integer | 0-127 | Note velocity |
| `mute` | boolean | - | Muted state |

### Track Info Object

```json
{
  "index": 0,
  "name": "Drums",
  "is_audio_track": false,
  "is_midi_track": true,
  "mute": false,
  "solo": false,
  "arm": false,
  "volume": 0.0,
  "panning": 0.0,
  "clip_slots": [ ],
  "devices": [ ]
}
```

### Clip Slot Object

```json
{
  "index": 0,
  "has_clip": true,
  "clip": {
    "name": "Clip 1",
    "length": 4.0,
    "is_playing": false,
    "is_recording": false
  }
}
```

### Device Object

```json
{
  "index": 0,
  "name": "Drum Rack",
  "class_name": "DrumGroupDevice",
  "type": "rack"
}
```

### Browser Item Object

```json
{
  "name": "Analog",
  "is_folder": false,
  "is_device": true,
  "is_loadable": true,
  "uri": "instruments:synths:analog"
}
```

---

## Socket Configuration

| Setting | Value |
|---------|-------|
| Host | localhost |
| Port | 9877 |
| Protocol | TCP |
| Encoding | UTF-8 |
| Read Timeout | 10s (default), 15s (state-modifying) |

---

## Connection Flow

1. MCP Server initiates TCP connection to `localhost:9877`
2. Connection validated with `get_session_info` command
3. Commands sent as JSON strings with newline delimiters
4. Responses received as JSON strings
5. Connection maintained for duration of session
6. Disconnect on MCP Server shutdown