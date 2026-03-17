#!/usr/bin/env python3
"""Generate noisy company name dataset for fuzzy dedup task."""
import csv
import json
import random
import re

random.seed(42)

CANONICAL_COMPANIES = [
    "Acme Corporation", "Blue Sky Technologies", "Bright Future Inc",
    "Capital Ventures", "Delta Systems", "Echo Analytics", "First Choice Media",
    "Global Dynamics", "Harbor Group", "Integrated Solutions",
    "Jupiter Labs", "Keystone Partners", "Lighthouse Digital",
    "Meridian Health", "Nordic Capital", "Orion Software",
    "Pacific Coast Logistics", "Quantum Computing", "Rapid Growth Ventures",
    "Stellar Innovations", "Titan Manufacturing", "United Services",
    "Vector Analytics", "Westside Consulting", "Xenon Technologies",
    "Yellowstone Energy", "Zenith Robotics", "Alpine Resources",
    "Beacon Financial", "Cascade Networks", "Delphi Research",
    "Emerald Group", "Frontier Aerospace", "Galaxy Media",
    "Helios Energy", "Iron Mountain", "Jade Software",
    "Kinetic Systems", "Lunar Technologies", "Maple Leaf",
    "Nexus Solutions", "Omega Partners", "Pinnacle Capital",
    "Quasar Labs", "Redwood Analytics", "Summit Ventures",
    "Terra Firma", "Umbra Security", "Vertex Systems",
    "Wildfire Media", "Axiom Technologies", "Bolt Energy",
    "Cobalt Networks", "Diamond Edge", "Element Five",
    "Falcon Industries", "Granite Partners", "Horizon Capital",
    "Iris Analytics", "Jasper Group", "Karma Digital",
    "Lumen Technologies", "Metro Systems", "Nova Partners",
    "Obsidian Security", "Prism Analytics", "Quest Ventures",
    "Radius Networks", "Sapphire Systems", "Torque Industries",
    "Union Pacific Tech", "Vortex Labs", "Waterfall Capital",
    "Xcel Energy Tech", "Yarrow Consulting", "Zephyr Analytics",
    "Amber Technologies", "Bronze Capital", "Copper Networks",
    "Dagger Systems", "Epoch Analytics", "Flint Industries",
    "Granite Bay Tech", "Hawk Security", "Indigo Solutions",
    "Jade Capital", "Kestrel Systems", "Lark Technologies",
    "Magnet Analytics", "Nitro Ventures", "Opal Networks",
    "Phoenix Rising", "Quartz Systems", "Raven Capital",
    "Silver Stream", "Topaz Analytics", "Umber Technologies",
    "Velvet Networks", "Wren Capital", "Xylem Solutions",
    "Yak Technologies", "Zinc Analytics", "Aether Systems",
    "Basalt Networks", "Cedar Capital", "Drift Technologies",
    "Elm Systems", "Fern Analytics", "Grove Capital",
    "Heron Technologies", "Ibis Solutions", "Juniper Networks",
    "Kite Capital", "Linden Systems", "Moss Analytics",
    "Nettle Technologies", "Oak Partners", "Pine Capital",
    "Quail Systems", "Reed Analytics", "Sage Technologies",
    "Thorn Capital", "Umber Systems", "Vine Analytics",
    "Willow Technologies", "Xanthic Capital", "Yew Systems",
    "Zeal Analytics", "Ardent Technologies", "Blaze Capital",
    "Crest Systems", "Dawn Analytics", "Edge Technologies",
    "Flow Capital", "Glow Systems", "Haze Analytics",
    "Ivory Technologies", "Jolt Capital", "Knot Systems",
    "Leaf Analytics", "Mist Technologies", "Neon Capital",
    "Orb Systems", "Pulse Analytics", "Quest Capital",
    "Rim Technologies", "Spark Systems", "Tide Analytics",
    "Urge Technologies", "Veil Capital", "Wave Systems",
    "Xray Analytics", "Yoke Technologies", "Zone Capital",
    "Arcadia Systems", "Bluff Analytics", "Cliff Technologies",
    "Dale Capital", "Fen Systems", "Glen Analytics",
    "Hill Technologies", "Isle Capital", "Knoll Systems",
    "Lake Analytics", "Moor Technologies", "Nook Capital",
    "Oaks Systems", "Peak Analytics", "Quay Technologies",
    "Rift Capital", "Shore Systems", "Tor Analytics",
    "Upland Technologies", "Vale Capital", "Wold Systems",
    "Xeric Analytics", "Yard Technologies", "Zeal Capital",
    "Arid Systems", "Basin Analytics", "Crag Technologies",
    "Dune Capital", "Escarpment Systems", "Fjord Analytics",
    "Gully Technologies", "Heath Capital", "Inlet Systems",
    "Jet Analytics", "Karst Technologies", "Loch Capital",
    "Mesa Systems", "Narrows Analytics", "Outcrop Technologies",
    "Pass Capital", "Quarry Systems", "Ravine Analytics",
    "Scarp Technologies", "Tarn Capital", "Upwelling Systems",
    "Veld Analytics", "Wash Technologies", "Xenolith Capital",
    "Yardang Systems", "Zawn Analytics",
]

SUFFIXES = ["Inc", "Inc.", "LLC", "Corp", "Corp.", "Corporation", "Co", "Co.",
            "Ltd", "Ltd.", "Group", "Partners", "Solutions", "Systems",
            "Technologies", "Analytics", "Capital", "Ventures"]

def strip_suffix(name):
    """Remove known suffixes from a company name."""
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if name.endswith(" " + s):
            return name[: -(len(s) + 1)].strip()
    return name

def add_typo(word):
    """Introduce a single character typo in a word."""
    if len(word) < 3:
        return word
    i = random.randint(1, len(word) - 2)
    chars = list(word)
    if random.random() < 0.5 and i + 1 < len(chars):
        chars[i], chars[i+1] = chars[i+1], chars[i]  # swap
    else:
        chars[i] = random.choice("abcdefghijklmnopqrstuvwxyz")
    return "".join(chars)

def generate_variant(canonical):
    """Generate a noisy variant of a canonical company name."""
    choice = random.random()
    base = strip_suffix(canonical)
    if choice < 0.10:
        return canonical.lower()
    elif choice < 0.20:
        return canonical.upper()
    elif choice < 0.30:
        new_suffix = random.choice(SUFFIXES)
        return f"{base} {new_suffix}"
    elif choice < 0.40:
        words = canonical.split()
        if len(words) > 1:
            idx = random.randint(0, len(words) - 1)
            words[idx] = add_typo(words[idx])
        return " ".join(words)
    elif choice < 0.50:
        return base
    elif choice < 0.58:
        return canonical.replace(" ", "  ")
    elif choice < 0.66:
        return canonical.replace(" ", "-")
    elif choice < 0.74:
        words = canonical.split()
        return " ".join(w[:1] + "." if i < len(words)-1 else w for i, w in enumerate(words))
    elif choice < 0.82:
        return canonical.replace("&", "and").replace("and", "&")
    elif choice < 0.90:
        return re.sub(r'\s+', ' ', canonical.strip())
    else:
        return canonical + "."

# Generate dataset
records = []
ground_truth = []
record_id = 1

for canonical in CANONICAL_COMPANIES:
    num_variants = random.randint(4, 10)
    cluster_ids = []
    # Always include the canonical form
    variants = [canonical] + [generate_variant(canonical) for _ in range(num_variants - 1)]
    for variant in variants:
        records.append((record_id, variant))
        cluster_ids.append(record_id)
        record_id += 1
    ground_truth.append({"canonical": canonical, "ids": cluster_ids})

# Shuffle records
random.shuffle(records)

with open("/app/companies.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "name"])
    writer.writerows(records)

with open("/app/ground_truth.json", "w") as f:
    json.dump(ground_truth, f)

print(f"Generated {len(records)} records across {len(CANONICAL_COMPANIES)} companies")
print("Saved to /app/companies.csv and /app/ground_truth.json")
