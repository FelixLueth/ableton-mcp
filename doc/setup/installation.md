# Installation

## Prerequisites

- **Ableton Live** 10 or newer
- **Python** 3.10 or newer
- **uv** package manager

## Install uv

### macOS

```bash
brew install uv
```

### Other Platforms

See official uv documentation: https://docs.astral.sh/uv/getting-started/installation/

## Option 1: Claude Desktop Integration

### 1. Configure Claude Desktop

Open Claude Desktop settings and add the MCP configuration:

1. Go to **Claude > Settings > Developer > Edit Config**
2. Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "uvx",
      "args": ["ableton-mcp"]
    }
  }
}
```

### 2. Install Ableton Remote Script

1. Copy `AbletonMCP_Remote_Script/__init__.py` to Ableton's Remote Scripts directory

**macOS:**
- Method 1: `Applications/Ableton Live XX/Contents/App-Resources/MIDI Remote Scripts/`
- Method 2: `~/Library/Preferences/Ableton/Live XX/User Remote Scripts/`

**Windows:**
- `C:\Users\[Username]\AppData\Roaming\Ableton\Live x.x.x\Preferences\User Remote Scripts`

2. Create folder `AbletonMCP` and place `__init__.py` inside

3. Launch Ableton Live

4. Go to **Preferences > Link, Tempo & MIDI**

5. Select "AbletonMCP" from Control Surface dropdown

6. Set Input and Output to "None"

---

## Option 2: Cursor Integration

### 1. Configure Cursor

1. Go to **Cursor Settings > MCP**
2. Add new MCP server with command:

```
uvx ableton-mcp
```

### 2. Install Remote Script

Follow steps 2-6 from Claude Desktop integration above.

---

## Option 3: Local Development

### 1. Clone Repository

```bash
git clone https://github.com/ahujasid/ableton-mcp.git
cd ableton-mcp
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Install Remote Script

Follow the Remote Script installation steps above.

### 4. Run MCP Server

```bash
python -m MCP_Server.server
```

Or use the console script:

```bash
uv run ableton-mcp
```

---

## Option 4: Docker (Smithery)

For Smithery deployment, use the provided `Dockerfile`:

```bash
docker build -t ableton-mcp .
docker run ableton-mcp
```

---

## Verify Installation

1. Ensure Ableton Live is running with the Remote Script loaded
2. Start Claude Desktop or Cursor
3. Look for the hammer icon indicating Ableton MCP tools are available
4. Try a simple command like "Get information about the current Ableton session"

---

## Troubleshooting

### Connection Issues

- Verify Ableton Remote Script is loaded (check Preferences > Link, Tempo & MIDI)
- Ensure port 9877 is not blocked
- Restart both Claude Desktop and Ableton Live

### Timeout Errors

- Simplify requests or break into smaller steps
- Ensure Ableton Live is fully loaded before making requests

### Still Not Working

- Check Claude Desktop logs for error messages
- Verify Python 3.10+ is installed: `python --version`