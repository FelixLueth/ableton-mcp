# Track Management

## Overview

Track management features enable creation, modification, and querying of MIDI and audio tracks in Ableton Live.

## Features

### Get Track Information

Retrieves detailed information about a specific track.

**MCP Tool:** `get_track_info`

**Implementation:** `MCP_Server/server.py:271-285`

**Command:** `get_track_info`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `track_index` | int | Index of the track (0-based) |

**Response:**
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
  "clip_slots": [
    {
      "index": 0,
      "has_clip": true,
      "clip": {
        "name": "Drums 1",
        "length": 4.0,
        "is_playing": false,
        "is_recording": false
      }
    }
  ],
  "devices": [
    {
      "index": 0,
      "name": "Drum Rack",
      "class_name": "DrumGroupDevice",
      "type": "rack"
    }
  ]
}
```

### Create MIDI Track

Creates a new MIDI track in the session.

**MCP Tool:** `create_midi_track`

**Implementation:** `MCP_Server/server.py:287-301`

**Command:** `create_midi_track`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `index` | int | Insert position (-1 for end of list) |

**Response:**
```json
{
  "index": 4,
  "name": "MIDI Track 4"
}
```

### Set Track Name

Renames an existing track.

**MCP Tool:** `set_track_name`

**Implementation:** `MCP_Server/server.py:304-319`

**Command:** `set_track_name`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `track_index` | int | Index of the track to rename |
| `name` | str | New name for the track |

**Response:**
```json
{
  "name": "Synth Lead"
}
```

---

## Remote Script Handlers

**File:** `AbletonMCP_Remote_Script/__init__.py`

### `_get_track_info()`

Location: lines 362-415

Collects:
- Track name
- Track type (audio/MIDI)
- Mute, solo, arm states
- Volume and panning
- Clip slots with clip metadata
- Devices with type classification

### `_create_midi_track()`

Location: lines 417-434

Creates track via `self._song.create_midi_track(index)`

### `_set_track_name()`

Location: lines 437-453

Sets `track.name` directly

---

## Usage Examples

### Get Track Info

```
Get information about track 0
```

### Create MIDI Track

```
Create a new MIDI track
```

### Rename Track

```
Rename track 2 to "Synth Lead"
```