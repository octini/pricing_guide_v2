import json
import re

WISH_REGEX = re.compile(
    r'(?:cast|use)[^.]{0,40}(?:the\s+)?\{@spell wish.*?\}|grant(?:s|ed|ing)?[^.]{0,40}\b(?:a|your|one)\s+(?:wish|wishes)',
    re.IGNORECASE
)

with open('trimmed_5etools_list.json', 'r') as f:
    items = json.load(f)

wish_items = []
for item in items:
    # Recursively extract text from entries
    def get_text(entries):
        text = ""
        for entry in entries:
            if isinstance(entry, str):
                text += entry + " "
            elif isinstance(entry, dict):
                if 'entries' in entry:
                    text += get_text(entry['entries'])
                elif 'items' in entry:
                    text += get_text(entry['items'])
        return text

    desc = get_text(item.get('entries', []))
    name = item.get('name', '')
    if WISH_REGEX.search(desc) or WISH_REGEX.search(name):
        wish_items.append(name)

print(f"Found {len(wish_items)} items with wish effect:")
print("\n".join(sorted(wish_items)))
