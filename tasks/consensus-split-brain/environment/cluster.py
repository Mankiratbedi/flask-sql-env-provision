#!/usr/bin/env python3
"""Simplified leader-based log replication cluster.

Three nodes: one Leader and two Followers. The leader accepts writes,
replicates to followers, and advances commit_index on majority ack.

KNOWN BUG: Followers never advance their commit_index from leader_commit,
so when a follower is promoted after a leader crash all writes appear lost.
"""
import queue
import threading
import time
import sys
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LogEntry:
    index: int
    term: int
    key: str
    value: str


@dataclass
class AppendEntriesMsg:
    leader_id: str
    prev_index: int
    prev_term: int
    entries: list
    leader_commit: int
    _reply_to: object = field(default=None, repr=False)


@dataclass
class AppendEntriesResp:
    node_id: str
    success: bool
    match_index: int


class Node:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.log: list = []
        self.commit_index: int = -1
        self.term: int = 0
        self.inbox: queue.Queue = queue.Queue()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def get_last_log_index(self) -> int:
        return len(self.log) - 1

    def get_last_log_term(self) -> int:
        return self.log[-1].term if self.log else 0

    def get_committed_state(self) -> dict:
        """Return key-value state of all committed log entries."""
        state = {}
        with self._lock:
            for i, entry in enumerate(self.log):
                if i <= self.commit_index:
                    state[entry.key] = entry.value
        return state

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        self.inbox.put(None)

    def _run(self):
        raise NotImplementedError


class Follower(Node):
    def __init__(self, node_id: str):
        super().__init__(node_id)
        self.match_index: int = -1

    def _run(self):
        while self._running:
            try:
                msg = self.inbox.get(timeout=0.05)
                if msg is None:
                    break
                if isinstance(msg, AppendEntriesMsg):
                    self._handle_append_entries(msg)
            except queue.Empty:
                continue

    def _handle_append_entries(self, msg: AppendEntriesMsg):
        if msg.prev_index >= 0:
            if msg.prev_index >= len(self.log):
                return
            if self.log[msg.prev_index].term != msg.prev_term:
                return

        for entry in msg.entries:
            if entry.index < len(self.log):
                self.log[entry.index] = entry
            else:
                self.log.append(entry)

        # BUG: commit_index is never updated from leader_commit.
        # Followers accumulate log entries but never advance commit_index.
        # When a follower is promoted, commit_index stays at -1 and
        # get_committed_state() returns empty — all writes appear lost.

        self.match_index = len(self.log) - 1
        if msg._reply_to is not None:
            msg._reply_to.put(AppendEntriesResp(
                node_id=self.node_id,
                success=True,
                match_index=self.match_index,
            ))


class Leader(Node):
    def __init__(self, node_id: str, followers: list):
        super().__init__(node_id)
        self.followers = followers
        self._write_queue: queue.Queue = queue.Queue()
        self._match_index = {f.node_id: -1 for f in followers}

    def write(self, key: str, value: str) -> bool:
        """Submit a write and wait for it to be committed. Returns True on success."""
        evt = threading.Event()
        self._write_queue.put((key, value, evt))
        return evt.wait(timeout=2.0)

    def _run(self):
        while self._running:
            try:
                item = self._write_queue.get(timeout=0.01)
                if item is None:
                    break
                key, value, evt = item
                self._handle_client_write(key, value, evt)
            except queue.Empty:
                self._send_heartbeats()

    def _send_heartbeats(self):
        for follower in self.followers:
            if not self._running:
                break
            msg = AppendEntriesMsg(
                leader_id=self.node_id,
                prev_index=self.get_last_log_index(),
                prev_term=self.get_last_log_term(),
                entries=[],
                leader_commit=self.commit_index,
            )
            try:
                follower.inbox.put_nowait(msg)
            except queue.Full:
                pass

    def _handle_client_write(self, key: str, value: str, evt: threading.Event):
        idx = len(self.log)
        entry = LogEntry(index=idx, term=self.term, key=key, value=value)
        self.log.append(entry)

        # Replicate to followers
        resp_queue: queue.Queue = queue.Queue()
        acks = 1  # leader counts itself

        for follower in self.followers:
            prev_idx = idx - 1
            prev_term = self.log[prev_idx].term if prev_idx >= 0 else 0
            msg = AppendEntriesMsg(
                leader_id=self.node_id,
                prev_index=prev_idx,
                prev_term=prev_term,
                entries=[entry],
                leader_commit=self.commit_index,
                _reply_to=resp_queue,
            )
            try:
                follower.inbox.put(msg, timeout=0.1)
            except queue.Full:
                pass

        # Collect acks (majority = leader + at least 1 follower)
        deadline = time.monotonic() + 1.0
        while acks < 2 and time.monotonic() < deadline:
            try:
                resp = resp_queue.get(timeout=0.05)
                if resp.success:
                    acks += 1
                    self._match_index[resp.node_id] = resp.match_index
            except queue.Empty:
                continue

        # Advance commit_index only after majority acknowledgment
        if acks >= 2:
            with self._lock:
                self.commit_index = idx

        evt.set()

    def promote_follower(self) -> Optional['Leader']:
        """Promote the first follower to a new leader."""
        if not self.followers:
            return None
        new_leader_node = self.followers[0]
        remaining = self.followers[1:]
        new_leader = Leader(
            node_id=new_leader_node.node_id + "_promoted",
            followers=remaining,
        )
        new_leader.log = list(new_leader_node.log)
        new_leader.commit_index = new_leader_node.commit_index
        new_leader.term = self.term + 1
        return new_leader


def run_test_scenario() -> bool:
    """Run a scenario that reveals the commit_index bug."""
    f1 = Follower("follower-1")
    f2 = Follower("follower-2")
    leader = Leader("leader-0", [f1, f2])

    f1.start()
    f2.start()
    leader.start()
    time.sleep(0.05)

    keys_written = {}
    for i in range(5):
        key = f"key{i}"
        value = f"value{i}"
        ok = leader.write(key, value)
        if ok:
            keys_written[key] = value

    # Give followers time to sync
    time.sleep(0.1)

    # Simulate leader crash
    leader.stop()
    time.sleep(0.05)

    new_leader = leader.promote_follower()
    if new_leader is None:
        print("ERROR: could not promote follower", file=sys.stderr)
        return False

    new_state = new_leader.get_committed_state()
    f1.stop()
    f2.stop()

    all_present = True
    for k, v in keys_written.items():
        if new_state.get(k) != v:
            print(f"DATA LOSS: {k}={v!r} missing from new leader (got {new_state.get(k)!r})",
                  file=sys.stderr)
            all_present = False

    return all_present


if __name__ == "__main__":
    ok = run_test_scenario()
    sys.exit(0 if ok else 1)
