#!/usr/bin/env python3
import ast
import io
import sys
import tokenize
from pathlib import Path


def _find_docstring_ranges(source: str):
    ranges = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ranges

    # Module docstring
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(
        getattr(tree.body[0], "value", None), ast.Constant
    ) and isinstance(tree.body[0].value.value, str):
        node = tree.body[0]
        ranges.append((node.lineno, getattr(node, "end_lineno", node.lineno)))

    # Class/Function docstrings
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(
                getattr(body[0], "value", None), ast.Constant
            ) and isinstance(body[0].value.value, str):
                ds = body[0]
                ranges.append((ds.lineno, getattr(ds, "end_lineno", ds.lineno)))

    return ranges


def strip_docstrings(source: str) -> str:
    lines = source.splitlines()
    ranges = _find_docstring_ranges(source)
    if not ranges:
        return source
    # Merge overlapping ranges
    ranges.sort()
    merged = []
    for start, end in ranges:
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    # Remove lines (1-based to 0-based)
    keep = []
    remove = set()
    for s, e in merged:
        remove.update(range(s - 1, e))
    for i, line in enumerate(lines):
        if i not in remove:
            keep.append(line)
    return "\n".join(keep) + ("\n" if source.endswith("\n") else "")


def strip_comments(source: str) -> str:
    buf = io.StringIO(source)
    out_tokens = []
    try:
        for tok in tokenize.generate_tokens(buf.readline):
            tok_type, tok_str, start, end, line = tok
            if tok_type == tokenize.COMMENT:
                # Drop comments
                continue
            out_tokens.append(tok)
        return tokenize.untokenize(out_tokens)
    except tokenize.TokenError:
        # Fallback: return original source if tokenization fails
        return source


def process_file(path: Path):
    src = path.read_text(encoding="utf-8")
    no_doc = strip_docstrings(src)
    no_comments = strip_comments(no_doc)
    path.write_text(no_comments, encoding="utf-8")


def main(argv):
    if len(argv) < 2:
        print("Usage: strip_comments.py <file1.py> [file2.py ...]", file=sys.stderr)
        return 2
    for p in argv[1:]:
        process_file(Path(p))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
