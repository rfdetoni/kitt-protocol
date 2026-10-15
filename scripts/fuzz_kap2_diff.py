#!/usr/bin/env python3
"""Deterministic KAP/2 Python ↔ TS differential test. No runtime dependencies."""
from __future__ import annotations
import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sdk/python"))
from kitt_protocol.kap2 import decode_kap2_frame  # noqa: E402
from kitt_protocol.models import ProtocolError  # noqa: E402

rng = random.Random(3202)
base = [f.read_text(encoding="utf-8") for f in sorted((ROOT / "fixtures/kap2").glob("*/*.k2"))]
if not base:
    raise SystemExit("KAP/2 corpus missing")


def mutate(text: str, variant: int) -> str:
    if variant == 0:
        return text
    if variant == 1:
        return "\ufeff" + text
    if variant == 2:
        return text.replace("\n", "\r\n")
    if variant == 3:
        return text[:-rng.randint(1, min(12, len(text)))]
    if variant == 4:
        return text.replace("\nK2/END", "\nK2 F\nK2/END")
    if variant == 5:
        return text.replace("\n", "\n\t", 1)
    if variant == 6:
        return text.replace("\n", "\n ", 1)
    if variant == 7:
        return text.replace(":", ": ", 1)
    if variant == 8:
        return text.replace("K2 F", "K2 W", 1)
    if variant == 9:
        return text + "\u00a0"
    if variant == 10:
        return text.replace("\n", "\n\a", 1)
    if variant == 11:
        return text.replace("true", '"true"').replace("false", '"false"')
    if variant == 12:
        return text.replace("K2/END", "K2/E", 1)
    if variant == 13:
        return text.replace("\n", "\n\n", 1)
    return text.replace("items[", "items[999", 1)


cases = [mutate(rng.choice(base), rng.randrange(15)) for _ in range(5000)]
process = subprocess.run(
    ["node", "scripts/kap2-batch.mjs"], cwd=ROOT,
    input=json.dumps(cases, ensure_ascii=True), text=True,
    capture_output=True, check=True, timeout=45,
)
remote = json.loads(process.stdout)
if len(remote) != len(cases):
    raise SystemExit("KAP/2 batch size mismatch")
for i, (raw, actual) in enumerate(zip(cases, remote)):
    try:
        result = {"ok": True, "frame": decode_kap2_frame(raw)}
    except ProtocolError:
        result = {"ok": False}
    if actual["ok"] != result["ok"] or result["ok"] and actual["frame"] != result["frame"]:
        raise SystemExit(f"KAP/2 differential mismatch at {i}: {raw!r}; Python={result!r}; TS={actual!r}")
print(f"KAP/2 differential: {len(cases)} seeded cases, Python ↔ TS parity OK")
