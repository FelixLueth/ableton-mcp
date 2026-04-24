# Track helpers - shared logic for track operations
import logging
from typing import Dict, Any

logger = logging.getLogger("AbletonMCPServer")

def format_track_info(result: Dict[str, Any]) -> str:
    """Format track info for display"""
    name = result.get("name", "Unnamed")
    track_type = result.get("type", "unknown")
    return f"{name} ({track_type})"
