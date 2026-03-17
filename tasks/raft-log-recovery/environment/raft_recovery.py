#!/usr/bin/env python3
# CANARY-0xF5A6B7C8-raft-log-recovery
"""Raft consensus log recovery tool — reads 3-node logs, recovers committed state."""

import json

LOG_DIR = "/app/logs"
OUTPUT_PATH = "/app/recovered_state.json"
NUM_NODES = 3
QUORUM = NUM_NODES // 2  # BUG-1: quorum must be strict majority = (NUM_NODES // 2) + 1


def load_node_logs():
    """Load log entries from all nodes."""
    nodes = []
    for i in range(NUM_NODES):
        with open(f"{LOG_DIR}/node_{i}.json") as f:
            data = json.load(f)
        nodes.append(data)
    return nodes


def get_commit_index(nodes):
    """
    Find highest log index agreed upon by a quorum of nodes.
    A log entry is committed if a quorum of nodes have an entry at that index
    with the same term.
    """
    index_agreement = {}
    for node in nodes:
        for entry in node["log"]:
            key = (entry["term"], entry["index"])
            index_agreement[key] = index_agreement.get(key, 0) + 1

    committed_index = -1
    for (term, idx), count in sorted(index_agreement.items(), key=lambda x: x[0][1]):
        if count >= QUORUM:  # BUG-1: should be > QUORUM (strict majority)
            committed_index = max(committed_index, idx)
    return committed_index


def get_highest_term_node(nodes):
    """Return the node with the highest current term (the leader's log)."""
    best = nodes[0]
    for node in nodes[1:]:
        if node["current_term"] <= best["current_term"]:  # BUG-2: should be <, not <=
            best = node
    return best


def apply_log(log_entries, up_to_index):
    """Apply committed log commands up to and including up_to_index."""
    state = {}
    for entry in log_entries:
        if entry["index"] >= up_to_index:  # BUG-3: should be >, skips the last committed entry
            break
        cmd = entry["command"]
        if cmd["op"] == "set":
            state[cmd["key"]] = cmd["value"]
        elif cmd["op"] == "delete":
            state.pop(cmd["key"], None)
    return state


def recover():
    nodes = load_node_logs()
    committed_index = get_commit_index(nodes)
    leader_node = get_highest_term_node(nodes)
    # BUG-4: snapshot applied AFTER log replay — overwrites correct log state
    raw_state = apply_log(leader_node["log"], committed_index)
    snapshot = leader_node.get("snapshot", {})
    final_state = {**raw_state, **snapshot}  # BUG-4: snapshot overwrites log (should be base)
    return {
        "committed_index": committed_index,
        "state": final_state,
        "node_count": NUM_NODES,
    }


if __name__ == "__main__":
    result = recover()
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f)
    print(f"Recovered: {result}")
