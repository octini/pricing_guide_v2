# src/prose_loader.py
"""Parse items-sublist.md to extract prose descriptions by item name."""

import re
from pathlib import Path
from typing import Optional


def load_prose_descriptions(md_path: Path) -> dict[str, str]:
    """
    Parse items-sublist.md and return a dict of {item_name_lower: description}.

    The markdown format is:
    #### Item Name

    Type, price, weight

    ---

    Description text...
    """
    text = md_path.read_text(encoding="utf-8")
    descriptions = {}

    # Split on h4 headers (the actual format in items-sublist.md)
    sections = re.split(r'^#### (.+)$', text, flags=re.MULTILINE)

    # sections[0] = preamble, then alternating: name, content
    for i in range(1, len(sections), 2):
        name = sections[i].strip()
        content = sections[i + 1].strip() if i + 1 < len(sections) else ""

        # Remove the type/price/weight line and separator lines
        # The format is: type/price line, then ---, then description, then ---
        # We want to extract just the description part

        # Split on --- separators
        parts = content.split("---")
        if len(parts) >= 2:
            # Description is typically between the first and second ---
            # But sometimes there are multiple --- separators
            # The actual description is usually in parts[1] or parts[2]
            desc_parts = []
            for part in parts[1:]:
                cleaned = part.strip()
                if cleaned and not cleaned.startswith("*Base items"):
                    desc_parts.append(cleaned)

            if desc_parts:
                description = " ".join(desc_parts)
            else:
                description = ""
        else:
            description = content.strip()

        # Clean up the description
        description = description.strip()

        descriptions[name.lower()] = description

    return descriptions
