"""Bounded, fail-closed KAP/2 model-facing serializer. The host owns authority."""
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
_KEY_TOKEN = r'(?:"(?:[^"\\]|\\.)*"|[A-Za-z_][A-Za-z0-9_]*)'
_FIELD = re.compile(rf"({_KEY_TOKEN})(?:\[([0-9]+)\](?:\{{(.+)\}})?)?:(?: (.*))?\Z")
_LITERAL = re.compile(rf"({_KEY_TOKEN})<<([A-Z_][A-Z0-9_]{{0,24}})(?::([0-9]+))?\Z")
_INTEGER = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
_DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)\.[0-9]+\Z")
_DENIED = frozenset(("__proto__", "prototype", "constructor"))


class KAP2Error(ProtocolError):
    def __init__(self, message: str, code: str = "E_FIELD", line: int | None = None):
        super().__init__(message)
        self.code = code
        self.line = line


def _fail(message: str, code: str = "E_FIELD", line: int | None = None) -> None:
    raise KAP2Error(message, code, line)


def _safe(value: str, line: int | None = None, literal: bool = False) -> None:
    for char in value:
        cp = ord(char)
        if 0xD800 <= cp <= 0xDFFF:
            _fail("Invalid KAP/2 Unicode scalar", "E_UTF8", line)
        if cp < 32 and not (literal and char in ("\n", "\t")) or cp == 127:
            _fail("Invalid KAP/2 control character", "E_SCALAR", line)


def _structure(line: str, number: int) -> None:
    if "\t" in line:
        _fail("KAP/2 tabs are forbidden", "E_TAB", number)
    if line.endswith(" "):
        _fail("KAP/2 trailing whitespace", "E_WHITESPACE", number)
    _safe(line, number)


def _key(token: str, line: int) -> str:
    if token.startswith('"'):
        try:
            value = json.loads(token)
        except ValueError:
            _fail("Invalid quoted KAP/2 key", "E_FIELD", line)
        if not isinstance(value, str):
            _fail("Invalid quoted KAP/2 key", "E_FIELD", line)
    else:
        if not _KEY.fullmatch(token):
            _fail("Invalid KAP/2 key", "E_FIELD", line)
        value = token
    _safe(value, line)
    if value in _DENIED:
        _fail("Unsafe KAP/2 field", "E_KEY_UNSAFE", line)
    return value


def _csv(text: str, line: int) -> list[tuple[str, bool]]:
    cells: list[tuple[str, bool]] = []
    pos = 0
    while pos <= len(text):
        start = pos
        if pos < len(text) and text[pos] == '"':
            pos += 1
            value: list[str] = []
            while pos < len(text):
                if text[pos] == '"':
                    if pos + 1 < len(text) and text[pos + 1] == '"':
                        value.append('"')
                        pos += 2
                    else:
                        pos += 1
                        break
                else:
                    value.append(text[pos])
                    pos += 1
            else:
                _fail("Unterminated KAP/2 CSV quote", "E_SCALAR", line)
            if pos < len(text) and text[pos] != ",":
                _fail("Invalid KAP/2 CSV delimiter", "E_SCALAR", line)
            cell = "".join(value)
            _safe(cell, line)
            cells.append((cell, True))
        else:
            while pos < len(text) and text[pos] != ",":
                if text[pos] == '"':
                    _fail("Unquoted KAP/2 CSV quote", "E_SCALAR", line)
                pos += 1
            cell = text[start:pos].strip(" ")
            _safe(cell, line)
            cells.append((cell, False))
        if pos == len(text):
            break
        pos += 1
    return cells


def _types(schema: Any) -> set[str]:
    if not isinstance(schema, dict):
        return set()
    types = schema.get("type")
    if isinstance(types, str):
        return {types}
    if isinstance(types, list) and all(isinstance(v, str) for v in types):
        return set(types)
    for name in ("anyOf", "oneOf"):
        alternatives = schema.get(name)
        if isinstance(alternatives, list) and alternatives and all(isinstance(s, dict) and "type" in s for s in alternatives):
            return set().union(*(_types(s) for s in alternatives))
    return set()


def _child(schema: Any, name: str | None = None) -> Any:
    if not isinstance(schema, dict):
        return None
    if name is None:
        return schema.get("items")
    properties = schema.get("properties")
    if isinstance(properties, dict) and name in properties:
        return properties[name]
    return schema.get("additionalProperties")


def _atom(text: str, line: int, schema: Any = None, quoted: bool = False) -> Any:
    if quoted:
        _safe(text, line)
        return text
    if text.startswith('"'):
        try:
            value = json.loads(text)
        except ValueError:
            _fail("Invalid KAP/2 quoted scalar", "E_SCALAR", line)
        if not isinstance(value, str):
            _fail("Quoted KAP/2 scalar must be a string", "E_SCALAR", line)
        _safe(value, line)
        return value
    _safe(text, line)
    if text == "-0" or (_DECIMAL.fullmatch(text) and text.startswith("-") and float(text) == 0):
        _fail("Noncanonical KAP/2 negative zero", "E_SCALAR", line)
    value: Any = text
    kind = "string"
    if text == "null":
        value, kind = None, "null"
    elif text in ("true", "false"):
        value, kind = text == "true", "boolean"
    elif _INTEGER.fullmatch(text):
        value, kind = int(text), "integer"
        if abs(value) > 2 ** 53 - 1:
            _fail("KAP/2 integer outside safe range", "E_NUMBER_RANGE", line)
    elif _DECIMAL.fullmatch(text):
        value, kind = float(text), "number"
        if not math.isfinite(value):
            _fail("KAP/2 non-finite decimal", "E_NUMBER_RANGE", line)
    types = _types(schema)
    if kind != "string" and "string" in types and not (types & ({kind} | ({"number"} if kind == "integer" else set()))):
        return text
    return value


def _lines(raw: str) -> list[str]:
    if not isinstance(raw, str):
        _fail("Invalid KAP/2 input", "E_UTF8")
    try:
        size = len(raw.encode("utf-8", "strict"))
    except UnicodeError:
        _fail("Invalid KAP/2 UTF-8", "E_UTF8")
    if size > _MAX_BYTES:
        _fail("KAP/2 exceeds 64 KiB", "E_SIZE")
    if "\ufeff" in raw:
        _fail("KAP/2 BOM forbidden", "E_UTF8")
    lines = raw.strip(" \r\n").split("\n")
    if len(lines) > _MAX_LINES:
        _fail("KAP/2 line limit exceeded", "E_LINES")
    return [line[:-1] if line.endswith("\r") else line for line in lines]


def _decode(raw: str, schema: Any = None) -> dict[str, Any]:
    lines = _lines(raw)
    if lines[-1] != "K2/END":
        _fail("Missing K2/END", "E_TERMINATOR")
    header = re.fullmatch(r"K2 ([TFWQ])(?: ([A-Za-z0-9_.:-]{1,64}))?", lines[0])
    if not header or (header[1] == "T") != (header[2] is not None):
        _fail("Invalid K2 header", "E_HEADER", 1)
    action, tool = header.groups()
    body = lines[1:-1]
    summary = ""
    offset = 1
    if body and body[0].startswith("@summary:"):
        _structure(body[0], 2)
        if not body[0].startswith("@summary: ") or len(body[0][10:]) > 400:
            _fail("Invalid KAP/2 summary", "E_SCALAR", 2)
        summary = body.pop(0)[10:]
        offset = 2
    if action in ("W", "Q") and body:
        _fail("KAP/2 W/Q body not allowed", "E_BODY_NOT_ALLOWED", offset + 1)
    cursor = 0

    def parse(indent: int, depth: int, current_schema: Any = None) -> dict[str, Any]:
        nonlocal cursor
        if depth > _MAX_DEPTH:
            _fail("KAP/2 depth exceeded", "E_DEPTH", offset + cursor + 1)
        obj: dict[str, Any] = {}
        while cursor < len(body):
            raw_line = body[cursor]
            number = offset + cursor + 1
            _structure(raw_line, number)
            leading = len(raw_line) - len(raw_line.lstrip(" "))
            if leading < indent:
                break
            if leading != indent:
                _fail("Invalid KAP/2 indentation", "E_INDENT", number)
            token = raw_line[indent:]
            field = _FIELD.fullmatch(token)
            literal = _LITERAL.fullmatch(token)
            if field is None and literal is None:
                _fail("Invalid KAP/2 field", "E_FIELD", number)
            key = _key((field or literal)[1], number)
            if key in obj:
                _fail("Duplicate KAP/2 key", "E_KEY_DUPLICATE", number)
            cursor += 1
            item_schema = _child(current_schema, key)
            if literal is not None:
                marker, count_text = literal[2], literal[3]
                start = cursor
                if count_text is None:
                    while cursor < len(body) and body[cursor] != marker:
                        cursor += 1
                    if cursor == len(body):
                        _fail("Unterminated KAP/2 literal", "E_LITERAL_UNTERMINATED", number)
                else:
                    expected = int(count_text)
                    if expected > _MAX_BYTES:
                        _fail("Literal too long", "E_LITERAL_LENGTH", number)
                    while cursor < len(body) and len("\n".join(body[start:cursor]).encode("utf-8")) < expected:
                        cursor += 1
                    if cursor >= len(body) or body[cursor] != marker or len("\n".join(body[start:cursor]).encode("utf-8")) != expected:
                        _fail("KAP/2 literal length mismatch", "E_LITERAL_LENGTH", number)
                text = "\n".join(body[start:cursor])
                _safe(text, number, literal=True)
                obj[key] = text
                cursor += 1
                continue
            count_text, columns, scalar = field[2], field[3], field[4]
            if count_text is not None:
                count = int(count_text)
                if count > _MAX_ITEMS:
                    _fail("KAP/2 array too large", "E_ARRAY_SIZE", number)
                if scalar is not None:
                    _fail("Unexpected KAP/2 array scalar", "E_FIELD", number)
                headers = None
                if columns is not None:
                    headers = [_key(json.dumps(text) if quoted else text, number) for text, quoted in _csv(columns, number)]
                    if len(set(headers)) != len(headers):
                        _fail("Duplicate KAP/2 table headers", "E_TABLE_HEADERS", number)
                result: list[Any] = []
                row_schema = _child(item_schema)
                for _ in range(count):
                    if cursor >= len(body):
                        _fail("Incomplete KAP/2 array", "E_ARRAY_ROWS", number)
                    row = body[cursor]
                    row_number = offset + cursor + 1
                    _structure(row, row_number)
                    row_leading = len(row) - len(row.lstrip(" "))
                    if row_leading != indent + 2:
                        _fail("Invalid KAP/2 array indentation", "E_ARRAY_ROWS", row_number)
                    payload = row[indent + 2:]
                    cursor += 1
                    if headers is not None:
                        cells = _csv(payload, row_number)
                        if len(cells) != len(headers):
                            _fail("Wrong KAP/2 table columns", "E_TABLE_COLUMNS", row_number)
                        result.append({head: _atom(value, row_number, _child(row_schema, head), quoted)
                                       for head, (value, quoted) in zip(headers, cells)})
                    elif payload == "-":
                        nested = parse(indent + 4, depth + 2, row_schema)
                        if not nested:
                            _fail("Empty KAP/2 object item", "E_FIELD", row_number)
                        result.append(nested)
                    elif payload.startswith("- "):
                        result.append(_atom(payload[2:], row_number, row_schema))
                    else:
                        _fail("Expected KAP/2 list item", "E_ARRAY_ROWS", row_number)
                obj[key] = result
            elif scalar == "{}":
                obj[key] = {}
            elif scalar is not None:
                obj[key] = _atom(scalar, number, item_schema)
            elif cursor < len(body) and body[cursor].startswith(" " * (indent + 2)):
                nested = parse(indent + 2, depth + 1, item_schema)
                if not nested:
                    _fail("Empty KAP/2 nested object", "E_FIELD", number)
                obj[key] = nested
            else:
                _fail("Missing KAP/2 field value", "E_FIELD", number)
        return obj

    if action == "F" and not body:
        _fail("Empty K2 final", "E_FIELD")
    if action in ("W", "Q"):
        content = None
    elif body and (_FIELD.fullmatch(body[0]) or _LITERAL.fullmatch(body[0])):
        content = parse(0, 0, schema)
        if cursor != len(body):
            _fail("Incomplete KAP/2 object", "E_INDENT", offset + cursor + 1)
    else:
        if action == "T":
            _fail("Tools require fields", "E_FIELD", offset + 1)
        for idx, line in enumerate(body):
            _structure(line, offset + idx + 1)
            if line == "K2/END" or re.match(r"K2 [TFWQ](?: |$)", line):
                _fail("Competing KAP/2 action", "E_COMPETING_FRAME", offset + idx + 1)
        content = "\n".join(body)
    if action == "F" and (not content or isinstance(content, str) and not content.strip()):
        _fail("Empty K2 final", "E_FIELD")
    return {"action": {"T": "use_tool", "F": "final_response", "W": "request_workspace", "Q": "request_tools"}[action],
            "tool": tool, "tool_input": content if action == "T" else None,
            "content": content if action == "F" else None,
            "reasoning_summary": summary, "loop": None}


def decode_kap2_frame(raw: str, schema: Any = None) -> dict[str, Any]:
    return _decode(raw, schema)


def decode_kap2_content(raw: str, schema: Any = None) -> dict[str, Any]:
    frame = _decode(raw, schema)
    if frame["action"] != "final_response" or not isinstance(frame["content"], dict):
        _fail("Expected structured K2 F", "E_HEADER")
    return frame["content"]


def _scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        if abs(value) > 2**53 - 1:
            _fail("Unsafe KAP/2 integer", "E_NUMBER_RANGE")
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value) or value == 0 and math.copysign(1, value) < 0:
            _fail("Noncanonical float", "E_SCALAR")
        rendered = str(value)
        if "e" in rendered or "E" in rendered:
            _fail("Nonrepresentable KAP/2 decimal", "E_SCALAR")
        return rendered
    if not isinstance(value, str):
        _fail("Unsupported KAP/2 value", "E_SCALAR")
    _safe(value)
    if "\n" in value or "\r" in value:
        _fail("Multiline values require literal blocks", "E_SCALAR")
    if (value == "" or value != value.strip(" ") or value.startswith('"') or
        value in ("true", "false", "null") or _INTEGER.fullmatch(value) or
        _DECIMAL.fullmatch(value) or value.startswith("-0") or '"' in value):
        return json.dumps(value, ensure_ascii=False)
    return value


def encode_kap2(value: dict[str, Any]) -> str:
    if not isinstance(value, dict) or not value:
        _fail("KAP/2 final must have fields", "E_FIELD")
    lines: list[str] = ["K2 F"]

    def name(key: str) -> str:
        if not isinstance(key, str):
            _fail("Non-string KAP/2 key", "E_FIELD")
        _safe(key)
        if key in _DENIED:
            _fail("Unsafe KAP/2 key", "E_KEY_UNSAFE")
        return key if _KEY.fullmatch(key) else json.dumps(key, ensure_ascii=False)

    def write(obj: dict[str, Any], indent: int) -> None:
        if indent // 2 > _MAX_DEPTH:
            _fail("KAP/2 nesting limit exceeded", "E_DEPTH")
        for key, field in obj.items():
            prefix = " " * indent + name(key)
            if isinstance(field, dict):
                if field:
                    lines.append(prefix + ":")
                    write(field, indent + 2)
                else:
                    lines.append(prefix + ": {}")
            elif isinstance(field, list):
                if len(field) > _MAX_ITEMS:
                    _fail("Array too large", "E_ARRAY_SIZE")
                lines.append(prefix + f"[{len(field)}]:")
                for row in field:
                    if isinstance(row, dict):
                        if not row:
                            _fail("Empty list object unsupported", "E_FIELD")
                        lines.append(" " * (indent + 2) + "-")
                        write(row, indent + 4)
                    else:
                        lines.append(" " * (indent + 2) + "- " + _scalar(row))
            elif isinstance(field, str) and "\n" in field:
                marker = "CODE"
                if any(line == marker for line in field.split("\n")):
                    marker = "KAP_LITERAL"
                if any(line == marker for line in field.split("\n")):
                    _fail("Literal marker collision", "E_LITERAL_LENGTH")
                lines.append(prefix + f"<<{marker}")
                lines.extend(field.split("\n"))
                lines.append(marker)
            else:
                lines.append(prefix + ": " + _scalar(field))
    write(value, 0)
    lines.append("K2/END")
    result = "\n".join(lines)
    if len(result.encode("utf-8")) > _MAX_BYTES or len(lines) > _MAX_LINES:
        _fail("Encoded KAP/2 limit exceeded", "E_SIZE")
    return result
