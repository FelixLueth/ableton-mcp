# MCP Endpoints

## Overview

The MCP Server exposes 16 tool endpoints that provide access to Ableton Live functionality.

## Tool Reference

### Session Management

#### get_session_info

```python
@mc p.tool()
def get_session_info(ctx: Context) -> str
```

Get detailed information about the current Ableton session.

**Returns:** JSON string with tempo, time signature, track count, and master track info.

#### set_tempo

```python
@mc p.tool()
def set_tempo(ctx: Context, tempo: float) -> str
```

Set the tempo of the Ableton session.

**Parameters:**
- `tempo` (float): New tempo in BPM

**Returns:** Confirmation message with new tempo.

---

### Track Management

#### get_track_info

```python
@mc p.tool()
def get_track_info(ctx: Context, track_index: int) -> str
```

Get detailed information about a specific track.

**Parameters:**
- `track_index` (int): Index of the track to query

**Returns:** JSON string with track name, type, mute/solo/arm states, volume, panning, clip slots, and devices.

#### create_midi_track

```python
@mc p.tool()
def create_midi_track(ctx: Context, index: int = -1) -> str
```

Create a new MIDI track.

**Parameters:**
- `index` (int): Insert position (-1 for end of list, default: -1)

**Returns:** Confirmation message with created track name.

#### set_track_name

```python
@mc p.tool()
def set_track_name(ctx: Context, track_index: int, name: str) -> str
```

Rename a track.

**Parameters:**
- `track_index` (int): Index of the track to rename
- `name` (str): New name for the track

**Returns:** Confirmation message with new track name.

---

### Clip Management

#### create_clip

```python
@mc p.tool()
def create_clip(
    ctx: Context,
    track_index: int,
    clip_index: int,
    length: float = 4.0
) -> str
```

Create a new MIDI clip.

**Parameters:**
- `track_index` (int): Target track index
- `clip_index` (int): Clip slot index
- `length` (float): Length in beats (default: 4.0)

**Returns:** Confirmation message with clip details.

#### add_notes_to_clip

```python
@mc p.tool()
def add_notes_to_clip(
    ctx: Context,
    track_index: int,
    clip_index: int,
    notes: List[Dict[str, Union[int, float, bool]]]
) -> str
```

Add MIDI notes to a clip.

**Parameters:**
- `track_index` (int): Track containing the clip
- `clip_index` (int): Clip slot containing the clip
- `notes` (List[Dict]): List of note dictionaries

**Note Format:**
```python
{
    "pitch": int,      # MIDI note 0-127
    "start_time": float,  # Start in beats
    "duration": float,    # Duration in beats
    "velocity": int,      # 0-127
    "mute": bool
}
```

**Returns:** Confirmation message with note count.

#### set_clip_name

```python
@mc p.tool()
def set_clip_name(
    ctx: Context,
    track_index: int,
    clip_index: int,
    name: str
) -> str
```

Rename a clip.

**Parameters:**
- `track_index` (int): Track containing the clip
- `clip_index` (int): Clip slot containing the clip
- `name` (str): New clip name

**Returns:** Confirmation message.

#### fire_clip

```python
@mc p.tool()
def fire_clip(ctx: Context, track_index: int, clip_index: int) -> str
```

Start playing a clip.

**Parameters:**
- `track_index` (int): Track containing the clip
- `clip_index` (int): Clip slot containing the clip

**Returns:** Confirmation message.

#### stop_clip

```python
@mc p.tool()
def stop_clip(ctx: Context, track_index: int, clip_index: int) -> str
```

Stop a playing clip.

**Parameters:**
- `track_index` (int): Track containing the clip
- `clip_index` (int): Clip slot containing the clip

**Returns:** Confirmation message.

---

### Transport Control

#### start_playback

```python
@mc p.tool()
def start_playback(ctx: Context) -> str
```

Start playback of the Ableton session.

**Returns:** Confirmation message.

#### stop_playback

```python
@mc p.tool()
def stop_playback(ctx: Context) -> str
```

Stop playback of the Ableton session.

**Returns:** Confirmation message.

---

### Browser Navigation

#### get_browser_tree

```python
@mc p.tool()
def get_browser_tree(ctx: Context, category_type: str = "all") -> str
```

Get a hierarchical tree of browser categories.

**Parameters:**
- `category_type` (str): Category to retrieve (default: "all")
  - Valid values: `all`, `instruments`, `sounds`, `drums`, `audio_effects`, `midi_effects`

**Returns:** Formatted browser tree with categories and subfolders.

#### get_browser_items_at_path

```python
@mc p.tool()
def get_browser_items_at_path(ctx: Context, path: str) -> str
```

Get browser items at a specific path.

**Parameters:**
- `path` (str): Browser path (e.g., "instruments/synths")

**Returns:** JSON string with items at the specified path, including names, types, and URIs.

#### load_instrument_or_effect

```python
@mc p.tool()
def load_instrument_or_effect(ctx: Context, track_index: int, uri: str) -> str
```

Load an instrument or effect onto a track.

**Parameters:**
- `track_index` (int): Target track index
- `uri` (str): Browser item URI

**Returns:** Confirmation message with loaded device names.

#### load_drum_kit

```python
@mc p.tool()
def load_drum_kit(
    ctx: Context,
    track_index: int,
    rack_uri: str,
    kit_path: str
) -> str
```

Load a drum rack and then load a specific drum kit.

**Parameters:**
- `track_index` (int): Target track index
- `rack_uri` (str): Drum rack URI (e.g., "Drums/Drum Rack")
- `kit_path` (str): Path to drum kit (e.g., "drums/acoustic/kit1")

**Returns:** Confirmation message with loaded kit name.