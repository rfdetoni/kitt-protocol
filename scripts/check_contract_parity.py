#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fail(message: str) -> None:
    raise SystemExit(f"protocol parity check failed: {message}")


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def rust_kinds() -> dict[str, str]:
    block = re.search(r"pub mod kinds \{(?P<body>.*?)\n\}", read("src/lib.rs"), re.S)
    if not block:
        fail("Rust kinds module not found")
    return dict(re.findall(r'pub const ([A-Z0-9_]+): &str = "([^"]+)";', block.group("body")))


def python_kinds() -> dict[str, str]:
    source = read("sdk/python/kitt_protocol/models.py")
    return dict(re.findall(r'^([A-Z][A-Z0-9_]+) = "([^"]+)"$', source, re.M))


def typescript_kinds() -> dict[str, str]:
    source = read("sdk/typescript/src/index.ts")
    block = re.search(r"export const KINDS = \{(?P<body>.*?)\} as const;", source, re.S)
    if not block:
        fail("TypeScript KINDS object not found")
    return dict(re.findall(r'\b([A-Z0-9_]+):\s*"([^"]+)"', block.group("body")))


def rust_enum(name: str) -> set[str]:
    source = read("src/lib.rs")
    match = re.search(
        rf"pub enum {re.escape(name)} \{{(?P<body>.*?)\n\}}",
        source,
        re.S,
    )
    if not match:
        fail(f"Rust enum {name} not found")
    variants = re.findall(r"^\s*([A-Z][A-Za-z0-9_]*)\s*,?\s*$", match.group("body"), re.M)
    return {snake(value) for value in variants}


def ts_union(name: str) -> set[str]:
    source = read("sdk/typescript/src/index.ts")
    match = re.search(
        rf"export type {re.escape(name)}\s*=\s*(?P<body>.*?);",
        source,
        re.S,
    )
    if not match:
        fail(f"TypeScript union {name} not found")
    return set(re.findall(r'"([^"]+)"', match.group("body")))


def schema_enum(property_name: str) -> set[str]:
    payload = json.loads(read("schemas/memory.schema.json"))
    values = payload["properties"][property_name]["enum"]
    return {str(value) for value in values}


def compare(label: str, *values: tuple[str, set[str] | dict[str, str]]) -> None:
    baseline_name, baseline = values[0]
    for name, value in values[1:]:
        if value != baseline:
            fail(f"{label} drift: {baseline_name}={baseline!r}; {name}={value!r}")


def required_memory_remember_fields() -> None:
    fields = ("sensitivity", "scope")

    python_source = read("sdk/python/kitt_protocol/models.py")
    module = ast.parse(python_source)
    python_class = next(
        (
            node
            for node in module.body
            if isinstance(node, ast.ClassDef) and node.name == "MemoryRememberRequest"
        ),
        None,
    )
    if python_class is None:
        fail("Python MemoryRememberRequest not found")

    python_fields = {
        node.target.id: node
        for node in python_class.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    for field in fields:
        node = python_fields.get(field)
        if node is None or node.value is not None:
            fail(f"Python MemoryRememberRequest.{field} must be required")

    typescript_source = read("sdk/typescript/src/index.ts")
    ts_block = re.search(
        r"export interface MemoryRememberRequest \{(?P<body>.*?)\n\}",
        typescript_source,
        re.S,
    )
    if not ts_block:
        fail("TypeScript MemoryRememberRequest not found")
    for field in fields:
        if not re.search(rf"\b{field}\s*:", ts_block.group("body")):
            fail(f"TypeScript MemoryRememberRequest.{field} must be required")

    rust_source = read("src/lib.rs")
    rust_block = re.search(
        r"pub struct MemoryRememberRequest \{(?P<body>.*?)\n\}",
        rust_source,
        re.S,
    )
    if not rust_block:
        fail("Rust MemoryRememberRequest not found")
    for field in fields:
        if not re.search(rf"pub {field}:\s*[^,]+,", rust_block.group("body")):
            fail(f"Rust MemoryRememberRequest.{field} must be required")


def agentic_planning_fields() -> None:
    python_module = ast.parse(read("sdk/python/kitt_protocol/agentic.py"))
    rust = read("src/agentic.rs")
    ts = read("sdk/typescript/src/index.ts")
    schema = json.loads(read("schemas/agentic-planning.schema.json"))["$defs"]
    for name in ("KittRequestMetadata", "HostExecutionState", "PlanTaskProposal", "PlanProposal", "SubagentReport"):
        cls = next(n for n in python_module.body if isinstance(n, ast.ClassDef) and n.name == name)
        py_fields = {n.target.id for n in cls.body if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)}
        rust_block = re.search(rf"pub struct {name} \{{([^}}]+)\}}", rust).group(1)
        ts_block = re.search(rf"export interface {name} \{{([^}}]+)\}}", ts).group(1)
        compare(name,
            ("python", py_fields),
            ("rust", set(re.findall(r"pub (\w+):", rust_block))),
            ("typescript", set(re.findall(r"(\w+)\??\s*:", ts_block))),
            ("schema", set(schema[name]["properties"])),
        )


def provider_argument_limit_parity() -> None:
    module = ast.parse(read("sdk/python/kitt_protocol/provider_limits.py"))
    assignment = next(node for node in module.body if isinstance(node, ast.Assign))
    def integer(expr):
        if isinstance(expr, ast.Constant) and type(expr.value) is int:
            return expr.value
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Mult):
            return integer(expr.left) * integer(expr.right)
        fail("provider argument limit is not a bounded integer expression")
    values = {"python": integer(assignment.value)}
    for label, path, pattern in (
        ("typescript", "sdk/typescript/src/provider-limits.ts", r"MAX_TOOL_ARGUMENT_BYTES = ([0-9 *]+);"),
        ("rust", "src/lib.rs", r"MAX_TOOL_ARGUMENT_BYTES: usize = ([0-9 *]+);"),
    ):
        match = re.search(pattern, read(path))
        if not match:
            fail(f"{label} provider argument limit missing")
        values[label] = integer(ast.parse(match.group(1), mode="eval").body)
    if len(set(values.values())) != 1:
        fail(f"provider argument limit drift: {values}")


def main() -> int:
    provider_argument_limit_parity()
    required_memory_remember_fields()
    agentic_planning_fields()
    compare(
        "message kinds",
        ("rust", rust_kinds()),
        ("python", python_kinds()),
        ("typescript", typescript_kinds()),
    )
    for rust_name, ts_name, schema_name in (
        ("MemoryKind", "MemoryKind", "kind"),
        ("Sensitivity", "Sensitivity", "sensitivity"),
        ("MemoryScope", "MemoryScope", "scope"),
    ):
        compare(
            rust_name,
            ("rust", rust_enum(rust_name)),
            ("typescript", ts_union(ts_name)),
            ("schema", schema_enum(schema_name)),
        )
    print("protocol parity: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
