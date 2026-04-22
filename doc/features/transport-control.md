# Transport Control

## Overview

Transport control features provide start and stop functionality for the Ableton Live playback.

## Features

### Start Playback

Starts playback of the Ableton session from the current position.

**MCP Tool:** `start_playback`

**Implementation:** `MCP_Server/server.py:479-488`

**Command:** `start_playback`

**Response:**
```json
{
  "playing": true
}
```

### Stop Playback

Stops playback of the Ableton session.

**MCP Tool:** `stop_playback`

**Implementation:** `MCP_Server/server.py:490-499`

**Command:** `stop_playback`

**Response:**
```json
{
  "playing": false
}
```

---

## Remote Script Handlers

**File:** `AbletonMCP_Remote_Script/__init__.py`

### `_start_playback()`

Location: lines 614-625

Calls `self._song.start_playing()`

### `_stop_playback()`

Location: lines 627-638

Calls `self._song.stop_playing()`

---

## Usage Examples

### Start Playback

```
Start playback
```

### Stop Playback

```
Stop playback
```

---

## Related Features

- **Fire Clip** (`fire_clip`) - Starts a specific clip (see Clip Management)
- **Stop Clip** (`stop_clip`) - Stops a specific clip (see Clip Management)
- **Set Tempo** (`set_tempo`) - Controls playback speed (see Session Management)