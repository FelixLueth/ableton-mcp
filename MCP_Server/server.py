# Ableton MCP Server - Main Entry Point
#
# This module provides the MCP server interface for Ableton Live.
# It exposes tools for session, track, clip, browser, and transport control.

import json
import logging

from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any

from mcp.server.fastmcp import FastMCP, Context

from MCP_Server.connection import get_ableton_connection, _ableton_connection
from MCP_Server import clip_helpers

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AbletonMCPServer")


# =============================================================================
# Error Handling
# =============================================================================

class AbletonNotRunningError(Exception):
    """Raised when Ableton Live is not running or Remote Script not loaded"""
    pass


class PortUnavailableError(Exception):
    """Raised when port 9877 is already in use"""
    pass


def _handle_connection_error(e: Exception) -> str:
    """Handle connection errors with structured messages"""
    error_msg = str(e)

    if "refused" in error_msg.lower() or "connection refused" in error_msg.lower():
        return json.dumps({
            "error": "ableton_not_running",
            "message": "Could not connect to Ableton Live. Ensure Ableton is running with the Remote Script loaded.",
            "hint": "Check Preferences > Link, Tempo & MIDI in Ableton"
        })

    if "timeout" in error_msg.lower():
        return json.dumps({
            "error": "timeout",
            "message": "Connection to Ableton timed out.",
            "hint": "Try again or restart Ableton"
        })

    if "address already in use" in error_msg.lower():
        return json.dumps({
            "error": "port_unavailable",
            "message": "Port 9877 is already in use.",
            "hint": "Check if another instance is running or kill the process using the port"
        })

    return json.dumps({
        "error": "connection_error",
        "message": f"Connection error: {error_msg}"
    })


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    try:
        logger.info("AbletonMCP server starting up")

        try:
            _ = get_ableton_connection()
            logger.info("Successfully connected to Ableton on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Ableton on startup: {str(e)}")
            logger.warning("Make sure the Ableton Remote Script is running")

        yield {}
    finally:
        global _ableton_connection
        if _ableton_connection:
            logger.info("Disconnecting from Ableton on shutdown")
            _ableton_connection.disconnect()
            _ableton_connection = None
        logger.info("AbletonMCP server shut down")


mcp = FastMCP(
    "AbletonMCP",
    lifespan=server_lifespan
)


# =============================================================================
# Session Tools
# =============================================================================

@mcp.tool()
def get_session_info(ctx: Context) -> str:
    """Get detailed information about the current Ableton session"""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_session_info")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting session info from Ableton: {str(e)}")
        return f"Error getting session info: {str(e)}"


@mcp.tool()
def set_tempo(ctx: Context, tempo: float) -> str:
    """Set the tempo of the Ableton session.
    
    Parameters:
    - tempo: The new tempo in BPM
    """
    try:
        ableton = get_ableton_connection()
        ableton.send_command("set_tempo", {"tempo": tempo})
        return f"Set tempo to {tempo} BPM"
    except Exception as e:
        logger.error(f"Error setting tempo: {str(e)}")
        return f"Error setting tempo: {str(e)}"


# =============================================================================
# Track Tools
# =============================================================================

@mcp.tool()
def get_track_info(ctx: Context, track_index: int) -> str:
    """Get detailed information about a specific track in Ableton.
    
    Parameters:
    - track_index: The index of the track to get information about
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_track_info", {"track_index": track_index})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting track info from Ableton: {str(e)}")
        return f"Error getting track info: {str(e)}"


@mcp.tool()
def create_midi_track(ctx: Context, index: int = -1) -> str:
    """Create a new MIDI track in the Ableton session.
    
    Parameters:
    - index: The index to insert the track at (-1 = end of list)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_midi_track", {"index": index})
        return f"Created new MIDI track: {result.get('name', 'unknown')}"
    except Exception as e:
        logger.error(f"Error creating MIDI track: {str(e)}")
        return f"Error creating MIDI track: {str(e)}"


@mcp.tool()
def set_track_name(ctx: Context, track_index: int, name: str) -> str:
    """Set the name of a track.
    
    Parameters:
    - track_index: The index of the track to rename
    - name: The new name for the track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_name", {"track_index": track_index, "name": name})
        return f"Renamed track to: {result.get('name', name)}"
    except Exception as e:
        logger.error(f"Error setting track name: {str(e)}")
        return f"Error setting track name: {str(e)}"


# =============================================================================
# Clip Tools
# =============================================================================

@mcp.tool()
def create_clip(ctx: Context, track_index: int, clip_index: int, length: float = 4.0) -> str:
    """Create a new MIDI clip in the specified track and clip slot.
    
    Parameters:
    - track_index: The index of the track to create the clip in
    - clip_index: The index of the clip slot to create the clip in
    - length: The length of the clip in beats (default: 4.0)
    """
    try:
        ableton = get_ableton_connection()
        ableton.send_command("create_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "length": length
        })
        return f"Created new clip at track {track_index}, slot {clip_index} with length {length} beats"
    except Exception as e:
        logger.error(f"Error creating clip: {str(e)}")
        return f"Error creating clip: {str(e)}"


@mcp.tool()
def add_notes_to_clip(
    ctx: Context,
    track_index: int,
    clip_index: int,
    notes: list
) -> str:
    """Add MIDI notes to a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - notes: List of note dictionaries, each with pitch, start_time, duration, velocity, and mute
    """
    try:
        ableton = get_ableton_connection()
        _ = ableton.send_command("add_notes_to_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "notes": notes
        })
        return f"Added {len(notes)} notes to clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error adding notes to clip: {str(e)}")
        return f"Error adding notes to clip: {str(e)}"


@mcp.tool()
def set_clip_name(ctx: Context, track_index: int, clip_index: int, name: str) -> str:
    """Set the name of a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - name: The new name for the clip
    """
    try:
        ableton = get_ableton_connection()
        ableton.send_command("set_clip_name", {
            "track_index": track_index,
            "clip_index": clip_index,
            "name": name
        })
        return f"Renamed clip at track {track_index}, slot {clip_index} to '{name}'"
    except Exception as e:
        logger.error(f"Error setting clip name: {str(e)}")
        return f"Error setting clip name: {str(e)}"


@mcp.tool()
def fire_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """Start playing a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    try:
        ableton = get_ableton_connection()
        ableton.send_command("fire_clip", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        return f"Started playing clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error firing clip: {str(e)}")
        return f"Error firing clip: {str(e)}"


@mcp.tool()
def stop_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """Stop playing a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    try:
        ableton = get_ableton_connection()
        ableton.send_command("stop_clip", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        return f"Stopped clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error stopping clip: {str(e)}")
        return f"Error stopping clip: {str(e)}"


# =============================================================================
# Transport Tools
# =============================================================================

@mcp.tool()
def start_playback(ctx: Context) -> str:
    """Start playing the Ableton session."""
    try:
        ableton = get_ableton_connection()
        _ = ableton.send_command("start_playback")
        return "Started playback"
    except Exception as e:
        logger.error(f"Error starting playback: {str(e)}")
        return f"Error starting playback: {str(e)}"


@mcp.tool()
def stop_playback(ctx: Context) -> str:
    """Stop playing the Ableton session."""
    try:
        ableton = get_ableton_connection()
        _ = ableton.send_command("stop_playback")
        return "Stopped playback"
    except Exception as e:
        logger.error(f"Error stopping playback: {str(e)}")
        return f"Error stopping playback: {str(e)}"


# =============================================================================
# Browser Tools
# =============================================================================

@mcp.tool()
def get_browser_tree(ctx: Context, category_type: str = "all") -> str:
    """Get a hierarchical tree of browser categories from Ableton.
    
    Parameters:
    - category_type: Type of categories to get ('all', 'instruments', 'sounds', 'drums', 'audio_effects', 'midi_effects')
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_browser_tree", {
            "category_type": category_type
        })

        if "available_categories" in result and len(result.get("categories", [])) == 0:
            available_cats = result.get("available_categories", [])
            return (f"No categories found for '{category_type}'. "
                   f"Available browser categories: {', '.join(available_cats)}")

        total_folders = result.get("total_folders", 0)
        formatted_output = f"Browser tree for '{category_type}' (showing {total_folders} folders):\n\n"

        def format_tree(item, indent=0):
            output = ""
            if item:
                prefix = "  " * indent
                name = item.get("name", "Unknown")
                path = item.get("path", "")
                has_more = item.get("has_more", False)

                output += f"{prefix}* {name}"
                if path:
                    output += f" (path: {path})"
                if has_more:
                    output += " [...]"
                output += "\n"

                for child in item.get("children", []):
                    output += format_tree(child, indent + 1)
            return output

        for category in result.get("categories", []):
            formatted_output += format_tree(category)
            formatted_output += "\n"

        return formatted_output
    except Exception as e:
        error_msg = str(e)
        if "Browser is not available" in error_msg:
            logger.error(f"Browser is not available in Ableton: {error_msg}")
            return "Error: The Ableton browser is not available. Make sure Ableton Live is fully loaded and try again."
        elif "Could not access Live application" in error_msg:
            logger.error(f"Could not access Live application: {error_msg}")
            return "Error: Could not access the Ableton Live application. Make sure Ableton Live is running and the Remote Script is loaded."
        else:
            logger.error(f"Error getting browser tree: {error_msg}")
            return f"Error getting browser tree: {error_msg}"


@mcp.tool()
def get_browser_items_at_path(ctx: Context, path: str) -> str:
    """Get browser items at a specific path in Ableton's browser.
    
    Parameters:
    - path: Path in the format "category/folder/subfolder"
            where category is one of the available browser categories in Ableton
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_browser_items_at_path", {
            "path": path
        })

        if "error" in result and "available_categories" in result:
            error = result.get("error", "")
            available_cats = result.get("available_categories", [])
            return (f"Error: {error}\n"
                   f"Available browser categories: {', '.join(available_cats)}")

        return json.dumps(result, indent=2)
    except Exception as e:
        error_msg = str(e)
        if "Browser is not available" in error_msg:
            logger.error(f"Browser is not available in Ableton: {error_msg}")
            return "Error: The Ableton browser is not available. Make sure Ableton Live is fully loaded and try again."
        elif "Could not access Live application" in error_msg:
            logger.error(f"Could not access Live application: {error_msg}")
            return "Error: Could not access the Ableton Live application. Make sure Ableton Live is running and the Remote Script is loaded."
        elif "Unknown or unavailable category" in error_msg:
            logger.error(f"Invalid browser category: {error_msg}")
            return f"Error: {error_msg}. Please check the available categories using get_browser_tree."
        elif "Path part" in error_msg and "not found" in error_msg:
            logger.error(f"Path not found: {error_msg}")
            return f"Error: {error_msg}. Please check the path and try again."
        else:
            logger.error(f"Error getting browser items at path: {error_msg}")
            return f"Error getting browser items at path: {error_msg}"


@mcp.tool()
def load_instrument_or_effect(ctx: Context, track_index: int, uri: str) -> str:
    """Load an instrument or effect onto a track using its URI.
    
    Parameters:
    - track_index: The index of the track to load the instrument on
    - uri: The URI of the instrument or effect to load (e.g., 'query:Synths#Instrument%20Rack:Bass:FileId_5116')
    """
    try:
        ableton = get_ableton_connection()
        _result = ableton.send_command("load_browser_item", {
            "track_index": track_index,
            "item_uri": uri
        })

        if _result.get("loaded", False):
            new_devices = _result.get("new_devices", [])
            if new_devices:
                return f"Loaded instrument with URI '{uri}' on track {track_index}. New devices: {', '.join(new_devices)}"
            else:
                devices = _result.get("devices_after", [])
                return f"Loaded instrument with URI '{uri}' on track {track_index}. Devices on track: {', '.join(devices)}"
        else:
            return f"Failed to load instrument with URI '{uri}'"
    except Exception as e:
        logger.error(f"Error loading instrument by URI: {str(e)}")
        return f"Error loading instrument by URI: {str(e)}"


@mcp.tool()
def load_drum_kit(ctx: Context, track_index: int, rack_uri: str, kit_path: str) -> str:
    """Load a drum rack and then load a specific drum kit into it.
    
    Parameters:
    - track_index: The index of the track to load on
    - rack_uri: The URI of the drum rack to load (e.g., 'Drums/Drum Rack')
    - kit_path: Path to the drum kit inside the browser (e.g., 'drums/acoustic/kit1')
    """
    try:
        ableton = get_ableton_connection()

        _rack_result = ableton.send_command("load_browser_item", {
            "track_index": track_index,
            "item_uri": rack_uri
        })

        if not _rack_result.get("loaded", False):
            return f"Failed to load drum rack with URI '{rack_uri}'"

        kit_result = ableton.send_command("get_browser_items_at_path", {
            "path": kit_path
        })

        if "error" in kit_result:
            return f"Loaded drum rack but failed to find drum kit: {kit_result.get('error')}"

        kit_items = kit_result.get("items", [])
        loadable_kits = [item for item in kit_items if item.get("is_loadable", False)]

        if not loadable_kits:
            return f"Loaded drum rack but no loadable drum kits found at '{kit_path}'"

        kit_uri = loadable_kits[0].get("uri")
        _ = ableton.send_command("load_browser_item", {
            "track_index": track_index,
            "item_uri": kit_uri
        })

        return f"Loaded drum rack and kit '{loadable_kits[0].get('name')}' on track {track_index}"
    except Exception as e:
        logger.error(f"Error loading drum kit: {str(e)}")
        return f"Error loading drum kit: {str(e)}"


# =============================================================================
# Drum Loop Tool (Phase 3)
# =============================================================================

@mcp.tool()
def create_drum_loop(
    ctx: Context,
    track_index: int,
    clip_index: int,
    pattern: str,
    length: float = 4.0,
    tempo: float = 120.0
) -> str:
    """Create a drum loop from a pattern string.
    
    Parameters:
    - track_index: The index of the track to create the clip in
    - clip_index: The index of the clip slot
    - pattern: Drum pattern string (e.g., "x...x...x...x...." or "x.|.x.|..|..")
    - length: Length of the clip in beats (default: 4.0)
    - tempo: Tempo in BPM for timing calculations (default: 120.0)
    
    Pattern Format:
    - 'x' = hit, '.' = rest
    - '|' separates instrument channels (kick|snare|hihat)
    - Each character is a 16th note
    
    Examples:
    - "x...x...x...x...." = eighth notes on all beats
    - "x.|x.|" = kick on 1 and 3, snare on 2 and 4
    """
    try:
        ableton = get_ableton_connection()

        notes = clip_helpers.create_drum_pattern(pattern, tempo)

        if not notes:
            return f"Error: No notes generated from pattern '{pattern}'"

        valid, error = clip_helpers.validate_notes(notes)
        if not valid:
            return f"Error: Invalid notes: {error}"

        _ = ableton.send_command("create_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "length": length
        })

        ableton.send_command("add_notes_to_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "notes": notes
        })

        return f"Created drum loop with {len(notes)} notes on track {track_index}, clip {clip_index}"
    except Exception as e:
        logger.error(f"Error creating drum loop: {str(e)}")
        return f"Error creating drum loop: {str(e)}"


# =============================================================================
# Introspection Tools (Phase 3)
# =============================================================================

@mcp.tool()
def list_tracks(ctx: Context) -> str:
    """List all tracks in the current Ableton session.
    
    Returns compact JSON with track names, types, and states.
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_session_info")

        tracks = result.get("tracks", [])
        track_list = []
        for i, track in enumerate(tracks):
            track_list.append({
                "index": i,
                "name": track.get("name", f"Track {i}"),
                "type": track.get("type", "unknown"),
                "muted": track.get("muted", False),
                "soloed": track.get("soloed", False),
                "armed": track.get("armed", False)
            })

        return json.dumps({"tracks": track_list, "count": len(track_list)}, indent=2)
    except Exception as e:
        logger.error(f"Error listing tracks: {str(e)}")
        return f"Error listing tracks: {str(e)}"


@mcp.tool()
def list_clips(ctx: Context, track_index: int) -> str:
    """List all clips in a track.
    
    Parameters:
    - track_index: The index of the track to list clips from
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_track_info", {"track_index": track_index})

        clip_slots = result.get("clip_slots", [])
        clips = []
        for i, slot in enumerate(clip_slots):
            if slot.get("has_clip"):
                clips.append({
                    "index": i,
                    "name": slot.get("clip_name", f"Clip {i}"),
                    "playing": slot.get("is_playing", False),
                    "looping": slot.get("is_looping", False)
                })

        return json.dumps({"track_index": track_index, "clips": clips, "count": len(clips)}, indent=2)
    except Exception as e:
        logger.error(f"Error listing clips: {str(e)}")
        return f"Error listing clips: {str(e)}"


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
