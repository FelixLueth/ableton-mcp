# Clip Management

## Overview

Clip management features enable creation, modification, triggering, and naming of MIDI clips in Ableton Live.

## Features

### Create Clip

Creates a new MIDI clip in a specified track and clip slot.

**MCP Tool:** `create_clip`

**Implementation:** `MCP_Server/server.py:321-341`

**Command:** `create_clip`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `track_index` | int | Target track index |
| `clip_index` | int | Clip slot index |
| `length` | float | Length in beats (default: 4.0) |

**Response:**
```json
{
  "name": "MIDI Clip",
  "length": 4.0
}
```

### Add Notes to Clip

Adds MIDI notes to an existing clip.

**MCP Tool:** `add_notes_to_clip`

**Implementation:** `MCP_Server/server.py:343-368`

**Command:** `add_notes_to_clip`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `track_index` | int | Track containing the clip |
| `clip_index` | int | Clip slot containing the clip |
| `notes` | List[Dict] | List of note dictionaries |

**Note Format:**
```json
{
  "pitch": 60,
  "start_time": 0.0,
  "duration": 0.25,
  "velocity": 100,
  "mute": false
}
```

| Field | Type | Description | Range |
|-------|------|-------------|-------|
| `pitch` | int | MIDI note number | 0-127 |
| `start_time` | float | Start time in beats | 0.0+ |
| `duration` | float | Note duration in beats | 0.0+ |
| `velocity` | int | Note velocity | 0-127 |
| `mute` | bool | Muted state | - |

**Response:**
```json
{
  "note_count": 8
}
```

### Set Clip Name

Renames an existing clip.

**MCP Tool:** `set_clip_name`

**Implementation:** `MCP_Server/server.py:370-390`

**Command:** `set_clip_name`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `track_index` | int | Track containing the clip |
| `clip_index` | int | Clip slot containing the clip |
| `name` | str | New clip name |

**Response:**
```json
{
  "name": "Intro Melody"
}
```

### Fire Clip

Starts playing a clip.

**MCP Tool:** `fire_clip`

**Implementation:** `MCP_Server/server.py:439-457`

**Command:** `fire_clip`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `track_index` | int | Track containing the clip |
| `clip_index` | int | Clip slot containing the clip |

**Response:**
```json
{
  "fired": true
}
```

### Stop Clip

Stops a playing clip.

**MCP Tool:** `stop_clip`

**Implementation:** `MCP_Server/server.py:459-477`

**Command:** `stop_clip`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `track_index` | int | Track containing the clip |
| `clip_index` | int | Clip slot containing the clip |

**Response:**
```json
{
  "stopped": true
}
```

---

## Remote Script Handlers

**File:** `AbletonMCP_Remote_Script/__init__.py`

### `_create_clip()`

Location: lines 455-482

Creates clip via `clip_slot.create_clip(length)`

### `_add_notes_to_clip()`

Location: lines 484-522

Converts note data to Ableton format and calls `clip.set_notes()`

### `_set_clip_name()`

Location: lines 524-549

Sets `clip.name` directly

### `_fire_clip()`

Location: lines 564-588

Calls `clip_slot.fire()`

### `_stop_clip()`

Location: lines 590-611

Calls `clip_slot.stop()`

---

## Usage Examples

### Create Clip

```
Create a 4-bar MIDI clip at track 0, slot 0
```

### Add Notes

```
Add a C major chord (C4, E4, G4) starting at beat 0 to the clip at track 0, slot 0
```

### Fire Clip

```
Play the clip at track 2, slot 0
```

### Stop Clip

```
Stop the clip at track 2, slot 0
```