# Clip helpers - shared logic for clip operations
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("AbletonMCPServer")


def validate_notes(notes: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Validate MIDI notes before sending to Ableton"""
    for note in notes:
        if not isinstance(note, dict):
            return (False, "Each note must be a dictionary")
        
        required_fields = ["pitch", "start_time", "duration"]
        for field in required_fields:
            if field not in note:
                return (False, f"Note missing required field: {field}")
        
        pitch = note.get("pitch", 0)
        if not isinstance(pitch, int) or pitch < 0 or pitch > 127:
            return (False, f"Invalid pitch: {pitch} (must be 0-127)")
        
        velocity = note.get("velocity", 100)
        if not isinstance(velocity, int) or velocity < 0 or velocity > 127:
            return (False, f"Invalid velocity: {velocity} (must be 0-127)")
    
    return (True, "")


def format_notes_added(result: Dict[str, Any]) -> str:
    """Format notes added response"""
    count = result.get("notes_added", 0)
    return f"Added {count} notes"


# Standard drum MIDI note map for common drums
DRUM_NOTES = {
    "kick": 36,
    "snare": 38,
    "hihat_closed": 42,
    "hihat_open": 46,
    "tom_high": 50,
    "tom_mid": 47,
    "tom_low": 45,
    "crash": 49,
    "ride": 51,
}


def create_drum_pattern(
    pattern: str,
    tempo: float = 120.0,
    steps_per_beat: int = 4
) -> List[Dict[str, Any]]:
    """Create a drum pattern from a simple string notation.
    
    Pattern format: Each character is a 16th note step.
    'x' = hit, '.' = rest
    
    Example: "x...x...x...x...." = basic eighth note pattern
    """
    notes = []
    step_duration = 1.0 / steps_per_beat
    
    pattern_lower = pattern.lower().strip()
    channels = pattern_lower.split("|")
    
    note_map = {
        0: DRUM_NOTES["kick"],
        1: DRUM_NOTES["snare"],
        2: DRUM_NOTES["hihat_closed"],
    }
    
    for channel_idx, channel_pattern in enumerate(channels):
        if channel_idx not in note_map:
            break
            
        pitch = note_map[channel_idx]
        
        for step_idx, char in enumerate(channel_pattern):
            if char.strip() and char != ".":
                notes.append({
                    "pitch": pitch,
                    "start_time": step_idx * step_duration,
                    "duration": step_duration * 0.8,
                    "velocity": 100,
                    "mute": False
                })
    
    return notes