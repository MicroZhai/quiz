"""ASCII-only merge script: reads _batch_new.json, merges into explanations_data.json"""
import json
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# Read new batch
with open(os.path.join(BASE, '_batch_new.json'), 'r', encoding='utf-8') as f:
    new_exps = json.load(f)

# Read existing
existing_path = os.path.join(BASE, 'explanations_data.json')
with open(existing_path, 'r', encoding='utf-8') as f:
    existing = json.load(f)

# Merge
existing.update(new_exps)

# Write back
with open(existing_path, 'w', encoding='utf-8') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"Merged {len(new_exps)} new entries, total: {len(existing)}")
print(f"New IDs: {sorted([int(k) for k in new_exps.keys()])}")
