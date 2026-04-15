import json
import re

WISH_REGEX = re.compile(
    r'(?:cast|use)[^.]{0,40}(?:the\s+)?\{@spell wish.*?\}|grant(?:s|ed|ing)?[^.]{0,40}\b(?:a|your|one)\s+(?:wish|wishes)',
    re.IGNORECASE
)

with open('trimmed_5etools_list.json', 'r') as f:
    items = json.load(f)

for item in items:
    name = item.get('name', '')
    if name in ['Luck Blade', 'Mudslick Tower']:
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
        print(f"--- {name} ---")
        match = WISH_REGEX.search(desc)
        print("REGEX MATCH:", bool(match))
        if match:
            print("MATCH TEXT:", match.group(0))
        
        import textwrap
        print(textwrap.fill(desc[:1000]))
        print()
