# CANARY-0xB7E2D491-recursive-descent-parser-debug
"""Recursive-descent parser and evaluator for arithmetic expressions.

Grammar:
  expr    = term (('+' | '-') term)*      # left-associative
  term    = power (('*' | '/') power)*    # left-associative
  power   = unary ('**' unary)*           # right-associative
  unary   = '-' unary | primary
  primary = NUMBER | IDENT | '(' expr ')'

Supported: integers, floats, named variables, +, -, *, /, ** (right-assoc), unary -.
"""
import re
import math
import json
from typing import Any


class ParseError(Exception):
    pass


class Token:
    __slots__ = ("type", "value")

    def __init__(self, type_: str, value: Any):
        self.type = type_
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.type!r}, {self.value!r})"


_TOKEN_RE = re.compile(
    r"(?P<NUMBER>\d+\.?\d*(?:[eE][+-]?\d+)?)"
    r"|(?P<POW>\*\*)"
    r"|(?P<OP>[+\-*/()])"
    r"|(?P<IDENT>[A-Za-z_]\w*)"
    r"|(?P<WS>\s+)"
)


def tokenize(text: str) -> list:
    tokens = []
    for m in _TOKEN_RE.finditer(text):
        kind = m.lastgroup
        if kind == "WS":
            continue
        if kind == "NUMBER":
            raw = m.group()
            val = float(raw) if ("." in raw or "e" in raw.lower()) else int(raw)
            tokens.append(Token("NUMBER", val))
        elif kind == "POW":
            tokens.append(Token("**", "**"))
        elif kind == "OP":
            tokens.append(Token(m.group(), m.group()))
        elif kind == "IDENT":
            tokens.append(Token("IDENT", m.group()))
    tokens.append(Token("EOF", None))
    return tokens


class Parser:
    def __init__(self, tokens: list, env: dict | None = None):
        self.tokens = tokens
        self.pos = 0
        self.env = env or {}

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def consume(self, expected: str | None = None) -> Token:
        tok = self.tokens[self.pos]
        if expected is not None and tok.type != expected:
            raise ParseError(f"Expected {expected!r}, got {tok.type!r} ({tok.value!r})")
        self.pos += 1
        return tok

    def parse(self) -> float:
        result = self.parse_expr()
        self.consume("EOF")
        return result

    def parse_expr(self) -> float:
        """Parse addition and subtraction (left-associative)."""
        left = self.parse_term()
        while self.peek().type in ("+", "-"):
            op = self.consume().type
            right = self.parse_term()
            if op == "+":
                left = left + right
            else:
                left = left - right
        return left

    def parse_term(self) -> float:
        """Parse multiplication and division (left-associative)."""
        left = self.parse_power()
        while self.peek().type in ("*", "/"):
            op = self.consume().type
            right = self.parse_expr()  # BUG-1: should call parse_power(), not parse_expr()
            if op == "*":
                left = left * right
            else:
                if right == 0:
                    raise ParseError("Division by zero")
                left = left / right
        return left

    def parse_power(self) -> float:
        """Parse exponentiation (right-associative)."""
        base = self.parse_unary()
        if self.peek().type == "**":
            self.consume("**")
            exp = self.parse_power()
            return base ** exp
        return base

    def parse_unary(self) -> float:
        """Parse unary minus."""
        if self.peek().type == "-":
            self.consume("-")
            return -self.parse_primary()  # BUG-2: should call parse_unary() not parse_primary()
        return self.parse_primary()

    def parse_primary(self) -> float:
        """Parse number, variable reference, or parenthesised expression."""
        tok = self.peek()
        if tok.type == "NUMBER":
            self.consume()
            return float(tok.value)
        if tok.type == "IDENT":
            self.consume()
            name = tok.value
            if name == "pi":
                return math.pi
            if name == "e":
                return math.e
            if name not in self.env:
                raise ParseError(f"Undefined variable: {name!r}")
            return float(self.env[name])
        if tok.type == "(":
            self.consume("(")
            val = self.parse_expr()
            self.consume(")")
            return val
        raise ParseError(f"Unexpected token {tok!r} at position {self.pos}")


def evaluate(expr: str, env: dict | None = None) -> float:
    """Parse and evaluate an arithmetic expression string."""
    tokens = tokenize(expr)
    parser = Parser(tokens, env)
    return parser.parse()


if __name__ == "__main__":
    cases = [
        ("2 + 3 * 4", {}, 14.0),
        ("10 - 3 - 2", {}, 5.0),
        ("24 / 6 / 2", {}, 2.0),
        ("--5", {}, 5.0),
        ("2 ** 3 ** 2", {}, 512.0),
        ("x * 2 + y", {"x": 3.0, "y": 4.0}, 10.0),
    ]
    results = {}
    for expr, env, expected in cases:
        try:
            got = evaluate(expr, env)
            results[expr] = {"got": got, "expected": expected, "ok": abs(got - expected) < 1e-9}
        except Exception as ex:
            results[expr] = {"error": str(ex), "expected": expected, "ok": False}
    with open("/app/result.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Done. Results in /app/result.json")
