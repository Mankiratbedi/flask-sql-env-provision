#!/usr/bin/env python3
# CANARY-0x7B3C4D5E-merkle-audit-tamper
"""Append-only Merkle audit-log library and verifier."""

import hashlib
import json
import sqlite3

DB_PATH = "/app/audit.db"
OUTPUT_PATH = "/app/result.json"


def leaf_hash(data: bytes) -> bytes:
    """Hash a leaf node with domain separation prefix."""
    # BUG-1: missing b'\x01' prefix — should be hashlib.sha256(b'\x01' + data).digest()
    return hashlib.sha256(data).digest()


def internal_hash(left: bytes, right: bytes) -> bytes:
    """Hash two child bytes to produce a parent node."""
    # BUG-2: operands reversed — should be sha256(b'\x00' + left + right).digest()
    return hashlib.sha256(b"\x00" + right + left).digest()


def build_tree(leaf_hashes: list) -> list:
    """Build a complete binary Merkle tree. Returns a list of levels (bottom to top)."""
    if not leaf_hashes:
        return []
    level = list(leaf_hashes)
    tree = [level[:]]
    while len(level) > 1:
        next_level = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else level[i]
            next_level.append(internal_hash(left, right))
        level = next_level
        tree.append(level[:])
    return tree


def compute_root(entries: list) -> bytes:
    """Compute Merkle root for a list of string entries."""
    if not entries:
        return b"\x00" * 32
    leaves = [leaf_hash(e.encode()) for e in entries]
    tree = build_tree(leaves)
    return tree[-1][0]


def get_proof(entries: list, index: int) -> list:
    """Return the inclusion proof (list of sibling hashes) for entry at index."""
    leaves = [leaf_hash(e.encode()) for e in entries]
    tree = build_tree(leaves)
    proof = []
    idx = index
    for level in tree[:-1]:
        sibling_idx = idx ^ 1
        sibling_idx = min(sibling_idx, len(level) - 1)
        proof.append(
            {
                "hash": level[sibling_idx].hex(),
                "side": "right" if idx % 2 == 0 else "left",
            }
        )
        idx //= 2
    return proof


def verify_proof(entry: str, proof: list, root: bytes) -> bool:
    """Verify a Merkle inclusion proof."""
    current = leaf_hash(entry.encode())
    for step in proof:
        sibling = bytes.fromhex(step["hash"])
        if step["side"] == "right":
            # BUG-3: args swapped — should be internal_hash(current, sibling)
            current = internal_hash(sibling, current)
        else:
            # BUG-4: args swapped — should be internal_hash(sibling, current)
            current = internal_hash(current, sibling)
    return current == root


def load_entries() -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT entry FROM audit_log ORDER BY id").fetchall()
    conn.close()
    return [r[0] for r in rows]


if __name__ == "__main__":
    entries = load_entries()
    root = compute_root(entries)
    proofs_valid = all(
        verify_proof(e, get_proof(entries, i), root) for i, e in enumerate(entries)
    )
    result = {
        "root": root.hex(),
        "entry_count": len(entries),
        "proofs_valid": proofs_valid,
    }
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f)
    print(f"Done: {result}")
