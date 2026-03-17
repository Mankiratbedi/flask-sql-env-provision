#!/bin/bash
set -euo pipefail

cat > /app/dedup.py << 'PYEOF'
#!/usr/bin/env python3
"""Reference dedup solution using rapidfuzz token_sort_ratio clustering."""
import csv
import json
import re
from rapidfuzz import fuzz

SUFFIXES = {
    "inc", "inc.", "llc", "corp", "corp.", "corporation", "co", "co.", "ltd",
    "ltd.", "group", "partners", "solutions", "systems", "technologies",
    "analytics", "capital", "ventures",
}


def normalize(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^a-z0-9 ]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    words = [w for w in name.split() if w not in SUFFIXES]
    return " ".join(words)


def main():
    with open("/app/companies.csv") as f:
        reader = csv.DictReader(f)
        records = [(int(row["id"]), row["name"]) for row in reader]

    # Union-Find for clustering
    parent = {rid: rid for rid, _ in records}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)

    norms = {rid: normalize(name) for rid, name in records}

    # Compare all pairs within normalized-name groups (bucket by first word)
    buckets: dict[str, list[int]] = {}
    for rid, norm in norms.items():
        key = norm.split()[0] if norm.split() else "_"
        buckets.setdefault(key, []).append(rid)

    for bucket_ids in buckets.values():
        for i in range(len(bucket_ids)):
            for j in range(i + 1, len(bucket_ids)):
                a, b = bucket_ids[i], bucket_ids[j]
                score = fuzz.token_sort_ratio(norms[a], norms[b])
                if score >= 85:
                    union(a, b)

    # Build clusters
    clusters_map: dict[int, list[int]] = {}
    for rid, _ in records:
        root = find(rid)
        clusters_map.setdefault(root, []).append(rid)

    # Use the longest original name as canonical
    name_map = {rid: name for rid, name in records}
    result = []
    for root, ids in clusters_map.items():
        canonical = max(ids, key=lambda i: len(name_map[i]))
        result.append({"canonical": name_map[canonical], "ids": sorted(ids)})

    with open("/app/clusters.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Found {len(result)} clusters from {len(records)} records")


if __name__ == "__main__":
    main()
PYEOF

python3 /app/dedup.py
echo "clusters.json generated"
