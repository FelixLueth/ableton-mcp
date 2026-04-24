# Browser helpers - shared logic for browser/preset operations
import logging
from typing import Dict, Any, List

logger = logging.getLogger("AbletonMCPServer")

BROWSER_CATEGORIES = ["instruments", "sounds", "drums", "audio_effects", "midi_effects"]


def validate_category(category: str) -> bool:
    """Validate browser category"""
    return category in BROWSER_CATEGORIES or category == "all"


def format_browser_tree(result: Dict[str, Any]) -> str:
    """Format browser tree for display"""
    categories = result.get("categories", [])
    if not categories:
        return "No browser items found"

    lines = []
    for category in categories:
        lines.append(f"- {category.get('name', 'Unknown')}")

    return "\n".join(lines)


def search_items(
    items: List[Dict[str, Any]],
    query: str,
    field: str = "name"
) -> List[Dict[str, Any]]:
    """Search items by field with partial matching"""
    query_lower = query.lower()
    results = []

    for item in items:
        value = item.get(field, "")
        if query_lower in value.lower():
            results.append(item)

    return results


def filter_loadable(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter items that can be loaded onto a track"""
    return [item for item in items if item.get("is_loadable", False)]
