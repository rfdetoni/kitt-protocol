"""Strict black-box API contract parser; independent review remains mandatory."""
from __future__ import annotations
import hashlib
import json
import re
import unicodedata

MAX_BYTES = 65536
TOP = {"target_dll", "function_name", "signature", "calling_convention", "observed_behaviors"}
SIG = {"return_type", "parameters"}
PARAM = {"name", "c_type", "direction"}
BEHAVIOR = {"case_id", "input_conditions", "expected_return", "last_error", "side_effects"}
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,127}\Z")
DLL = re.compile(r"[A-Za-z0-9_-]{1,96}\.dll\Z")
CASE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
LEAK = [
    re.compile(r"\b(?:uvar\d*|ivar\d*|local_[0-9a-z]+|fun_[0-9a-f]+|dat_[0-9a-f]+)\b", re.I),
    re.compile(r"\b(?:rtlp[a-z0-9_]+|basep[a-z0-9_]+)\b", re.I),
    re.compile(r"\b(?:goto|sizeof|__asm|assembly|decompil\w*|disassembl\w*|stack\s*offset|stack\s*slot|register\s+[a-z0-9]+|ghidra|rizin|radare2)\b", re.I),
    re.compile(r"(?:0x[0-9a-f]{10,}|\b[A-Za-z0-9+/]{96,}={0,2}\b)", re.I),
    re.compile(r"(?:[{};]|->|/\*|\*/|\\x[0-9a-f]{2}|\\u[0-9a-f]{4}|\b(?:if\s*\(|while\s*\(|for\s*\(|return\s+|mov\s+[a-z]+\s*,))", re.I),
]


class CleanRoomContractError(ValueError):
    pass


def _pairs(pairs):
    result = {}
    for key, val in pairs:
        if key in result:
            raise CleanRoomContractError("duplicate JSON key")
        result[key] = val
    return result


def _constant(value):
    raise CleanRoomContractError("non-finite number")


def _object(value, required, label):
    if not isinstance(value, dict) or set(value) != required:
        raise CleanRoomContractError(label + ": wrong fields")


def _text(value, label, limit, pattern=None):
    if not isinstance(value, str) or not 1 <= len(value) <= limit:
        raise CleanRoomContractError(label + ": invalid length")
    if unicodedata.normalize("NFKC", value) != value:
        raise CleanRoomContractError(label + ": noncanonical Unicode")
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise CleanRoomContractError(label + ": control character")
    if pattern is not None and pattern.fullmatch(value) is None:
        raise CleanRoomContractError(label + ": invalid public identifier")
    if any(expr.search(value) for expr in LEAK):
        raise CleanRoomContractError(label + ": possible internal detail")
    return value


def validate_cleanroom_contract(value):
    """Reject unknown fields, malformed inputs and common implementation leaks."""
    _object(value, TOP, "contract")
    _text(value["target_dll"], "target_dll", 100, DLL)
    _text(value["function_name"], "function_name", 128, IDENT)
    if not isinstance(value["calling_convention"], str) or value["calling_convention"] not in {"WINAPI", "CDECL", "FASTCALL", "THISCALL"}:
        raise CleanRoomContractError("invalid calling convention")
    sig = value["signature"]
    _object(sig, SIG, "signature")
    _text(sig["return_type"], "return_type", 120)
    params = sig["parameters"]
    if not isinstance(params, list) or len(params) > 48:
        raise CleanRoomContractError("invalid parameters")
    names = set()
    for item in params:
        _object(item, PARAM, "parameter")
        name = _text(item["name"], "name", 96, IDENT)
        if name in names:
            raise CleanRoomContractError("duplicate parameter")
        names.add(name)
        _text(item["c_type"], "c_type", 120)
        if not isinstance(item["direction"], str) or item["direction"] not in {"IN", "OUT", "IN_OUT", "OPT"}:
            raise CleanRoomContractError("invalid direction")
    cases = value["observed_behaviors"]
    if not isinstance(cases, list) or not 1 <= len(cases) <= 128:
        raise CleanRoomContractError("invalid behavior cases")
    seen = set()
    for item in cases:
        _object(item, BEHAVIOR, "behavior")
        case_id = _text(item["case_id"], "case_id", 64, CASE)
        if case_id in seen:
            raise CleanRoomContractError("duplicate case_id")
        seen.add(case_id)
        for key, limit in (("input_conditions", 640), ("expected_return", 160),
                           ("last_error", 160), ("side_effects", 640)):
            _text(item[key], key, limit)
    return value


def decode_cleanroom_contract(raw):
    if isinstance(raw, str):
        raw = raw.encode("utf-8", "strict")
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise CleanRoomContractError("contract exceeds byte limit")
    try:
        data = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=_pairs,
                          parse_constant=_constant)
    except (ValueError, UnicodeError) as exc:
        raise CleanRoomContractError("invalid JSON") from exc
    return validate_cleanroom_contract(data)


def canonical_cleanroom_bytes(data):
    validate_cleanroom_contract(data)
    raw = json.dumps(data, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":"), allow_nan=False).encode("ascii")
    if len(raw) > MAX_BYTES:
        raise CleanRoomContractError("canonical contract exceeds byte limit")
    return raw


def cleanroom_digest(data):
    return hashlib.sha256(canonical_cleanroom_bytes(data)).hexdigest()
