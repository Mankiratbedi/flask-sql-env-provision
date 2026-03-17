# Fuzzy Dedup Pipeline

You have a CSV file of ~1500 company name records scraped from multiple sources. Many records refer to the same company but with different spellings, abbreviations, suffixes, typos, or formatting.

## Data

`/app/companies.csv` — columns: `id` (integer), `name` (string)

```bash
head -5 /app/companies.csv
# id,name
# 1,Acme Corporation
# 2,acme corp
# 3,ACME CORPORATION
# ...
```

## Your Task

Write `/app/dedup.py` that:
1. Reads `/app/companies.csv`
2. Groups records that refer to the same company
3. Writes `/app/clusters.json`

## Output Format

`/app/clusters.json` must be a JSON array of cluster objects:
```json
[
  {"canonical": "Acme Corporation", "ids": [1, 47, 203]},
  {"canonical": "Blue Sky Technologies", "ids": [12, 88]},
  ...
]
```

- Every record `id` from the CSV must appear in exactly one cluster
- `canonical` is the representative name you choose for the cluster (any of the members is fine)
- Clusters must be non-overlapping and cover all records

## Evaluation

Your clusters will be evaluated against a held-out ground truth using **pairwise F1**:
- **Precision**: of all pairs you put in the same cluster, what fraction truly belong together?
- **Recall**: of all truly-duplicate pairs, what fraction did you correctly group?

Target: **F1 ≥ 0.75**

## Available Library

`rapidfuzz` is pre-installed. It provides fast fuzzy string matching:
```python
from rapidfuzz import fuzz, process
score = fuzz.token_sort_ratio("Acme Corp", "Acme Corporation")  # 0..100
```

## Hint

Good strategies: normalize (lowercase, remove punctuation, strip common suffixes), then cluster by similarity threshold. Consider what threshold balances precision vs recall.
