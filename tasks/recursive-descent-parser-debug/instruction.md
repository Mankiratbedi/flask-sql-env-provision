# Recursive Descent Parser Debug

<!-- CANARY-0xB7E2D491-recursive-descent-parser-debug -->

The arithmetic expression parser at `/app/expr_parser.py` implements a recursive-descent evaluator supporting integers, floats, variables, `+`, `-`, `*`, `/`, `**` (right-associative), and unary `-`. There are exactly two bugs in the parsing methods. Fix both bugs in `/app/expr_parser.py`. Make minimal, targeted fixes — do not rewrite from scratch.

The bugs affect:
- `parse_term`: calls the wrong sub-parser for the right-hand operand of `*` and `/`, breaking operator precedence
- `parse_unary`: calls the wrong sub-parser after consuming `-`, preventing chained unary negation such as `--x`
