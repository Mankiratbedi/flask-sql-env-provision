# Hash Oracle Reverse Engineering

A stripped binary at `/app/hash_oracle` implements a custom 32-bit hash function. No source code is available.

## Binary Interface

- Reads one line of **lowercase hex** from stdin
- Outputs the hash as an **unsigned decimal integer** followed by a newline

```bash
echo "deadbeef" | /app/hash_oracle   # outputs a decimal number
echo "" | /app/hash_oracle            # hash of empty byte string
echo "00" | /app/hash_oracle          # hash of single zero byte
echo "ff" | /app/hash_oracle          # hash of single 0xff byte
```

## Your Task

Reverse-engineer the hash algorithm by probing the binary with carefully chosen inputs, then implement it in Python.

Create `/app/myhash.py` containing a function:

```python
def custom_hash(data: bytes) -> int:
    """Return the 32-bit hash as an unsigned integer (0..4294967295)."""
    ...
```

## Strategy

- Start with simple inputs: empty string, individual byte values `\x00` through `\xff`
- Look for an initialization constant — what does the empty-string hash tell you?
- Test repeated bytes and single-bit differences to identify the mixing operations
- Common operations: XOR, bit rotation, multiplication by a constant

## Output

`/app/myhash.py` must define `custom_hash(data: bytes) -> int` returning values in `[0, 4294967295]`.
