import re
import csv

wish_regex = re.compile(r'(?:cast|use)[^.]{0,40}(?:the\s+)?\{@spell wish.*?\}|grant(?:s|ed|ing)?[^.]{0,40}\b(?:a|your|one)\s+(?:wish|wishes)', re.IGNORECASE)

with open('items-sublist.md', 'r') as f:
    text = f.read()

# Try to find Monster Hunter's Dagger +1 section
idx = text.find("Monster Hunter's Dagger +1")
print(idx)
