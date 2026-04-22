# Browser Navigation

## Overview

Browser navigation features enable exploration and loading of Ableton's built-in instruments, effects, and sounds.

## Features

### Get Browser Tree

Retrieves a hierarchical tree of browser categories from Ableton.

**MCP Tool:** `get_browser_tree`

**Implementation:** `MCP_Server/server.py:501-562`

**Command:** `get_browser_tree`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `category_type` | str | Category to retrieve (default: "all") |

**Valid Category Types:**
- `all` - All categories
- `instruments` - Instruments
- `sounds` - Sounds
- `drums` - Drums
- `audio_effects` - Audio effects
- `midi_effects` - MIDI effects

**Response:**
```json
{
  "type": "instruments",
  "categories": [
    {
      "name": "Instruments",
      "path": "Instruments",
      "children": [
        {
          "name": "Synths",
          "path": "Instruments/Synths"
        },
        {
          "name": "Keys",
          "path": "Instruments/Keys"
        }
      ]
    }
  ],
  "total_folders": 15
}
```

### Get Browser Items at Path

Retrieves items at a specific path in Ableton's browser.

**MCP Tool:** `get_browser_items_at_path`

**Implementation:** `MCP_Server/server.py:564-603`

**Command:** `get_browser_items_at_path`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | str | Browser path (e.g., "instruments/synths") |

**Response:**
```json
{
  "path": "instruments/synths",
  "name": "Synths",
  "uri": "instruments:synths",
  "is_folder": true,
  "items": [
    {
      "name": "Analog",
      "is_folder": false,
      "is_device": true,
      "is_loadable": true,
      "uri": "instruments:synths:analog"
    }
  ]
}
```

### Load Instrument or Effect

Loads an instrument or effect onto a track using its URI.

**MCP Tool:** `load_instrument_or_effect`

**Implementation:** `MCP_Server/server.py:408-437`

**Command:** `load_browser_item`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `track_index` | int | Target track index |
| `uri` | str | Browser item URI |

**Response:**
```json
{
  "loaded": true,
  "new_devices": ["Analog"],
  "devices_after": ["Analog", "Drum Pad"]
}
```

### Load Drum Kit

Helper function to load a drum rack and then a specific drum kit.

**MCP Tool:** `load_drum_kit`

**Implementation:** `MCP_Server/server.py:605-652`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `track_index` | int | Target track index |
| `rack_uri` | str | Drum rack URI (e.g., "Drums/Drum Rack") |
| `kit_path` | str | Path to drum kit (e.g., "drums/acoustic/kit1") |

---

## Remote Script Handlers

**File:** `AbletonMCP_Remote_Script/__init__.py`

### `get_browser_tree()`

Location: lines 823-937

Returns simplified browser tree with categories:
- Instruments
- Sounds
- Drums
- Audio Effects
- MIDI Effects

### `get_browser_items_at_path()`

Location: lines 939-1062

Navigates the browser path and returns all items at that location.

### `_load_browser_item()`

Location: lines 726-759

1. Validates track index
2. Finds browser item by URI
3. Selects the track
4. Loads item via `app.browser.load_item()`

### `_find_browser_item_by_uri()`

Location: lines 761-800

Recursively searches browser for item with matching URI.

---

## Usage Examples

### Explore Instruments

```
Show me all available instruments in Ableton's browser
```

### Find Specific Synth

```
Get browser items at path "instruments/synths"
```

### Load Instrument

```
Load the "Analog" synth onto track 0
```

### Load Drum Kit

```
Load an 808 drum kit onto track 1
```