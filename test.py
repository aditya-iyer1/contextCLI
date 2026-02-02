# Testing manifest.json structure, format

import json
from collections import Counter

def raw_diagnostics(path="manifest.json"):
    with open(path, "r") as f:
        data = json.load(f)

    print(f"--- Manifest Stats ---")
    print(f"Total Samples: {len(data)}")
    
    lengths = [ex["context_tokens"] for ex in data]
    print(f"Min Tokens: {min(lengths)}")
    print(f"Max Tokens: {max(lengths)}")
    print(f"Avg Tokens: {int(sum(lengths)/len(lengths))}")

    # Inspect the 'metadata' keys specifically
    # We want to see what 'extra' stuff is being carried over
    print(f"\n--- Metadata Key Inspection ---")
    if data[0].get("metadata"):
        print(f"Keys in metadata: {list(data[0]['metadata'].keys())}")
        # If there are nested keys in the question/document within metadata
        # check if those 'tokens' lists are bloating the file size
    
    # Check for empty strings or None values
    empty_contexts = sum(1 for ex in data if not ex["context"])
    print(f"\n--- Data Integrity ---")
    print(f"Empty Contexts: {empty_contexts}")
    print(f"Unique IDs: {len(set(ex['id'] for ex in data))}")

if __name__ == "__main__":
    raw_diagnostics()