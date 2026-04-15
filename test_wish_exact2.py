import re
from src.prose_loader import load_prose_descriptions
from pathlib import Path

prose_map = load_prose_descriptions(Path('items-sublist.md'))

wish_regex = re.compile(r'\b(?:cast|use)\b[^.]{0,40}(?:the\s+)?(?:\*wish\*|\bwish\b\s*spell)|grant(?:s|ed|ing)?[^.]{0,40}\b(?:a|your|one)\s+(?:\*wishes?\*|\bwishes?\b)', re.IGNORECASE)

for k, v in prose_map.items():
    if wish_regex.search(v):
        print(k)

