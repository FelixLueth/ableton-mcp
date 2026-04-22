# Data Flow

## Command Flow

### Typical Request-Response Cycle

```
1. AI Client                          MCP Server                         Remote Script
   │                                     │                                  │
   │  MCP tool invocation ─────────────►   │                                  │
   │                                     │                                  │
   │  Send command (JSON) ────────────►  │  TCP sendall() ────────────────►  │
   │                                     │                                  │
   │                                     │                                  │ receive()
   │                                     │                                  │ _process_command()
   │                                     │                                  │ schedule_message()
   │                                     │                                  │
   │  TCP recv() ◄───────────────────    │  Response (JSON) ◄────────────  │
   │                                     │                                  │
   │  MCP response ◄──────────────────   │                                  │
```

### State-Modifying Commands

Commands that modify Ableton's state (`create_midi_track`, `set_tempo`, `fire_clip`, etc.) follow a modified flow:

1. Small delay (100ms) before sending
2. Command sent with modified flags
3. Timeout increased to 15 seconds
4. Response received
5. Small delay (100ms) after response

## Data Formats

### Request Format

```json
{
  "type": "command_type",
  "params": {
    "key": "value"
  }
}
```

### Response Format

```json
{
  "status": "success",
  "result": {
    "key": "value"
  }
}
```

Error responses:

```json
{
  "status": "error",
  "message": "Error description"
}
```

## Connection Lifecycle

### Startup Sequence

```
1. MCP Server starts (mcp.run())
2. Lifespan manager initializes
3. get_ableton_connection() called
4. Socket connection attempt (up to 3 retries)
5. Connection validated with get_session_info
6. Connection stored globally
```

### Runtime Connection Management

- Connection is reused across requests
- Connection health checked with empty send before reuse
- Dead connections trigger reconnection
- Disconnect on server shutdown

### Shutdown Sequence

```
1. Lifespan manager cleanup
2. Global connection retrieved
3. Socket closed
4. Connection cleared
```

## Thread Safety

The Remote Script executes state-modifying commands on Ableton's main thread:

1. Command received and identified as modifying
2. Response queue created
3. Main thread task defined
4. `schedule_message()` queues task
5. Main thread executes task
6. Result placed in queue
7. Handler retrieves result from queue

This ensures thread-safe access to Ableton's internal state.

## Session Data Access

### Song Reference

Cached on Remote Script initialization:

```python
self._song = self.song()
```

Accessed via Ableton's internal API for all session operations.

### Track Access

```python
track = self._song.tracks[track_index]
```

### Clip Access

```python
clip_slot = track.clip_slots[clip_index]
clip = clip_slot.clip
```

### Browser Access

```python
app = self.application()
browser = app.browser
```