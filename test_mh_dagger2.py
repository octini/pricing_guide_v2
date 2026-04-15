import re
import csv

wish_regex = re.compile(r'(?:cast|use)[^.]{0,40}(?:the\s+)?\{@spell wish.*?\}|grant(?:s|ed|ing)?[^.]{0,40}\b(?:a|your|one)\s+(?:wish|wishes)', re.IGNORECASE)

prose_dict = {}
current_item = None
current_text = []

with open('items-sublist.md', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('#### '):
            if current_item:
                prose_dict[current_item] = '\n'.join(current_text).strip()
            current_item = line[5:].strip()
            current_text = []
        elif current_item:
            current_text.append(line)
if current_item:
    prose_dict[current_item] = '\n'.join(current_text).strip()

name = "Monster Hunter's Dagger +1"
desc = prose_dict.get(name, '').lower()
match = wish_regex.search(desc)
if match:
    print("MATCH:", match.group(0))
    start = max(0, match.start() - 50)
    end = min(len(desc), match.end() + 50)
    print("CONTEXT:", desc[start:end])
else:
    print("No match")
