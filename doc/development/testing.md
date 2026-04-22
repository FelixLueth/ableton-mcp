# Testing

## Overview

The repository does not currently include a formal test suite.

---

## Testing Strategy

### Manual Testing

#### Prerequisites

1. Ableton Live running with Remote Script loaded
2. MCP Server running locally
3. Claude Desktop or Cursor connected

#### Test Categories

| Category | Examples |
|----------|----------|
| Session | Get/verify session info, set tempo |
| Tracks | Create track, get track info, rename |
| Clips | Create clip, add notes, fire/stop |
| Transport | Start/stop playback |
| Browser | Get browser tree, load instrument |

### Integration Testing

#### Test Connection

```python
# Verify connection by sending get_session_info
command = {"type": "get_session_info", "params": {}}
sock.sendall(json.dumps(command).encode())
response = sock.recv(8192)
result = json.loads(response.decode())
assert result["status"] == "success"
```

#### Test Command Round-Trip

```python
# Test command and response format
command = {"type": "set_tempo", "params": {"tempo": 120.0}}
sock.sendall(json.dumps(command).encode())
response = sock.recv(8192)
result = json.loads(response.decode())
assert result["result"]["tempo"] == 120.0
```

### Error Handling Tests

| Scenario | Expected Behavior |
|----------|-----------------|
| Invalid track index | Error response with IndexError message |
| Empty clip slot | Error response indicating no clip |
| Port not available | Connection refused |
| Ableton not running | Connection timeout |

---

## Debugging

### Enable Verbose Logging

In `MCP_Server/server.py`, set log level to DEBUG:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

### Remote Script Logs

Check Ableton's log file or status bar for Remote Script output.

### Network Debugging

Use `netstat` or `lsof` to verify port 9877 is listening:

```bash
# macOS
lsof -i :9877

# Linux
netstat -tlnp | grep 9877
```

---

## Test Commands

### Session Tests

```bash
# Get session info
echo '{"type":"get_session_info","params":{}}' | nc localhost 9877

# Set tempo
echo '{"type":"set_tempo","params":{"tempo":128}}' | nc localhost 9877
```

### Track Tests

```bash
# Create track
echo '{"type":"create_midi_track","params":{"index":-1}}' | nc localhost 9877

# Get track info
echo '{"type":"get_track_info","params":{"track_index":0}}' | nc localhost 9877
```

---

## CI/CD Considerations

For future CI/CD implementation:

1. Mock Ableton Live API for unit tests
2. Integration tests with headless Ableton (if supported)
3. Docker-based testing environment
4. Automated endpoint validation