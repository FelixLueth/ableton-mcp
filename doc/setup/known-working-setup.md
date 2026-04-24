# Known Working Setup Guide

This guide provides a reproducible setup for Ableton Live 12 + MCP + Opencode across operating systems.

## Architecture Overview

```
Opencode ──MCP (stdio)──> MCP Server ──TCP (port 9877)──> Ableton Remote Script ──> Ableton Live
```

The system requires three components to communicate:
1. **Ableton Live** - Digital Audio Workstation with Remote Script loaded
2. **MCP Server** - Python server exposing Ableton functionality as MCP tools
3. **Opencode** - MCP client sending natural language commands

## Prerequisites

| Requirement | Minimum Version | Notes |
|-------------|----------------|-------|
| Ableton Live | 10+ | Live 12 recommended |
| Python | 3.10+ | - |
| uv | Latest | Package manager |
| Opencode | Latest | MCP client |

---

## Step 1: Python Environment Setup

### Install uv (All Platforms)

```bash
# macOS
brew install uv

# Linux/Windows (via installer)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### Install MCP Server

```bash
# Option 1: Direct execution (recommended for initial testing)
uvx ableton-mcp

# Option 2: Local development
git clone https://github.com/ahujasid/ableton-mcp.git
cd ableton-mcp
uv sync
```

---

## Step 2: Remote Script Installation

The Remote Script is a plugin that runs inside Ableton Live and enables external control.

### Ableton Remote Scripts Concept

Remote Scripts are Python-based plugins that extend Ableton Live's control surface capabilities. When loaded, they can:
- Receive commands from external applications
- Access the Live Object Model (LOM) to control sessions
- Expose internal functionality via a socket server

### Installation Paths

Create the `AbletonMCP` folder in one of these locations:

#### macOS (Live 12)

**User Library (Recommended - requires fewer permissions):**
```
~/Library/Preferences/Ableton/Live 12.0/User Remote Scripts/
```

**Application Bundle (System-wide):**
```
/Applications/Ableton Live 12.app/Contents/App-Resources/MIDI Remote Scripts/
```

#### Windows

**User Preferences:**
```
%APPDATA%\Ableton\Live 12.0\Preferences\User Remote Scripts\
```

**Program Files:**
```
C:\Program Files\Ableton\Live 12.0\Resources\MIDI Remote Scripts\
```

#### Linux (Experimental)

```
~/.config/Ableton/Live 12.0/User Remote Scripts/
```

### Installation Steps

1. Create the `AbletonMCP` folder in your chosen Remote Scripts path
2. Copy the contents of `AbletonMCP_Remote_Script/` into the `AbletonMCP` folder
3. Restart Ableton Live completely

**Folder Structure After Installation:**
```
AbletonMCP/
├── __init__.py          # Required: creates instance
├── control_surface.py  # Main control surface class
├── socket_server.py    # TCP server on port 9877
├── command_router.py    # Routes commands to handlers
├── handlers/           # Command handlers
│   ├── session_handler.py
│   ├── track_handler.py
│   ├── clip_handler.py
│   └── browser_handler.py
└── utils/
    └── logger.py
```

---

## Step 3: Enable Remote Script in Ableton

1. Open Ableton Live
2. Go to **Preferences > Link, Tempo & MIDI**
3. Find the **Control Surface** dropdown
4. Select "AbletonMCP"
5. Set **Input** and **Output** to "None" (or any MIDI ports if needed)
6. Close preferences

---

## Step 4: Configure Opencode

Add to your `opencode.jsonc` configuration:

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

---

## Step 5: Connection Validation

### Checklist

Complete each step to verify the setup:

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Start Ableton Live | Application launches |
| 2 | Verify Remote Script loaded | Check preferences - "AbletonMCP" selected |
| 3 | Start Opencode | MCP server starts |
| 4 | Check port availability | Port 9877 not used by other process |
| 5 | Test connection | `opencode mcp list` shows "AbletonMCP" |

### Minimal Connection Test

Run this to verify basic functionality:

```bash
# 1. Check MCP server is running
opencode mcp list

# 2. Test basic command
opencode "Get the current session tempo"
```

Expected response includes tempo in BPM.

### Verifying TCP Connection

```bash
# macOS/Linux
lsof -i :9877

# Windows (PowerShell)
netstat -ano | findstr "9877"
```

If the Remote Script loaded successfully, you should see a process listening on port 9877.

---

## Troubleshooting

### Issue: Remote Script Not Showing in Preferences

**Symptoms:** "AbletonMCP" not in Control Surface dropdown

**Solutions:**
1. Restart Ableton Live completely (not just project)
2. Verify Remote Script files are in correct location
3. Check Python files have correct permissions
4. Review Ableton's log file for errors

**Finding Ableton Log Files:**
- macOS: `~/Library/Logs/Ableton/`
- Windows: `%APPDATA%\Ableton\Live \logs\`

### Issue: Port 9877 Not Available

**Symptoms:** MCP server fails to connect

**Solutions:**
```
# Find what's using port 9877
lsof -i :9877

# Kill the process if needed
kill -9 <PID>
```

### Issue: MCP Server Connects But Commands Fail

**Symptoms:** Connection established but operations timeout

**Solutions:**
1. Verify Ableton is fully loaded before sending commands
2. Simplify requests into smaller steps
3. Check Ableton's CPU usage is not maxed
4. Look for errors in both Ableton log and MCP output

### Issue: "Could Not Connect to Ableton"

**Symptoms:** Error message on startup

**Solutions:**
1. Ensure Ableton Live is running
2. Verify Remote Script is loaded (check preferences)
3. Try restarting both Ableton and Opencode
4. Check firewall is not blocking localhost connections

---

## Environment Variables

For advanced configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `ABLETON_MCP_HOST` | localhost | TCP server host |
| `ABLETON_MCP_PORT` | 9877 | TCP server port |
| `ABLETON_MCP_TIMEOUT` | 15 | Response timeout (seconds) |

---

## Testing Without Ableton

For development testing without Ableton running:

```bash
# Install mock server (if available)
uvx ableton-mcp --mock
```

This runs the MCP server with a simulated Ableton for testing MCP tools.

---

## Quick Reference

| Component | Location | Port |
|-----------|----------|------|
| MCP Server | MCP_Server/server.py | stdio |
| Remote Script | AbletonMCP/ | 9877 |
| Opencode Config | opencode.jsonc | - |

### Common Commands

```bash
# List available tools
opencode mcp list

# Get session info
opencode "Get current session tempo and time signature"

# Create track and set tempo
opencode "Create a new MIDI track and set tempo to 120 BPM"
```