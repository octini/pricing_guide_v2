# src/utils
import re
from typing import Optional
from urllib.parse import quote


def normalize_item_name(name: str) -> str:
    """Normalize item name for fuzzy matching: lowercase, move leading +N to suffix."""
    name = name.strip()
    
    # Move leading "+N " to end: "+1 Longsword" → "longsword +1"
    leading_plus = re.match(r'^(\+\d+)\s+(.+)$', name)
    if leading_plus:
        bonus, rest = leading_plus.groups()
        name = f"{rest} {bonus}"
    
    # Lowercase, remove parentheses (keep content), strip extra punctuation
    name = name.lower()
    name = re.sub(r'[()]', '', name)
    name = re.sub(r"[',]", '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def parse_value_cp(value: Optional[int]) -> Optional[float]:
    """Convert value field (copper pieces) to gold pieces. Returns None if zero or null."""
    if value is None or value == 0:
        return None
    return value / 100.0


def get_5etools_url(item_name: str, source: str) -> str:
    """Build a 5e.tools item URL from item name and source code."""
    name_part = item_name.lower().replace(' ', '%20')
    source_part = source.lower()
    return f"https://5e.tools/items.html#{name_part}_{source_part}"
