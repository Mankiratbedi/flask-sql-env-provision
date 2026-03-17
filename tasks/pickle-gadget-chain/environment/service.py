#!/usr/bin/env python3
"""Secure object storage service.

Deserializes objects from pickle format using a strict class allowlist,
then persists them to disk.

Usage: python3 service.py < payload.pkl
"""
import io
import pickle
import json
import sys


ALLOWED_CLASSES = {
    ('builtins', 'list'),
    ('builtins', 'dict'),
    ('builtins', 'tuple'),
    ('builtins', 'int'),
    ('builtins', 'str'),
    ('builtins', 'float'),
}


class SafeUnpickler(pickle.Unpickler):
    """Unpickler that restricts deserialization to an explicit class allowlist."""

    def find_class(self, module: str, name: str):
        if (module, name) not in ALLOWED_CLASSES:
            raise pickle.UnpicklingError(
                f"Deserialization of {module}.{name} is not allowed"
            )
        return super().find_class(module, name)


def deserialize(data: bytes) -> object:
    return SafeUnpickler(io.BytesIO(data)).load()


def persist(obj: object, output_path: str) -> None:
    """Persist a deserialized object to disk.

    For dict objects, registers each key-value pair as a named variable
    in the local scope for downstream processing before writing.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            # Register key-value pairs as named local variables
            # so they can be referenced by name in later pipeline stages.
            exec(f"stored_{key} = {value!r}")  # BUG: key is not sanitized

    with open(output_path, 'w') as f:
        json.dump({'status': 'saved', 'type': type(obj).__name__}, f)


def main():
    payload = sys.stdin.buffer.read()
    try:
        obj = deserialize(payload)
    except pickle.UnpicklingError as e:
        print(f"Deserialization blocked: {e}", file=sys.stderr)
        sys.exit(1)
    persist(obj, '/app/output.json')
    print("Object saved to /app/output.json")


if __name__ == '__main__':
    main()
