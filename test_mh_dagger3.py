from pathlib import Path
from src.prose_loader import load_prose_descriptions
import re

prose_map = load_prose_descriptions(Path('items-sublist.md'))
desc = prose_map.get("monster hunter's dagger +1", "")

wish_regex = re.compile(r'(?:cast|use)[^.]{0,40}(?:the\s+)?\{@spell wish.*?\}|grant(?:s|ed|ing)?[^.]{0,40}\b(?:a|your|one)\s+(?:wish|wishes)', re.IGNORECASE)
match = wish_regex.search(desc)

print("Match:", bool(match))
if match:
    print("Match text:", match.group(0))
    print("Full desc:", desc)
