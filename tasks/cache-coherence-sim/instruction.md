# MESI Cache Coherence Simulator — Debug

<!-- CANARY-0x9C1D2E3F-cache-coherence-sim -->

A MESI cache-coherence protocol simulator at `/app/mesi_sim.py` models four processors sharing main memory via a bus. Given deterministic access traces, the simulator should produce the exact final memory state after all operations.

There are exactly four bugs in `/app/mesi_sim.py`. The bugs are syntactically valid — the simulator runs without exceptions but produces wrong final memory values for specific access sequences. Fix all four and make minimal, targeted changes — do not rewrite from scratch.

After fixing, run the simulator on all three traces and write results to `/app/result.json`:

```bash
python3 /app/mesi_sim.py
```

`/app/result.json` must be a JSON object with keys `trace_a`, `trace_b`, and `trace_c`, each mapping to a dict of `{ "address": final_value }` pairs representing final memory contents after the trace completes.
