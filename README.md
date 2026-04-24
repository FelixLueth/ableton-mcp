# AbletonMCP

Ableton Live integration through the Model Context Protocol (MCP). Control Ableton Live sessions using natural language prompts via Opencode.

## Overview

AbletonMCP connects AI assistants to Ableton Live through an MCP server. The system consists of:

- **MCP Server** – Python-based server that exposes Ableton functionality as MCP tools
- **Ableton Remote Script** – Plugin that runs inside Ableton Live
- **Opencode** – MCP client that sends natural language commands

## Architecture

```
Opencode ──MCP (stdio)──> MCP Server ──TCP──> Ableton Remote Script ──> Ableton Live
```

### Components

| Component | Location | Purpose |
|-----------|----------|---------|
| MCP Server | `MCP_Server/server.py` | Exposes MCP tools, manages connection |
| Remote Script | `AbletonMCP_Remote_Script/__init__.py` | Runs inside Ableton, executes commands |

## Prerequisites

- Ableton Live 10 or newer
- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/) package manager
- Opencode

## Installation

### 1. Install uv

```bash
# macOS
brew install uv

# Other platforms
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install MCP Server

```bash
uvx ableton-mcp
```

Or for local development:

```bash
git clone https://github.com/ahujasid/ableton-mcp.git
cd ableton-mcp
uv sync
```

### 3. Install Ableton Remote Script

1. Create folder `AbletonMCP` in Ableton's Remote Scripts directory:

   **macOS (Live 12):**
   ```
   ~/Library/Preferences/Ableton/Live 12.0/User Remote Scripts/
   ```

   **Windows:**
   ```
   %APPDATA%\Ableton\Live 12.0\Preferences\User Remote Scripts\
   ```

2. Copy `AbletonMCP_Remote_Script/__init__.py` into the `AbletonMCP` folder

3. Restart Ableton Live

4. Go to **Preferences > Link, Tempo & MIDI**

5. Select "AbletonMCP" from the Control Surface dropdown

6. Set Input and Output to "None"

### 4. Configure Opencode

Add to your `opencode.jsonc`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "ableton": {
      "type": "local",
      "command": ["uvx", "ableton-mcp"],
      "enabled": true
    }
  }
}
```

## Running

### Using the Start Script

The project includes a cross-platform start script that manages runtime modes:

```bash
./scripts/start.sh          # Normal mode: use published package (uvx ableton-mcp)
./scripts/start.sh --local # Local mode: use local repository code
./scripts/start.sh --clean # Clear uv cache and start in normal mode
```

**Mode differences:**

| Mode | Command | When to use |
|------|---------|-------------|
| normal | `uvx ableton-mcp` | Regular users, running the published package |
| local | `./scripts/start.sh --local` | Development, testing local changes |

**Important:** `uvx ableton-mcp` may use a cached/published package and therefore may not include local uncommitted changes. Use `--local` mode for development.

### Manual Running

1. Start Ableton Live
2. Start Opencode
3. MCP server connects automatically

Verify connection:

```bash
opencode mcp list
```

## Available Tools

### Session

- `get_session_info` – Get session metadata (tempo, time signature, track count)
- `get_full_session_state` – Get compact overview of session (tracks, clips, devices) optimized for LLM introspection
- `set_tempo` – Set tempo in BPM

### Track

- `get_track_info` – Get track details
- `create_midi_track` – Create new MIDI track
- `set_track_name` – Rename track

### Clip

- `create_clip` – Create new MIDI clip
- `add_notes_to_clip` – Add MIDI notes to clip
- `set_clip_name` – Rename clip
- `fire_clip` – Start clip playback
- `stop_clip` – Stop clip playback

### Transport

- `start_playback` – Start session playback
- `stop_playback` – Stop session playback

### Browser

- `get_browser_tree` – Get browser category tree
- `get_browser_items_at_path` – Get items at browser path
- `load_instrument_or_effect` – Load device onto track
- `load_drum_kit` – Load drum rack with kit

## First Test

Try these prompts in Opencode:

```
Get information about the current Ableton session
Get a full overview of the current session
Create a new MIDI track
Set the tempo to 120 BPM
```

## Limitations

- `get_full_session_state` does not include MIDI note data or full device parameter trees

## Troubleshooting

### Remote Script not showing up

- Verify Ableton is restarted after installing the Remote Script
- Check Preferences > Link, Tempo & MIDI > Control Surface

### MCP not connecting

- Ensure Ableton is running with Remote Script loaded
- Check that port 9877 is available: `lsof -i :9877`

### uvx not found

- Verify uv is installed: `uv --version`
- Ensure uv is in your PATH

### Ableton not responding

- Simplify requests or break into smaller steps
- Ensure Ableton Live is fully loaded before making requests

## Limitations

- Only one MCP client at a time
- Both components must run on the same machine
- Ableton Live must be running when MCP Server connects
- Script reload requires restarting Ableton
- `get_full_session_state` does not include MIDI note data or full device parameter trees (v1.0)

## License

MIT