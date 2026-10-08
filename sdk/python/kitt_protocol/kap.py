"""KAP/1 structured final-result decoder for non-proxy model backends."""
from __future__ import annotations

import math
import re
from typing import Any

from .models import ProtocolError

_FIELD = re.compile(r"(STRING|INTEGER|DECIMAL|BOOLEAN|NULL|ARRAY|OBJECT) ([A-Za-z0-9_.]+)(?: = (.*))?\Z")
_SEGMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|0|[1-9][0-9]{0,4}\Z")
_DENIED = frozenset(("__proto__", "prototype", "constructor"))
_MISSING = object()


def decode_kap_content(raw: str) -> dict[str, Any]:
    """Parse exactly one bounded KAP FINAL containing structured content."""
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > 65536:
        raise ProtocolError("KAP exceeds 64 KiB")
    text = raw.strip()
    tick = chr(96) * 3
    fenced = re.fullmatch(
        re.escape(tick) + r"(?:kap|text)?\r?\n([\s\S]*?)\r?\n" + re.escape(tick),
        text, re.IGNORECASE,
    )
    if fenced:
        text = fenced.group(1)
    lines = text.split("\n")
    if len(lines) > 3000 or lines[0].rstrip("\r") != "KITT/1" or lines[-1].rstrip("\r") != "KITT/END":
        raise ProtocolError("Invalid KAP envelope")

    root: dict[str, Any] = {}
    assigned: set[str] = set()
    action = None

    def put(path: str, value: Any) -> None:
        parts = path.split(".")
        if (
            len(path) > 512 or len(parts) > 20
            or any(not _SEGMENT.fullmatch(part) or part in _DENIED for part in parts)
            or path in assigned
        ):
            raise ProtocolError("Duplicate or invalid KAP path")
        node: Any = root
        for index, part in enumerate(parts):
            key: int | str = int(part) if isinstance(node, list) and part.isdecimal() else part
            if isinstance(node, list) and (not isinstance(key, int) or key > 1024):
                raise ProtocolError("Invalid KAP list index")
            last = index == len(parts) - 1
            if isinstance(node, list):
                if len(node) <= key:
                    node.extend([_MISSING] * (key + 1 - len(node)))
                if last:
                    if node[key] is not _MISSING:
                        raise ProtocolError("Duplicate KAP field")
                    node[key] = value
                else:
                    if node[key] is _MISSING:
                        node[key] = [] if parts[index + 1].isdecimal() else {}
                    node = node[key]
            elif isinstance(node, dict):
                if last:
                    if key in node:
                        raise ProtocolError("Duplicate KAP field")
                    node[key] = value
                else:
                    if key not in node:
                        node[key] = [] if parts[index + 1].isdecimal() else {}
                    node = node[key]
            else:
                raise ProtocolError("Conflicting KAP types")
        assigned.add(path)

    i = 1
    while i < len(lines) - 1:
        line = lines[i].rstrip("\r")
        if line.startswith("ACTION ") and action is None:
            action = line[7:]
        elif line.startswith("TEXT "):
            end = next((j for j in range(i + 1, len(lines)) if lines[j].rstrip("\r") == "KITT/ENDTEXT"), -1)
            if end < 0 or end >= len(lines) - 1:
                raise ProtocolError("Unterminated KAP TEXT")
            put(line[5:], "\n".join(lines[i + 1:end]))
            i = end
        else:
            match = _FIELD.fullmatch(line)
            if match is None:
                raise ProtocolError("Unknown KAP directive")
            kind, path, value = match.groups()
            if kind == "STRING" and value is not None:
                parsed: Any = value
            elif kind == "INTEGER" and value is not None and re.fullmatch(r"-?(0|[1-9][0-9]*)", value):
                parsed = int(value)
                if abs(parsed) > 2 ** 53 - 1:
                    raise ProtocolError("Invalid integer")
            elif kind == "DECIMAL" and value is not None and re.fullmatch(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?", value):
                parsed = float(value)
                if not math.isfinite(parsed):
                    raise ProtocolError("Invalid decimal")
            elif kind == "BOOLEAN" and value in {"true", "false"}:
                parsed = value == "true"
            elif kind in {"NULL", "ARRAY", "OBJECT"} and value is None:
                parsed = None if kind == "NULL" else [] if kind == "ARRAY" else {}
            else:
                raise ProtocolError("Invalid KAP value")
            put(path, parsed)
        i += 1
    if action != "FINAL" or set(root) != {"content"} or not isinstance(root["content"], dict):
        raise ProtocolError("Expected a structured FINAL")

    def check(item: Any) -> None:
        if isinstance(item, list):
            if any(element is _MISSING for element in item):
                raise ProtocolError("Sparse KAP arrays")
            for element in item:
                check(element)
        elif isinstance(item, dict):
            for element in item.values():
                check(element)

    check(root["content"])
    return root["content"]
