# Session helpers - shared logic for session operations
import logging
from typing import Dict, Any

logger = logging.getLogger("AbletonMCPServer")

def format_session_info(result: Dict[str, Any]) -> str:
    """Format session info for display"""
    tempo = result.get("tempo", "N/A")
    time_signature = result.get("time_signature", "N/A")
    track_count = result.get("track_count", 0)
    return f"Tempo: {tempo} BPM, Time Signature: {time_signature}, Tracks: {track_count}"