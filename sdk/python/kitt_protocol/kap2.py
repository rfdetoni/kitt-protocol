"""KAP/2 compact model-facing final decoder.

Only structured FINAL payloads are decoded here. Tool authority belongs to the host.
The grammar intentionally supports a bounded, deterministic subset of TOON.
"""
from __future__ import annotations

import json
import math
import re
from typing import Any

from .models import ProtocolError

_MAX_BYTES = 65536
_MAX_LINES = 3000
_MAX_DEPTH = 20
_MAX_ITEMS = 1024
_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_FIELD = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)(?:\[([0-9]+)\](?:\{([A-Za-z0-9_,]+)\})?)?:(?: (.*))?\Z")
_LITERAL = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)<<([A-Z_][A-Z0-9_]{0,24})\Z")
_INTEGER = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
_DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)\.[0-9]+\Z")
_DENIED = frozenset(("__proto__", "prototype", "constructor"))


def _atom(text: str) -> Any:
    if text.startswith('"'):
        try:
            value = json.loads(text)
        except (ValueError, TypeError) as exc:
            raise ProtocolError("Invalid KAP/2 quoted scalar") from exc
        if not isinstance(value, str):
            raise ProtocolError("Quoted KAP/2 scalar must be a string")
        return value
    if text == "true":
        return True
    if text == "false":
        return False
    if text == "null":
        return None
    if _INTEGER.fullmatch(text):
        value = int(text)
        if abs(value) > 2**53 - 1:
            raise ProtocolError("KAP/2 integer outside safe range")
        return value
    if _DECIMAL.fullmatch(text):
        value = float(text)
        if not math.isfinite(value):
            raise ProtocolError("KAP/2 non-finite decimal")
        return value
    return text


def _csv(line: str) -> list[str]:
    """TOON-style CSV cells with doubled quotes, retaining quoted scalar types."""
    cells: list[str] = []
    i = 0
    while i <= len(line):
        start = i
        if i < len(line) and line[i] == '"':
            i += 1
            value: list[str] = []
            while i < len(line):
                if line[i] == '"':
                    if i + 1 < len(line) and line[i + 1] == '"':
                        value.append('"')
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    value.append(line[i])
                    i += 1
            else:
                raise ProtocolError("Unterminated KAP/2 CSV quote")
            if i < len(line) and line[i] != ',':
                raise ProtocolError("Invalid KAP/2 CSV delimiter")
            cells.append(json.dumps("".join(value)))
        else:
            while i < len(line) and line[i] != ',':
                if line[i] == '"':
                    raise ProtocolError("Unquoted KAP/2 CSV quote")
                i += 1
            cells.append(line[start:i].strip())
        if i == len(line):
            break
        i += 1
    return cells


def decode_kap2_content(raw: str) -> dict[str, Any]:
    """Decode exactly one structured K2 F envelope, without implicit repair."""
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > _MAX_BYTES:
        raise ProtocolError("KAP/2 exceeds 64 KiB")
    lines = raw.strip().split("\n")
    if len(lines) > _MAX_LINES or lines[0].rstrip("\r") != "K2 F" or lines[-1].rstrip("\r") != "K2/END":
        raise ProtocolError("Expected a complete structured K2 F envelope")
    body = [line.rstrip("\r") for line in lines[1:-1]]
    index = 0

    def parse(indent: int, depth: int) -> dict[str, Any]:
        nonlocal index
        if depth > _MAX_DEPTH:
            raise ProtocolError("KAP/2 nesting limit exceeded")
        result: dict[str, Any] = {}
        while index < len(body):
            raw_line = body[index]
            if "\t" in raw_line:
                raise ProtocolError("KAP/2 tabs are forbidden")
            spaces = len(raw_line) - len(raw_line.lstrip(" "))
            if spaces < indent:
                break
            if spaces != indent:
                raise ProtocolError("Invalid KAP/2 indentation")
            line = raw_line[indent:]
            match = _FIELD.fullmatch(line)
            literal = _LITERAL.fullmatch(line)
            if not match and not literal:
                raise ProtocolError("Invalid KAP/2 field")
            key = (match or literal).group(1)
            if key in _DENIED or key in result:
                raise ProtocolError("Unsafe or duplicate KAP/2 field")
            index += 1
            if literal:
                marker = literal.group(2)
                start = index
                while index < len(body) and body[index] != marker:
                    index += 1
                if index == len(body):
                    raise ProtocolError("Unterminated KAP/2 literal")
                result[key] = "\n".join(body[start:index])
                index += 1
                continue
            count_text, fields_text, scalar = match.group(2, 3, 4)
            if count_text is not None:
                count = int(count_text)
                if count > _MAX_ITEMS:
                    raise ProtocolError("KAP/2 array too large")
                headers = fields_text.split(",") if fields_text else None
                if headers and (len(set(headers)) != len(headers) or any(not _KEY.fullmatch(h) or h in _DENIED for h in headers)):
                    raise ProtocolError("Invalid KAP/2 table headers")
                if scalar is not None:
                    raise ProtocolError("KAP/2 array cannot have scalar")
                rows: list[Any] = []
                for _ in range(count):
                    if index >= len(body) or not body[index].startswith(" " * (indent + 2)) or body[index].startswith(" " * (indent + 3)):
                        raise ProtocolError("Wrong KAP/2 row count or indentation")
                    row = body[index][indent + 2:]
                    index += 1
                    if headers:
                        cells = _csv(row)
                        if len(cells) != len(headers):
                            raise ProtocolError("Wrong KAP/2 table column count")
                        rows.append(dict(zip(headers, (_atom(cell) for cell in cells))))
                    else:
                        if not row.startswith("- "):
                            raise ProtocolError("Expected KAP/2 list item")
                        rows.append(_atom(row[2:]))
                result[key] = rows
            elif scalar is not None:
                result[key] = _atom(scalar)
            elif index < len(body) and body[index].startswith(" " * (indent + 2)):
                result[key] = parse(indent + 2, depth + 1)
            else:
                result[key] = {}
        return result

    parsed = parse(0, 0)
    if index != len(body) or not parsed:
        raise ProtocolError("Incomplete KAP/2 final content")
    return parsed
