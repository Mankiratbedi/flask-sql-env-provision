# ASAN Heap Detective

A C key-value store has a memory safety bug that causes it to crash in production.

## Your Task

1. Read the source code at `/app/kvstore.c` and the crash trace at `/app/asan_trace.txt`
2. Identify and fix the memory safety bug directly in `/app/kvstore.c`
3. Compile the fixed binary:
   ```bash
   gcc -O2 -o /app/kvstore_fixed /app/kvstore.c
   ```
4. Verify your fix:
   ```bash
   /app/kvstore_fixed < /app/trigger.txt
   ```

## The Program

`kvstore.c` implements an in-memory key-value store that reads commands from stdin:

```
SET <key> <value>    # store a value
GET <key>            # print key=value, or key=NOT_FOUND
DELETE <key>         # remove a key
```

## Expected Output

When run with `/app/trigger.txt`, the fixed binary must produce **exactly**:
```
alice=100
alice=NOT_FOUND
bob=200
```

Without crashing or producing undefined behavior.

## Deliverables

- Fixed `/app/kvstore.c` (the root cause must be properly fixed)
- Compiled `/app/kvstore_fixed` binary
