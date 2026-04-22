# Session Management

## Overview

Session management features provide access to and control of the overall Ableton Live session state.

## Features

### Get Session Information

Retrieves metadata about the current Ableton Live session.

**MCP Tool:** `get_session_info`

**Implementation:** `MCP_Server/server.py:260-269`

**Command:** `get_session_info`

**Response:**
```json
{
  "tempo": 120.0,
  "signature_numerator": 4,
  "signature_denominator": 4,
  "track_count": 8,
  "return_track_count": 2,
  "master_track": {
    "name": "Master",
    "volume": 0.0,
    "panning": 0.0
  }
}
```

### Set Tempo

Sets the tempo of the Ableton session.

**MCP Tool:** `set_tempo`

**Implementation:** `MCP_Server/server.py:392-406`

**Command:** `set_tempo`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `tempo` | float | New tempo in BPM |

**Response:**
```json
{
  "tempo": 120.0
}
```

---

## Remote Script Handlers

**File:** `AbletonMCP_Remote_Script/__init__.py`

### `_get_session_info()`

Location: lines 342-360

Retrieves:
- Current tempo
- Time signature (numerator/denominator)
- Track count
- Return track count
- Master track volume and panning

### `_set_tempo()`

Location: lines 551-562

Sets `self._song.tempo` to the specified value.

---

## Usage Examples

### Get Session Info

```
Get information about the current Ableton session
```

### Set Tempo

```
Set the tempo to 120 BPM
```